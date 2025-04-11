#  SPDX-License-Identifier: Apache-2.0
#  Copyright 2025 The Foundry Visionmongers Ltd
"""
Tests that cover the openassetio.ui.hostApi.UIDelegate class.
"""
from unittest import mock

# pylint: disable=missing-class-docstring,invalid-name,missing-function-docstring
# pylint: disable=redefined-outer-name
import pytest

from openassetio import Context
from openassetio.trait import TraitsData
from openassetio.ui.access import UIAccess
from openassetio.ui.hostApi import UIDelegate


class Test_UIDelegate_identifier:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, ui_delegate, mock_ui_delegate_interface
    ):
        mock_ui_delegate_interface.mock.identifier.return_value = "mock_identifier"

        assert ui_delegate.identifier() == "mock_identifier"


class Test_UIDelegate_displayName:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, ui_delegate, mock_ui_delegate_interface
    ):
        mock_ui_delegate_interface.mock.displayName.return_value = "mock_displayName"

        assert ui_delegate.displayName() == "mock_displayName"


class Test_UIDelegate_info:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, ui_delegate, mock_ui_delegate_interface
    ):
        mock_ui_delegate_interface.mock.info.return_value = {"a": "b"}

        assert ui_delegate.info() == {"a": "b"}


class Test_UIDelegate_settings:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, ui_delegate, mock_ui_delegate_interface, a_host_session
    ):
        mock_ui_delegate_interface.mock.settings.return_value = {"c": "d"}

        assert ui_delegate.settings() == {"c": "d"}

        mock_ui_delegate_interface.mock.settings.assert_called_once_with(a_host_session)


class Test_UIDelegate_initialize:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, ui_delegate, mock_ui_delegate_interface, a_host_session
    ):
        ui_delegate.initialize({"c": "d"})

        mock_ui_delegate_interface.mock.initialize.assert_called_once_with(
            {"c": "d"}, a_host_session
        )


class Test_UIDelegate_close:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, ui_delegate, mock_ui_delegate_interface, a_host_session
    ):
        ui_delegate.close()

        mock_ui_delegate_interface.mock.close.assert_called_once_with(a_host_session)

    def test_when_destroyed_then_close_called(self, mock_ui_delegate_interface, a_host_session):
        UIDelegate(mock_ui_delegate_interface, a_host_session)

        mock_ui_delegate_interface.mock.close.assert_called_once_with(a_host_session)

    def test_when_destroyed_and_close_raises_then_exception_logged(
        self, mock_ui_delegate_interface, a_host_session, mock_logger
    ):
        error = RuntimeError("Boom!")
        mock_ui_delegate_interface.mock.close.side_effect = error

        UIDelegate(mock_ui_delegate_interface, a_host_session)

        args, _kwargs = mock_logger.mock.log.call_args
        assert args[0] == mock_logger.Severity.kError
        assert args[1].startswith(
            "Exception closing UI delegate during destruction: RuntimeError: Boom!"
        )


class Test_UIDelegate_populateUI:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        ui_delegate,
        mock_ui_delegate_interface,
        a_traits_data,
        mock_ui_delegate_request_interface,
        a_context,
        a_host_session,
    ):
        mock_ui_delegate_interface.mock.populateUI.return_value = None

        ui_delegate.populateUI(
            a_traits_data,
            UIAccess.kRead,
            mock_ui_delegate_request_interface,
            a_context,
        )

        mock_ui_delegate_interface.mock.populateUI.assert_called_once_with(
            a_traits_data,
            UIAccess.kRead,
            mock.ANY,  # Middleware type, see below.
            a_context,
            a_host_session,
        )

        initial_request = mock_ui_delegate_interface.mock.populateUI.call_args[0][2]
        # Exploit nativeData to detect that the middleware-wrapped
        # request is the provided request.
        assert (
            initial_request.nativeData()
            is mock_ui_delegate_request_interface.mock.nativeData.return_value
        )

    def test_when_interface_returns_None_then_middleware_returns_None(
        self,
        ui_delegate,
        mock_ui_delegate_interface,
        a_traits_data,
        mock_ui_delegate_request_interface,
        a_context,
    ):
        expected = None
        mock_ui_delegate_interface.mock.populateUI.return_value = expected

        actual = ui_delegate.populateUI(
            a_traits_data,
            UIAccess.kRead,
            mock_ui_delegate_request_interface,
            a_context,
        )

        assert actual is expected

    def test_when_interface_returns_state_then_middleware_returns_wrapped_state(
        self,
        ui_delegate,
        mock_ui_delegate_interface,
        a_traits_data,
        mock_ui_delegate_request_interface,
        mock_ui_delegate_state_interface,
        a_context,
    ):
        mock_ui_delegate_interface.mock.populateUI.return_value = mock_ui_delegate_state_interface

        initial_state = ui_delegate.populateUI(
            a_traits_data,
            UIAccess.kRead,
            mock_ui_delegate_request_interface,
            a_context,
        )

        # Exploit nativeData to detect that the middleware-wrapped state
        # is the returned state.
        expected_native_data = mock_ui_delegate_state_interface.mock.nativeData.return_value
        actual_native_data = initial_state.nativeData()

        assert actual_native_data is expected_native_data


class Test_UIDelegate_uiPolicy:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, ui_delegate, mock_ui_delegate_interface, a_context, a_host_session, a_traits_data
    ):
        expected = a_traits_data
        mock_ui_delegate_interface.mock.uiPolicy.return_value = expected

        actual = ui_delegate.uiPolicy(
            {"d", "e"},
            UIAccess.kRead,
            a_context,
        )

        mock_ui_delegate_interface.mock.uiPolicy.assert_called_once_with(
            {"d", "e"},
            UIAccess.kRead,
            a_context,
            a_host_session,
        )
        assert actual == expected


@pytest.fixture
def a_traits_data():
    return TraitsData({"a", "b", "c"})


@pytest.fixture
def a_context():
    return Context()


@pytest.fixture
def ui_delegate(mock_ui_delegate_interface, a_host_session):
    return UIDelegate(mock_ui_delegate_interface, a_host_session)
