// SPDX-License-Identifier: Apache-2.0
// Copyright 2024-2025 The Foundry Visionmongers Ltd
// Copyright Contributors to the OpenImageIO project.
// Much of the cross-platform code below is taken and modified from the
// OpenImageIO project.

#include <algorithm>
#include <cstddef>
#include <exception>
#include <filesystem>
#include <iterator>
#include <memory>
#include <string>
#include <string_view>
#include <utility>
#ifdef _WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#endif

#include <fmt/core.h>

#include <openassetio/export.h>
#include <openassetio/errors/exceptions.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/pluginSystem/CppPluginSystem.hpp>
#include <openassetio/pluginSystem/CppPluginSystemPlugin.hpp>
#include <openassetio/typedefs.hpp>

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace pluginSystem {

namespace {
#if defined(_WIN32)
// Dummy values
#define RTLD_LAZY 0
#define RTLD_LOCAL 0

/**
 * Implement POSIX dlopen for Windows.
 *
 * For unicode support, using wchar_t / LoadLibraryW. Handily, on
 * Windows std::filesystem::path::c_str returns a wchar_t*, so the
 * divergence between POSIX/Windows dlopen and path::c_str marries up
 * appropriately for the platform.
 *
 * Note that the second parameter, the RTLD_ mode, is ignored. Windows
 * approximates RTLD_LOCAL.
 */
void* dlopen(const wchar_t* filename, [[maybe_unused]] int mode) { return LoadLibraryW(filename); }

/**
 * Implement POSIX dlclose for Windows.
 */
bool dlclose(void* handle) { return FreeLibrary(static_cast<HMODULE>(handle)) != 0; }

/**
 * Implement POSIX dlsym for Windows.
 */
void* dlsym(void* handle, const char* symbol) {
  return static_cast<void*>(GetProcAddress(static_cast<HMODULE>(handle), symbol));
}

/**
 * Implement POSIX dlerror for Windows.
 *
 * Diverge from POSIX by returning a std::string rather than char*, so
 * we don't have to worry about keeping track of global state. Handlily,
 * all our usages of dlerror can accept either a std::string or a char*
 * so it works cross-platform.
 */
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
// Shared module library file extension.
constexpr std::string_view kLibExt = ".dll";
// Path separator for encoding multiple search paths in a single string.
constexpr char kPathSep = ';';
#else
// Shared module library file extension.
constexpr std::string_view kLibExt = ".so";
// Path separator for encoding multiple search paths in a single string.
constexpr char kPathSep = ':';
#endif
}  // namespace

CppPluginSystemPtr CppPluginSystem::make(log::LoggerInterfacePtr logger) {
  return std::make_shared<CppPluginSystem>(CppPluginSystem{std::move(logger)});
}

void CppPluginSystem::reset() {
  // Note: do not dlclose plugins - they may be in use.
  plugins_.clear();
}

CppPluginSystem::CppPluginSystem(log::LoggerInterfacePtr logger) : logger_{std::move(logger)} {}

// NOLINTNEXTLINE(bugprone-easily-swappable-parameters)
void CppPluginSystem::scan(const std::string_view paths, const std::string_view moduleHookName) {
  std::size_t pathsStartIdx = 0;
  std::size_t pathsEndIdx = 0;

  // Loop through each path in ';'/:'-delimited paths string.
  while ((pathsStartIdx = paths.find_first_not_of(kPathSep, pathsEndIdx)) != std::string::npos) {
    pathsEndIdx = paths.find(kPathSep, pathsStartIdx);
    const std::filesystem::path directoryPath =
        paths.substr(pathsStartIdx, pathsEndIdx - pathsStartIdx);

    // Check the provided path is actually a searchable directory.
    if (!is_directory(directoryPath)) {
      logger_->debug(fmt::format("CppPluginSystem: Skipping as not a directory '{}'",
                                 directoryPath.string()));
      continue;
    }

    // Loop each item in the provided search path.
    for (const std::filesystem::directory_entry& directoryEntry :
         std::filesystem::directory_iterator{directoryPath}) {
      std::filesystem::path filePath = directoryEntry.path();

      // Assume the item in the search path is a plugin file and attempt
      // to load it.
      if (MaybeIdentifierAndPlugin idAndPlugin = maybeLoadPlugin(filePath, moduleHookName)) {
        logger_->debug(fmt::format("CppPluginSystem: Registered plug-in '{}' from '{}'",
                                   idAndPlugin->first, filePath.string()));
        // Register the successfully loaded plugin.
        plugins_[std::move(idAndPlugin->first)] = {std::move(filePath),
                                                   std::move(idAndPlugin->second)};
      }
    }
  }
}

Identifiers CppPluginSystem::identifiers() const {
  Identifiers result;
  result.reserve(plugins_.size());
  std::transform(begin(plugins_), end(plugins_), std::back_inserter(result),
                 [](const auto& iter) { return iter.first; });
  return result;
}

const CppPluginSystem::PathAndPlugin& CppPluginSystem::plugin(const Identifier& identifier) const {
  const auto iter = plugins_.find(identifier);
  if (iter == plugins_.end()) {
    throw errors::InputValidationException{fmt::format(
        "CppPluginSystem: No plug-in registered with the identifier '{}'", identifier)};
  }

  return iter->second;
}

CppPluginSystem::MaybeIdentifierAndPlugin CppPluginSystem::maybeLoadPlugin(
    const std::filesystem::path& filePath, const std::string_view moduleHookName) {
  // Check the proposed path is actually a file.
  if (!is_regular_file(filePath)) {
    logger_->debug(fmt::format("CppPluginSystem: Ignoring as it is not a library binary '{}'",
                               filePath.string()));
    return {};
  }

  // Check the proposed file name looks like a shared library.
  if (filePath.extension() != kLibExt) {
    logger_->debug(fmt::format("CppPluginSystem: Ignoring as it is not a library binary '{}'",
                               filePath.string()));
    return {};
  }

  // Open the binary.
  //
  // Use RTLD_LOCAL to avoid pollution of global namespace, and to
  // better match Windows behaviour (which ignores the flags, see
  // above).
  //
  // Note that this is considered a `noexcept` operation. On GCC it is
  // hackily possible to catch exceptions at static initialization time,
  // but is UB.
  void* handle = dlopen(filePath.c_str(), RTLD_LAZY | RTLD_LOCAL);

  if (!handle) {
    logger_->debug(fmt::format("CppPluginSystem: Failed to open library '{}': {}",
                               filePath.string(), dlerror()));
    return {};
  }

  // Get the entrypoint function.
  // NOLINTNEXTLINE(*-suspicious-stringview-data-usage)
  void* entrypoint = dlsym(handle, moduleHookName.data());
  if (!entrypoint) {
    logger_->debug(fmt::format("CppPluginSystem: No top-level '{}' function in '{}': {}",
                               moduleHookName, filePath.string(), dlerror()));
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

  // The entry point function should be a no-argument function that
  // returns a function pointer. I.e. a factory function for creating a
  // PluginFactory.
  // NOLINTNEXTLINE(cppcoreguidelines-pro-type-reinterpret-cast)
  const auto pluginFactoryFactory = reinterpret_cast<PluginFactory (*)()>(entrypoint);

  // Calling the entry point function yields a PluginFactory function
  // pointer. As noted above, this is a `noexcept` operation.
  const PluginFactory pluginFactory = pluginFactoryFactory();

  // Finally, we get the actual plugin object from the factory function
  // pointer. Again, this is a `noexcept` operation.
  CppPluginSystemPluginPtr plugin = pluginFactory();

  // Check if the shared_ptr contains nullptr.
  if (!plugin) {
    logger_->warning(
        fmt::format("CppPluginSystem: Null plugin returned by '{}'", filePath.string()));

    dlclose(handle);
    return {};
  }

  // Get plugin's unique identifier.
  Identifier identifier;
  try {
    identifier = plugin->identifier();
  } catch (const std::exception& exc) {
    logger_->warning(
        fmt::format("CppPluginSystem: Caught exception calling 'identifier' of '{}': {}",
                    filePath.string(), exc.what()));
    plugin.reset();
  } catch (...) {
    logger_->warning(
        fmt::format("CppPluginSystem: Caught exception calling 'identifier' of '{}':"
                    " <unknown non-exception value caught>",
                    filePath.string()));
    plugin.reset();
  }

  // Unload the library if an exception was caught whilst retrieving the
  // identifier.
  //
  // Must wait til after the try-catch to close handle, since exception
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
