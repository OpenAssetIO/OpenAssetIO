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
Testing that ManagerInterface methods release the GIL.
"""
# pylint: disable=redefined-outer-name,too-many-public-methods
# pylint: disable=invalid-name,c-extension-no-member,protected-access
# pylint: disable=missing-class-docstring,missing-function-docstring
import pytest

# pylint: disable=no-name-in-module
from openassetio import _openassetio
from openassetio.ui.managerApi import UIDelegateInterface


class Test_UIDelegateInterface_gil:
    """
    Check all methods release the GIL during C++ function body
    execution.

    See docstring for similar test under `test_managerinterface_gil.py`
    for details on how these tests are structured.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all UIDelegateInterface methods.
        """
        unimplemented = find_unimplemented_test_cases(UIDelegateInterface, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, mock_ui_delegate_interface, a_threaded_mock_ui_delegate_interface):
        a_threaded_mock_ui_delegate_interface.{method}()
"""
                )

        assert unimplemented == []

    def test_identifier(self, mock_ui_delegate_interface, a_threaded_mock_ui_delegate_interface):
        mock_ui_delegate_interface.mock.identifier.return_value = ""
        a_threaded_mock_ui_delegate_interface.identifier()

    def test_info(self, mock_ui_delegate_interface, a_threaded_mock_ui_delegate_interface):
        mock_ui_delegate_interface.mock.info.return_value = {}
        a_threaded_mock_ui_delegate_interface.info()


@pytest.fixture
def a_threaded_mock_ui_delegate_interface(mock_ui_delegate_interface):
    """
    Wrap in a C++ proxy UI delegate that asserts the Python GIL is
    released before forwarding calls to mock_ui_delegate_interface in a
    separate thread.

    This is used to (indirectly) detect that Python binding API entry
    points release the GIL before continuing on to the C++
    implementation.
    """
    return _openassetio._testutils.gil.wrapInThreadedUIDelegateInterface(
        mock_ui_delegate_interface
    )
