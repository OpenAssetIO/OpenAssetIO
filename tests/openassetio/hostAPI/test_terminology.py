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
from unittest import mock

import pytest

import openassetio.hostAPI.terminology as tgy
from openassetio.hostAPI import Manager, Session
from openassetio.managerAPI import ManagerInterface


all_terminology_keys = (
    tgy.kTerm_Asset,
    tgy.kTerm_Assets,
    tgy.kTerm_Manager,
    tgy.kTerm_Publish,
    tgy.kTerm_Publishing,
    tgy.kTerm_Published,
    tgy.kTerm_Shot,
    tgy.kTerm_Shots
)


class MockTerminologyManager(Manager):
    kTerm_custom = "custom"
    kTermValue_custom = "alternative"

    __mockDisplayName = "Mock Terminology Manager"
    __mockTerminology = {
        tgy.kTerm_Asset: 'mock-asset',
        tgy.kTerm_Assets: 'mock-assets',
        tgy.kTerm_Publish: 'mock-publish',
        tgy.kTerm_Publishing: 'mock-publishing',
        tgy.kTerm_Published: 'mock-published',
        tgy.kTerm_Shot: 'mock-shot',
        tgy.kTerm_Shots: 'mock-shots',
        kTerm_custom: kTermValue_custom
    }

    # ManagerInterface methods

    def updateTerminology(self, strings):
        strings.update(self.__mockTerminology)

    def displayName(self):
        return self.__mockDisplayName

    # Test helpers

    @classmethod
    def expectedTerminology(cls):
        expected = dict(cls.__mockTerminology)
        expected[tgy.kTerm_Manager] = cls.__mockDisplayName
        return expected


@pytest.fixture
def mock_manager():
    return MockTerminologyManager(
        mock.create_autospec(ManagerInterface), mock.create_autospec(Session))


@pytest.fixture
def mapper(mock_manager):
    return tgy.Mapper(mock_manager)


def test_defaultTerminology():
    # Ensure we have pre-defined keys for anything in the default dictionary
    assert set(all_terminology_keys) == set(tgy.defaultTerminology.keys())

    for value in tgy.defaultTerminology.values():
        assert isinstance(value, str)
        assert value != ""


class TestMapper:

    def test_construction(self, mock_manager):
        custom_terminology = {
            mock_manager.kTerm_custom: mock_manager.kTermValue_custom}
        a_mapper = tgy.Mapper(mock_manager, terminology=custom_terminology)
        assert (a_mapper.replaceTerms("{%s}" % mock_manager.kTerm_custom) ==
                mock_manager.kTermValue_custom)

    def test_replaceTerms(self, mock_manager, mapper):
        input = ", ".join(["{%s}" % k for k in all_terminology_keys])
        expected = input.format(**mock_manager.expectedTerminology())
        assert mapper.replaceTerms(input) == expected

    def test_replaceTermsUnknownTokensDebraced(self, mapper):
        input = "{an} unknown {token}"
        expected = "an unknown token"
        assert mapper.replaceTerms(input) == expected
