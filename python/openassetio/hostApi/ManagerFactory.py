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


__all__ = ["ManagerFactory"]


class ManagerFactory(_openassetio.hostApi.ManagerFactory):
    """
    @see @fqref{hostApi.ManagerFactory} "hostApi.ManagerFactory".
    """

    def __init__(self, hostInterface, managerImplementationFactory, logger):
        _openassetio.hostApi.ManagerFactory.__init__(
            self, hostInterface, managerImplementationFactory, logger
        )

    def createManager(self, identifier):
        """
        @see @fqref{hostApi.ManagerFactory.createManager}
        "ManagerFactory.createManager".
        """
        cppManager = super().createManager(identifier)
        # pylint: disable=protected-access
        return Manager(cppManager._interface(), cppManager._hostSession())

    @staticmethod
    def createManagerForInterface(identifier, hostInterface, managerImplementationFactory, logger):
        """
        @see @fqref{hostApi.ManagerFactory.createManagerForInterface}
        "ManagerFactory.createManagerForInterface".
        """
        cppManager = _openassetio.hostApi.ManagerFactory.createManagerForInterface(
            identifier, hostInterface, managerImplementationFactory, logger
        )
        # pylint: disable=protected-access
        return Manager(cppManager._interface(), cppManager._hostSession())

    @staticmethod
    def defaultManagerForInterface(hostInterface, managerImplementationFactory, logger):
        """
        @see @fqref{hostApi.ManagerFactory.defaultManagerForInterface}
        "ManagerFactory.defaultManagerForInterface".
        """
        cppManager = _openassetio.hostApi.ManagerFactory.defaultManagerForInterface(
            hostInterface, managerImplementationFactory, logger
        )
        if cppManager:
            # pylint: disable=protected-access
            return Manager(cppManager._interface(), cppManager._hostSession())
        return None
