#include <iostream>
#include <chrono>
#include <functional>
#include <random>
#include <string>
#include <algorithm>

#include <openassetio/specification/Specification.hpp>
#include <openassetio/trait/TraitBase.hpp>
using namespace openassetio;

constexpr size_t nIterations = 100000;
const size_t dbSize = 1000000;

std::chrono::nanoseconds MeasureRuntime(std::function<void(void)> func)
{
  const auto start = std::chrono::high_resolution_clock::now();
  func();
  const auto stop = std::chrono::high_resolution_clock::now();
  return stop - start;
}

auto MeasureRuntimeMs(std::function<void(void)> func)
{
  return std::chrono::duration_cast<std::chrono::milliseconds>(MeasureRuntime(func)).count();
}

///////////////////////////////////////////////////////////
/// Enlarge the path so we likely exceed the small string optimization length
const std::string kSubDirectory = "0123456789_0123456789_0123456789/";

std::string getEntityReference(size_t i) 
{
  return std::string("ams://" + kSubDirectory + "myasset_") + std::to_string(i);
}

std::string getPrimaryString(size_t i) 
{
  return std::string("file://" + kSubDirectory + "myasset_") + std::to_string(i);
}

///////////////////////////////////////////////////////////
struct BlobTrait : trait::TraitBase<BlobTrait> {

  static inline const trait::TraitId kId{"blob"};
  static inline const trait::property::Key kUrl{"url"};

  using TraitBase<BlobTrait>::TraitBase;

  [[nodiscard]] trait::TraitPropertyStatus getUrl(trait::property::Str* out) const {
    return getTraitProperty(out, kId, kUrl);
  }

  void setUrl(trait::property::Str url) {
    specification()->setTraitProperty(kId, kUrl, std::move(url));
  }
};

///////////////////////////////////////////////////////////
class OldManagerInterface
{
public:
  OldManagerInterface(const std::unordered_map<std::string, std::string>& refToPrimStrs) : refToPrimStrs{refToPrimStrs} {}
  std::string resolveEntityReference(const std::string& ref);

private:
  const std::unordered_map<std::string, std::string>& refToPrimStrs;
};

std::string OldManagerInterface::resolveEntityReference(const std::string& ref)
{
  return refToPrimStrs.at(ref);
}

///////////////////////////////////////////////////////////
auto benchmarkOldManager(const std::unordered_map<std::string, std::string>& refToPrimStrs, const std::vector<std::string>& refs)
{
  OldManagerInterface oldMgr(refToPrimStrs);

  const auto doLookups = [&oldMgr, &refs]() {
    for(size_t i = 0; i < nIterations; ++i) {
      const auto& ref = refs[i];
      const auto& primStr = oldMgr.resolveEntityReference(ref);
    }
  };

  return MeasureRuntimeMs(doLookups);
}

///////////////////////////////////////////////////////////
class NewManagerInterface
{
public:
  NewManagerInterface(const std::unordered_map<std::string, std::string>& refToPrimStrs) : refToPrimStrs{refToPrimStrs} {}
  std::shared_ptr<specification::Specification> resolve(const std::string& ref, const specification::Specification::TraitIds& traitIds);

private:
  const std::unordered_map<std::string, std::string>& refToPrimStrs;
};

std::shared_ptr<specification::Specification> NewManagerInterface::resolve(const std::string& ref, const specification::Specification::TraitIds& traitIds)
{
  specification::Specification::TraitIds populatedTraits;
  bool getPath = false;
  if(std::find(traitIds.cbegin(), traitIds.cend(), BlobTrait::kId) != traitIds.cend()) {
    populatedTraits.insert(BlobTrait::kId);
    getPath = true;
  }
  auto result = std::make_shared<specification::Specification>(populatedTraits);
  if(getPath) {
    BlobTrait btrait(result);
    btrait.setUrl(refToPrimStrs.at(ref));
  }
  return result;
}

///////////////////////////////////////////////////////////
auto benchmarkNewManager(const std::unordered_map<std::string, std::string>& refToPrimStrs, const std::vector<std::string>& refs)
{
  NewManagerInterface newMgr(refToPrimStrs);

  const auto doLookups = [&newMgr, &refs]() {
    for(size_t i = 0; i < nIterations; ++i) {
      const auto& ref = refs[i];
      const auto spec = newMgr.resolve(ref, {BlobTrait::kId});
      BlobTrait btrait(spec);
      trait::property::Str url;
      const auto success = btrait.getUrl(&url);
    }
  };

  return MeasureRuntimeMs(doLookups);
}

///////////////////////////////////////////////////////////
int main()
{
  std::cout << "CAUTION: on Windows do not run this in a Visual Studio command prompt "
    << "('x64 Native Tools Command Prompt for VS') or the measurements may fluctuate, "
    << "use a basic CMD shell" << std::endl;

  std::cout << "       Iterations: " << nIterations << std::endl;
  std::cout << "AMS database size: " << dbSize << std::endl;

  // Set up database
  std::unordered_map<std::string, std::string> refToPrimStrs;
  for(size_t i = 0; i < dbSize; ++i) {
    refToPrimStrs[getEntityReference(i)] = getPrimaryString(i);
  }

  // Set up a list of random refs we want to look up
  std::vector<std::string> refs;
  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> randAssetIndexDistrib(0, dbSize - 1);
  for(size_t i = 0; i < nIterations; ++i) {
    const auto rnd = randAssetIndexDistrib(gen);
    refs.emplace_back(getEntityReference(rnd));
  }

  const auto oldTime = benchmarkOldManager(refToPrimStrs, refs);
  std::cout << "resolveEntityReference: " << oldTime << " ms" << std::endl;

  const auto newTime = benchmarkNewManager(refToPrimStrs, refs);
  std::cout << "resolve: " << newTime << " ms" << std::endl;
}
