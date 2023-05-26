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

from unittest.mock import Mock, call

import pytest

from openassetio import EntityReference
from openassetio.managerApi import ManagerInterface, ManagerStateBase


class Test_ManagerInterface_identifier:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(ManagerInterface.identifier)
        assert method_introspector.is_implemented_once(ManagerInterface, "identifier")

    def test_when_not_overridden_then_raises_exception(self):
        with pytest.raises(RuntimeError) as err:
            ManagerInterface().identifier()
        assert (
            str(err.value) == 'Tried to call pure virtual function "ManagerInterface::identifier"'
        )


class Test_ManagerInterface_displayName:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(ManagerInterface.displayName)
        assert method_introspector.is_implemented_once(ManagerInterface, "displayName")

    def test_when_not_overridden_then_raises_exception(self):
        with pytest.raises(RuntimeError) as err:
            ManagerInterface().displayName()
        assert (
            str(err.value) == 'Tried to call pure virtual function "ManagerInterface::displayName"'
        )


class Test_ManagerInterface_info:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(ManagerInterface.info)
        assert method_introspector.is_implemented_once(ManagerInterface, "info")

    def test_when_not_overridden_then_returns_empty_dict(self):
        info = ManagerInterface().info()

        assert isinstance(info, dict)
        assert info == {}


class Test_ManagerInterface_createState:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(ManagerInterface.createState)
        assert method_introspector.is_implemented_once(ManagerInterface, "createState")

    def test_default_implementation_returns_none(self, a_host_session):
        assert ManagerInterface().createState(a_host_session) is None


class Test_ManagerInterface_createChildState:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(ManagerInterface.createChildState)
        assert method_introspector.is_implemented_once(ManagerInterface, "createChildState")

    def test_default_implementation_raises_RuntimeError(self, a_host_session):
        with pytest.raises(RuntimeError):
            ManagerInterface().createChildState(ManagerStateBase(), a_host_session)

    def test_when_none_is_supplied_then_TypeError_is_raised(self, a_host_session):
        with pytest.raises(TypeError):
            ManagerInterface().createChildState(None, a_host_session)


class Test_ManagerInterface_persistenceTokenForState:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(
            ManagerInterface.persistenceTokenForState
        )
        assert method_introspector.is_implemented_once(
            ManagerInterface, "persistenceTokenForState"
        )

    def test_when_none_is_supplied_then_TypeError_is_raised(self, a_host_session):
        with pytest.raises(TypeError):
            ManagerInterface().persistenceTokenForState(None, a_host_session)

    def test_default_implementation_raises_RuntimeError(self, a_host_session):
        with pytest.raises(RuntimeError):
            ManagerInterface().persistenceTokenForState(ManagerStateBase(), a_host_session)


class Test_ManagerInterface_stateFromPersistenceToken:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(
            ManagerInterface.stateFromPersistenceToken
        )
        assert method_introspector.is_implemented_once(
            ManagerInterface, "stateFromPersistenceToken"
        )

    def test_when_none_is_supplied_then_TypeError_is_raised(self, a_host_session):
        with pytest.raises(TypeError):
            ManagerInterface().createChildState(None, a_host_session)

    def test_default_implementation_raises_RuntimeError(self, a_host_session):
        with pytest.raises(RuntimeError):
            ManagerInterface().stateFromPersistenceToken("", a_host_session)


class Test_ManagerInterface_defaultEntityReference:
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(ManagerInterface.defaultEntityReference)
        assert method_introspector.is_implemented_once(ManagerInterface, "defaultEntityReference")

    def test_when_given_single_trait_set_then_returns_single_empty_ref(self, manager_interface):
        refs = manager_interface.defaultEntityReference([()], Mock(), Mock())
        assert refs == [""]

    def test_when_given_multiple_trait_set_then_returns_corresponding_number_of_empty_refs(
        self, manager_interface
    ):
        refs = manager_interface.defaultEntityReference([(), (), ()], Mock(), Mock())
        assert refs == ["", "", ""]


class Test_ManagerInterface_entityVersion:
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(ManagerInterface.entityVersion)
        assert method_introspector.is_implemented_once(ManagerInterface, "entityVersion")

    def test_when_given_single_ref_then_returns_single_empty_name(self, manager_interface):
        names = manager_interface.entityVersion([Mock()], Mock(), Mock())
        assert names == [""]

    def test_when_given_multiple_refs_then_returns_corresponding_number_of_empty_names(
        self, manager_interface
    ):
        names = manager_interface.entityVersion([Mock(), Mock(), Mock()], Mock(), Mock())
        assert names == ["", "", ""]


class Test_ManagerInterface_entityVersions:
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(ManagerInterface.entityVersions)
        assert method_introspector.is_implemented_once(ManagerInterface, "entityVersions")

    def test_when_given_single_ref_then_returns_single_empty_version_dicts(
        self, manager_interface
    ):
        versions = manager_interface.entityVersions([Mock()], Mock(), Mock())
        assert versions == [{}]

    def test_when_given_multiple_refs_then_returns_corresponding_number_of_empty_version_dicts(
        self, manager_interface
    ):
        versions = manager_interface.entityVersions([Mock(), Mock(), Mock()], Mock(), Mock())
        assert versions == [{}, {}, {}]


class Test_ManagerInterface_finalizedEntityVersion:
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(ManagerInterface.finalizedEntityVersion)
        assert method_introspector.is_implemented_once(ManagerInterface, "finalizedEntityVersion")

    def test_when_given_refs_then_returns_refs_unaltered(self, manager_interface):
        refs = Mock()

        finalized_refs = manager_interface.finalizedEntityVersion(refs, Mock(), Mock())

        assert finalized_refs == refs


class Test_ManagerInterface_getWithRelationship:
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(ManagerInterface.getWithRelationship)
        assert method_introspector.is_implemented_once(ManagerInterface, "getWithRelationship")

    def test_returns_empty_list_for_each_input(self, manager_interface):
        success_callback = Mock()
        error_callback = Mock()

        for refs in (
            [],
            [Mock()],
            [Mock(), Mock()],
        ):
            manager_interface.getWithRelationship(
                Mock(), refs, Mock(), Mock(), success_callback, error_callback
            )

            error_callback.assert_not_called()
            success_callback.assert_has_calls([call(i, []) for i in range(len(refs))])

            success_callback.reset_mock()


class Test_ManagerInterface_getWithRelationships:
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(ManagerInterface.getWithRelationships)
        assert method_introspector.is_implemented_once(ManagerInterface, "getWithRelationships")

    def test_returns_empty_list_for_each_input(self, manager_interface):
        success_callback = Mock()
        error_callback = Mock()

        for rels in (
            [],
            [Mock()],
            [Mock(), Mock()],
        ):
            manager_interface.getWithRelationships(
                rels, Mock(), Mock(), Mock(), success_callback, error_callback
            )

            error_callback.assert_not_called()
            success_callback.assert_has_calls([call(i, []) for i in range(len(rels))])

            success_callback.reset_mock()


class Test_ManagerInterface__createEntityReference:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(
            ManagerInterface._createEntityReference  # pylint:disable=protected-access
        )
        assert method_introspector.is_implemented_once(ManagerInterface, "_createEntityReference")

    def test_when_input_is_string_then_wrapped_in_entity_reference(self, manager_interface):
        a_string = "some string"
        # pylint: disable=protected-access
        actual = manager_interface._createEntityReference(a_string)
        assert isinstance(actual, EntityReference)
        assert actual.toString() == a_string

    def test_when_input_is_none_then_typeerror_raised(self, manager_interface):
        with pytest.raises(TypeError):
            manager_interface._createEntityReference(None)  # pylint: disable=protected-access

    def test_when_input_is_not_a_string_then_typeerror_raised(self, manager_interface):
        with pytest.raises(TypeError):
            manager_interface._createEntityReference(1)  # pylint: disable=protected-access

    def test_is_entity_reference_string_is_not_called(self, mock_manager_interface):
        # pylint: disable=protected-access
        _ = mock_manager_interface._createEntityReference("some string")
        mock_manager_interface.mock.isEntityReferenceString.assert_not_called()


@pytest.fixture
def manager_interface():
    return ManagerInterface()
