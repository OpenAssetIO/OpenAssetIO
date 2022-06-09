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

from openassetio import Context, managerAPI, TraitsData


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
        assert context.managerInterfaceState is None

    def test_when_constructed_with_args_then_has_configuration_from_args(self):
        class TestState(managerAPI.ManagerStateBase):
            pass

        expected_access = Context.kReadMultiple
        expected_retention = Context.kSession
        expected_locale = TraitsData()
        expected_state = TestState()

        a_context = Context(expected_access, expected_retention, expected_locale, expected_state)

        assert a_context.access == expected_access
        assert a_context.retention == expected_retention
        assert a_context.locale is expected_locale
        assert a_context.managerInterfaceState is expected_state


class Test_Context_access:
    def test_when_set_to_unknown_value_then_raises_ValueError(self, a_context):
        with pytest.raises(ValueError) as err:
            a_context.access = "unrecognized"

        assert (str(err.value) ==
                "'unrecognized' is not a valid Access Pattern"
                " (read, readMultiple, write, writeMultiple, unknown)")


class Test_Context_retention:
    def test_when_set_to_unknown_value_then_raises_ValueError(self, a_context):
        with pytest.raises(ValueError) as err:
            a_context.retention = 123

        assert (str(err.value) ==
                "123 (123) is not a valid Retention (ignored, transient, session, permanent)")


class Test_Context_locale:
    def test_when_set_to_unknown_value_then_raises_ValueError(self, a_context):
        with pytest.raises(ValueError) as err:
            a_context.locale = object()

        assert (str(err.value) ==
                "Locale must be an instance of"
                " <class 'openassetio._openassetio.TraitsData'> (not <class 'object'>)")

    def test_when_set_to_None_then_returns_None(self, a_context):
        a_context.locale = None

        assert a_context.locale is None


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
