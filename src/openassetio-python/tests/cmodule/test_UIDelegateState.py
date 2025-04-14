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
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name
"""
Tests for the Python bindings of the UIDelegateRequest/State[Interface]
classes.
"""
import re

from openassetio import _openassetio  # pylint: disable=no-name-in-module
from openassetio.errors import InputValidationException

import pytest

ui = _openassetio._testutils.ui  # pylint: disable=protected-access


class Test_UIDelegateRequestInterface:
    def test_when_nativeData_non_pyobject_then_raises(self):

        expected_error = re.escape(
            "Python UI delegates only accept Python objects: C++ type 'double' is not supported"
        )

        request = ui.createUIDelegateRequestInterfaceWithNonPyObjectNativeData()

        with pytest.raises(InputValidationException, match=expected_error):
            request.nativeData()

    def test_when_returns_raw_cpython_then_ok(self):
        request = ui.createUIDelegateRequestInterfaceWithRawCPythonNativeData()

        assert request.nativeData() == 42


class Test_UIDelegateStateInterface:
    def test_when_nativeData_non_pyobject_then_raises(self):

        expected_error = re.escape(
            "Python UI delegates only accept Python objects: C++ type 'double' is not supported"
        )

        state = ui.createUIDelegateStateInterfaceWithNonPyObjectNativeData()

        with pytest.raises(InputValidationException, match=expected_error):
            state.nativeData()

    def test_when_returns_raw_cpython_then_ok(self):
        state = ui.createUIDelegateStateInterfaceWithRawCPythonNativeData()

        assert state.nativeData() == 42


class Test_UIDelegateRequest:
    def test_when_nativeData_non_pyobject_then_raises(self):

        expected_error = re.escape(
            "Python UI delegates only accept Python objects: C++ type 'double' is not supported"
        )

        request = ui.createUIDelegateRequestWithNonPyObjectNativeData()

        with pytest.raises(InputValidationException, match=expected_error):
            request.nativeData()

    def test_when_returns_raw_cpython_then_ok(self):
        request = ui.createUIDelegateRequestWithRawCPythonNativeData()

        assert request.nativeData() == 42


class Test_UIDelegateState:
    def test_when_nativeData_non_pyobject_then_raises(self):

        expected_error = re.escape(
            "Python UI delegates only accept Python objects: C++ type 'double' is not supported"
        )

        state = ui.createUIDelegateStateWithNonPyObjectNativeData()

        with pytest.raises(InputValidationException, match=expected_error):
            state.nativeData()

    def test_when_returns_raw_cpython_then_ok(self):
        state = ui.createUIDelegateStateWithRawCPythonNativeData()

        assert state.nativeData() == 42
