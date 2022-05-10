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
Tests for the Python-specific Trait base class.
"""

# pylint: disable=invalid-name,missing-class-docstring
# pylint: disable=redefined-outer-name,no-self-use
# pylint: disable=missing-function-docstring

from unittest import mock

from openassetio import TraitsData, Trait


class Test_Trait_Construction:
    def test_exposes_wrapped_data_via_protected_member(self):
        a_data = mock.Mock()
        trait = ACustomTrait(a_data)
        assert trait._data is a_data  # pylint: disable=protected-access


class Test_Trait_isValid:
    def test_when_data_has_trait_returns_true(self):
        a_data = TraitsData({ACustomTrait.kId})
        trait = ACustomTrait(a_data)
        assert trait.isValid() is True

    def test_when_data_does_not_have_trait_returns_false(self):
        a_data = TraitsData({"someOtherTrait"})
        trait = ACustomTrait(a_data)
        assert trait.isValid() is False


class Test_Trait_imbue:
    def test_when_data_empty_then_adds_trait(self):
        a_data = TraitsData()
        trait = ACustomTrait(a_data)
        trait.imbue()
        assert trait.isValid()
        assert trait.kId in a_data.traitIds()

    def test_when_data_has_trait_then_is_noop(self):
        a_data = TraitsData({ACustomTrait.kId})
        trait = ACustomTrait(a_data)
        trait.imbue()


class Test_Trait_imbueTo:
    def test_when_data_empty_then_adds_trait(self):
        a_data = TraitsData()
        ACustomTrait.imbueTo(a_data)
        assert ACustomTrait.kId in a_data.traitIds()

    def test_when_data_has_trait_then_is_noop(self):
        a_data = TraitsData({ACustomTrait.kId})
        ACustomTrait.imbueTo(a_data)


class ACustomTrait(Trait):
    kId = "customTrait"
