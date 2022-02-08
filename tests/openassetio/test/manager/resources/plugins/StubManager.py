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

from openassetio import constants
from openassetio.managerAPI import ManagerInterface
from openassetio.pluginSystem import ManagerPlugin


class StubManager(ManagerInterface):
    """
    A stub manager implementation that provides functionality
    required for the tests/openassetio/test/manager
    test suite to function.
    """
    # TODO Remove once we have closed #163
    # pylint: disable=abstract-method
    @staticmethod
    def identifier():
        return "org.openassetio.test.manager.stubManager"

    def displayName(self):
        return "Stub Manager"

    def initialize(self, hostSession):
        # pylint: disable=unused-argument
        pass

    def managementPolicy(self, specifications, context, hostSession, entityRef=None):
        # pylint: disable=unused-argument
        return [constants.kIgnored for _ in range(len(specifications))]


class StubManagerPlugin(ManagerPlugin):
    """
    Provides an alternate implementation of the ModulePlugin
    to aid testing of path precedence.
    """
    @staticmethod
    def identifier():
        return StubManager.identifier()

    @classmethod
    def interface(cls):
        return StubManager()


# pylint: disable=invalid-name
plugin = StubManagerPlugin
