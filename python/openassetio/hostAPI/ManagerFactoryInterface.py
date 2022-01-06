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
@namespace openassetio.hostAPI.ManagerFactoryInterface
A single-class module, providing the ManagerFactoryInterface class.
"""


import abc


__all__ = ['ManagerFactoryInterface']


class ManagerFactoryInterface(object, metaclass=abc.ABCMeta):
    """
    Manager Factories are responsible for instantiating classes that
    derive from @ref openassetio.managerAPI.ManagerInterface or @needsref
    openassetio-ui.implementation.ManagerUIDelegate for use within an
    host.

    ManagerFactoryInterface defines the abstract interface that any such
    factory must adopt.
    """

    def __init__(self, logger):
        super(ManagerFactoryInterface, self).__init__()
        self._logger = logger

    @abc.abstractmethod
    def identifiers(self):
        """
        @return list, all identifiers known to the factory.
        @see @ref openassetio.pluginSystem.ManagerPlugin "ManagerPlugin"
        """
        raise NotImplementedError

    @abc.abstractmethod
    def managers(self):
        """
        @return dict, Keyed by identifiers, each value is a dict
        containing information about the Manager provided by the plugin.
        This dict has the following keys:
            @li **name** The display name of the Manager suitable for UI
            use.
            @li **identifier** It's identifier
            @li **info** The info dict from the Manager (see:
            @ref openassetio.managerAPI.ManagerInterface.ManagerInterface.info
            "ManagerInterface.info")
            @li **plugin** The plugin class that represents the Manager
            (see: @ref openassetio.pluginSystem.ManagerPlugin "ManagerPlugin")
        """
        raise NotImplementedError

    @abc.abstractmethod
    def managerRegistered(self, identifier):
        """
        @return bool, True if the supplied identifier is known to the
        factory.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def instantiate(self, identifier, cache=True):
        """
        Creates an instance of the @ref
        openassetio.managerAPI.ManagerInterface "ManagerInterface" with
        the specified identifier.

        @param identifier str, The identifier of the ManagerInterface
        to instantiate.

        @param cache bool, When True the created instance will be
        cached, and immediately returned by subsequence calls to this
        function with the same identifier - instead of creating a new
        instance. If False, a new instance will be created each, and
        never retained.

        @returns openassetio.managerAPI.ManagerInterface

        @todo[tc] Should 'cache' be removed, or set to False by default?
        It prevents a Session managing the lifetime of an instance.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def instantiateUIDelegate(self, managerInterfaceInstance, cache=True):
        """
        Creates an instance of the @needsref ManagerUIDelegate for the
        specified manager interface.

        @param managerInterfaceInstance openassetio.managerAPI.ManagerInterface,
        the instance of a ManagerInterface to retrieve the UI delegate for.

        @param cache bool, When True the created instance will be
        cached, and immediately returned by subsequence calls to this
        function with the same identifier - instead of creating a new
        instance. If False, a new instance will be created each, and
        never retained.
        """
        raise NotImplementedError
