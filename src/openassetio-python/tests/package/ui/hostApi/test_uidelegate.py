#  SPDX-License-Identifier: Apache-2.0
#  Copyright 2025 The Foundry Visionmongers Ltd
"""
Tests that cover the openassetio.ui.hostApi.UIDelegate class.
"""
# pylint: disable=missing-class-docstring,invalid-name,missing-function-docstring
# pylint: disable=redefined-outer-name
import pytest

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


@pytest.fixture
def ui_delegate(mock_ui_delegate_interface, a_host_session):
    return UIDelegate(mock_ui_delegate_interface, a_host_session)
