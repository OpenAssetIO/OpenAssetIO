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
Tests that cover the openassetio.hostAPI.Specification class.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

from openassetio import Specification


class PrefixASpec(Specification):
    _prefix = "prefixA"
    _type = "spec"
    # Properties
    aString = Specification.TypedProperty(str)
    anInt = Specification.TypedProperty(int)


class PrefixAChildSpec(Specification):
    _prefix = "prefixA"
    _type = "spec.child"


class PrefixBSpec(Specification):
    _prefix = "prefixB"
    _type = "spec"


class Test_Specification_construction:

    def test_when_constructed_then_has_expected_schema_components(self):
        a_spec = PrefixASpec()

        assert a_spec.schema() == "prefixA:spec"
        assert a_spec.prefix() == "prefixA"
        assert a_spec.type() == "spec"

    def test_when_constructed_with_data_then_has_corresponding_fields(self):
        a_spec = PrefixASpec(data={"aString": "cat", "anInt": 5})

        assert a_spec.field("aString") == "cat"
        assert a_spec.aString == "cat"

        assert a_spec.field("anInt") == 5
        assert a_spec.anInt == 5

    def test_when_adding_attributes_after_construction_then_an_attribute_error_is_raised(self):
        a_spec = PrefixASpec()

        with pytest.raises(AttributeError):
            a_spec.cat = 5  # pylint: disable=attribute-defined-outside-init


class Test_Specification_isOfType:

    def test_when_called_with_own_type_then_returns_true(self):
        a_spec = PrefixASpec()
        assert a_spec.isOfType("spec") is True

    def test_when_called_with_another_type_then_returns_false(self):
        a_spec = PrefixASpec()
        assert a_spec.isOfType("another") is False

    def test_when_called_with_own_class_then_returns_true(self):
        a_spec = PrefixASpec()
        assert a_spec.isOfType(PrefixASpec) is True

    def test_when_called_with_another_class_with_same_type_then_returns_false(self):
        a_spec = PrefixASpec()
        assert a_spec.isOfType(PrefixBSpec) is False

    def test_when_called_with_child_of_own_type_then_returns_false(self):
        a_spec = PrefixASpec()
        assert a_spec.isOfType("spec.child") is False

    def test_when_called_with_parent_of_own_type_then_returns_true(self):
        a_spec = PrefixAChildSpec()
        assert a_spec.isOfType("spec") is True

    def test_when_called_with_parent_of_own_type_and_derived_disabled_then_returns_false(self):
        a_spec = PrefixAChildSpec()
        assert a_spec.isOfType("spec", includeDerived=False) is False

    def test_when_called_with_class_with_parent_of_own_type_then_returns_true(self):
        a_spec = PrefixAChildSpec()
        assert a_spec.isOfType(PrefixASpec) is True

    def test_when_called_with_class_with_parent_of_own_type_and_derived_disabled_then_returns_false(self):  # pylint: disable=line-too-long
        a_spec = PrefixAChildSpec()
        assert a_spec.isOfType(PrefixASpec, includeDerived=False) is False


class Test_Specification_schemaComponents:

    def test_when_called_with_valid_schmea_then_returns_prefix_and_type(self):
        assert Specification.schemaComponents(
            "prefix:type") == ("prefix", "type")

    def test_when_called_without_a_prefix_then_returns_empty_prefix(self):
        assert Specification.schemaComponents("type") == ("", "type")

    def test_when_called_with_generateSchema_then_result_is_same_as_input(self):
        a_schema = "prefix:type"
        assert Specification.generateSchema(
            *Specification.schemaComponents(a_schema)) == a_schema
