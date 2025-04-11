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
Tests for the default implementations of
UIDelegateImplementationFactoryInterface methods.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

from openassetio.ui.hostApi import UIDelegateImplementationFactoryInterface


class Test_UIDelegateImplementationFactoryInterface:
    def test_has_logger(self, mock_logger, a_ui_delegate_interface_factory_interface):
        # pylint: disable=protected-access
        assert a_ui_delegate_interface_factory_interface._logger is mock_logger

    def test_logger_is_readonly(self, a_ui_delegate_interface_factory_interface):
        with pytest.raises(AttributeError):
            # pylint: disable=protected-access
            a_ui_delegate_interface_factory_interface._logger = "something"


class Test_UIDelegateImplementationFactoryInterface_identifiers:
    def test_when_not_overridden_then_raises_exception(
        self, a_ui_delegate_interface_factory_interface
    ):
        with pytest.raises(RuntimeError) as err:
            a_ui_delegate_interface_factory_interface.identifiers()
        assert (
            str(err.value) == "Tried to call pure virtual function"
            ' "UIDelegateImplementationFactoryInterface::identifiers"'
        )


class Test_UIDelegateImplementationFactoryInterface_instantiate:
    def test_when_not_overridden_then_raises_exception(
        self, a_ui_delegate_interface_factory_interface
    ):
        with pytest.raises(RuntimeError) as err:
            a_ui_delegate_interface_factory_interface.instantiate("a.ui_delegate.identifier")
        assert (
            str(err.value) == "Tried to call pure virtual function"
            ' "UIDelegateImplementationFactoryInterface::instantiate"'
        )


@pytest.fixture
def a_ui_delegate_interface_factory_interface(mock_logger):
    return UIDelegateImplementationFactoryInterface(mock_logger)
