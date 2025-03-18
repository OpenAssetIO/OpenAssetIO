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
Tests for the UIDelegateStateInterface base class.
"""
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name,redefined-outer-name)

import pytest

from openassetio.ui.managerApi import UIDelegateStateInterface


class Test_UIDelegateStateInterface_entityReferences:
    def test_default_implementation_returns_empty_list(self, ui_delegate_state_interface):
        assert ui_delegate_state_interface.entityReferences() == []


class Test_UIDelegateStateInterface_entityTraitsDatas:
    def test_default_implementation_returns_empty_list(self, ui_delegate_state_interface):
        assert ui_delegate_state_interface.entityTraitsDatas() == []


class Test_UIDelegateStateInterface_nativeData:
    def test_default_implementation_returns_None(self, ui_delegate_state_interface):
        assert ui_delegate_state_interface.nativeData() is None


class Test_UIDelegateStateInterface_updateRequestCallback:
    def test_default_implementation_returns_None(self, ui_delegate_state_interface):
        assert ui_delegate_state_interface.updateRequestCallback() is None


@pytest.fixture
def ui_delegate_state_interface():
    return UIDelegateStateInterface()
