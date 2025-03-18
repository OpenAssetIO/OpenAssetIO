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
Testing that UIDelegateInterface methods release the GIL.
"""
from openassetio import Context
from openassetio.trait import TraitsData
from openassetio.ui.access import UIAccess

# pylint: disable=redefined-outer-name,too-many-public-methods
# pylint: disable=invalid-name,c-extension-no-member,protected-access
# pylint: disable=missing-class-docstring,missing-function-docstring

from openassetio.ui.managerApi import UIDelegateInterface, UIDelegateRequest


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

    def test_displayName(self, mock_ui_delegate_interface, a_threaded_mock_ui_delegate_interface):
        mock_ui_delegate_interface.mock.displayName.return_value = ""
        a_threaded_mock_ui_delegate_interface.displayName()

    def test_info(self, mock_ui_delegate_interface, a_threaded_mock_ui_delegate_interface):
        mock_ui_delegate_interface.mock.info.return_value = {}
        a_threaded_mock_ui_delegate_interface.info()

    def test_settings(
        self, mock_ui_delegate_interface, a_threaded_mock_ui_delegate_interface, a_host_session
    ):
        mock_ui_delegate_interface.mock.settings.return_value = {}
        a_threaded_mock_ui_delegate_interface.settings(a_host_session)

    def test_initialize(self, a_threaded_mock_ui_delegate_interface, a_host_session):
        a_threaded_mock_ui_delegate_interface.initialize({}, a_host_session)

    def test_close(self, a_threaded_mock_ui_delegate_interface, a_host_session):
        a_threaded_mock_ui_delegate_interface.close(a_host_session)

    def test_populateUI(
        self,
        mock_ui_delegate_interface,
        a_threaded_mock_ui_delegate_interface,
        mock_ui_delegate_request_interface,
        a_host_session,
    ):
        mock_ui_delegate_interface.mock.populateUI.return_value = None
        a_threaded_mock_ui_delegate_interface.populateUI(
            TraitsData(),
            UIAccess.kRead,
            UIDelegateRequest(mock_ui_delegate_request_interface),
            Context(),
            a_host_session,
        )

    def test_uiPolicy(
        self, mock_ui_delegate_interface, a_threaded_mock_ui_delegate_interface, a_host_session
    ):
        mock_ui_delegate_interface.mock.uiPolicy.return_value = TraitsData()
        a_threaded_mock_ui_delegate_interface.uiPolicy(
            set(),
            UIAccess.kRead,
            Context(),
            a_host_session,
        )
