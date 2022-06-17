// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
#include "lib.hpp"

void openassetio::LocateableContentTrait::setUrl(openassetio::Str url) {
  data()->setTraitProperty(kId, kUrl, std::move(url));
}

VectorManagerInterface::Results VectorManagerInterface::resolve(
    const EntityRefs& entityRefs, const TraitSet& traitSet,
    [[maybe_unused]] const openassetio::ContextPtr& context,
    [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession) {
  Results results(entityRefs.size());

  for (std::size_t idx = 0; idx < entityRefs.size(); ++idx) {
    const auto iter = database.find(entityRefs[idx]);

    if (iter == database.end()) {
      results[idx] = ErrorCodeAndMessage{kErrorInvalidEntityReference, "not found in database"};

    } else {
      auto traitsData = std::make_shared<openassetio::TraitsData>();

      for (const auto& traitId : traitSet) {
        if (traitId == openassetio::LocateableContentTrait::kId) {
          openassetio::LocateableContentTrait{traitsData}.setUrl(iter->second);
        }
      }
      results[idx] = std::move(traitsData);
    }
  }

  return results;
}

void CallbackManagerInterface::resolve(
    const EntityRefs& entityRefs, const TraitSet& traitSet,
    [[maybe_unused]] const openassetio::ContextPtr& context,
    [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession,
    const SuccessCallback& successCallback, const ErrorCallback& errorCallback) {
  for (std::size_t idx = 0; idx < entityRefs.size(); ++idx) {
    const auto iter = database.find(entityRefs[idx]);

    if (iter == database.end()) {
      errorCallback(idx,
                    ErrorCodeAndMessage{kErrorInvalidEntityReference, "not found in database"});

    } else {
      auto traitsData = std::make_shared<openassetio::TraitsData>();

      for (const auto& traitId : traitSet) {
        if (traitId == openassetio::LocateableContentTrait::kId) {
          openassetio::LocateableContentTrait{traitsData}.setUrl(iter->second);
        }
      }

      successCallback(idx, std::move(traitsData));
    }
  }
}

const CallbackManagerInterface::DummyData CallbackManagerInterface::kDummyData{};

void CallbackFnPtrManagerInterface::resolve(
    const EntityRefs& entityRefs, const TraitSet& traitSet,
    [[maybe_unused]] const openassetio::ContextPtr& context,
    [[maybe_unused]] const openassetio::managerApi::HostSessionPtr& hostSession,
    const SuccessCallback successCallback, const ErrorCallback errorCallback, void* userData) {
  for (std::size_t idx = 0; idx < entityRefs.size(); ++idx) {
    const auto iter = database.find(entityRefs[idx]);

    if (iter == database.end()) {
      errorCallback(userData, idx,
                    ErrorCodeAndMessage{kErrorInvalidEntityReference, "not found in database"});

    } else {
      auto traitsData = std::make_shared<openassetio::TraitsData>();

      for (const auto& traitId : traitSet) {
        if (traitId == openassetio::LocateableContentTrait::kId) {
          openassetio::LocateableContentTrait{traitsData}.setUrl(iter->second);
        }
      }

      successCallback(userData, idx, std::move(traitsData));
    }
  }
}

// NOLINTNEXTLINE(readability-convert-member-functions-to-static)
void HostApplication::doSuccess(const EntityRef& entityRef,
                                const openassetio::TraitsDataPtr& traitsData, char otherData) {
  (void)entityRef;
  (void)traitsData;
  (void)otherData;
}

// NOLINTNEXTLINE(readability-convert-member-functions-to-static)
void HostApplication::doError(const EntityRef& entityRef, const ErrorCodeAndMessage& error,
                              char otherData) {
  (void)entityRef;
  (void)error;
  (void)otherData;
}
