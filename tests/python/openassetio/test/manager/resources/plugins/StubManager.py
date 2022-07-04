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
An OpenAssetIO ManagerPlugin and stub ManagerInterface implementation
providing dummy data and input validation for the manager
test suite.
"""

from openassetio import TraitsData
from openassetio.managerApi import ManagerInterface
from openassetio.pluginSystem import ManagerPlugin


class StubManager(ManagerInterface):
    """
    A stub manager implementation that provides functionality
    required for the tests/python/openassetio/test/manager
    test suite to function.
    """
    # TODO: @pylint Remove once we have closed #163
    # pylint: disable=abstract-method

    # pylint: disable=no-self-use,missing-function-docstring

    def __init__(self):
        super().__init__()
        self.__settings = None
        self.__info = {}

    def identifier(self):
        return "org.openassetio.test.manager.stubManager"

    def displayName(self):
        return "Stub Manager"

    def info(self):
        return self.__info

    def setSettings(self, settings, hostSession):
        self.__settings = settings

    def getSettings(self, hostSession):
        return self.__settings

    def initialize(self, hostSession):
        self.__info["host_identifier"] = hostSession.host().identifier()

    def managementPolicy(self, traitSets, context, hostSession):
        # pylint: disable=unused-argument
        return [TraitsData() for _ in traitSets]


class StubManagerPlugin(ManagerPlugin):
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
plugin = StubManagerPlugin
