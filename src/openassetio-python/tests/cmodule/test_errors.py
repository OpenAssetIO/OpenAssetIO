#
#   Copyright 2023 The Foundry Visionmongers Ltd
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
Tests of C++ binding utilities for exception types.
"""

# pylint: disable=invalid-name,redefined-outer-name,protected-access
# pylint: disable=missing-class-docstring,missing-function-docstring
import inspect
from unittest import mock

import pytest

from openassetio import _openassetio  # pylint: disable=no-name-in-module
from openassetio import errors


all_exceptions = (
    errors.OpenAssetIOException,
    errors.ConfigurationException,
    errors.InputValidationException,
    errors.NotImplementedException,
    errors.UnhandledException,
    errors.BatchElementException,
)


class Test_errors:
    def test_all_exceptions_list_is_exhaustive(self):
        for _, cls in inspect.getmembers(errors, inspect.isclass):
            if issubclass(cls, BaseException):
                assert cls in all_exceptions

    @pytest.mark.parametrize("exception_type", all_exceptions)
    def test_when_cpp_exception_thrown_then_can_be_caught_as_corresponding_python_exception(
        self, exception_type
    ):
        with pytest.raises(exception_type, match="Explosion!"):
            _openassetio._testutils.throwException(exception_type.__name__, "Explosion!")

    @pytest.mark.parametrize("exception_type", all_exceptions)
    def test_when_cpp_exception_thrown_then_can_be_caught_as_OpenAssetIOException(
        self, exception_type
    ):
        assert _openassetio._testutils.isThrownExceptionCatchableAs(
            throwExceptionName=exception_type.__name__,
            catchExceptionName=errors.OpenAssetIOException.__name__,
        )
        with pytest.raises(errors.OpenAssetIOException, match="Explosion!"):
            _openassetio._testutils.throwException(exception_type.__name__, "Explosion!")

    def test_when_ConfigurationException_thrown_then_can_be_caught_as_InputValidationException(
        self,
    ):
        assert _openassetio._testutils.isThrownExceptionCatchableAs(
            throwExceptionName=errors.ConfigurationException.__name__,
            catchExceptionName=errors.InputValidationException.__name__,
        )
        with pytest.raises(errors.InputValidationException, match="Explosion!"):
            _openassetio._testutils.throwException(
                errors.ConfigurationException.__name__, "Explosion!"
            )

    @pytest.mark.parametrize("exception_type", all_exceptions)
    def test_when_python_exception_thrown_then_can_be_caught_in_cpp(
        self, exception_type, exception_thrower
    ):
        exception = make_exception(exception_type)

        exception_thrower.callee.side_effect = exception

        assert _openassetio._testutils.isPythonExceptionCatchableAs(
            exception_thrower, exception_type.__name__
        )

    @pytest.mark.parametrize("exception_type", all_exceptions)
    def test_when_python_exception_thrown_then_can_be_caught_in_cpp_as_stl_base_type(
        self, exception_type, exception_thrower
    ):
        exception = make_exception(exception_type)

        exception_thrower.callee.side_effect = exception

        _openassetio._testutils.throwPythonExceptionAndCatchAsStdException(exception_thrower)

    @pytest.mark.parametrize("exception_type", all_exceptions)
    def test_when_python_exception_thrown_then_can_be_caught_in_cpp_rethrown_and_caught_in_python(
        self, exception_type, exception_thrower
    ):
        exception = make_exception(exception_type)

        exception_thrower.callee.side_effect = exception

        with pytest.raises(exception_type) as err:
            _openassetio._testutils.throwPythonExceptionCatchAsCppExceptionAndRethrow(
                exception_thrower, exception_type.__name__
            )

        assert err.value is exception

    def test_when_non_OpenAssetIO_exception_thrown_then_not_translated_to_cpp_exception(
        self, exception_thrower
    ):
        # Same name, but different exception.
        class OpenAssetIOException(Exception):
            pass

        exception = OpenAssetIOException()

        exception_thrower.callee.side_effect = exception

        with pytest.raises(OpenAssetIOException):
            # Should fail to catch and propagate back.
            _openassetio._testutils.isPythonExceptionCatchableAs(
                exception_thrower, "OpenAssetIOException"
            )


def make_exception(exception_type):
    if exception_type == errors.BatchElementException:
        error = errors.BatchElementError(
            errors.BatchElementError.ErrorCode.kInvalidEntityReference, "Explosion!"
        )
        exception = exception_type(123, error, "Another explosion!")
    else:
        exception = exception_type("Explosion!")

    return exception


class PyExceptionThrower(_openassetio._testutils.ExceptionThrower):
    """
    Subclass of pybind11-bound abstract C++ class, which is expected to
    throw the same exception from each of its methods.

    Each method corresponds to an OpenAssetIO-customized pybind11
    override macro.

    The `callee` member gives a single customisation point to configure
    the result of calling a method (i.e. the particular exception to
    throw), which should be done using the Mock class's `side_effect`
    property.
    """

    def __init__(self):
        _openassetio._testutils.ExceptionThrower.__init__(self)
        self.callee = mock.Mock()

    def throwFromOverride(self):
        self.callee()

    def throwFromOverridePure(self):
        self.callee()

    def throwFromOverrideName(self):
        self.callee()

    def throwFromOverrideArgs(self):
        self.callee()


@pytest.fixture
def exception_thrower():
    return PyExceptionThrower()
