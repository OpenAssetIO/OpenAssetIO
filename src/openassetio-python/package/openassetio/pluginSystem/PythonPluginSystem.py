#
#   Copyright 2013-2025 The Foundry Visionmongers Ltd
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""
@namespace openassetio.pluginSystem.PythonPluginSystem
A single-class module, providing the PythonPluginSystem class.
"""

import os.path
import importlib.metadata
import importlib.util
import hashlib
import sys
import traceback

from ..errors import InputValidationException


__all__ = ["PythonPluginSystem"]


class PythonPluginSystem(object):
    """
    Loads Python Packages, using entry point discovery or from a custom
    search path. If they contain a top-level 'plugin' attribute, that
    holds a class derived from PythonPluginSystemPlugin, it will be
    registered with its identifier. Once a plug-in has registered an
    identifier, any subsequent registrations with that id will be
    skipped.
    """

    __validModuleExtensions = (".py", ".pyc")

    def __init__(self, logger):
        self.__logger = logger
        self.reset()

    def reset(self):
        """
        Clears any previously loaded plugins.
        """
        self.__map = {}
        self.__paths = {}

    def scan(
        self,
        paths,
        pathsEnvVar,
        entryPointName,
        disableEntryPointsEnvVar,
        disableEntryPoints,
        moduleHookName,
    ):
        """
        Searches the supplied paths and/or entry points for modules that
        define a PythonPluginSystemPlugin through a supplied top-level
        variable.

        @param paths `str` A list of paths to search, delimited by
        `os.pathsep`. Set to blank (or otherwise falsey) to use the
        environment variable given by @p pathsEnvVar instead.

        @param pathsEnvVar `str` The name of the environment variable
        that contains paths to search, formatted as given in @p paths.
        If @p paths is set then this environment variable is unused.

        @param entryPointName `str` The name of the entry point group
        to search for plugins.

        @param disableEntryPointsEnvVar `str` An environment variable
        that, if set, will disable scanning for entry point plugins,
        unless overridden by @p disableEntryPoints.

        @param disableEntryPoints `Optional[bool]` Set to `True` or
        `False` to force disabling or enabling of entry point plugins,
        respectively. Set to `None` to enable unless @p
        disableEntryPointsEnvVar is set.

        @param moduleHookName `str` The name of the top-level variable
        that contains the plugin class.
        """
        if not paths:
            paths = os.environ.get(pathsEnvVar)

        if disableEntryPoints is None:
            disableEntryPoints = os.environ.get(disableEntryPointsEnvVar, False)

        if not paths and disableEntryPoints:
            self.__logger.warning(
                "PythonPluginSystem: No search paths specified and entry point plugins are"
                f" disabled, no plugins will load - check ${pathsEnvVar} is set.",
            )
            return

        if paths:
            self.scan_paths(paths, moduleHookName)

        if not disableEntryPoints:
            self.scan_entry_points(entryPointName, moduleHookName)
        else:
            self.__logger.debug("Entry point based plugins are disabled")

    def scan_paths(self, paths, moduleHookName):
        """
        Searches the supplied paths for modules that define a
        PythonPluginSystemPlugin through a supplied top-level variable.

        Paths are searched left-to-right, but only the first instance of
        any given plugin identifier will be used, and subsequent
        registrations ignored. This means entries to the left of the
        paths list take precedence over ones to the right.

        @note Precedence order is undefined for plugins sharing the
        same identifier within the same directory.

        @param paths `str` A list of paths to search, delimited by
        `os.pathsep`.

        @param moduleHookName `str` The name of the top-level variable
        that contains the plugin class.
        """
        self.__logger.debug(f"PythonPluginSystem: Searching {paths}")

        for path in paths.split(os.pathsep):
            if not os.path.isdir(path):
                self.__logger.debug(f"PythonPluginSystem: Skipping as not a directory {path}")

            for item in os.listdir(path):
                itemPath = os.path.join(path, item)

                if os.path.isdir(itemPath):
                    # The directory could be a package, check for __init__.py
                    initFile = os.path.join(itemPath, "__init__.py")
                    if os.path.exists(initFile):
                        itemPath = initFile
                    else:
                        self.__logger.debug(
                            "PythonPluginSystem: Ignoring as it is not a python package "
                            f"contianing __init__.py {itemPath}"
                        )
                        continue
                else:
                    # Its a file, check if it is a .py/.pyc module
                    _, ext = os.path.splitext(itemPath)
                    if ext not in self.__validModuleExtensions:
                        self.__logger.debug(
                            f"PythonPluginSystem: Ignoring as it is not a Python module {itemPath}"
                        )
                        continue

                self.__logger.debug(f"PythonPluginSystem: Attempting to load {itemPath}")

                self.__load(itemPath, moduleHookName)

    def scan_entry_points(self, entryPointName, moduleHookName):
        """
        Searches packages for entry points that define a
        PythonPluginSystemPlugin through a given top-level variable.

        @note The order of discovery is determined by `importlib`, only
        the first plugin with any given identifier will be registered.

        @param entryPointName `str` The entry point name to search for
        (see: importlib.metadata.entry_points group).

        @param moduleHookName `str` The name of the top-level variable
        that contains the plugin class.

        @returns True if entry point discovery is possible, False if
        there was a problem loading importlib.metadata.
        """

        self.__logger.debug(
            f"PythonPluginSystem: Searching packages for '{entryPointName}' entry points."
        )

        for entryPoint in importlib.metadata.entry_points(group=entryPointName):
            self.__logger.debug(f"PythonPluginSystem: Found entry point in {entryPoint.name}")
            try:
                module = entryPoint.load()
            except Exception:  # pylint: disable=broad-except
                self.__logger.error(
                    f"PythonPluginSystem: Caught exception loading {entryPoint.name}:\n"
                    + traceback.format_exc()
                )
                continue

            if moduleHook := getattr(module, moduleHookName, None):
                self.register(moduleHook, module.__file__)
            elif hasattr(module, "plugin"):
                self.__logger.warning(
                    "PythonPluginSystem: Use of top-level 'plugin' variable is deprecated, "
                    f"use `{moduleHookName}` instead. {module.__file__}"
                )
                self.register(module.plugin, module.__file__)
            else:
                self.__logger.error(
                    f"PythonPluginSystem: No top-level '{moduleHookName}' variable "
                    f"{module.__file__}"
                )

        return True

    def identifiers(self):
        """
        Returns the identifiers known to the plugin system.

        If @ref scan has not been called, then this will be empty.

        @return `List[str]`
        """
        return list(self.__map.keys())

    def plugin(self, identifier):
        """
        Retrieves the plugin that provides the given identifier.

        @return @ref openassetio.pluginSystem.PythonPluginSystemPlugin
        "PythonPluginSystemPlugin"

        @exception errors.InputValidationException Raised if no plugin
        provides the specified identifier.
        """

        if identifier not in self.__map:
            msg = "PythonPluginSystem: No plug-in registered with the identifier '%s'" % identifier
            raise InputValidationException(msg)

        return self.__map[identifier]

    def register(self, cls, path="<unknown>"):
        """
        Allows manual registration of a PythonPluginSystemPlugin derived
        class.

        This can be used to register plugins using means other than
        the built-in file system scanning.

        @param cls @ref openassetio.pluginSystem.PythonPluginSystemPlugin
        "PythonPluginSystemPlugin"

        @param path `str` Some reference to where this plugin
        originated, used for debug messaging when duplicate
        registrations of the same identifier are encountered.
        """
        identifier = cls.identifier()
        if identifier in self.__map:
            self.__logger.debug(
                f"PythonPluginSystem: Skipping class '{cls}' defined in '{path}'. "
                f"Already registered by '{self.__paths[identifier]}'"
            )
            return

        self.__logger.debug(f"PythonPluginSystem: Registered plug-in '{cls}' from '{path}'")

        self.__map[identifier] = cls
        self.__paths[identifier] = path

    def __load(self, path, moduleHookName):
        """
        Loads the specified python file and registers it's plugin.
        The file must expose a top-level variable with a name
        corresponding to the given module hook name.

        @param path `str` This can be either a single-file module,
        or the __init__.py at the root of a package.

        @param moduleHookName `str` The name of the top-level variable
        that contains the plugin class.
        """

        # Make a unique namespace to ensure the plugin identifier is
        # all that really matters
        moduleName = hashlib.md5(path.encode("utf-8")).hexdigest()

        try:
            spec = importlib.util.spec_from_file_location(moduleName, path)
            if spec is None:
                raise RuntimeError("Unable to determine module spec")

            module = importlib.util.module_from_spec(spec)

            # Without this, for package imports we get:
            #   'No module named '<moduleName>'
            sys.modules[spec.name] = module

            spec.loader.exec_module(module)

        except Exception:  # pylint: disable=broad-except
            self.__logger.error(
                f"PythonPluginSystem: Caught exception loading {path}:\n" + traceback.format_exc()
            )
            return

        if moduleHook := getattr(module, moduleHookName, None):
            # Store where this plugin was loaded from. Not entirely
            # accurate, but more useful for debugging than it not being
            # there.
            moduleHook.__file__ = path
            self.register(moduleHook, module.__file__)
        elif hasattr(module, "plugin"):
            self.__logger.warning(
                "PythonPluginSystem: Use of top-level 'plugin' variable is deprecated, "
                f"use `{moduleHookName}` instead. {module.__file__}"
            )
            # Store where this plugin was loaded from. Not entirely
            # accurate, but more useful for debugging than it not being
            # there.
            module.plugin.__file__ = path
            self.register(module.plugin, module.__file__)
        else:
            self.__logger.error(
                f"PythonPluginSystem: No top-level '{moduleHookName}' variable {module.__file__}"
            )
