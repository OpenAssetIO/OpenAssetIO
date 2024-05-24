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
An OpenAssetIO PythonPluginSystemManagerPlugin and stub ManagerInterface
implementation providing dummy data and input validation for the manager
test suite.
"""

from openassetio.managerApi import ManagerInterface
from openassetio.pluginSystem import PythonPluginSystemManagerPlugin
from openassetio.trait import TraitsData


class StubManager(ManagerInterface):
    """
    A stub manager implementation that provides functionality
    required for the src/openassetio-python/tests/package/test/manager
    test suite to function.
    """

    # TODO: @pylint Remove once we have closed #163
    # pylint: disable=abstract-method

    # pylint: disable=no-self-use,missing-function-docstring

    def __init__(self):
        super().__init__()
        self.__settings = {}
        self.__info = {}

    def identifier(self):
        return "org.openassetio.test.manager.stubManager"

    def displayName(self):
        return "Stub Manager"

    def info(self):
        return self.__info

    def settings(self, hostSession):
        # pylint: disable=unused-argument
        return self.__settings

    def initialize(self, managerSettings, hostSession):
        self.__settings = managerSettings
        self.__info["host_identifier"] = hostSession.host().identifier()

    def hasCapability(self, capability):
        return capability in (
            ManagerInterface.Capability.kEntityReferenceIdentification,
            ManagerInterface.Capability.kManagementPolicyQueries,
            ManagerInterface.Capability.kEntityTraitIntrospection,
        )

    def managementPolicy(self, traitSets, access, context, hostSession):
        # pylint: disable=unused-argument
        return [TraitsData() for _ in traitSets]

    def isEntityReferenceString(self, _):
        return False


class StubManagerPlugin(PythonPluginSystemManagerPlugin):
    """
    Provides an alternate implementation of the ModulePlugin
    to aid testing of path precedence.
    """

    @staticmethod
    def identifier():
        return "org.openassetio.test.manager.stubManager"

    @classmethod
    def interface(cls):
        return StubManager()


# pylint: disable=invalid-name
openassetioPlugin = StubManagerPlugin
