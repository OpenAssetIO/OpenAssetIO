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
Tests for the default implementations of UIDelegateInterface methods.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

from openassetio import errors
from openassetio.ui.managerApi import UIDelegateInterface


class Test_UIDelegateInterface_identifier:
    def test_is_pure_virtual(self, ui_delegate_interface, pure_virtual_error_msg):
        with pytest.raises(RuntimeError, match=pure_virtual_error_msg.format("identifier")):
            ui_delegate_interface.identifier()


class Test_UIDelegateInterface_displayName:
    def test_is_pure_virtual(self, ui_delegate_interface, pure_virtual_error_msg):
        with pytest.raises(RuntimeError, match=pure_virtual_error_msg.format("displayName")):
            ui_delegate_interface.displayName()


class Test_UIDelegateInterface_info:
    def test_when_not_overridden_then_returns_empty_dict(self, ui_delegate_interface):
        info = ui_delegate_interface.info()

        assert isinstance(info, dict)
        assert info == {}


class Test_UIDelegateInterface_settings:
    def test_when_not_overridden_then_returns_empty_dict(
        self, ui_delegate_interface, a_host_session
    ):
        settings = ui_delegate_interface.settings(a_host_session)

        assert isinstance(settings, dict)
        assert settings == {}


class Test_UIDelegateInterface_initialize:
    def test_when_settings_not_provided_then_default_implementation_ok(
        self, ui_delegate_interface, a_host_session
    ):
        # Lack of exception means all good.
        ui_delegate_interface.initialize({}, a_host_session)

    def test_when_settings_provided_then_default_implementation_raises(
        self, ui_delegate_interface, a_host_session
    ):
        expected_error_message = (
            "Settings provided but are not supported. "
            "The initialize method has not been implemented by the UI delegate."
        )

        with pytest.raises(errors.InputValidationException, match=expected_error_message):
            ui_delegate_interface.initialize({"some": "setting"}, a_host_session)


@pytest.fixture
def ui_delegate_interface():
    return UIDelegateInterface()


@pytest.fixture
def pure_virtual_error_msg():
    return 'Tried to call pure virtual function "UIDelegateInterface::{}"'
