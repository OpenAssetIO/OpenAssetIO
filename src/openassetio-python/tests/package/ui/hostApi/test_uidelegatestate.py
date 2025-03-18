#
#   Copyright 2025 The Foundry Visionmongers Ltd
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
Tests for the UIDelegateState middleware class.
"""
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name,redefined-outer-name
from unittest import mock

import pytest

from openassetio import EntityReference
from openassetio.trait import TraitsData
from openassetio.ui.hostApi import UIDelegateState


class Test_UIDelegateState_entityReferences:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, mock_ui_delegate_state_interface, ui_delegate_state
    ):
        expected = [EntityReference("abc")]
        mock_ui_delegate_state_interface.mock.entityReferences.return_value = expected

        actual = ui_delegate_state.entityReferences()

        assert actual == expected


class Test_UIDelegateState_entityTraitsDatas:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, mock_ui_delegate_state_interface, ui_delegate_state
    ):
        expected = [TraitsData({"abc"})]
        mock_ui_delegate_state_interface.mock.entityTraitsDatas.return_value = expected

        actual = ui_delegate_state.entityTraitsDatas()

        assert actual == expected


class Test_UIDelegateState_nativeData:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, mock_ui_delegate_state_interface, ui_delegate_state
    ):
        expected = mock.Mock()
        mock_ui_delegate_state_interface.mock.nativeData.return_value = expected

        actual = ui_delegate_state.nativeData()

        assert actual is expected


class Test_UIDelegateState_updateRequestCallback:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        ui_delegate_state,
        mock_ui_delegate_state_interface,
        mock_ui_delegate_request_interface,
    ):
        interface_callback = mock.Mock()
        mock_ui_delegate_state_interface.mock.updateRequestCallback.return_value = (
            interface_callback
        )

        # Get wrapped callback.
        middleware_callback = ui_delegate_state.updateRequestCallback()
        # Middleware constructs a UIDelegateRequest wrapping the given
        # UIDelegateRequestInterface and passes it along to our
        # interface_callback.
        middleware_callback(mock_ui_delegate_request_interface)

        interface_callback.assert_called_once()
        ui_delegate_request = interface_callback.call_args[0][0]
        assert (
            ui_delegate_request.nativeData()
            is mock_ui_delegate_request_interface.mock.nativeData.return_value
        )

    def test_when_middleware_callback_called_with_None_then_interface_callback_called_with_None(
        self,
        ui_delegate_state,
        mock_ui_delegate_state_interface,
    ):
        interface_callback = mock.Mock()
        mock_ui_delegate_state_interface.mock.updateRequestCallback.return_value = (
            interface_callback
        )

        ui_delegate_state.updateRequestCallback()(None)

        interface_callback.assert_called_once_with(None)

    def test_when_interface_callback_is_None_then_middleware_callback_is_None(
        self,
        ui_delegate_state,
        mock_ui_delegate_state_interface,
    ):
        mock_ui_delegate_state_interface.mock.updateRequestCallback.return_value = None

        middleware_callback = ui_delegate_state.updateRequestCallback()

        assert middleware_callback is None


@pytest.fixture
def ui_delegate_state(mock_ui_delegate_state_interface):
    return UIDelegateState(mock_ui_delegate_state_interface)
