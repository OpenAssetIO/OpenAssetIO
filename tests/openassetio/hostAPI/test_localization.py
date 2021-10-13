#
#   Copyright 2013-2021 [The Foundry Visionmongers Ltd]
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

import pytest

import openassetio.hostAPI.localization as lzn
from openassetio.managerAPI import ManagerInterface


all_localization_keys = (
    lzn.kLocalizationKey_Asset,
    lzn.kLocalizationKey_Assets,
    lzn.kLocalizationKey_Manager,
    lzn.kLocalizationKey_Publish,
    lzn.kLocalizationKey_Publishing,
    lzn.kLocalizationKey_Published,
    lzn.kLocalizationKey_Shot,
    lzn.kLocalizationKey_Shots
)


class MockLocalizationManager(ManagerInterface):
    kLocalizationKey_custom = "custom"
    kLocalizationValue_custom = "alternative"

    __mockDisplayName = "Mock Localizing Manager"
    __mockTerminology = {
        lzn.kLocalizationKey_Asset: 'mock-asset',
        lzn.kLocalizationKey_Assets: 'mock-assets',
        lzn.kLocalizationKey_Publish: 'mock-publish',
        lzn.kLocalizationKey_Publishing: 'mock-publishing',
        lzn.kLocalizationKey_Published: 'mock-published',
        lzn.kLocalizationKey_Shot: 'mock-shot',
        lzn.kLocalizationKey_Shots: 'mock-shots',
        kLocalizationKey_custom: kLocalizationValue_custom
    }

    # ManagerInterface methods

    def localizeStrings(self, strings):
        strings.update(self.__mockTerminology)

    def getDisplayName(self):
        return self.__mockDisplayName

    # Test helpers

    @classmethod
    def expectedTerminology(cls):
        expected = dict(cls.__mockTerminology)
        expected[lzn.kLocalizationKey_Manager] = cls.__mockDisplayName
        return expected


@pytest.fixture
def mock_manager():
    return MockLocalizationManager()


@pytest.fixture
def localizer(mock_manager):
    return lzn.Localizer(mock_manager)


def test_defaultTerminology():
    # Ensure we have pre-defined keys for anything in the default dictionary
    assert set(all_localization_keys) == set(lzn.defaultTerminology.keys())

    for value in lzn.defaultTerminology.values():
        assert isinstance(value, str)
        assert value != ""


class TestLocalizer:

    def test_construction(self, mock_manager):
        custom_terminology = {
            mock_manager.kLocalizationKey_custom: mock_manager.kLocalizationValue_custom}
        a_localizer = lzn.Localizer(mock_manager, terminology=custom_terminology)
        assert (a_localizer.localizeString("{%s}" % mock_manager.kLocalizationKey_custom) ==
                mock_manager.kLocalizationValue_custom)

    def test_localizeString(self, mock_manager, localizer):
        input = ", ".join(["{%s}" % k for k in all_localization_keys])
        expected = input.format(**mock_manager.expectedTerminology())
        assert localizer.localizeString(input) == expected

    def test_localizeStringUnknownTokensDebraced(self, localizer):
        input = "{an} unknown {token}"
        expected = "an unknown token"
        assert localizer.localizeString(input) == expected
