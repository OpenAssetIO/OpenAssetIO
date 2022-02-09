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
Tests that cover the openassetio.hostAPI.transactions module.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

## TODO (tc) These tests make assertions against methods called on the
## manager interface, not the manager. This is technically conflating
## concerns as it is making assumptions about the way Manager works.
## We should instead be mocking that.

from unittest import mock

import pytest

from openassetio import Context
from openassetio.hostAPI import transactions as t, Manager
from openassetio.managerAPI import HostSession, ManagerInterface


@pytest.fixture
def mock_host_session():
    return mock.create_autospec(HostSession)


@pytest.fixture
def mock_manager(mock_host_session):
    mock_interface = mock.create_autospec(ManagerInterface)
    return Manager(mock_interface, mock_host_session)


@pytest.fixture
def transaction_coordinator(mock_manager):
    return t.TransactionCoordinator(mock_manager)


@pytest.fixture
def a_context():
    context = Context()
    context.managerInterfaceState = "some-manager-state"
    return context


@pytest.fixture
def a_scoped_group(a_context):
    mocked_coordinator = mock.create_autospec(t.TransactionCoordinator)
    return t.ScopedActionGroup(mocked_coordinator, a_context)


class Test_TransactionCoordinator_manager:

    def test_when_manager_called_then_returns_the_constructor_supplied_manager(
            self, mock_manager):

        coordinator = t.TransactionCoordinator(mock_manager)
        assert coordinator.manager() is mock_manager


class Test_TransactionCoordinator_scopedActionGroup:

    def test_ScopedActionGroup_instance_returned(
            self, transaction_coordinator, a_context):

        scoped_group = transaction_coordinator.scopedActionGroup(a_context)
        assert isinstance(scoped_group, t.ScopedActionGroup)

    def test_cancels_on_exception_by_default(
            self, transaction_coordinator, a_context):

        scoped_group = transaction_coordinator.scopedActionGroup(a_context)
        assert scoped_group.cancelOnException is True


class Test_TransactionCoordinator_pushActionGroup:
    # pylint: disable=protected-access

    def test_actionGroup_depth_is_incremented(
            self, transaction_coordinator, a_context):

        assert a_context.actionGroupDepth == 0
        transaction_coordinator.pushActionGroup(a_context)
        assert a_context.actionGroupDepth == 1
        transaction_coordinator.pushActionGroup(a_context)
        assert a_context.actionGroupDepth == 2

    def test_when_called_repeatedly_then_startTransaction_only_called_once(
            self, transaction_coordinator, mock_host_session, a_context):

        mock_interface = transaction_coordinator.manager()._interface()
        state = a_context.managerInterfaceState

        assert_transaction_calls(
            mock_interface, mock_host_session, start=None, finish=None, cancel=None)

        transaction_coordinator.pushActionGroup(a_context)
        assert_transaction_calls(
            mock_interface, mock_host_session, start=state, finish=None, cancel=None)

        transaction_coordinator.pushActionGroup(a_context)
        assert_transaction_calls(
            mock_interface, mock_host_session, start=None, finish=None, cancel=None)


class Test_TransactionCoordinator_popActionGroup:
    # pylint: disable=protected-access

    def test_actionGroup_depth_is_decremented(
            self, transaction_coordinator, a_context):

        a_context.actionGroupDepth = 2
        transaction_coordinator.popActionGroup(a_context)
        assert a_context.actionGroupDepth == 1
        transaction_coordinator.popActionGroup(a_context)
        assert a_context.actionGroupDepth == 0

    def test_when_called_repeatedly_then_finishTransaction_only_called_once(
            self, transaction_coordinator, mock_host_session, a_context):

        mock_interface = transaction_coordinator.manager()._interface()
        state = a_context.managerInterfaceState

        a_context.actionGroupDepth = 2

        transaction_coordinator.popActionGroup(a_context)
        assert a_context.actionGroupDepth == 1
        assert_transaction_calls(
            mock_interface, mock_host_session, start=None, finish=None, cancel=None)

        transaction_coordinator.popActionGroup(a_context)
        assert a_context.actionGroupDepth == 0
        assert_transaction_calls(
            mock_interface, mock_host_session, start=None, finish=state, cancel=None)

        with pytest.raises(RuntimeError):
            transaction_coordinator.popActionGroup(a_context)
        assert_transaction_calls(
            mock_interface, mock_host_session, start=None, finish=None, cancel=None)

    def test_when_depth_is_zero_then_RuntimeError_is_raised(
            self, transaction_coordinator, a_context):

        a_context.actionGroupDepth = 0

        with pytest.raises(RuntimeError):
            transaction_coordinator.popActionGroup(a_context)

    def test_when_depth_is_zero_then_manager_is_not_called(
            self, mock_host_session, transaction_coordinator, a_context):

        a_context.actionGroupDepth = 0

        try:
            transaction_coordinator.popActionGroup(a_context)
        except Exception:  # pylint: disable=broad-except
            pass

        assert_transaction_calls(
            transaction_coordinator.manager()._interface(), mock_host_session,
            start=None, finish=None, cancel=None)


class Test_TransactionCoordinator_cancelActions:
    # pylint: disable=protected-access

    def test_when_depth_is_zero_then_manager_is_not_called_and_true_is_returned(
            self, transaction_coordinator, mock_host_session, a_context):

        mock_interface = transaction_coordinator.manager()._interface()
        # Ensure the manager will return a different value to the
        # expected one so we can verify that the return value is not
        # from the manager.
        mock_interface.cancelTransaction.return_value = False

        a_context.actionGroupDepth = 0

        transaction_coordinator.cancelActions(a_context)
        assert_transaction_calls(
            mock_interface, mock_host_session, start=None, finish=None, cancel=None)


    def test_when_depth_is_not_zero_then_manager_is_called_and_its_result_returned(
            self, transaction_coordinator, mock_host_session, a_context):

        mock_interface = transaction_coordinator.manager()._interface()
        state = a_context.managerInterfaceState

        # We can't use a `mock` value as a sentinel to verify that the
        # return _is_ actually the value from the manager, as this won't
        # roundtrip through C++, so we instead have to test both
        # possible permutations.

        mock_interface.cancelTransaction.return_value = True

        a_context.actionGroupDepth = 1
        assert transaction_coordinator.cancelActions(a_context) is True
        assert_transaction_calls(
            mock_interface, mock_host_session, start=None, finish=None, cancel=state)

        mock_interface.cancelTransaction.return_value = False

        a_context.actionGroupDepth = 2
        assert transaction_coordinator.cancelActions(a_context) is False
        assert_transaction_calls(
            mock_interface, mock_host_session, start=None, finish=None, cancel=state)

    def test_when_depth_is_not_zero_then_depth_is_reset_to_zero_after_call(
            self, transaction_coordinator, a_context):

        a_context.actionGroupDepth = 123
        transaction_coordinator.cancelActions(a_context)
        assert a_context.actionGroupDepth == 0


class Test_TransactionCoordinator_actionGroupDepth:
    # pylint: disable=protected-access

    def test_returns_context_depth(self, transaction_coordinator, a_context):

        assert a_context.actionGroupDepth == 0
        assert transaction_coordinator.actionGroupDepth(a_context) == 0

        transaction_coordinator.pushActionGroup(a_context)
        assert transaction_coordinator.actionGroupDepth(a_context) == 1

        a_context.actionGroupDepth = 77
        assert transaction_coordinator.actionGroupDepth(a_context) == 77


class Test_TransactionCoordinator_freeze_thaw:
    # pylint: disable=protected-access

    def test_when_frozen_and_thawed_then_context_depth_and_state_are_restored(
            self, transaction_coordinator, mock_host_session, a_context):

        mock_manager = transaction_coordinator.manager()._interface()

        state = a_context.managerInterfaceState
        mock_frozen_state = f"frozen-{state}"

        mock_manager.freezeState.return_value = mock_frozen_state
        mock_manager.thawState.return_value = state

        action_group_depth = 4

        a_context.actionGroupDepth = action_group_depth

        # Freeze

        token = transaction_coordinator.freezeManagerState(a_context)
        mock_manager.freezeState.assert_called_once_with(state, mock_host_session)
        assert isinstance(token, str)
        assert token != ""

        # Clear context (this isn't done by freeze)

        a_context.managerInterfaceState = None
        a_context.actionGroupDepth = 0

        mock_manager.thawState.assert_not_called()

        # Thaw

        transaction_coordinator.thawManagerState(token, a_context)
        mock_manager.thawState.assert_called_once_with(mock_frozen_state, mock_host_session)
        assert a_context.managerInterfaceState == state
        assert a_context.actionGroupDepth == action_group_depth


class Test_ScopedActionGroup:
    # pylint: disable=protected-access

    def test_scope_is_pushed_on_entry_and_popped_on_exit(
            self, a_scoped_group):

        mock_coordinator = a_scoped_group._ScopedActionGroup__transactionCoordinator
        a_context = a_scoped_group._ScopedActionGroup__context

        with a_scoped_group:
            assert_action_group_calls(mock_coordinator, push=a_context, pop=None, cancel=None)

        assert_action_group_calls(mock_coordinator, push=None, pop=a_context, cancel=None)

    def test_when_an_exception_raised_then_actions_are_cancelled(
            self, a_scoped_group):

        mock_coordinator = a_scoped_group._ScopedActionGroup__transactionCoordinator
        a_context = a_scoped_group._ScopedActionGroup__context

        with pytest.raises(RuntimeError):
            with a_scoped_group:
                raise RuntimeError

            assert_action_group_calls(mock_coordinator, push=None, pop=None, cancel=a_context)

    def test_when_cancelOnException_is_false_and_an_exception_raised_then_scope_is_popped(
            self, a_scoped_group):

        mock_coordinator = a_scoped_group._ScopedActionGroup__transactionCoordinator
        a_context = a_scoped_group._ScopedActionGroup__context

        a_scoped_group.cancelOnException = False

        with pytest.raises(RuntimeError):
            with a_scoped_group:
                raise RuntimeError

            assert_action_group_calls(mock_coordinator, push=None, pop=a_context, cancel=None)


#
# Utilities
#

def assert_action_group_calls(mock_coordinator, push, pop, cancel):
    """
    A convenience methods that checks the actionGroup related methods
    of the supplied mock TransactionCoordinator object have been called
    with the specified arguments. If any of the supplied arguments are None,
    then it will be asserted that the method was not called.
    """

    for method, arg in (
            (mock_coordinator.pushActionGroup, push),
            (mock_coordinator.popActionGroup, pop),
            (mock_coordinator.cancelActions, cancel)
    ):
        if arg is None:
            method.assert_not_called()
        else:
            method.assert_called_once_with(arg)

    mock_coordinator.reset_mock()

def assert_transaction_calls(mock_manager, mock_host_session, start, finish, cancel):
    """
    Asserts that the start/finish/cancelTransaction methods of the
    supplied mock interface have been called with the specified args and
    host session. If any of the supplied args are None, then it will be
    asserted that the method was not called.
    """
    for method, arg in (
            (mock_manager.startTransaction, start),
            (mock_manager.finishTransaction, finish),
            (mock_manager.cancelTransaction, cancel)
    ):
        if arg is None:
            method.assert_not_called()
        else:
            method.assert_called_once_with(arg, mock_host_session)

    mock_manager.reset_mock()
