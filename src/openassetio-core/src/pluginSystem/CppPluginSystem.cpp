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

void* dlopen(const wchar_t* filename, int) { return LoadLibraryW(filename); }

bool dlclose(void* handle) { return FreeLibrary(static_cast<HMODULE>(handle)) != 0; }

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

void CppPluginSystem::scan(const std::string_view paths) {
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

  void* handle{nullptr};

  // Open the binary.
  //
  // Use RTLD_LOCAL to avoid pollution of global namespace, and to
  // better match Windows behaviour (which ignores the flags, see
  // above).
  //
  // Note that this is considered a `noexcept` operation. On GCC it is
  // hackily possible to catch exceptions at static initialization time,
  // but is UB.
  handle = dlopen(filePath.c_str(), RTLD_LAZY | RTLD_LOCAL);

  if (!handle) {
    logger_->debug(fmt::format("CppPluginSystem: Failed to open library '{}': {}",
                               filePath.string(), dlerror()));
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
  //
  // Note that this is considered a `noexcept` operation. This is for
  // the best cross-platform consistency. I.e. By default, POSIX can
  // support exceptions from both the initial entrypoint function
  // and from the PluginFactory function pointer. Windows
  // cannot support exceptions (fatal "access violation") from either.
  CppPluginSystemPluginPtr plugin = reinterpret_cast<PluginFactory (*)()>(entrypoint)()();

  if (!plugin) {
    logger_->debug(
        fmt::format("CppPluginSystem: Null plugin returned by '{}'", filePath.string()));

    dlclose(handle);
    return {};
  }

  // Get plugin's unique identifier.
  openassetio::Identifier identifier;
  try {
    identifier = plugin->identifier();
  } catch (const std::exception& exc) {
    logger_->debug(
        fmt::format("CppPluginSystem: Caught exception calling 'identifier' of '{}': {}",
                    filePath.string(), exc.what()));
    plugin.reset();
  } catch (...) {
    logger_->debug(
        fmt::format("CppPluginSystem: Caught exception calling 'identifier' of '{}':"
                    " <unknown non-exception value caught>",
                    filePath.string()));
    plugin.reset();
  }
  // Must wait til after try-catch to close handle, since exception
  // object needs a chance to destruct whilst the plugin binary is still
  // loaded.
  if (!plugin) {
    dlclose(handle);
    return {};
  }

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
