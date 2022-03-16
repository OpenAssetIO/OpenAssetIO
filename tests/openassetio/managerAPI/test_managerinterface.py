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
Tests for the default implementations of ManagerInterface methods.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

from unittest.mock import Mock

import pytest

from openassetio.managerAPI import ManagerInterface


@pytest.fixture
def manager_interface():
    return ManagerInterface()


class Test_ManagerInterface_defaultEntityReference:
    def test_when_given_single_spec_then_returns_single_empty_ref(self, manager_interface):
        refs = manager_interface.defaultEntityReference([Mock()], Mock(), Mock())
        assert refs == [""]

    def test_when_given_multiple_specs_then_returns_corresponding_number_of_empty_refs(
            self, manager_interface):
        refs = manager_interface.defaultEntityReference([Mock(), Mock(), Mock()], Mock(), Mock())
        assert refs == ["", "", ""]


class Test_ManagerInterface_entityVersion:
    def test_when_given_single_ref_then_returns_single_empty_name(self, manager_interface):
        names = manager_interface.entityVersion([Mock()], Mock(), Mock())
        assert names == [""]

    def test_when_given_multiple_refs_then_returns_corresponding_number_of_empty_names(
            self, manager_interface):
        names = manager_interface.entityVersion([Mock(), Mock(), Mock()], Mock(), Mock())
        assert names == ["", "", ""]


class Test_ManagerInterface_entityVersions:
    def test_when_given_single_ref_then_returns_single_empty_version_dicts(
            self, manager_interface):
        versions = manager_interface.entityVersions([Mock()], Mock(), Mock())
        assert versions == [{}]

    def test_when_given_multiple_refs_then_returns_corresponding_number_of_empty_version_dicts(
            self, manager_interface):
        versions = manager_interface.entityVersions([Mock(), Mock(), Mock()], Mock(), Mock())
        assert versions == [{}, {}, {}]


class Test_ManagerInterface_finalizedEntityVersion:

    def test_when_given_refs_then_returns_refs_unaltered(self, manager_interface):
        refs = Mock()

        finalized_refs = manager_interface.finalizedEntityVersion(refs, Mock(), Mock())

        assert finalized_refs == refs
