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
Tests that cover the openassetio.hostApi.terminology module.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

import openassetio.hostApi.terminology as tgy
from openassetio.hostApi import Manager


all_terminology_keys = (
    tgy.kTerm_Asset,
    tgy.kTerm_Assets,
    tgy.kTerm_Manager,
    tgy.kTerm_Publish,
    tgy.kTerm_Publishing,
    tgy.kTerm_Published,
    tgy.kTerm_Shot,
    tgy.kTerm_Shots,
)


class MockTerminologyManager(Manager):
    kTerm_custom = "custom"
    kTermValue_custom = "alternative"

    __mockDisplayName = "Mock Terminology Manager"
    __mockTerminology = {
        tgy.kTerm_Asset: "mock-asset",
        tgy.kTerm_Assets: "mock-assets",
        tgy.kTerm_Publish: "mock-publish",
        tgy.kTerm_Publishing: "mock-publishing",
        tgy.kTerm_Published: "mock-published",
        tgy.kTerm_Shot: "mock-shot",
        tgy.kTerm_Shots: "mock-shots",
        kTerm_custom: kTermValue_custom,
    }

    # ManagerInterface methods

    def updateTerminology(self, stringDict):
        stringDict.update(self.__mockTerminology)

    def displayName(self):
        return self.__mockDisplayName

    # Test helpers

    @classmethod
    def expectedTerminology(cls):
        expected = dict(cls.__mockTerminology)
        expected[tgy.kTerm_Manager] = cls.__mockDisplayName
        return expected


@pytest.fixture
def mock_manager(mock_manager_interface, a_host_session):
    return MockTerminologyManager(mock_manager_interface, a_host_session)


@pytest.fixture
def mapper(mock_manager):
    return tgy.Mapper(mock_manager)


class Test_defaultTerminology:
    def test_has_expected_keys(self):
        # Ensure we have pre-defined keys for anything in the default dictionary
        assert set(all_terminology_keys) == set(tgy.defaultTerminology.keys())

    def test_values_are_strings_and_not_empty(self):
        for value in tgy.defaultTerminology.values():
            assert isinstance(value, str)
            assert value != ""


class Test_Mapper_init:
    def test_when_constructed_with_custom_terminology_then_it_is_used_for_replacement(
        self, mock_manager
    ):
        custom_terminology = {mock_manager.kTerm_custom: mock_manager.kTermValue_custom}
        a_mapper = tgy.Mapper(mock_manager, terminology=custom_terminology)
        assert (
            a_mapper.replaceTerms(f"{{{mock_manager.kTerm_custom}}}")
            == mock_manager.kTermValue_custom
        )


class Test_Mapper_replaceTerms:
    def test_when_called_with_known_terms_then_they_are_replaced_with_target_terminology(
        self, mock_manager, mapper
    ):
        all_terms_str = ", ".join([f"{k}" for k in all_terminology_keys])
        expected = all_terms_str.format(**mock_manager.expectedTerminology())
        assert mapper.replaceTerms(all_terms_str) == expected

    def test_when_called_with_unknown_terms_then_their_braces_are_removed(self, mapper):
        input_str = "{an} unknown {token}"
        expected = "an unknown token"
        assert mapper.replaceTerms(input_str) == expected
