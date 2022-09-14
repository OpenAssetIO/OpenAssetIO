#
#   Copyright 2013-2021 The Foundry Visionmongers Ltd
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
import importlib.util
import hashlib
import sys

from .. import exceptions


__all__ = ["PythonPluginSystem"]


class PythonPluginSystem(object):
    """
    Loads Python Packages on a custom search path. If they manager a
    top-level 'plugin' attribute, that holds a class derived from
    PythonPluginSystemPlugin, it will be registered with its identifier.
    Once a plug-in has registered an identifier, any subsequent
    registrations with that id will be skipped.
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

    def scan(self, paths):
        """
        Searches the supplied paths for modules that define a
        PythonPluginSystemPlugin through a top-level `plugin` variable.

        Paths are searched right-to-left, but only the first instance of
        any given plugin identifier will be used, and subsequent
        registrations ignored. This means entries to the left of the
        paths list take precedence over ones to the right.

        @note Precedence order is undefined for plugins sharing the
        same identifier within the same directory.

        Any existing plugins registered with the PythonPluginSystem will be
        cleared before scanning.

        @param paths `str` A list of paths to search, delimited by
        `os.pathsep`.
        """
        self.reset()

        self.__logger.log(
            self.__logger.Severity.kDebug, "PythonPluginSystem: Searching %s" % paths
        )

        for path in paths.split(os.pathsep):

            if not os.path.isdir(path):
                msg = "PythonPluginSystem: Skipping as it is not a directory %s" % path
                self.__logger.log(self.__logger.Severity.kDebug, msg)

            for item in os.listdir(path):

                itemPath = os.path.join(path, item)

                if os.path.isdir(itemPath):
                    # The directory could be a package, check for __init__.py
                    initFile = os.path.join(itemPath, "__init__.py")
                    if os.path.exists(initFile):
                        itemPath = initFile
                    else:
                        msg = (
                            "PythonPluginSystem: Ignoring as it is not a python package "
                            "contianing __init__.py %s" % itemPath
                        )
                        self.__logger.log(self.__logger.Severity.kDebug, msg)
                        continue
                else:
                    # Its a file, check if it is a .py/.pyc module
                    _, ext = os.path.splitext(itemPath)
                    if ext not in self.__validModuleExtensions:
                        msg = (
                            "PythonPluginSystem: Ignoring as its not a python module %s" % itemPath
                        )
                        self.__logger.log(self.__logger.Severity.kDebug, msg)
                        continue

                self.__logger.log(
                    self.__logger.Severity.kDebug,
                    "PythonPluginSystem: Attempting to load %s" % itemPath,
                )

                self.__load(itemPath)

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

        @exception openassetio.exceptions.PluginError Raised if no
        plugin provides the specified identifier.
        """

        if identifier not in self.__map:
            msg = "PythonPluginSystem: No plug-in registered with the identifier '%s'" % identifier
            raise exceptions.PluginError(msg)

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
            msg = (
                "PythonPluginSystem: Skipping class '%s' defined in '%s'."
                " Already registered by '%s'" % (cls, path, self.__paths[identifier])
            )
            self.__logger.log(self.__logger.Severity.kDebug, msg)
            return

        msg = "PythonPluginSystem: Registered plug-in '%s' from '%s'" % (cls, path)
        self.__logger.log(self.__logger.Severity.kDebug, msg)

        self.__map[identifier] = cls
        self.__paths[identifier] = path

    def __load(self, path):
        """
        Loads the specified python file and registers it's plugin.
        The file must expose a top-level 'plugin' variable.

        @param path `str` This can be either a single-file module,
        or the __init__.py at the root of a package.
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

        except Exception as ex:  # pylint: disable=broad-except
            msg = "PythonPluginSystem: Caught exception loading plug-in from %s:\n%s" % (path, ex)
            self.__logger.log(self.__logger.Severity.kWarning, msg)
            return

        if not hasattr(module, "plugin"):
            msg = "PythonPluginSystem: No top-level 'plugin' variable %s" % path
            self.__logger.log(self.__logger.Severity.kWarning, msg)
            return

        # Store where this plugin was loaded from. Not entirely
        # accurate, but more useful for debugging than it not being
        # there.
        module.plugin.__file__ = path

        self.register(module.plugin, path)
