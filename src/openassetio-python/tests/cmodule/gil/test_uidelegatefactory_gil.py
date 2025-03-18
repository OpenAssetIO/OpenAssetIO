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
from openassetio.ui.hostApi import UIDelegateImplementationFactoryInterface, UIDelegateFactory


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


class Test_UIDelegateFactory_gil:
    """
    UIDelegateFactory is one of the more complex cases for testing GIL
    release, since it has actual logic inside it, and has multiple
    dependencies.

    This is the same problem as for testing ManagerFactory. See
    `test_managerfactory_gil.py:Test_ManagerFactory_gil` for a
    discussion of the approach taken there and here.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all methods.
        """
        unimplemented = find_unimplemented_test_cases(UIDelegateFactory, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(
            self, a_ui_delegate_factory, mock_ui_delegate_impl_factory, mock_logger,
            mock_host_interface
    ):
        a_ui_delegate_factory.{method}(
                mock_host_interface, a_threaded_ui_delegate_impl_factory, mock_logger
        )
"""
                )

        assert not unimplemented

    def test_availableUIDelegates(
        self,
        a_ui_delegate_factory,
        mock_ui_delegate_impl_factory,
    ):
        mock_ui_delegate_impl_factory.mock.identifiers.return_value = []

        a_ui_delegate_factory.availableUIDelegates()

        mock_ui_delegate_impl_factory.mock.identifiers.assert_called()

    def test_createUIDelegate(
        self, a_ui_delegate_factory, mock_ui_delegate_impl_factory, mock_ui_delegate_interface
    ):
        mock_ui_delegate_impl_factory.mock.instantiate.return_value = mock_ui_delegate_interface

        a_ui_delegate_factory.createUIDelegate("")

        mock_ui_delegate_impl_factory.mock.instantiate.assert_called()

    def test_createUIDelegateForInterface(
        self,
        a_threaded_ui_delegate_impl_factory,
        mock_logger,
        mock_host_interface,
        mock_ui_delegate_impl_factory,
        mock_ui_delegate_interface,
    ):
        mock_ui_delegate_impl_factory.mock.instantiate.return_value = mock_ui_delegate_interface

        UIDelegateFactory.createUIDelegateForInterface(
            "", mock_host_interface, a_threaded_ui_delegate_impl_factory, mock_logger
        )

        mock_ui_delegate_impl_factory.mock.instantiate.assert_called()

    def test_defaultUIDelegateForInterface(
        self,
        a_threaded_ui_delegate_impl_factory,
        mock_logger,
        mock_host_interface,
        mock_ui_delegate_impl_factory,
        tmp_path,
        monkeypatch,
        mock_ui_delegate_interface,
    ):
        mock_ui_delegate_impl_factory.mock.instantiate.return_value = mock_ui_delegate_interface
        config_path = tmp_path / "ui_delegate.toml"
        config_path.write_text('[ui_delegate]\nidentifier = "something"')

        # First overload

        UIDelegateFactory.defaultUIDelegateForInterface(
            str(config_path),
            mock_host_interface,
            a_threaded_ui_delegate_impl_factory,
            mock_logger,
        )

        mock_ui_delegate_impl_factory.mock.instantiate.assert_called()

        # Second overload

        mock_ui_delegate_impl_factory.mock.instantiate.reset_mock()
        monkeypatch.setenv("OPENASSETIO_DEFAULT_CONFIG", str(config_path))

        UIDelegateFactory.defaultUIDelegateForInterface(
            mock_host_interface, a_threaded_ui_delegate_impl_factory, mock_logger
        )

        mock_ui_delegate_impl_factory.mock.instantiate.assert_called()

    def test_identifiers(
        self,
        a_ui_delegate_factory,
        mock_ui_delegate_impl_factory,
    ):
        mock_ui_delegate_impl_factory.mock.identifiers.return_value = []

        a_ui_delegate_factory.identifiers()

        mock_ui_delegate_impl_factory.mock.identifiers.assert_called()


@pytest.fixture
def a_ui_delegate_factory(mock_host_interface, a_threaded_ui_delegate_impl_factory, mock_logger):
    return UIDelegateFactory(mock_host_interface, a_threaded_ui_delegate_impl_factory, mock_logger)


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
