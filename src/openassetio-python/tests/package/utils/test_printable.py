#
# Copyright 2024 The Foundry Visionmongers Ltd

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Tests that cover the printing and formatting openassetio types
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=too-few-public-methods
# pylint: disable=missing-class-docstring,missing-function-docstring

from ast import literal_eval
import pytest

from openassetio import EntityReference
from openassetio.errors import BatchElementError
from openassetio.managerApi import ManagerInterface
from openassetio.managerApi import ManagerStateBase
from openassetio.hostApi import Manager
from openassetio import Context
from openassetio.trait import TraitsData


def checkBasicPrintable(value, expected_str, expected_repr=None):
    if expected_repr is None:
        expected_repr = expected_str

    assert str(value) == expected_str
    assert repr(value) == expected_repr


def checkBasicPrintableContains(value, expected_str, expected_repr=None):
    if expected_repr is None:
        expected_repr = expected_str

    assert expected_str in str(value)
    assert expected_repr in repr(value)


# This function is here because we can't assume order of set and map types.
# Doing this characterwise check is _almost_ just as good.
def checkBasicPrintableByCharacters(value, expected_str, expected_repr=None):
    if expected_repr is None:
        expected_repr = expected_str

    assert sorted(expected_str) == sorted(str(value))
    assert sorted(expected_repr) == sorted(repr(value))


class Test_Printable:
    def test_print_infoDictionary(self, an_info_dictionary):
        checkBasicPrintableByCharacters(
            an_info_dictionary, "{'key1': 'value1', 'key2': False, 'key3': 1, 'key4': 1.23}"
        )

    def test_print_traitSet(self, a_trait_set):
        checkBasicPrintableByCharacters(a_trait_set, "{'trait2', 'trait1'}")

    def test_print_traitSets(self, a_trait_sets):
        checkBasicPrintableByCharacters(
            a_trait_sets, "[{'trait2', 'trait1'}, {'trait4', 'trait3'}]"
        )

    def test_print_batchElementError(self, a_batch_element_error):
        checkBasicPrintableContains(
            a_batch_element_error,
            "invalidTraitSet: Invalid trait set",
            "<openassetio._openassetio.errors.BatchElementError object at 0x",
        )

    def test_print_entityReference(self, an_entity_reference):
        checkBasicPrintable(
            an_entity_reference,
            "test:///an_entity_reference",
            "EntityReference('test:///an_entity_reference')",
        )

    def test_print_entityReferences(self, an_entity_references):
        checkBasicPrintable(
            an_entity_references,
            (
                "[EntityReference('test:///an_entity_reference_1'), "
                "EntityReference('test:///an_entity_reference_2')]"
            ),
        )

    def test_print_identifier(self, an_identifier):
        checkBasicPrintable(an_identifier, "an identifier", "'an identifier'")

    def test_print_str(self, a_str):
        checkBasicPrintable(a_str, "example string", "'example string'")

    def test_print_stringMap(self, a_string_map):
        checkBasicPrintableByCharacters(a_string_map, "{'key1': 'value1', 'key2': 'value2'}")

    def test_print_managerInterface_capability(self, a_managerInterface_capability):
        checkBasicPrintable(
            a_managerInterface_capability, "Capability.kPublishing", "<Capability.kPublishing: 5>"
        )

    def test_print_managercapability(self, a_manager_capability):
        checkBasicPrintable(
            a_manager_capability, "Capability.kPublishing", "<Capability.kPublishing: 5>"
        )

    def test_print_context(self, a_context):
        # No closing brace on purpose, to account for variant managerState memory address
        checkBasicPrintableContains(
            a_context,
            r"{'locale': {'aTrait': {'aIntTraitProperty': 2}}, 'managerState': 0x",
            "<openassetio._openassetio.Context object at 0x",
        )

    def test_print_traitsData(self, a_traitsData):

        expected = {
            "aTrait": {"aIntTraitProperty": 2, "aBoolTraitProperty": False},
            "a.long.namespaced.trait.that.goes.on.and.on.and.on": {
                "aIntTraitProperty": 2,
                "aStringTraitProperty": "a string",
                "aBoolTraitProperty": True,
            },
            "a.trait.with.no.properties": {},
        }

        # Traitsdata output should literally be a python dict.
        traitsData_out_dict = literal_eval(str(a_traitsData))

        assert traitsData_out_dict == expected


@pytest.fixture
def an_info_dictionary():
    return {"key1": "value1", "key2": False, "key3": 1, "key4": 1.23}


@pytest.fixture
def a_trait_set():
    return set({"trait1", "trait2"})


@pytest.fixture
def a_trait_sets():
    return [{"trait1", "trait2"}, {"trait3", "trait4"}]


@pytest.fixture
def a_batch_element_error():
    return BatchElementError(BatchElementError.ErrorCode.kInvalidTraitSet, "Invalid trait set")


@pytest.fixture
def an_entity_reference():
    return EntityReference("test:///an_entity_reference")


@pytest.fixture
def an_entity_references():
    return [
        EntityReference("test:///an_entity_reference_1"),
        EntityReference("test:///an_entity_reference_2"),
    ]


@pytest.fixture
def an_identifier():
    return "an identifier"


@pytest.fixture
def a_str():
    return "example string"


@pytest.fixture
def a_string_map():
    return {"key1": "value1", "key2": "value2"}


@pytest.fixture
def a_managerInterface_capability():
    return ManagerInterface.Capability.kPublishing


@pytest.fixture
def a_manager_capability():
    return Manager.Capability.kPublishing


@pytest.fixture
def a_context():
    context = Context()
    context.locale.setTraitProperty("aTrait", "aIntTraitProperty", 2)
    context.managerState = ManagerStateBase()
    return context


@pytest.fixture
def a_traitsData():
    traitsData = TraitsData()
    traitsData.setTraitProperty("aTrait", "aIntTraitProperty", 2)
    traitsData.setTraitProperty("aTrait", "aBoolTraitProperty", False)
    traitsData.setTraitProperty(
        "a.long.namespaced.trait.that.goes.on.and.on.and.on", "aIntTraitProperty", 2
    )
    traitsData.setTraitProperty(
        "a.long.namespaced.trait.that.goes.on.and.on.and.on", "aStringTraitProperty", "a string"
    )
    traitsData.setTraitProperty(
        "a.long.namespaced.trait.that.goes.on.and.on.and.on", "aBoolTraitProperty", True
    )
    traitsData.addTrait("a.trait.with.no.properties")
    return traitsData


@pytest.fixture
def a_manager(mock_manager_interface, a_host_session):
    return Manager(mock_manager_interface, a_host_session)
