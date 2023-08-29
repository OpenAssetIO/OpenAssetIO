#
#   Copyright 2022 The Foundry Visionmongers Ltd
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
Tests that cover the openassetio.Context class.
"""

# pylint: disable=invalid-name,no-self-use,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
import pytest

from openassetio import Context, managerApi, TraitsData


class Test_Context_init:
    def test_when_constructed_with_no_args_then_has_default_configuration(self):
        context = Context()
        assert context.locale is None
        assert context.managerState is None

    def test_when_constructed_with_args_then_has_configuration_from_args(self):
        class TestState(managerApi.ManagerStateBase):
            pass

        expected_locale = TraitsData()
        expected_state = TestState()

        a_context = Context(expected_locale, expected_state)

        assert a_context.locale is expected_locale
        assert a_context.managerState is expected_state
        assert isinstance(a_context.managerState, TestState)


class Test_Context_locale:
    def test_when_set_to_unknown_value_then_raises_ValueError(self, a_context):
        expected_msg = (
            r"incompatible function arguments.*\n.*arg0: openassetio._openassetio.TraitsData"
        )

        with pytest.raises(TypeError, match=expected_msg):
            a_context.locale = object()

    def test_when_set_to_None_then_returns_None(self, a_context):
        a_context.locale = None

        assert a_context.locale is None

    def test_when_set_to_valid_data_then_holds_reference_to_that_data(self, a_context):
        expected_data = TraitsData()
        a_context.locale = expected_data

        actual_data = a_context.locale

        assert actual_data is expected_data


class Test_Context_managerState:
    def test_when_set_to_unknown_type_then_raises_TypeError(self, a_context):
        expected_msg = (
            r"incompatible function arguments.*\n"
            r".*arg1: openassetio._openassetio.managerApi.ManagerStateBase"
        )

        with pytest.raises(TypeError, match=expected_msg):
            a_context.managerState = object()

    def test_when_set_to_None_then_returns_None(self, a_context):
        a_context.managerState = None

        assert a_context.managerState is None

    def test_when_set_to_valid_data_then_holds_reference_to_that_data(self, a_context):
        expected_data = managerApi.ManagerStateBase()
        a_context.managerState = expected_data

        actual_data = a_context.managerState

        assert actual_data is expected_data


@pytest.fixture
def a_context():
    return Context()
