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


class Test_Context:
    def test_access_constants_are_unique(self):
        consts = (
            Context.Access.kRead,
            Context.Access.kWrite,
            Context.Access.kCreateRelated,
            Context.Access.kUnknown,
        )
        assert len(set(consts)) == len(consts)

    def test_access_constants_are_not_exported(self):
        with pytest.raises(AttributeError):
            Context.kRead  # pylint: disable=pointless-statement

    def test_access_names_indices_match_constants(self):
        assert Context.kAccessNames[int(Context.Access.kRead)] == "read"
        assert Context.kAccessNames[int(Context.Access.kWrite)] == "write"
        assert Context.kAccessNames[int(Context.Access.kCreateRelated)] == "createRelated"
        assert Context.kAccessNames[int(Context.Access.kUnknown)] == "unknown"


class Test_Context_init:
    def test_when_constructed_with_no_args_then_has_default_configuration(self):
        context = Context()
        assert context.access == Context.Access.kUnknown
        assert context.locale is None
        assert context.managerState is None

    def test_when_constructed_with_args_then_has_configuration_from_args(self):
        class TestState(managerApi.ManagerStateBase):
            pass

        expected_access = Context.Access.kRead
        expected_locale = TraitsData()
        expected_state = TestState()

        a_context = Context(expected_access, expected_locale, expected_state)

        assert a_context.access == expected_access
        assert a_context.locale is expected_locale
        assert a_context.managerState is expected_state
        assert isinstance(a_context.managerState, TestState)


class Test_Context_access:
    def test_when_set_to_unknown_type_then_raises_ValueError(self, a_context):
        expected_msg = (
            r"incompatible function arguments.*\n"
            r".*arg0: openassetio._openassetio.Context.Access"
        )

        with pytest.raises(TypeError, match=expected_msg):
            a_context.access = 0

    def test_when_set_to_known_value_then_stores_that_value(self, a_context):
        for expected_access in (
            Context.Access.kRead,
            Context.Access.kWrite,
            Context.Access.kCreateRelated,
        ):
            a_context.access = expected_access
            assert a_context.access == expected_access


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


class Test_Context_isForRead:
    def test_when_called_with_read_context_then_returns_true(self):
        assert Context(access=Context.Access.kRead).isForRead() is True

    def test_when_called_with_write_context_then_returns_false(self):
        assert Context(access=Context.Access.kWrite).isForRead() is False

    def test_when_called_with_createRelated_context_then_returns_false(self):
        assert Context(access=Context.Access.kCreateRelated).isForRead() is False

    def test_when_called_with_unknown_access_context_then_returns_false(self):
        assert Context(access=Context.Access.kUnknown).isForRead() is False


class Test_Context_isForWrite:
    def test_when_called_with_write_context_then_returns_true(self):
        assert Context(access=Context.Access.kWrite).isForWrite() is True

    def test_when_called_with_createRelated_context_then_returns_true(self):
        assert Context(access=Context.Access.kCreateRelated).isForWrite() is True

    def test_when_called_with_read_context_then_returns_false(self):
        assert Context(access=Context.Access.kRead).isForWrite() is False

    def test_when_called_with_unknown_access_context_then_returns_false(self):
        assert Context(access=Context.Access.kUnknown).isForWrite() is False


@pytest.fixture
def a_context():
    return Context()
