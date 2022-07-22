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
            Context.kRead,
            Context.kReadMultiple,
            Context.kWrite,
            Context.kWriteMultiple,
            Context.kUnknown,
        )
        assert len(set(consts)) == len(consts)

    def test_access_constants_alias_Access_child_class_constants(self):
        assert Context.kRead is Context.Access.kRead
        assert Context.kReadMultiple is Context.Access.kReadMultiple
        assert Context.kWrite is Context.Access.kWrite
        assert Context.kWriteMultiple is Context.Access.kWriteMultiple
        assert Context.kUnknown is Context.Access.kUnknown

    def test_access_names_indices_match_constants(self):
        assert Context.kAccessNames[Context.kRead] == "read"
        assert Context.kAccessNames[Context.kReadMultiple] == "readMultiple"
        assert Context.kAccessNames[Context.kWrite] == "write"
        assert Context.kAccessNames[Context.kWriteMultiple] == "writeMultiple"
        assert Context.kAccessNames[Context.kUnknown] == "unknown"

    def test_retention_constants_alias_Retention_child_class_constants(self):
        assert Context.kIgnored is Context.Retention.kIgnored
        assert Context.kTransient is Context.Retention.kTransient
        assert Context.kSession is Context.Retention.kSession
        assert Context.kPermanent is Context.Retention.kPermanent

    def test_retention_constants_are_unique(self):
        consts = (Context.kIgnored, Context.kTransient, Context.kSession, Context.kPermanent)
        assert len(set(consts)) == len(consts)

    def test_retention_names_indices_match_constants(self):
        assert Context.kRetentionNames[Context.kIgnored] == "ignored"
        assert Context.kRetentionNames[Context.kTransient] == "transient"
        assert Context.kRetentionNames[Context.kSession] == "session"
        assert Context.kRetentionNames[Context.kPermanent] == "permanent"


class Test_Context_init:
    def test_when_constructed_with_no_args_then_has_default_configuration(self):
        context = Context()
        assert context.access == Context.kUnknown
        assert context.retention == Context.kTransient
        assert context.locale is None
        assert context.managerState is None

    def test_when_constructed_with_args_then_has_configuration_from_args(self):
        class TestState(managerApi.ManagerStateBase):
            pass

        expected_access = Context.kReadMultiple
        expected_retention = Context.kSession
        expected_locale = TraitsData()
        expected_state = TestState()

        a_context = Context(expected_access, expected_retention, expected_locale, expected_state)

        assert a_context.access == expected_access
        assert a_context.retention == expected_retention
        assert a_context.locale is expected_locale
        assert a_context.managerState is expected_state
        assert isinstance(a_context.managerState, TestState)


class Test_Context_access:
    def test_when_set_to_unknown_type_then_raises_ValueError(self, a_context):

        expected_msg = (r"incompatible function arguments.*\n"
                        r".*arg0: openassetio._openassetio.Context.Access")

        with pytest.raises(TypeError, match=expected_msg):
            a_context.access = 0

    def test_when_set_to_known_value_then_stores_that_value(self, a_context):

        for expected_access in (
                Context.kRead, Context.kReadMultiple, Context.kWrite, Context.kWriteMultiple):
            a_context.access = expected_access
            assert a_context.access == expected_access


class Test_Context_retention:
    def test_when_set_to_unknown_type_then_raises_ValueError(self, a_context):
        expected_msg = (r"incompatible function arguments.*\n"
                        r".*arg0: openassetio._openassetio.Context.Retention")

        with pytest.raises(TypeError, match=expected_msg):
            a_context.retention = 0

    def test_when_set_to_known_value_then_stores_that_value(self, a_context):
        for expected_retention in (
                Context.kIgnored, Context.kTransient, Context.kSession, Context.kPermanent):
            a_context.retention = expected_retention
            assert a_context.retention == expected_retention


class Test_Context_locale:
    def test_when_set_to_unknown_value_then_raises_ValueError(self, a_context):
        expected_msg = (r"incompatible function arguments.*\n"
                        r".*arg0: openassetio._openassetio.TraitsData")

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
        expected_msg = (r"incompatible function arguments.*\n"
                        r".*arg1: openassetio._openassetio.managerApi.ManagerStateBase")

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
        assert Context(access=Context.kRead).isForRead() is True

    def test_when_called_with_readMultiple_context_then_returns_true(self):
        assert Context(access=Context.kReadMultiple).isForRead() is True

    def test_when_called_with_write_context_then_returns_false(self):
        assert Context(access=Context.kWrite).isForRead() is False

    def test_when_called_with_writeMultiple_context_then_returns_false(self):
        assert Context(access=Context.kWriteMultiple).isForRead() is False

    def test_when_called_with_unknown_access_context_then_returns_false(self):
        assert Context(access=Context.kUnknown).isForRead() is False


class Test_Context_isForWrite:
    def test_when_called_with_write_context_then_returns_true(self):
        assert Context(access=Context.kWrite).isForWrite() is True

    def test_when_called_with_writeMultiple_context_then_returns_true(self):
        assert Context(access=Context.kWriteMultiple).isForWrite() is True

    def test_when_called_with_read_context_then_returns_false(self):
        assert Context(access=Context.kRead).isForWrite() is False

    def test_when_called_with_readMultiple_context_then_returns_false(self):
        assert Context(access=Context.kReadMultiple).isForWrite() is False

    def test_when_called_with_unknown_access_context_then_returns_false(self):
        assert Context(access=Context.kUnknown).isForWrite() is False


class Test_Context_isForMultiple:
    def test_when_called_with_read_context_then_returns_false(self):
        assert Context(access=Context.kRead).isForMultiple() is False

    def test_when_called_with_readMultiple_context_then_returns_true(self):
        assert Context(access=Context.kReadMultiple).isForMultiple() is True

    def test_when_called_with_write_context_then_returns_false(self):
        assert Context(access=Context.kWrite).isForMultiple() is False

    def test_when_called_with_writeMultiple_context_then_returns_true(self):
        assert Context(access=Context.kWriteMultiple).isForMultiple() is True

    def test_when_called_with_unknown_access_context_then_returns_false(self):
        assert Context(access=Context.kUnknown).isForMultiple() is False


@pytest.fixture
def a_context():
    return Context()
