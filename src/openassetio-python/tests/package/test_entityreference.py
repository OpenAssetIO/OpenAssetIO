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
Tests for the EntityReference type.
"""

# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

from openassetio import EntityReference


class Test_EntityReference_inheritance:
    def test_class_is_final(self):
        with pytest.raises(TypeError):

            class _(EntityReference):
                pass


class Test_EntityReference_toString:
    def test_returns_constructor_supplied_string(self):
        expected = "ref://some/entity/🐈"
        an_entity_reference = EntityReference(expected)
        assert an_entity_reference.toString() == expected


class Test_EntityReference_equality:
    def test_when_same_then_compares_equal(self):
        assert EntityReference("something") == EntityReference("something")

    def test_when_not_same_then_compares_unequal(self):
        assert EntityReference("something") != EntityReference("something else")


class Test_EntityReference_string_equivalence:
    def test_when_used_with_format_then_result_contains_toString_value(self):
        a_ref = EntityReference("Some 🍟 with that?")
        assert f"{a_ref}" == a_ref.toString()
