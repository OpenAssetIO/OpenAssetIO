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
Tests for the BatchElementError type.
"""

# pylint: disable=no-self-use, too-few-public-methods
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

from openassetio import (
    BatchElementError,
    BatchElementException,
    UnknownBatchElementException,
    InvalidEntityReferenceBatchElementException,
    MalformedEntityReferenceBatchElementException,
    EntityAccessErrorBatchElementException,
    EntityResolutionErrorBatchElementException,
    InvalidPreflightHintBatchElementException,
)


class Test_BatchElementError_ErrorCode:
    def test_code_values(self):
        assert int(BatchElementError.ErrorCode.kUnknown) == 128
        assert int(BatchElementError.ErrorCode.kInvalidEntityReference) == 129
        assert int(BatchElementError.ErrorCode.kMalformedEntityReference) == 130
        assert int(BatchElementError.ErrorCode.kEntityAccessError) == 131
        assert int(BatchElementError.ErrorCode.kEntityResolutionError) == 132
        assert int(BatchElementError.ErrorCode.kInvalidPreflightHint) == 133


class Test_BatchElementError_inheritance:
    def test_class_is_final(self):
        with pytest.raises(TypeError):

            class _(BatchElementError):
                pass


class Test_BatchElementError_init:
    def test_when_invalid_code_then_raises_TypeError(self):
        expected_error = r"incompatible constructor arguments.*\n.*BatchElementError.ErrorCode"

        with pytest.raises(TypeError, match=expected_error):
            BatchElementError(-123, "whatever")

    def test_when_valid_code_then_contains_given_error_code_and_message(self):
        expected_code = BatchElementError.ErrorCode.kUnknown
        expected_message = "An error: 🐈"

        a_batch_element_error = BatchElementError(expected_code, expected_message)

        assert a_batch_element_error.code == expected_code
        assert a_batch_element_error.message == expected_message

    def test_when_code_modified_then_raises_AttributeError(self):
        a_batch_element_error = BatchElementError(BatchElementError.ErrorCode.kUnknown, "whatever")

        with pytest.raises(AttributeError):
            a_batch_element_error.code = BatchElementError.ErrorCode.kUnknown

    def test_when_message_modified_then_raises_AttributeError(self):
        a_batch_element_error = BatchElementError(BatchElementError.ErrorCode.kUnknown, "whatever")

        with pytest.raises(AttributeError):
            a_batch_element_error.message = "whatever"


class Test_BatchElementError_equality:
    def test_when_comparing_with_same_data_then_are_equal(self):
        expected_code = BatchElementError.ErrorCode.kUnknown
        expected_message = "message"

        a_batch_element_error = BatchElementError(expected_code, expected_message)
        b_batch_element_error = BatchElementError(expected_code, expected_message)

        assert a_batch_element_error == b_batch_element_error

    def test_when_comparing_with_different_code_then_are_not_equal(self):
        expected_code = BatchElementError.ErrorCode.kUnknown
        expected_message = "message"

        a_batch_element_error = BatchElementError(expected_code, expected_message)
        b_batch_element_error = BatchElementError(
            BatchElementError.ErrorCode.kEntityResolutionError, expected_message
        )

        assert a_batch_element_error != b_batch_element_error

    def test_when_comparing_with_different_message_then_are_not_equal(
        self,
    ):
        expected_code = BatchElementError.ErrorCode.kUnknown
        expected_message = "message"

        a_batch_element_error = BatchElementError(expected_code, expected_message)
        b_batch_element_error = BatchElementError(expected_code, "another message")

        assert a_batch_element_error != b_batch_element_error


@pytest.mark.parametrize(
    "exception_type",
    [
        BatchElementException,
        UnknownBatchElementException,
        InvalidEntityReferenceBatchElementException,
        MalformedEntityReferenceBatchElementException,
        EntityAccessErrorBatchElementException,
        EntityResolutionErrorBatchElementException,
        InvalidPreflightHintBatchElementException,
    ],
)
# Note: these tests are not sufficient to assert that C++ exceptions
# are appropriately translated. This will be implicitly tested via e.g.
# `resolve` tests.
class Test_BatchElementException:
    def test_can_catch_as_self_type(self, exception_type):
        expected_message = "some string"
        expected_code = BatchElementError.ErrorCode.kUnknown

        a_batch_element_error = BatchElementError(expected_code, expected_message)

        with pytest.raises(exception_type, match=expected_message) as exc:
            raise exception_type(123, a_batch_element_error)

        assert exc.value.index == 123
        assert exc.value.error.code == expected_code
        assert exc.value.error.message == expected_message

    def test_can_catch_as_BatchElementException(self, exception_type):
        expected_message = "some string"
        expected_code = BatchElementError.ErrorCode.kUnknown

        a_batch_element_error = BatchElementError(expected_code, expected_message)

        with pytest.raises(BatchElementException, match=expected_message) as exc:
            raise exception_type(123, a_batch_element_error)

        assert exc.value.index == 123
        assert exc.value.error.code == expected_code
        assert exc.value.error.message == expected_message
