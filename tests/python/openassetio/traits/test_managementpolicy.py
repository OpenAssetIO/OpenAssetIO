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
Tests that cover the openassetio.traits.managementPolicy traits.
"""

# pylint: disable=invalid-name,no-self-use,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
import pytest

from openassetio import TraitsData, TraitBase
from openassetio.traits.managementPolicy import ManagedTrait, WillManagePathTrait


class Test_ManagedTrait:
    def test_subclass(self):
        assert issubclass(ManagedTrait, TraitBase)

    def test_traitId(self):
        assert ManagedTrait.kId == "openassetio.Managed"


class Test_ManagedTrait_getExclusive:
    @pytest.mark.parametrize("expected", [True, False])
    def test_when_property_is_set_then_returns_expected_value(
        self, a_managed_traitsData, expected
    ):
        a_managed_traitsData.setTraitProperty(ManagedTrait.kId, "exclusive", expected)
        assert ManagedTrait(a_managed_traitsData).getExclusive() == expected

    def test_when_property_not_set_then_returns_None(self, a_managed_traitsData):
        assert ManagedTrait(a_managed_traitsData).getExclusive() is None

    def test_when_property_not_set_and_default_given_then_returns_default(
        self, a_managed_traitsData
    ):
        expected = "something"

        actual = ManagedTrait(a_managed_traitsData).getExclusive(defaultValue=expected)

        assert actual == expected

    def test_when_property_has_wrong_type_then_raises_TypeError(self, a_managed_traitsData):
        a_managed_traitsData.setTraitProperty(ManagedTrait.kId, "exclusive", 123)

        with pytest.raises(TypeError) as err:
            assert ManagedTrait(a_managed_traitsData).getExclusive()

        assert str(err.value) == "Invalid stored value type: '123' [int]"

    def test_when_property_has_wrong_type_and_default_given_then_returns_default(
        self, a_managed_traitsData
    ):
        a_managed_traitsData.setTraitProperty(ManagedTrait.kId, "exclusive", 123)

        expected = "something"

        actual = ManagedTrait(a_managed_traitsData).getExclusive(defaultValue=expected)

        assert actual == expected


class Test_ManagedTrait_setExclusive:
    @pytest.mark.parametrize("expected", [True, False])
    def test_when_set_then_trait_data_contains_value(self, a_managed_traitsData, expected):
        trait = ManagedTrait(a_managed_traitsData)

        trait.setExclusive(expected)

        actual = a_managed_traitsData.getTraitProperty(ManagedTrait.kId, "exclusive")
        assert actual == expected

    @pytest.mark.parametrize("expected", [True, False])
    def test_when_traitsData_does_not_have_trait_then_set_also_imbues(
        self, an_empty_traitsData, expected
    ):
        trait = ManagedTrait(an_empty_traitsData)

        trait.setExclusive(expected)

        actual = an_empty_traitsData.getTraitProperty(ManagedTrait.kId, "exclusive")
        assert actual == expected

    def test_when_type_is_wrong_then_TypeError_is_raised(self, a_managed_traitsData):
        trait = ManagedTrait(a_managed_traitsData)

        with pytest.raises(TypeError) as err:
            trait.setExclusive(123)

        assert str(err.value) == "exclusive must be a bool"


class Test_WillManagePathTrait:
    def test_subclass(self):
        assert issubclass(WillManagePathTrait, TraitBase)

    def test_traitId(self):
        assert WillManagePathTrait.kId == "openassetio.WillManagePath"


@pytest.fixture
def an_empty_traitsData():
    return TraitsData(set())


@pytest.fixture
def a_managed_traitsData():
    return TraitsData({ManagedTrait.kId})
