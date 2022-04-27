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

import pytest

from openassetio import Specification, Trait


class Test_Trait_Construction:
    def test_exposes_wrapped_specification_via_protected_member(self, a_custom_trait_class):
        a_specification = mock.Mock()
        trait = a_custom_trait_class(a_specification)
        assert trait._specification is a_specification  # pylint: disable=protected-access


class Test_Trait_isValid:
    def test_when_specification_has_trait_returns_true(self, a_custom_trait_class):
        a_specification = Specification({a_custom_trait_class.kId})
        trait = a_custom_trait_class(a_specification)
        assert trait.isValid() is True

    def test_when_specification_does_not_have_trait_returns_false(self, a_custom_trait_class):
        a_specification = Specification({"someOtherTrait"})
        trait = a_custom_trait_class(a_specification)
        assert trait.isValid() is False


@pytest.fixture
def a_custom_trait_class():
    class CustomTrait(Trait):
        kId = "customTrait"
    return CustomTrait
