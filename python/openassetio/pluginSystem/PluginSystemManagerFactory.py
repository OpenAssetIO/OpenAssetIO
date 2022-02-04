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
@namespace openassetio.pluginSystem.PluginSystemManagerFactory
A single-class module, providing the PluginSystemManagerFactory class.
"""

import os

from ..hostAPI.ManagerFactoryInterface import ManagerFactoryInterface

from .PluginSystem import PluginSystem


__all__ = ['PluginSystemManagerFactory', ]


class PluginSystemManagerFactory(ManagerFactoryInterface):
    """
    A Factory to manage @ref openassetio.pluginSystem.ManagerPlugin
    derived plugins and instantiation of Manager and UIDelegate
    instances. Not usually used directly by a @ref host, which instead
    uses the @ref openassetio.hostAPI.Session

    @envvar **OPENASSETIO_PLUGIN_PATH** *str* A PATH-style list of
    directories to search for @ref
    openassetio.pluginSystem.ManagerPlugin based plugins. It uses the
    platform-native delimiter.  Searched left to right.
    """

    ## The Environment Variable to read the plug-in search path from
    kPluginEnvVar = "OPENASSETIO_PLUGIN_PATH"

    def __init__(self, logger, paths=None):

        super(PluginSystemManagerFactory, self).__init__(logger)

        self.__pluginManager = None
        self.__instances = {}
        self.__delegates = {}
        self.__paths = paths

    def __scan(self):
        """
        Scans for ManagerPlugins, and registers them with the factory
        instance.

        @param paths `str` A searchpath string to search for plug-ins.
        If None, then the contents of the Environment Variable
        @ref kPluginEnvVar is used instead.
        """

        if not self.__paths:
            self.__paths = os.environ.get(self.kPluginEnvVar, "")
            if not self.__paths:
                self._logger.log(
                    ("%s is not set. It is somewhat unlikely that you will "
                     + "find any plugins...") % self.kPluginEnvVar, self._logger.kWarning)

        self.__pluginManager = PluginSystem(self._logger)

        # We do this after instantiating, so that the lifetime of the manager is
        # consistent with cases where some paths were set.
        if self.__paths:
            self.__pluginManager.scan(self.__paths)

    def identifiers(self):
        """
        @return list, all identifiers known to the factory.
        @see @ref openassetio.pluginSystem.ManagerPlugin "ManagerPlugin"
        """
        if not self.__pluginManager:
            self.__scan()

        return self.__pluginManager.identifiers()

    def managers(self):
        """
        @return dict, Keyed by identifiers, each value is a dict
        containing information about the Manager provided by the plugin.
        This dict has the following keys:
          @li **name** The display name of the Manager suitable for UI
          use.
          @li **identifier** It's identifier
          @li **info** The info dict from the Manager (see: @ref
          openassetio.managerAPI.ManagerInterface.ManagerInterface.info
          "ManagerInterface.info")
          @li **plugin** The plugin class that represents the Manager
          (see: @ref openassetio.pluginSystem.ManagerPlugin
          "ManagerPlugin")
        """

        if not self.__pluginManager:
            self.__scan()

        managers = {}

        identifiers = self.__pluginManager.identifiers()
        for identifier in identifiers:

            try:
                plugin = self.__pluginManager.plugin(identifier)
                interface = plugin.interface()
            except Exception as ex:  # pylint: disable=broad-except
                self._logger.log(
                    "Error loading plugin for '%s': %s" % (identifier, ex), self._logger.kCritical)
                continue

            managerIdentifier = interface.identifier()
            managers[identifier] = {
                'name': interface.displayName(),
                'identifier': managerIdentifier,
                'info': interface.info(),
                'plugin': plugin
            }

            if identifier != managerIdentifier:
                msg = ("Manager '%s' is not registered with the same identifier as it's plugin"
                       " ('%s' instead of '%s')"
                       % (interface.displayName(), managerIdentifier, identifier))
                self._logger.log(msg, self._logger.kWarning)

        return managers

    def managerRegistered(self, identifier):
        """
        @return bool, True if the supplied identifier is known to the
        factory.
        """
        if not self.__pluginManager:
            self.__scan()

        return identifier in self.__pluginManager.identifiers()

    def instantiate(self, identifier, cache=True):
        """
        Creates an instance of the @ref
        openassetio.managerAPI.ManagerInterface "ManagerInterface" with
        the specified identifier.

        @param identifier `str` The identifier of the ManagerInterface
        to instantiate.

        @param cache `bool` When True the created instance will be
        cached, and immediately returned by subsequence calls to this
        function with the same identifier - instead of creating a new
        instance. If False, a new instance will be created each, and
        never retained.

        @returns openassetio.managerAPI.ManagerInterface
        """

        if not self.__pluginManager:
            self.__scan()

        if cache and identifier in self.__instances:
            return self.__instances[identifier]

        self._logger.log(f"Instantiating {identifier}", self._logger.kDebug)
        plugin = self.__pluginManager.plugin(identifier)
        interface = plugin.interface()

        if cache:
            self.__instances[identifier] = interface

        return interface

    def instantiateUIDelegate(self, managerInterfaceInstance, cache=True):
        """
        Creates an instance of the @needsref ManagerUIDelegate for the
        specified identifier.

        @param managerInterfaceInstance openassetio.managerAPI.ManagerInterface
        The instance of a ManagerInterface to retrieve the UI
        delegate for.

        @param cache `bool` When True the created instance will be
        cached, and immediately returned by subsequence calls to this
        function with the same identifier - instead of creating a new
        instance. If False, a new instance will be created each, and
        never retained.
        """

        if not self.__pluginManager:
            self.__scan()

        ## @todo This probably has some retention issues we need to deal with
        if cache and managerInterfaceInstance in self.__delegates:
            return self.__delegates[managerInterfaceInstance]

        identifier = managerInterfaceInstance.identifier()
        plugin = self.__pluginManager.plugin(identifier)
        delegateInstance = plugin.uiDelegate(managerInterfaceInstance)

        if cache:
            self.__delegates[managerInterfaceInstance] = delegateInstance

        return delegateInstance
