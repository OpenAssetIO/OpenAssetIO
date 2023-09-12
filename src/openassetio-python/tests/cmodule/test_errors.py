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

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
from unittest import mock

import pytest

from openassetio import _openassetio_test  # pylint: disable=no-name-in-module
from openassetio import errors


class Test_errors:
    def test_when_cpp_exception_thrown_then_can_be_caught_as_corresponding_python_exception(self):
        exceptions = (
            errors.OpenAssetIOException,
            errors.ConfigurationException,
            errors.InputValidationException,
            errors.NotImplementedException,
            errors.UnhandledException,
        )

        for exception in exceptions:
            with pytest.raises(exception, match="Explosion!"):
                _openassetio_test.throwException(exception.__name__, "Explosion!")

    def test_when_cpp_exception_thrown_then_can_be_caught_as_OpenAssetIOException(self):
        exceptions = (
            errors.ConfigurationException,
            errors.InputValidationException,
            errors.NotImplementedException,
            errors.UnhandledException,
        )

        for exception in exceptions:
            assert _openassetio_test.isThrownExceptionCatchableAs(
                throwExceptionName=exception.__name__,
                catchExceptionName=errors.OpenAssetIOException.__name__,
            )
            with pytest.raises(errors.OpenAssetIOException, match="Explosion!"):
                _openassetio_test.throwException(exception.__name__, "Explosion!")

    def test_when_ConfigurationException_thrown_then_can_be_caught_as_InputValidationException(
        self,
    ):
        assert _openassetio_test.isThrownExceptionCatchableAs(
            throwExceptionName=errors.ConfigurationException.__name__,
            catchExceptionName=errors.InputValidationException.__name__,
        )
        with pytest.raises(errors.InputValidationException, match="Explosion!"):
            _openassetio_test.throwException(errors.ConfigurationException.__name__, "Explosion!")
