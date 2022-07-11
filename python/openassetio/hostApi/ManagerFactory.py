#
#   Copyright 2022 The Foundry Visionmongers Ltd
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
@namespace openassetio.hostApi.Manager
A single-class module, providing the ManagerFactory class.

@todo This module is a temporary measure until we reach parity between
C++ and Python Manager and HostSession classes.
"""

from .. import _openassetio  # pylint: disable=no-name-in-module

from .Manager import Manager
from ..managerApi.HostSession import HostSession


__all__ = ['ManagerFactory']


class ManagerFactory(_openassetio.hostApi.ManagerFactory):
    """
    @see @fqref{hostApi.ManagerFactory} "hostApi.ManagerFactory".
    """
    def __init__(self, hostInterface, managerInterfaceFactory, logger):
        _openassetio.hostApi.ManagerFactory.__init__(
            self, hostInterface, managerInterfaceFactory, logger)
        self.__managerInterfaceFactory = managerInterfaceFactory
        self.__hostInterface = hostInterface
        self.__logger = logger

    def createManager(self, identifier):
        """
        @see @fqref{hostApi.ManagerFactory.createManager}
        "ManagerFactory.createManager".
        """
        return Manager(
            self.__managerInterfaceFactory.instantiate(identifier),
            HostSession(_openassetio.managerApi.Host(self.__hostInterface), self.__logger))

    @staticmethod
    def createManagerForInterface(identifier, hostInterface, managerInterfaceFactory, logger):
        """
        @see @fqref{hostApi.ManagerFactory.createManagerForInterface}
        "ManagerFactory.createManagerForInterface".
        """
        return Manager(
            managerInterfaceFactory.instantiate(identifier),
            HostSession(_openassetio.managerApi.Host(hostInterface), logger))
