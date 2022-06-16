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

from openassetio.managerAPI import ManagerInterface, ManagerStateBase


class Test_ManagerInterface_identifier:
    def test_when_not_overridden_then_raises_exception(self):
        with pytest.raises(RuntimeError) as err:
            ManagerInterface().identifier()
        assert(str(err.value) ==
               'Tried to call pure virtual function "ManagerInterface::identifier"')

    def test_when_overridden_then_returns_value(self, manager_interface):
        assert manager_interface.identifier() == "stub.manager"


class Test_ManagerInterface_displayName:
    def test_when_not_overridden_then_raises_exception(self):
        with pytest.raises(RuntimeError) as err:
            ManagerInterface().displayName()
        assert(str(err.value) ==
               'Tried to call pure virtual function "ManagerInterface::displayName"')

    def test_when_overridden_then_returns_value(self, manager_interface):
        assert manager_interface.displayName() == "Stub Manager"


class Test_ManagerInterface_info:
    def test_when_not_overridden_then_returns_empty_dict(self):
        info = ManagerInterface().info()

        assert isinstance(info, dict)
        assert info == {}

    def test_when_overridden_then_returns_expected_dict(self, manager_interface):
        info = manager_interface.info()

        assert isinstance(info, dict)
        assert info == {"stub": "info"}


class Test_ManagerInterface_createState:
    def test_default_implementation_returns_none(self, mock_host_session):
        assert ManagerInterface().createState(mock_host_session) is None

    def test_when_overridden_then_returns_value(self, manager_interface, mock_host_session):
        assert manager_interface.createState(mock_host_session).value == "a state"


class Test_ManagerInterface_createChildState:
    def test_default_implementation_raises_RuntimeError(self, mock_host_session):
        with pytest.raises(RuntimeError):
            ManagerInterface().createChildState(ManagerStateBase(), mock_host_session)

    def test_when_none_is_supplied_then_TypeError_is_raised(self, mock_host_session):
        with pytest.raises(TypeError):
            ManagerInterface().createChildState(None, mock_host_session)

    def test_when_overridden_then_returns_value(
            self, persistence_manager_interface, mock_host_session):
        a_state = persistence_manager_interface.createState(mock_host_session)

        assert (
            persistence_manager_interface.createChildState(a_state, mock_host_session).value
            == "a child state of a state"
        )


class Test_ManagerInterface_persistenceTokenForState:
    def test_when_none_is_supplied_then_TypeError_is_raised(self, mock_host_session):
        with pytest.raises(TypeError):
            ManagerInterface().persistenceTokenForState(None, mock_host_session)

    def test_default_implementation_raises_RuntimeError(self, mock_host_session):
        with pytest.raises(RuntimeError):
            ManagerInterface().persistenceTokenForState(ManagerStateBase(), mock_host_session)

    def test_when_overridden_then_returns_value(
            self, persistence_manager_interface, mock_host_session):
        a_state = persistence_manager_interface.createState(mock_host_session)
        expected_token = f"<{a_state.value}>"
        assert (
            persistence_manager_interface.persistenceTokenForState(a_state, mock_host_session)
            == expected_token
        )


class Test_ManagerInterface_stateFromPersistenceToken:
    def test_when_none_is_supplied_then_TypeError_is_raised(self, mock_host_session):
        with pytest.raises(TypeError):
            ManagerInterface().createChildState(None, mock_host_session)

    def test_default_implementation_raises_RuntimeError(self, mock_host_session):
        with pytest.raises(RuntimeError):
            ManagerInterface().stateFromPersistenceToken("", mock_host_session)

    def test_when_overridden_then_returns_value(self, manager_interface, mock_host_session):
        a_state = manager_interface.createState(mock_host_session)

        assert (
            manager_interface.createChildState(a_state, mock_host_session).value
            == "a child state of a state"
        )


class Test_ManagerInterface_defaultEntityReference:
    def test_when_given_single_trait_set_then_returns_single_empty_ref(self, manager_interface):
        refs = manager_interface.defaultEntityReference([()], Mock(), Mock())
        assert refs == [""]

    def test_when_given_multiple_trait_set_then_returns_corresponding_number_of_empty_refs(
            self, manager_interface):
        refs = manager_interface.defaultEntityReference([(), (), ()], Mock(), Mock())
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


class StubManagerInterface(ManagerInterface):
    # pylint: disable=abstract-method

    class StubManagerState(ManagerStateBase):
        def __init__(self, value):
            super().__init__()
            self.value = value

    # TODO(DF): @pylint - remove once all abstract methods migrated
    def identifier(self):
        return "stub.manager"

    def displayName(self):
        return "Stub Manager"

    def info(self):
        return {"stub": "info"}

    def createState(self, _):
        return StubManagerInterface.StubManagerState("a state")

    def createChildState(self, parentState, _):
        return StubManagerInterface.StubManagerState(f"a child state of {parentState.value}")


class PersistenceStubManagerInterface(StubManagerInterface):
    # pylint: disable=abstract-method

    def persistenceTokenForState(self, state, _):
        return f"<{state.value}>"

    def stateFromPersistenceToken(self, token, _):
        value = token[1:-1]
        return StubManagerInterface.StubManagerState(value)


@pytest.fixture
def manager_interface():
    return StubManagerInterface()

@pytest.fixture
def persistence_manager_interface():
    return PersistenceStubManagerInterface()
