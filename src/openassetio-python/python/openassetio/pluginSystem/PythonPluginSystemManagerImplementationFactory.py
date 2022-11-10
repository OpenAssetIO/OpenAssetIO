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

    @envvar **OPENASSETIO_PLUGIN_PATH** *str* A PATH-style list of
    directories to search for @ref openassetio.pluginSystem.PythonPluginSystemManagerPlugin
    based plugins. It uses the platform-native delimiter.  Searched left
    to right.
    """

    ## The Environment Variable to read the plug-in search path from
    kPluginEnvVar = "OPENASSETIO_PLUGIN_PATH"

    def __init__(self, logger, paths=None):

        super(PythonPluginSystemManagerImplementationFactory, self).__init__(logger)

        self.__pluginManager = None
        self.__paths = paths

    def __scan(self):
        """
        Scans for PythonPluginSystemManagerPlugins, and registers them
        with the factory instance.

        @param paths `str` A searchpath string to search for plug-ins.
        If None, then the contents of the Environment Variable
        @ref kPluginEnvVar is used instead.
        """

        if not self.__paths:
            self.__paths = os.environ.get(self.kPluginEnvVar, "")
            if not self.__paths:
                self._logger.log(
                    self._logger.Severity.kWarning,
                    "%s is not set. It is somewhat unlikely that you will find any plugins..."
                    % self.kPluginEnvVar,
                )

        self.__pluginManager = PythonPluginSystem(self._logger)

        # We do this after instantiating, so that the lifetime of the manager is
        # consistent with cases where some paths were set.
        if self.__paths:
            self.__pluginManager.scan(self.__paths)

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
        Creates an instance of the @ref
        openassetio.managerApi.ManagerInterface "ManagerInterface" with
        the specified identifier.

        @param identifier `str` The identifier of the ManagerInterface
        to instantiate.

        @returns openassetio.managerApi.ManagerInterface
        """

        if not self.__pluginManager:
            self.__scan()

        self._logger.log(self._logger.Severity.kDebug, f"Instantiating {identifier}")
        plugin = self.__pluginManager.plugin(identifier)
        interface = plugin.interface()

        return interface
