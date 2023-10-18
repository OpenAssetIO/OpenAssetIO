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
Testing that LoggerInterface methods release the GIL.
"""
# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name,c-extension-no-member
# pylint: disable=missing-class-docstring,missing-function-docstring
import pytest

# pylint: disable=no-name-in-module
from openassetio import _openassetio_test
from openassetio.log import LoggerInterface


class Test_LoggerInterface_gil:
    """
    Check all methods release the GIL during C++ function body
    execution.

    See docstring for similar test under `gil/Test_ManagerInterface.py`
    for details on how these tests are structured.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all methods.
        """
        unimplemented = find_unimplemented_test_cases(LoggerInterface, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_threaded_logger_interface):
        a_threaded_logger_interface.{method}("")
"""
                )

        assert unimplemented == []

    def test_critical(self, a_threaded_logger_interface):
        a_threaded_logger_interface.critical("")

    def test_debug(self, a_threaded_logger_interface):
        a_threaded_logger_interface.debug("")

    def test_debugApi(self, a_threaded_logger_interface):
        a_threaded_logger_interface.debugApi("")

    def test_error(self, a_threaded_logger_interface):
        a_threaded_logger_interface.error("")

    def test_info(self, a_threaded_logger_interface):
        a_threaded_logger_interface.info("")

    def test_log(self, a_threaded_logger_interface):
        a_threaded_logger_interface.log(LoggerInterface.Severity.kInfo, "")

    def test_progress(self, a_threaded_logger_interface):
        a_threaded_logger_interface.progress("")

    def test_warning(self, a_threaded_logger_interface):
        a_threaded_logger_interface.warning("")


@pytest.fixture
def a_threaded_logger_interface(mock_logger):
    return _openassetio_test.gil.wrapInThreadedLoggerInterface(mock_logger)
