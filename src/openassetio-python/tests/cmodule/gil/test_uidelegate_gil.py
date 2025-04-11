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
Testing that UIDelegate methods release the GIL.
"""
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name,redefined-outer-name
import pytest

from openassetio import Context
from openassetio.trait import TraitsData
from openassetio.ui.access import UIAccess
from openassetio.ui.hostApi import UIDelegate


class Test_UIDelegate_gil:
    """
    Check all methods release the GIL during C++ function body
    execution.

    See docstring for similar test under `test_manager_gil.py`
    for details on how these tests are structured.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all UIDelegateInterface methods.
        """
        unimplemented = find_unimplemented_test_cases(UIDelegate, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, mock_ui_delegate_interface, a_threaded_ui_delegate):
        a_threaded_ui_delegate.{method}()
"""
                )

        assert unimplemented == []

    def test_identifier(self, mock_ui_delegate_interface, a_threaded_ui_delegate):
        mock_ui_delegate_interface.mock.identifier.return_value = ""
        a_threaded_ui_delegate.identifier()

    def test_displayName(self, mock_ui_delegate_interface, a_threaded_ui_delegate):
        mock_ui_delegate_interface.mock.displayName.return_value = ""
        a_threaded_ui_delegate.displayName()

    def test_info(self, mock_ui_delegate_interface, a_threaded_ui_delegate):
        mock_ui_delegate_interface.mock.info.return_value = {}
        a_threaded_ui_delegate.info()

    def test_settings(self, mock_ui_delegate_interface, a_threaded_ui_delegate):
        mock_ui_delegate_interface.mock.identifier.return_value = ""
        a_threaded_ui_delegate.identifier()

    def test_initialize(self, a_threaded_ui_delegate):
        a_threaded_ui_delegate.initialize({})

    def test_close(self, a_threaded_ui_delegate):
        a_threaded_ui_delegate.close()

    def test_populateUI(
        self,
        a_threaded_ui_delegate,
        mock_ui_delegate_interface,
        mock_ui_delegate_request_interface,
    ):
        mock_ui_delegate_interface.mock.populateUI.return_value = None
        a_threaded_ui_delegate.populateUI(
            TraitsData(),
            UIAccess.kRead,
            mock_ui_delegate_request_interface,
            Context(),
        )

    def test_uiPolicy(self, a_threaded_ui_delegate, mock_ui_delegate_interface):
        mock_ui_delegate_interface.mock.uiPolicy.return_value = TraitsData()
        a_threaded_ui_delegate.uiPolicy(
            set(),
            UIAccess.kRead,
            Context(),
        )


@pytest.fixture
def a_threaded_ui_delegate(a_threaded_mock_ui_delegate_interface, a_host_session):
    """
    Returns a UIDelegate instance that is backed by a threaded
    UIDelegateInterface that errors on being called with the GIL held.
    """
    return UIDelegate(a_threaded_mock_ui_delegate_interface, a_host_session)
