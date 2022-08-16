// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#pragma once

#include <functional>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <variant>
#include <vector>

#include <openassetio/Context.hpp>
#include <openassetio/TraitsData.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/trait/TraitBase.hpp>

#include <perftest/export.h>

using Database = std::unordered_map<std::string, std::string>;
using TraitSet = std::unordered_set<std::string>;
using EntityRef = std::string;
using EntityRefs = std::vector<EntityRef>;

/**
 * Error value type.
 */
struct ErrorCodeAndMessage {
  int code;
  std::string message;
};
constexpr int kErrorInvalidEntityReference = 123;

/**
 * Dummy pretend host application that has some methods to handle
 * success and error cases of individual entity references coming from
 * a bulk resolve().
 */
struct OPENASSETIO_PERFTEST_LIB_EXPORT HostApplication {
  void doSuccess(const EntityRef& entityRef, const openassetio::TraitsDataPtr& traitsData,
                 char otherData = 0);

  void doError(const EntityRef& entityRef, const ErrorCodeAndMessage& error, char otherData = 0);
};

namespace openassetio {
/**
 * A "locateableContent" trait to use for resolve() queries.
 */
struct LocateableContentTrait : trait::TraitBase<LocateableContentTrait> {
  static inline const trait::TraitId kId{"locateableContent"};
  static inline const trait::property::Key kUrl{"url"};

  using TraitBase<LocateableContentTrait>::TraitBase;

  void setUrl(std::string url);
};
}  // namespace openassetio

///////////////////////////////////////////////////////////

/**
 * A ManagerInterface with a resolve() that returns a vector of results.
 */
struct OPENASSETIO_PERFTEST_LIB_EXPORT VectorManagerInterface {
  using ResultOrError = std::variant<openassetio::TraitsDataPtr, ErrorCodeAndMessage>;
  using Results = std::vector<ResultOrError>;

  const Database& database;

  Results resolve(const EntityRefs& entityRefs, const TraitSet& traitSet,
                  [[maybe_unused]] const openassetio::ContextPtr& context,
                  [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession);
};

///////////////////////////////////////////////////////////

/**
 * A ManagerInterface with a resolve() that executes a std::function
 * callback on each result.
 */
struct OPENASSETIO_PERFTEST_LIB_EXPORT CallbackManagerInterface {
  using SuccessCallback = std::function<void(std::size_t, openassetio::TraitsDataPtr)>;
  using ErrorCallback = std::function<void(std::size_t, ErrorCodeAndMessage)>;

  const Database& database;

  /**
   * Dummy data for busting small object optimisation in std::function.
   *
   * Initialised in .cpp to avoid any inlining/stripping shenanigans.
   *
   * Experimentally determined that std::function in GCC 9.3 has a 16
   * byte SSO (and aligns at 8 byte boundaries, an 8 byte pointer plus 9
   * bytes would give a sizeof of 24 bytes). So the following data plus
   * any other capture results in a busted SSO.
   */
  struct DummyData {
    const char kData[16] = {0};
  };
  static const DummyData kDummyData;

  void resolve(const EntityRefs& entityRefs, const TraitSet& traitSet,
               [[maybe_unused]] const openassetio::ContextPtr& context,
               [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession,
               const SuccessCallback& successCallback, const ErrorCallback& errorCallback);
};

/**
 * A ManagerInterface with a resolve() that executes a function pointer
 * callback on each result.
 */
struct OPENASSETIO_PERFTEST_LIB_EXPORT CallbackFnPtrManagerInterface {
  using SuccessCallback = void (*)(void* userData, std::size_t, openassetio::TraitsDataPtr);
  using ErrorCallback = void (*)(void* userData, std::size_t, ErrorCodeAndMessage);

  const Database& database;

  void resolve(const EntityRefs& entityRefs, const TraitSet& traitSet,
               [[maybe_unused]] const openassetio::ContextPtr& context,
               [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession,
               SuccessCallback successCallback, ErrorCallback errorCallback, void* userData);
};
