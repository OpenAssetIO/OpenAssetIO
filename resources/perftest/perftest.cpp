#include <iostream>
#include <chrono>
#include <functional>
#include <random>
#include <string>
#include <algorithm>
#include <unordered_map>

#include <openassetio/TraitsData.hpp>
#include <openassetio/trait/TraitBase.hpp>
using namespace openassetio; // NOLINT(google-build-using-namespace)

constexpr size_t kNIterations = 100000;
const size_t kDbSize = 1000000;

std::chrono::nanoseconds measureRuntime(const std::function<void(void)>& func)
{
  const auto start = std::chrono::high_resolution_clock::now();
  func();
  const auto stop = std::chrono::high_resolution_clock::now();
  return stop - start;
}

auto measureRuntimeMs(const std::function<void(void)>& func)
{
  return std::chrono::duration_cast<std::chrono::milliseconds>(measureRuntime(func)).count();
}

///////////////////////////////////////////////////////////
/// Enlarge the path so we likely exceed the small string optimization length
const std::string kSubDirectory = "0123456789_0123456789_0123456789/";

std::string getEntityReference(size_t i)
{
  return "ams://" + kSubDirectory + "myasset_" + std::to_string(i);
}

std::string getPrimaryString(size_t i)
{
  return "file://" + kSubDirectory + "myasset_" + std::to_string(i);
}

///////////////////////////////////////////////////////////
struct BlobTrait : trait::TraitBase<BlobTrait> {

  static inline const trait::TraitId kId{"blob"};
  static inline const trait::property::Key kUrl{"url"};

  using TraitBase<BlobTrait>::TraitBase;

  [[nodiscard]] trait::TraitPropertyStatus getUrl(Str* out) const {
    return getTraitProperty(out, kId, kUrl);
  }

  void setUrl(Str url) {
    data()->setTraitProperty(kId, kUrl, std::move(url));
  }
};

///////////////////////////////////////////////////////////
class OldManagerInterface
{
public:
  explicit OldManagerInterface(const std::unordered_map<std::string, std::string>& refToPrimStrs) : refToPrimStrs_{refToPrimStrs} {}
  std::string resolveEntityReference(const std::string& ref);

private:
  const std::unordered_map<std::string, std::string>& refToPrimStrs_;
};

std::string OldManagerInterface::resolveEntityReference(const std::string& ref)
{
  return refToPrimStrs_.at(ref);
}

///////////////////////////////////////////////////////////
auto benchmarkOldManager(const std::unordered_map<std::string, std::string>& refToPrimStrs, const std::vector<std::string>& refs)
{
  OldManagerInterface oldMgr(refToPrimStrs);

  const auto doLookups = [&oldMgr, &refs]() {
    for(size_t i = 0; i < kNIterations; ++i) {
      const auto& ref = refs[i];
      [[maybe_unused]] const auto& _ = oldMgr.resolveEntityReference(ref);
    }
  };

  return measureRuntimeMs(doLookups);
}

///////////////////////////////////////////////////////////
class NewManagerInterface
{
public:
  explicit NewManagerInterface(const std::unordered_map<std::string, std::string>& refToPrimStrs) : refToPrimStrs_{refToPrimStrs} {}
  std::shared_ptr<TraitsData> resolve(const std::string& ref, const TraitsData::TraitSet& traitSet);

private:
  const std::unordered_map<std::string, std::string>& refToPrimStrs_;
};

std::shared_ptr<TraitsData> NewManagerInterface::resolve(const std::string& ref, const TraitsData::TraitSet& traitSet)
{
  TraitsData::TraitSet populatedTraits;
  bool getPath = false;
  if(std::find(traitSet.cbegin(), traitSet.cend(), BlobTrait::kId) != traitSet.cend()) {
    populatedTraits.insert(BlobTrait::kId);
    getPath = true;
  }
  auto result = std::make_shared<TraitsData>(populatedTraits);
  if(getPath) {
    BlobTrait btrait(result);
    btrait.setUrl(refToPrimStrs_.at(ref));
  }
  return result;
}

///////////////////////////////////////////////////////////
auto benchmarkNewManager(const std::unordered_map<std::string, std::string>& refToPrimStrs, const std::vector<std::string>& refs)
{
  NewManagerInterface newMgr(refToPrimStrs);

  const auto doLookups = [&newMgr, &refs]() {
    for(size_t i = 0; i < kNIterations; ++i) {
      const auto& ref = refs[i];
      const auto spec = newMgr.resolve(ref, {BlobTrait::kId});
      BlobTrait btrait(spec);
      Str url;
      [[maybe_unused]] const auto _ = btrait.getUrl(&url);
    }
  };

  return measureRuntimeMs(doLookups);
}

///////////////////////////////////////////////////////////
int main()
{
  try { // bugprone-exception-escape
    std::cout << "CAUTION: on Windows do not run this in a Visual Studio command prompt "
      << "('x64 Native Tools Command Prompt for VS') or the measurements may fluctuate, "
      << "use a basic CMD shell" << std::endl;

    std::cout << "       Iterations: " << kNIterations << std::endl;
    std::cout << "AMS database size: " << kDbSize << std::endl;

    // Set up database
    std::unordered_map<std::string, std::string> refToPrimStrs;
    for(size_t i = 0; i < kDbSize; ++i) {
      refToPrimStrs[getEntityReference(i)] = getPrimaryString(i);
    }

    // Set up a list of random refs we want to look up
    std::vector<std::string> refs;
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> randAssetIndexDistrib(0, kDbSize - 1);
    for(size_t i = 0; i < kNIterations; ++i) {
      const auto rnd = size_t(randAssetIndexDistrib(gen));
      refs.emplace_back(getEntityReference(rnd));
    }

    const auto oldTime = benchmarkOldManager(refToPrimStrs, refs);
    std::cout << "resolveEntityReference: " << oldTime << " ms" << std::endl;

    const auto newTime = benchmarkNewManager(refToPrimStrs, refs);
    std::cout << "resolve: " << newTime << " ms" << std::endl;
  } catch (...) { }
}
