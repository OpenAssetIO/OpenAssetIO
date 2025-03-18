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
Testing that UIDelegateFactory/UIDelegateImplementationFactoryInterface
methods release the GIL.
"""
# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=invalid-name,c-extension-no-member
# pylint: disable=missing-class-docstring,missing-function-docstring
from unittest import mock

import pytest

# pylint: disable=no-name-in-module
from openassetio import _openassetio
from openassetio.ui.hostApi import UIDelegateImplementationFactoryInterface


class Test_UIDelegateImplementationFactoryInterface_gil:
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
        unimplemented = find_unimplemented_test_cases(
            UIDelegateImplementationFactoryInterface, self
        )

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_threaded_ui_delegate_impl_factory, mock_ui_delegate_impl_factory):
        a_threaded_ui_delegate_impl_factory.{method}()
"""
                )

        assert not unimplemented

    def test_identifiers(self, a_threaded_ui_delegate_impl_factory, mock_ui_delegate_impl_factory):
        mock_ui_delegate_impl_factory.mock.identifiers.return_value = []
        a_threaded_ui_delegate_impl_factory.identifiers()

    def test_instantiate(
        self,
        a_threaded_ui_delegate_impl_factory,
        mock_ui_delegate_impl_factory,
        mock_ui_delegate_interface,
    ):
        mock_ui_delegate_impl_factory.mock.instantiate.return_value = mock_ui_delegate_interface
        a_threaded_ui_delegate_impl_factory.instantiate("")


@pytest.fixture
def a_threaded_ui_delegate_impl_factory(mock_ui_delegate_impl_factory, mock_logger):
    return _openassetio._testutils.gil.wrapInThreadedUIDelegateImplFactory(
        mock_logger, mock_ui_delegate_impl_factory
    )


@pytest.fixture
def mock_ui_delegate_impl_factory(mock_logger):
    return MockUIDelegateImplFactoryInterface(mock_logger)


class MockUIDelegateImplFactoryInterface(UIDelegateImplementationFactoryInterface):
    """
    `UIDelegateImplementationFactoryInterface` implementation that
    delegates all calls to a public `Mock` instance.
    """

    def __init__(self, logger):
        super().__init__(logger)
        self.mock = mock.create_autospec(
            UIDelegateImplementationFactoryInterface, spec_set=True, instance=True
        )

    def identifiers(self):
        return self.mock.identifiers()

    def instantiate(self, identifier):
        return self.mock.instantiate(identifier)
