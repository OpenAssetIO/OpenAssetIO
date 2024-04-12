#
#   Copyright 2013-2022 The Foundry Visionmongers Ltd
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
@namespace openassetio.pluginSystem.PythonPluginSystemManagerImplementationFactory
A single-class module, providing the
PythonPluginSystemManagerImplementationFactory class.
"""

import os

from ..hostApi import ManagerImplementationFactoryInterface

from .PythonPluginSystem import PythonPluginSystem


__all__ = [
    "PythonPluginSystemManagerImplementationFactory",
]


class PythonPluginSystemManagerImplementationFactory(ManagerImplementationFactoryInterface):
    """
    A Factory to manage @ref openassetio.pluginSystem.PythonPluginSystemManagerPlugin
    derived plugins. Not usually used directly by a @ref host, which
    instead uses the @fqref{hostApi.ManagerFactory} "ManagerFactory".

    The factory loads plugins from entry points registered within the
    `openassetio.manager_plugin` entry point group, as well as
    additional plugins found under paths specified in the
    `OPENASSETIO_PLUGIN_PATH` env var.

    @envvar **OPENASSETIO_PLUGIN_PATH** *str* A **PATH**-style list of
    directories to search for @ref
    openassetio.pluginSystem.PythonPluginSystemManagerPlugin
    "PythonPluginSystemManagerPlugin" based plugins. It uses the
    platform-native delimiter.  Searched left to right. Plugins found
    here will take precedence over those discovered through package
    entry points. Note: this search path is entirely independent of
    **PYTHONPATH** and doesn't need to be a subset of those paths. This
    allows OpenAssetIO plugins to be managed entirely independent of the
    python runtime if desired, and masked from `import` statements. Note
    that this environment variable is also used by the
    @fqref{pluginSystem.CppPluginSystemManagerImplementationFactory}
    "CppPluginSystemManagerImplementationFactory".

    @envvar **OPENASSETIO_DISABLE_ENTRYPOINTS_PLUGINS** when set,
    disables entry point based plugin discovery. This can be useful if
    it is not in use, to avoid unnecessary filesystem access during
    library initialization. **OPENASSETIO_PLUGIN_PATH** plugins take
    precedence over any entry point based ones.
    """

    ## The Environment Variable to read the plug-in search path from
    kPluginEnvVar = "OPENASSETIO_PLUGIN_PATH"
    ## The Environment Variable to control the discovery of entry point based plugins
    kDisableEntryPointsEnvVar = "OPENASSETIO_DISABLE_ENTRYPOINTS_PLUGINS"

    ## The name of the ManagerPlugin entry point for entry point
    ## discovered plugins.
    kPackageEntryPointGroup = "openassetio.manager_plugin"

    def __init__(self, logger, paths=None, disableEntryPointsPlugins=None):
        """
        Creates a new factory. The factory scans for plugins lazily on
        the first invocation of @ref identifiers or @ref instantiate.

        @param logger @fqref{log.LoggerInterface} "LoggerInterface"
        implementation that will be used to output information about
        plugin loading.

        @param paths `str` Paths to search for plugins. Defaults to the
        value of the @ref kPluginEnvVar environment variable.

        @param disableEntryPointsPlugins `bool` Controls whether
        package entry point based plugin discovery is allowed. Defaults
        to False unless the @ref kDisableEntryPointsEnvVar environment
        variable is set.
        """

        super(PythonPluginSystemManagerImplementationFactory, self).__init__(logger)

        self.__pluginManager = None

        if paths is None:
            paths = os.environ.get(self.kPluginEnvVar, "")
        self.__paths = paths

        if disableEntryPointsPlugins is None:
            disableEntryPointsPlugins = os.environ.get(self.kDisableEntryPointsEnvVar, False)
        self.__disableEntryPointsPlugins = disableEntryPointsPlugins

    def __scan(self):
        """
        Scans for PythonPluginSystemManagerPlugins, and registers them
        with the factory instance.
        """
        # Construct this here, so we have this even if we early out
        self.__pluginManager = PythonPluginSystem(self._logger)

        if not self.__paths and self.__disableEntryPointsPlugins:
            self._logger.log(
                self._logger.Severity.kWarning,
                "No search paths specified and entry point plugins are disabled, no plugins "
                f"will load - check ${self.kPluginEnvVar} is set.",
            )
            return

        # We scan custom paths first, so they take precedence over entry
        # point plugins

        if self.__paths:
            self.__pluginManager.scan(self.__paths)

        if self.__disableEntryPointsPlugins:
            self._logger.debug("Entry point based plugins are disabled")
        else:
            self.__pluginManager.scan_entry_points(self.kPackageEntryPointGroup)

    def identifiers(self):
        """
        @return list, all identifiers known to the factory.
        @see @ref openassetio.pluginSystem.PythonPluginSystemManagerPlugin
        "PythonPluginSystemManagerPlugin"
        """
        if not self.__pluginManager:
            self.__scan()

        return self.__pluginManager.identifiers()

    def instantiate(self, identifier):
        """
        Creates an instance of the
        @fqref{managerApi.ManagerInterface}"ManagerInterface"
        with the specified identifier.

        @param identifier `str` The identifier of the ManagerInterface
        to instantiate.

        @returns openassetio.managerApi.ManagerInterface

        @throws InputValidationException if the requested identifier has
        not been registered.

        @throws RuntimeError if the requested plugin is valid but has
        no `interface` method.
        """

        if not self.__pluginManager:
            self.__scan()

        self._logger.log(self._logger.Severity.kDebug, f"Instantiating {identifier}")
        plugin = self.__pluginManager.plugin(identifier)
        interface = plugin.interface()

        return interface
