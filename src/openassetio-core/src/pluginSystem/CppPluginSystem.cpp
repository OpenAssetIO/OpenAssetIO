// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 The Foundry Visionmongers Ltd
// Copyright Contributors to the OpenImageIO project.
// Much of the cross-platform code below is taken and modified from the
// OpenImageIO project.

#ifdef _WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#endif

#include <filesystem>

#include <fmt/format.h>

#include <openassetio/errors/exceptions.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystem.hpp>
#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

namespace {
constexpr const char* kEntrypointFnName = "openassetioPlugin";

#if defined(_WIN32)
// Dummy values
#define RTLD_LAZY 0
#define RTLD_LOCAL 0

void* dlopen(const char* filename, int) {
  const std::string_view filename_u8{filename};
  const int size =
      MultiByteToWideChar(CP_UTF8, 0, filename_u8.data(), filename_u8.size(), NULL, 0);
  std::wstring filename_w(size, 0);
  MultiByteToWideChar(CP_UTF8, 0, filename_u8.data(), filename_u8.size(), filename_w.data(), size);
  return LoadLibraryW(filename_w.c_str());
}

bool dlclose(void* handle) { return FreeLibrary(static_cast<HMODULE>(plugin_handle)) != 0; }

void* dlsym(void* handle, const char* symbol) {
  return static_cast<void*>(GetProcAddress(static_cast<HMODULE>(handle), symbol));
}

std::string dlerror() {
  LPVOID lpMsgBuf{};
  std::string win32Error;
  if (FormatMessageA(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM |
                         FORMAT_MESSAGE_IGNORE_INSERTS,
                     NULL, GetLastError(), MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
                     (LPSTR)&lpMsgBuf, 0, NULL)) {
    win32Error = (LPSTR)lpMsgBuf;
  }
  LocalFree(lpMsgBuf);
  return win32Error;
}
#endif

#if defined(_WIN32)
constexpr std::string_view kLibExt = ".dll";
constexpr char kPathSep = ';';
#else
constexpr std::string_view kLibExt = ".so";
constexpr char kPathSep = ':';
#endif
}  // namespace

CppPluginSystemPtr CppPluginSystem::make(log::LoggerInterfacePtr logger) {
  return std::shared_ptr<CppPluginSystem>(new CppPluginSystem{std::move(logger)});
}

void CppPluginSystem::reset() {
  // Note: do not dlclose plugins - they may be in use.
  plugins_.clear();
}

CppPluginSystem::CppPluginSystem(log::LoggerInterfacePtr logger) : logger_{std::move(logger)} {}

void CppPluginSystem::scan(std::string_view paths) {
  std::size_t pathsStartIdx = 0;
  std::size_t pathsEndIdx = 0;

  // Loop through each path in ';'/:'-delimited paths string.
  while ((pathsStartIdx = paths.find_first_not_of(kPathSep, pathsEndIdx)) != std::string::npos) {
    pathsEndIdx = paths.find(kPathSep, pathsStartIdx);
    const std::filesystem::path directoryPath =
        paths.substr(pathsStartIdx, pathsEndIdx - pathsStartIdx);

    if (!std::filesystem::is_directory(directoryPath)) {
      logger_->debug(fmt::format("CppPluginSystem: Skipping as not a directory '{}'",
                                 directoryPath.string()));
      continue;
    }

    for (const std::filesystem::directory_entry& directoryEntry :
         std::filesystem::directory_iterator{directoryPath}) {
      std::filesystem::path filePath = directoryEntry.path();

      if (MaybeIdentifierAndPlugin idAndPlugin = maybeLoadPlugin(filePath)) {
        logger_->debug(fmt::format("CppPluginSystem: Registered plug-in '{}' from '{}'",
                                   idAndPlugin->first, filePath.string()));
        plugins_[std::move(idAndPlugin->first)] = {std::move(filePath),
                                                   std::move(idAndPlugin->second)};
      }
    }
  }
}

std::vector<openassetio::Str> CppPluginSystem::identifiers() const {
  std::vector<openassetio::Str> result;
  result.reserve(plugins_.size());
  std::transform(begin(plugins_), end(plugins_), std::back_inserter(result),
                 [](const auto& iter) { return iter.first; });
  return result;
}

CppPluginSystem::PathAndPlugin CppPluginSystem::plugin(const Identifier& identifier) const {
  const auto iter = plugins_.find(identifier);
  if (iter == plugins_.end()) {
    throw errors::InputValidationException{fmt::format(
        "CppPluginSystem: No plug-in registered with the identifier '{}'", identifier)};
  }

  return iter->second;
}

CppPluginSystem::MaybeIdentifierAndPlugin CppPluginSystem::maybeLoadPlugin(
    const std::filesystem::path& filePath) {
  if (!std::filesystem::is_regular_file(filePath)) {
    logger_->debug(fmt::format("CppPluginSystem: Ignoring as it is not a library binary '{}'",
                               filePath.string()));
    return {};
  }

  if (filePath.extension() != kLibExt) {
    logger_->debug(fmt::format("CppPluginSystem: Ignoring as it is not a library binary '{}'",
                               filePath.string()));
    return {};
  }

  // Open the binary.
  void* handle;
  try {
    handle = dlopen(filePath.c_str(), RTLD_LAZY | RTLD_LOCAL);
    if (!handle) {
      logger_->debug(fmt::format("CppPluginSystem: Failed to open library '{}': {}",
                                 filePath.string(), dlerror()));
      return {};
    }
  } catch (const std::exception& exc) {
    logger_->debug(
        fmt::format("CppPluginSystem: Caught exception during static initialisation of '{}': {}",
                    filePath.string(), exc.what()));
    return {};
  } catch (...) {
    logger_->debug(
        fmt::format("CppPluginSystem: Caught exception during static initialisation of '{}':"
                    " <unknown non-exception value caught>",
                    filePath.string()));
    return {};
  }

  // Get the entrypoint function.
  void* entrypoint = dlsym(handle, kEntrypointFnName);
  if (!entrypoint) {
    logger_->debug(fmt::format("CppPluginSystem: No top-level '{}' function in '{}': {}",
                               kEntrypointFnName, filePath.string(), dlerror()));
    dlclose(handle);
    return {};
  }

  // Load the plugin object.
  CppPluginSystemPluginPtr plugin;
  try {
    plugin = reinterpret_cast<CppPluginSystemPluginPtr (*)()>(entrypoint)();
  } catch (const std::exception& exc) {
    logger_->debug(fmt::format("CppPluginSystem: Caught exception calling '{}' of '{}': {}",
                               kEntrypointFnName, filePath.string(), exc.what()));
    dlclose(handle);
    return {};
  } catch (...) {
    logger_->debug(
        fmt::format("CppPluginSystem: Caught exception calling '{}' of '{}':"
                    " <unknown non-exception value caught>",
                    kEntrypointFnName, filePath.string()));
    dlclose(handle);
    return {};
  }

  openassetio::Identifier identifier = plugin->identifier();

  // Ensure it's not already been registered.
  if (const auto iter = plugins_.find(identifier); iter != plugins_.end()) {
    logger_->debug(
        fmt::format("CppPluginSystem: Skipping '{}' defined in '{}'. Already registered by '{}'",
                    identifier, filePath.string(), iter->second.first.string()));
    plugin.reset();  // Must destroy _before_ closing lib.
    dlclose(handle);
    return {};
  }

  return {{std::move(identifier), std::move(plugin)}};
}
}  // namespace pluginSystem
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
