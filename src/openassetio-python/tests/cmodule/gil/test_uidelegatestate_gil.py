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
Testing that UIDelegateState/Request[Interface] methods release the GIL.
"""
# pylint: disable=redefined-outer-name,too-many-public-methods
# pylint: disable=invalid-name,c-extension-no-member,protected-access
# pylint: disable=missing-class-docstring,missing-function-docstring
import pytest

# pylint: disable=no-name-in-module
from openassetio import _openassetio
from openassetio.ui.managerApi import UIDelegateStateInterface, UIDelegateRequest
from openassetio.ui.hostApi import UIDelegateRequestInterface, UIDelegateState


class Test_UIDelegateRequestInterface_gil:
    """
    Check all methods release the GIL during C++ function body
    execution.

    See docstring for similar test under `test_managerinterface_gil.py`
    for details on how these tests are structured.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all methods.
        """
        unimplemented = find_unimplemented_test_cases(UIDelegateRequestInterface, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_threaded_ui_delegate_request_interface):
        a_threaded_ui_delegate_request_interface.{method}()
"""
                )

        assert unimplemented == []

    def test_entityReferences(self, a_threaded_ui_delegate_request_interface):
        a_threaded_ui_delegate_request_interface.entityReferences()

    def test_entityTraitsDatas(self, a_threaded_ui_delegate_request_interface):
        a_threaded_ui_delegate_request_interface.entityTraitsDatas()

    def test_nativeData(self, a_threaded_ui_delegate_request_interface):
        a_threaded_ui_delegate_request_interface.nativeData()

    def test_stateChangedCallback(self, a_threaded_ui_delegate_request_interface):
        a_threaded_ui_delegate_request_interface.stateChangedCallback()


class Test_UIDelegateStateInterface_gil:
    """
    Check all methods release the GIL during C++ function body
    execution.

    See docstring for similar test under `test_managerinterface_gil.py`
    for details on how these tests are structured.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all methods.
        """
        unimplemented = find_unimplemented_test_cases(UIDelegateStateInterface, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_threaded_ui_delegate_state_interface):
        a_threaded_ui_delegate_state_interface.{method}()
"""
                )

        assert unimplemented == []

    def test_entityReferences(self, a_threaded_ui_delegate_state_interface):
        a_threaded_ui_delegate_state_interface.entityReferences()

    def test_entityTraitsDatas(self, a_threaded_ui_delegate_state_interface):
        a_threaded_ui_delegate_state_interface.entityTraitsDatas()

    def test_nativeData(self, a_threaded_ui_delegate_state_interface):
        a_threaded_ui_delegate_state_interface.nativeData()

    def test_updateRequestCallback(self, a_threaded_ui_delegate_state_interface):
        a_threaded_ui_delegate_state_interface.updateRequestCallback()


class Test_UIDelegateRequest_gil:
    """
    Check all methods release the GIL during C++ function body
    execution.

    See docstring for similar test under `test_manager_gil.py`
    for details on how these tests are structured.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all methods.
        """
        unimplemented = find_unimplemented_test_cases(UIDelegateRequest, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_threaded_ui_delegate_request):
        a_threaded_ui_delegate_request.{method}()
"""
                )

        assert unimplemented == []

    def test_entityReferences(self, a_threaded_ui_delegate_request):
        a_threaded_ui_delegate_request.entityReferences()

    def test_entityTraitsDatas(self, a_threaded_ui_delegate_request):
        a_threaded_ui_delegate_request.entityTraitsDatas()

    def test_nativeData(self, a_threaded_ui_delegate_request):
        a_threaded_ui_delegate_request.nativeData()

    def test_stateChangedCallback(self, a_threaded_ui_delegate_request):
        a_threaded_ui_delegate_request.stateChangedCallback()


class Test_UIDelegateState_gil:
    """
    Check all methods release the GIL during C++ function body
    execution.

    See docstring for similar test under `test_manager_gil.py`
    for details on how these tests are structured.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all methods.
        """
        unimplemented = find_unimplemented_test_cases(UIDelegateState, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_threaded_ui_delegate_state):
        a_threaded_ui_delegate_state.{method}()
"""
                )

        assert unimplemented == []

    def test_entityReferences(self, a_threaded_ui_delegate_state):
        a_threaded_ui_delegate_state.entityReferences()

    def test_entityTraitsDatas(self, a_threaded_ui_delegate_state):
        a_threaded_ui_delegate_state.entityTraitsDatas()

    def test_nativeData(self, a_threaded_ui_delegate_state):
        a_threaded_ui_delegate_state.nativeData()

    def test_updateRequestCallback(self, a_threaded_ui_delegate_state):
        a_threaded_ui_delegate_state.updateRequestCallback()


@pytest.fixture
def a_threaded_ui_delegate_request_interface(mock_ui_delegate_request_interface):
    return _openassetio._testutils.gil.wrapInThreadedUIDelegateRequestInterface(
        mock_ui_delegate_request_interface
    )


@pytest.fixture
def a_threaded_ui_delegate_state_interface(mock_ui_delegate_state_interface):
    return _openassetio._testutils.gil.wrapInThreadedUIDelegateStateInterface(
        mock_ui_delegate_state_interface
    )


@pytest.fixture
def a_threaded_ui_delegate_request(a_threaded_ui_delegate_request_interface):
    return UIDelegateRequest(a_threaded_ui_delegate_request_interface)


@pytest.fixture
def a_threaded_ui_delegate_state(a_threaded_ui_delegate_state_interface):
    return UIDelegateState(a_threaded_ui_delegate_state_interface)
