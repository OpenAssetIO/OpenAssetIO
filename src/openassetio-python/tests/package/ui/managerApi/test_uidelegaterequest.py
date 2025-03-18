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
Tests for the UIDelegateRequest middleware class.
"""
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name,redefined-outer-name)
from unittest import mock

import pytest

from openassetio import EntityReference, errors
from openassetio.trait import TraitsData
from openassetio.ui.managerApi import UIDelegateRequest


class Test_UIDelegateRequest_entityReferences:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, mock_ui_delegate_request_interface, ui_delegate_request
    ):
        expected = [EntityReference("abc")]
        mock_ui_delegate_request_interface.mock.entityReferences.return_value = expected

        actual = ui_delegate_request.entityReferences()

        assert actual == expected


class Test_UIDelegateRequest_entityTraitsDatas:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, mock_ui_delegate_request_interface, ui_delegate_request
    ):
        expected = [TraitsData({"abc"})]
        mock_ui_delegate_request_interface.mock.entityTraitsDatas.return_value = expected

        actual = ui_delegate_request.entityTraitsDatas()

        assert actual == expected


class Test_UIDelegateRequest_nativeData:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, mock_ui_delegate_request_interface, ui_delegate_request
    ):
        expected = mock.Mock()
        mock_ui_delegate_request_interface.mock.nativeData.return_value = expected

        actual = ui_delegate_request.nativeData()

        assert actual is expected


class Test_UIDelegateRequest_stateChangedCallback:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        ui_delegate_request,
        mock_ui_delegate_state_interface,
        mock_ui_delegate_request_interface,
    ):
        interface_callback = mock.Mock()
        mock_ui_delegate_request_interface.mock.stateChangedCallback.return_value = (
            interface_callback
        )

        # Get wrapped callback.
        middleware_callback = ui_delegate_request.stateChangedCallback()
        # Middleware constructs a UIDelegateState wrapping the given
        # UIDelegateStateInterface and passes it along to our
        # interface_callback.
        middleware_callback(mock_ui_delegate_state_interface)

        interface_callback.assert_called_once()
        ui_delegate_state = interface_callback.call_args[0][0]
        assert (
            ui_delegate_state.nativeData()
            is mock_ui_delegate_state_interface.mock.nativeData.return_value
        )

    def test_when_middleware_callback_called_with_None_then_exception_raised(
        self,
        ui_delegate_request,
        mock_ui_delegate_request_interface,
    ):
        interface_callback = mock.Mock()
        mock_ui_delegate_request_interface.mock.stateChangedCallback.return_value = (
            interface_callback
        )

        with pytest.raises(
            errors.InputValidationException, match="Cannot call callback with null state."
        ):
            ui_delegate_request.stateChangedCallback()(None)

    def test_when_interface_callback_is_None_then_middleware_callback_is_None(
        self,
        ui_delegate_request,
        mock_ui_delegate_request_interface,
    ):
        mock_ui_delegate_request_interface.mock.stateChangedCallback.return_value = None

        middleware_callback = ui_delegate_request.stateChangedCallback()

        assert middleware_callback is None


@pytest.fixture
def ui_delegate_request(mock_ui_delegate_request_interface):
    return UIDelegateRequest(mock_ui_delegate_request_interface)
