#
#   Copyright 2013-2021 [The Foundry Visionmongers Ltd]
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

import pytest
from unittest import mock

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


class TestTransactionCoordinator:

    def test_construction(self, mock_manager):
        coordinator = t.TransactionCoordinator(mock_manager)
        assert coordinator.manager() is mock_manager

    def test_scopedActionGroup(self, transaction_coordinator, a_context):
        scoped_group = transaction_coordinator.scopedActionGroup(a_context)
        assert isinstance(scoped_group, t.ScopedActionGroup)
        assert scoped_group.cancelOnException is True

    def test_pushActionGroup(self, transaction_coordinator, mock_host_session, a_context):

        mock_manager = transaction_coordinator.manager()._getInterface()
        state = a_context.managerInterfaceState

        assert a_context.actionGroupDepth == 0
        self.__assertTransactionCalls(
            mock_manager, mock_host_session, start=None, finish=None, cancel=None)

        transaction_coordinator.pushActionGroup(a_context)
        assert a_context.actionGroupDepth == 1
        self.__assertTransactionCalls(
            mock_manager, mock_host_session, start=state, finish=None, cancel=None)

        transaction_coordinator.pushActionGroup(a_context)
        assert a_context.actionGroupDepth == 2
        self.__assertTransactionCalls(
            mock_manager, mock_host_session, start=None, finish=None, cancel=None)

    def test_popActionGroup(self, transaction_coordinator, mock_host_session, a_context):

        mock_manager = transaction_coordinator.manager()._getInterface()
        state = a_context.managerInterfaceState

        a_context.actionGroupDepth = 2

        transaction_coordinator.popActionGroup(a_context)
        assert a_context.actionGroupDepth == 1
        self.__assertTransactionCalls(
            mock_manager, mock_host_session, start=None, finish=None, cancel=None)

        transaction_coordinator.popActionGroup(a_context)
        assert a_context.actionGroupDepth == 0
        self.__assertTransactionCalls(
            mock_manager, mock_host_session, start=None, finish=state, cancel=None)

        with pytest.raises(RuntimeError):
            transaction_coordinator.popActionGroup(a_context)
        self.__assertTransactionCalls(
            mock_manager, mock_host_session, start=None, finish=None, cancel=None)

    def test_cancelActions(self, transaction_coordinator, mock_host_session, a_context):

        mock_manager = transaction_coordinator.manager()._getInterface()
        state = a_context.managerInterfaceState

        # Check return values and depth management

        mock_manager.cancelTransaction.return_value = True

        a_context.actionGroupDepth = 2
        assert transaction_coordinator.cancelActions(a_context) is True
        self.__assertTransactionCalls(
            mock_manager, mock_host_session, start=None, finish=None, cancel=state)
        assert a_context.actionGroupDepth == 0

        mock_manager.cancelTransaction.return_value = False

        a_context.actionGroupDepth = 2
        assert transaction_coordinator.cancelActions(a_context) is False
        self.__assertTransactionCalls(
            mock_manager, mock_host_session, start=None, finish=None, cancel=state)
        assert a_context.actionGroupDepth == 0

        # Check depth == 0 is an early-out

        mock_manager.cancelTransaction.return_value = False

        a_context.actionGroupDepth = 0
        assert transaction_coordinator.cancelActions(a_context) is True
        self.__assertTransactionCalls(
            mock_manager, mock_host_session, start=None, finish=None, cancel=None)
        assert a_context.actionGroupDepth == 0

    def test_actionGroupDepth(self, transaction_coordinator, a_context):

        assert a_context.actionGroupDepth == 0
        assert transaction_coordinator.actionGroupDepth(a_context) == 0

        transaction_coordinator.pushActionGroup(a_context)
        assert transaction_coordinator.actionGroupDepth(a_context) == 1

        a_context.actionGroupDepth = 77
        assert transaction_coordinator.actionGroupDepth(a_context) == 77

    def test_managerInterfaceState_freeze_thaw(
            self, transaction_coordinator, mock_host_session, a_context):

        mock_manager = transaction_coordinator.manager()._getInterface()

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

    @staticmethod
    def __assertTransactionCalls(mock_manager, mock_host_session, start, finish, cancel):

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


class TestScopedActionGroup:

    def test_scope(self, a_scoped_group):

        mock_coordinator = a_scoped_group._ScopedActionGroup__transactionCoordinator
        a_context = a_scoped_group._ScopedActionGroup__context

        a_scoped_group.cancelOnException = True

        with a_scoped_group:
            self.__assertActionGroupCalls(mock_coordinator, push=a_context, pop=None, cancel=None)

        self.__assertActionGroupCalls(mock_coordinator, push=None, pop=a_context, cancel=None)

        with pytest.raises(RuntimeError):
            with a_scoped_group:
                self.__assertActionGroupCalls(
                    mock_coordinator, push=a_context, pop=None, cancel=None)
                raise RuntimeError

            self.__assertActionGroupCalls(mock_coordinator, push=None, pop=None, cancel=a_context)

    def test_scope_does_not_cancel(self, a_scoped_group):

        mock_coordinator = a_scoped_group._ScopedActionGroup__transactionCoordinator
        a_context = a_scoped_group._ScopedActionGroup__context

        a_scoped_group.cancelOnException = False

        with pytest.raises(RuntimeError):
            with a_scoped_group:
                self.__assertActionGroupCalls(
                    mock_coordinator, push=a_context, pop=None, cancel=None)
                raise RuntimeError

            self.__assertActionGroupCalls(mock_coordinator, push=None, pop=a_context, cancel=None)

    @staticmethod
    def __assertActionGroupCalls(mock_coordinator, push, pop, cancel):

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
