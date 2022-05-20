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
Tests for the Python-specific SpecificationBase base class.
"""

# pylint: disable=invalid-name,missing-class-docstring
# pylint: disable=redefined-outer-name,no-self-use
# pylint: disable=missing-function-docstring

import pytest

from openassetio import SpecificationBase, Trait, TraitsData


class Test_SpecificationBase_Construction:
    def test_default_constructor_raises_error(self):
        with pytest.raises(TypeError):
            SpecificationBase()  # pylint: disable=no-value-for-parameter

    def test_when_supplied_invalid_object_then_raises_TypeError(self):
        with pytest.raises(TypeError):
            SpecificationBase({})
        with pytest.raises(TypeError):
            SpecificationBase(None)
        with pytest.raises(TypeError):
            SpecificationBase("a string")

    def test_when_passed_data_then_wraps(self):
        a_data = TraitsData()
        specification = SpecificationBase(a_data)
        assert specification.traitsData() is a_data


class Test_SpecificationBase_create:
    def test_all_traits_set_in_data(self):
        specification = ATestSpecification.create()
        data = specification.traitsData()
        assert data.traitIds() == ATestSpecification.kTraitIds


class ATrait(Trait):
    kId = "a"

    def setProperty(self, value):
        self._data.setTraitProperty(self.kId, "property", value)

    def getProperty(self):
        return self._data.getTraitProperty(self.kId, "property")


class ATestSpecification(SpecificationBase):
    kTraitIds = {ATrait.kId, "🐝"}

    def aTrait(self):
        return ATrait(self._data)
