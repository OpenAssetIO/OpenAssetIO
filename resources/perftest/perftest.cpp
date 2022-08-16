#include <chrono>
#include <functional>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <unordered_map>

#include <openassetio/Context.hpp>
#include <openassetio/TraitsData.hpp>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>

#include "lib.hpp"

namespace {
/// Number of raw test results to print before showing summary stats.
constexpr const std::size_t kResultsToShow = 5;
}  // namespace

///////////////////////////////////////////////////////////

/**
 * Test fixture for generating a simple database, a set of entity
 * references to query, and boilerplate for calling API methods.
 */
struct Fixture {
  using Inputs = std::vector<std::string>;

  // Fixture parameters:

  /// Size of "database" (map of entity ref to url) to generate.
  const std::size_t databaseSize;
  /// Size of input vector of entity refs to use for a bulk resolve().
  const std::size_t inputSize;
  /// Probability of input entity ref not being found in the database.
  const double missingFraction;

  // Test inputs:

  /// AMS "database" mapping entity refs to urls.
  const Database database = createDatabase(databaseSize);
  /// Entity references to query.
  const Inputs inputs = createInputs(databaseSize, inputSize, missingFraction);

  // Required structures for OpenAssetIO calls:

  /// The set of traits to query, "locateableContent" being the only
  /// recognized trait.
  const TraitSet traitSet = {"locateableContent", "somethingElse"};
  /// Dummy host application to call with resolve()d element.
  HostApplication hostApplication{};
  /// Context required for API methods.
  const openassetio::ContextPtr context = openassetio::Context::make();
  /// Host required for HostSession.
  openassetio::managerApi::HostPtr host =
      openassetio::managerApi::Host::make(std::make_shared<HostImpl>());
  /// HostSession required for API methods.
  const openassetio::managerApi::HostSessionPtr hostSession =
      openassetio::managerApi::HostSession::make(host, std::make_shared<LoggerImpl>());

 private:
  /// A dummy HostInterface implementation to satisfy abstract base.
  struct HostImpl : openassetio::hostApi::HostInterface {
    [[nodiscard]] openassetio::Str identifier() const override { return {}; }
    [[nodiscard]] std::string displayName() const override { return {}; }
  };
  /// A dummy LoggerInterface implementation
  struct LoggerImpl : openassetio::log::LoggerInterface {
    void log([[maybe_unused]] openassetio::log::LoggerInterface::Severity severity,
             [[maybe_unused]] const std::string& message) override {}
  };

  /// Enlarge the path so we likely exceed the small string optimization length
  static inline const std::string kSubDirectory = "0123456789_0123456789_0123456789/";

  /// Construct an entity reference.
  static std::string entityRef(const std::size_t id) {
    return "ams://" + kSubDirectory + "asset_" + std::to_string(id);
  }

  /// Construct a URL.
  static std::string entityUrl(const std::size_t id) {
    return "file://" + kSubDirectory + "asset_" + std::to_string(id);
  }

  /// Create the database that will be queried.
  static Database createDatabase(std::size_t databaseSize) {
    Database database;

    for (size_t id = 0; id < databaseSize; ++id) {
      database[entityRef(id)] = entityUrl(id);
    }
    return database;
  }

  /// Create the input entity refs that will be queried in the database.
  static Inputs createInputs(const std::size_t databaseSize, const std::size_t inputsSize,
                             const double missingFraction) {
    Inputs inputs;

    std::mt19937 mersenneTwister{std::random_device{}()};
    // Random distribution for entity ref IDs.
    std::uniform_int_distribution<std::size_t> dbDistrib(0, databaseSize - 1);
    // Random distribution for proportion of entity refs that are not
    // to be found in the database.
    std::uniform_real_distribution missingDistrib(0.0, 1.0);

    for (size_t n = 0; n < inputsSize; ++n) {
      // Random entity ref ID to to query.
      const std::size_t id = dbDistrib(mersenneTwister);
      auto ref = entityRef(id);

      if (missingDistrib(mersenneTwister) < missingFraction) {
        ref += "-missing";
      }

      inputs.push_back(std::move(ref));
    }

    return inputs;
  }
};

///////////////////////////////////////////////////////////
// Test cases:

/**
 * resolve() input entity refs to a vector, then call host application
 * with the result.
 */
void vectorResolve(Fixture& fixture) {
  VectorManagerInterface managerInterface{fixture.database};

  auto const results = managerInterface.resolve(fixture.inputs, fixture.traitSet, fixture.context,
                                                fixture.hostSession);

  for (std::size_t idx = 0; idx < fixture.inputs.size(); ++idx) {
    std::visit(
        [&](auto&& value) {
          using ValueType = std::decay_t<decltype(value)>;
          if constexpr (std::is_same_v<ValueType, openassetio::TraitsDataPtr>) {
            fixture.hostApplication.doSuccess(fixture.inputs[idx], value);
          } else if constexpr (std::is_same_v<ValueType, ErrorCodeAndMessage>) {
            fixture.hostApplication.doError(fixture.inputs[idx], value);
          }
        },
        results[idx]);
  }
}

/**
 * resolve() input entity refs through callbacks to the host application
 * with the result.
 */
void callbackResolve(Fixture& fixture) {
  CallbackManagerInterface managerInterface{fixture.database};

  managerInterface.resolve(
      fixture.inputs, fixture.traitSet, fixture.context, fixture.hostSession,
      // NOLINTNEXTLINE(performance-unnecessary-value-param)
      [&fixture](const std::size_t idx, openassetio::TraitsDataPtr traitsData) {
        fixture.hostApplication.doSuccess(fixture.inputs[idx], traitsData);
      },
      // NOLINTNEXTLINE(performance-unnecessary-value-param)
      [&fixture](const std::size_t idx, ErrorCodeAndMessage error) {
        fixture.hostApplication.doError(fixture.inputs[idx], error);
      });
}

/**
 * resolve() input entity refs through callbacks and append to vector,
 * then iterate vector and call host application with the result.
 */
void callbackResolveToVector(Fixture& fixture) {
  CallbackManagerInterface managerInterface{fixture.database};

  VectorManagerInterface::Results results(fixture.inputs.size());

  managerInterface.resolve(
      fixture.inputs, fixture.traitSet, fixture.context, fixture.hostSession,
      [&results](const std::size_t idx, openassetio::TraitsDataPtr traitsData) {
        results[idx] = std::move(traitsData);
      },
      [&results](const std::size_t idx, ErrorCodeAndMessage error) {
        results[idx] = std::move(error);
      });

  for (std::size_t idx = 0; idx < fixture.inputs.size(); ++idx) {
    std::visit(
        [&](auto&& value) {
          using ValueType = std::decay_t<decltype(value)>;
          if constexpr (std::is_same_v<ValueType, openassetio::TraitsDataPtr>) {
            fixture.hostApplication.doSuccess(fixture.inputs[idx], value);
          } else if constexpr (std::is_same_v<ValueType, ErrorCodeAndMessage>) {
            fixture.hostApplication.doError(fixture.inputs[idx], value);
          }
        },
        results[idx]);
  }
}

/**
 * resolve() input entity refs through callbacks to the host application
 * with the result, with the callback lambda hosting a large capture
 * that escapes (GCC 9.3) small-size optimisation.
 */
void callbackResolveWithLargeCapture(Fixture& fixture) {
  CallbackManagerInterface managerInterface{fixture.database};

  managerInterface.resolve(
      fixture.inputs, fixture.traitSet, fixture.context, fixture.hostSession,
      [&fixture, ssoBust = CallbackManagerInterface::kDummyData](
          // NOLINTNEXTLINE(performance-unnecessary-value-param)
          const std::size_t idx, openassetio::TraitsDataPtr traitsData) {
        fixture.hostApplication.doSuccess(fixture.inputs[idx], traitsData, ssoBust.kData[0]);
      },
      [&fixture, ssoBust = CallbackManagerInterface::kDummyData](
          const std::size_t idx,
          // NOLINTNEXTLINE(performance-unnecessary-value-param)
          ErrorCodeAndMessage error) {
        fixture.hostApplication.doError(fixture.inputs[idx], error, ssoBust.kData[0]);
      });
}

/**
 * resolve() input entity refs through function pointer callbacks to the
 * host application with the result.
 */
void callbackFnPtrResolve(Fixture& fixture) {
  CallbackFnPtrManagerInterface managerInterface{fixture.database};

  managerInterface.resolve(
      fixture.inputs, fixture.traitSet, fixture.context, fixture.hostSession,

      // NOLINTNEXTLINE(performance-unnecessary-value-param)
      [](void* userData, const std::size_t idx, openassetio::TraitsDataPtr traitsData) {
        auto* pfixture = static_cast<Fixture*>(userData);
        pfixture->hostApplication.doSuccess(pfixture->inputs[idx], traitsData);
      },
      // NOLINTNEXTLINE(performance-unnecessary-value-param)
      [](void* userData, const std::size_t idx, ErrorCodeAndMessage error) {
        auto* pfixture = static_cast<Fixture*>(userData);
        pfixture->hostApplication.doError(pfixture->inputs[idx], error);
      },
      &fixture);
}

///////////////////////////////////////////////////////////

/**
 * Utility to time the above test cases.
 */
struct Benchmarker {
 private:
  using Idx = std::size_t;
  using Epoch = std::size_t;
  using Size = std::size_t;
  using Fraction = double;
  using Duration = std::chrono::nanoseconds;
  static constexpr std::string_view kDurationSuffix = "ns";
  using Ratio = double;
  using Ratios = std::vector<Ratio>;
  using RatioPair = std::pair<Idx, Idx>;

  /**
   * Convenience to hold a test case function and its printable name.
   */
  struct Case {
    using CaseFn = void (*)(Fixture&);
    const CaseFn caseFn;
    const std::string name;
  };

  static constexpr Idx kCallbackCaseIdx = 0;
  static constexpr Idx kVectorCaseIdx = 1;
  static constexpr Idx kCallbackToVectorCaseIdx = 2;
  static constexpr Idx kCallbackFnPtrCaseIdx = 3;
  static constexpr Idx kCallbackLargeCaptureCaseIdx = 4;

  /// Cases to test.
  static inline const std::array kCases{
      Case{&callbackResolve, "callback"}, Case{&vectorResolve, "vector"},
      Case{&callbackResolveToVector, "callbackToVector"},
      Case{&callbackFnPtrResolve, "callbackFnPtr"},
      Case{&callbackResolveWithLargeCapture, "callbackLargeCapture"}};

  /// Pairs of cases to compare as ratio of their timings.
  static constexpr std::array kRatioPairs{
      RatioPair{kVectorCaseIdx, kCallbackCaseIdx},
      RatioPair{kVectorCaseIdx, kCallbackToVectorCaseIdx},
      RatioPair{kCallbackToVectorCaseIdx, kCallbackCaseIdx},
      RatioPair{kVectorCaseIdx, kCallbackFnPtrCaseIdx},
      RatioPair{kCallbackFnPtrCaseIdx, kCallbackCaseIdx},
      RatioPair{kVectorCaseIdx, kCallbackLargeCaptureCaseIdx},
      RatioPair{kCallbackLargeCaptureCaseIdx, kCallbackCaseIdx}};

  using CasesTiming = std::array<Duration, kCases.size()>;

 public:
  using CasesTimings = std::vector<CasesTiming>;

  Epoch numEpochs;
  Epoch numWarmupEpochs;
  Size databaseSize;
  Size inputSize;
  Fraction missingFraction;

  /**
   * Perform benchmark after first warming up.
   *
   * We tend to see a slowdown in the first few epochs caused by
   * caching, CPU throttling, etc.
   */
  CasesTimings benchmark() {
    // Warm up.
    for (Epoch epoch = 0; epoch < numWarmupEpochs; ++epoch) {
      executeAndMeasureAllCases();
    }

    // Do benchmark.

    CasesTimings casesTimings(numEpochs);

    for (Epoch epoch = 0; epoch < numEpochs; ++epoch) {
      casesTimings[epoch] = executeAndMeasureAllCases();
    }
    return casesTimings;
  }

  /**
   * Dump test case timings and timing ratios between them.
   */
  static void dumpTimings(const CasesTimings& timings) {
    // Calculate timing ratios.

    std::array<Ratios, kRatioPairs.size()> ratios;
    for (Idx ratioIdx = 0; ratioIdx < kRatioPairs.size(); ++ratioIdx) {
      ratios[ratioIdx] =
          calcRatios(timings, kRatioPairs[ratioIdx].first, kRatioPairs[ratioIdx].second);
    }

    // Gather spreadsheet of data.

    using Row = std::vector<double>;
    using Matrix = std::vector<Row>;
    Matrix data(timings.size());

    for (Epoch epoch = 0; epoch < data.size(); ++epoch) {
      data[epoch].resize(kCases.size() + kRatioPairs.size());

      for (Idx caseIdx = 0; caseIdx < kCases.size(); ++caseIdx) {
        data[epoch][caseIdx] = static_cast<double>(timings[epoch][caseIdx].count());
      }

      for (Idx ratioIdx = 0; ratioIdx < kRatioPairs.size(); ++ratioIdx) {
        data[epoch][kCases.size() + ratioIdx] = ratios[ratioIdx][epoch];
      }
    }

    // Column headings.

    std::cout << kCases[0].name << " (" << kDurationSuffix << ")";
    for (Idx caseIdx = 1; caseIdx < kCases.size(); ++caseIdx) {
      std::cout << ", " << kCases[caseIdx].name << " (" << kDurationSuffix << ")";
    }
    for (const auto& [numeratorCaseIdx, deominatorCaseIdx] : kRatioPairs) {
      std::cout << ", " << kCases[numeratorCaseIdx].name << "/" << kCases[deominatorCaseIdx].name;
    }
    std::cout << "\n";

    // Print spreadsheet of data.
    Idx rowIdx;
    for (rowIdx = 0; rowIdx < data.size() && rowIdx < kResultsToShow; ++rowIdx) {
      std::cout << data[rowIdx][0];
      for (std::size_t columnIdx = 1; columnIdx < data[rowIdx].size(); ++columnIdx) {
        std::cout << ", " << data[rowIdx][columnIdx];
      }
      std::cout << "\n";
    }
    if (rowIdx < data.size()) {
      std::cout << std::flush;
      std::cerr << "... skipping rest ..." << std::endl;
    }

    // Summary statistics.

    std::cout << "\n";
    std::cout << "numerator/denominator, mean, std dev\n";

    for (Idx ratioIdx = 0; ratioIdx < kRatioPairs.size(); ++ratioIdx) {
      std::cout << kCases[kRatioPairs[ratioIdx].first].name << "/"
                << kCases[kRatioPairs[ratioIdx].second].name << ", ";
      const auto& [meanRatio, stdDevRatio] = ratioStats(ratios[ratioIdx]);
      std::cout << meanRatio << ", " << stdDevRatio << "\n";
    }
  }

 private:
  /**
   * Calculate the ratios of timings for each run between two test
   * cases.
   */
  static Ratios calcRatios(const CasesTimings& timings, Idx numeratorCaseIdx,
                           Idx denominatorCaseIdx) {
    std::vector<Ratio> ratios;
    ratios.reserve(timings.size());

    for (const auto& timing : timings) {
      ratios.push_back(calcRatio(timing, numeratorCaseIdx, denominatorCaseIdx));
    }
    return ratios;
  }

  /**
   * Calculate the ratio of timings for a single run between two test
   * cases.
   */
  static constexpr Ratio calcRatio(const CasesTiming& timing, Idx numeratorCaseIdx,
                                   Idx denominatorCaseIdx) {
    return static_cast<double>(timing[numeratorCaseIdx].count()) /
           static_cast<double>(timing[denominatorCaseIdx].count());
  }

  /**
   * Calculate mean and standard deviation of given timing ratio list.
   */
  static std::pair<Ratio, Ratio> ratioStats(const Ratios& ratios) {
    const Ratio meanRatio =
        std::reduce(ratios.begin(), ratios.end(), 0.0) / static_cast<Ratio>(ratios.size());

    const Ratio stdDevRatio =
        std::sqrt(std::transform_reduce(ratios.begin(), ratios.end(), 0.0, std::plus<Ratio>{},
                                        [meanRatio](const Ratio ratio) {
                                          return (ratio - meanRatio) * (ratio - meanRatio);
                                        }) /
                  static_cast<Ratio>(ratios.size()));

    return {meanRatio, stdDevRatio};
  }

  /**
   * Perform a single run of all test cases and measure the time it
   * takes to perform.
   */
  CasesTiming executeAndMeasureAllCases() {
    CasesTiming timing;
    for (Idx caseIdx = 0; caseIdx < kCases.size(); ++caseIdx) {
      timing[caseIdx] = executeAndMeasureCase(kCases[caseIdx].caseFn);
    }
    return timing;
  }

  /**
   * Measure the time a test case function takes to execute.
   */
  Duration executeAndMeasureCase(const Case::CaseFn& func) {
    Fixture fixture{databaseSize, inputSize, missingFraction};

    const auto start = std::chrono::high_resolution_clock::now();
    func(fixture);
    const auto stop = std::chrono::high_resolution_clock::now();

    return std::chrono::duration_cast<Duration>(stop - start);
  }
};

///////////////////////////////////////////////////////////

int main(int argc, const char** argv) {  // NOLINT(bugprone-exception-escape)
  std::cerr << "CAUTION: on Windows do not run this in a Visual Studio command prompt "
            << "('x64 Native Tools Command Prompt for VS') or the measurements may fluctuate, "
            << "use a basic CMD shell" << std::endl;

  constexpr int kExpectedArgs = 6;

  if (argc < kExpectedArgs) {
    throw std::runtime_error{
        "Insufficient arguments: <num epochs> <num warmups> <database size> <query size> "
        "<fraction not found>"};
  }

  const auto numEpochs = static_cast<std::size_t>(std::atoi(argv[1]));
  const auto numWarmUpEpochs = static_cast<std::size_t>(std::atoi(argv[2]));
  const auto databaseSize = static_cast<std::size_t>(std::atoi(argv[3]));
  const auto inputSize = static_cast<std::size_t>(std::atoi(argv[4]));
  const double missingFraction = std::atof(argv[5]);

  std::cerr << "                      Epochs: " << numEpochs << std::endl;
  std::cerr << "              Warm up epochs: " << numWarmUpEpochs << std::endl;
  std::cerr << "               Database size: " << databaseSize << std::endl;
  std::cerr << "   Num inputs for bulk query: " << inputSize << std::endl;
  std::cerr << "Fraction of inputs not found: " << missingFraction << std::endl;

  Benchmarker benchmarker{numEpochs, numWarmUpEpochs, databaseSize, inputSize, missingFraction};

  std::cerr << "Begin benchmark..." << std::endl;

  // Perform benchmarking loop.

  const Benchmarker::CasesTimings timings = benchmarker.benchmark();

  // Dump the output.

  Benchmarker::dumpTimings(timings);
}
