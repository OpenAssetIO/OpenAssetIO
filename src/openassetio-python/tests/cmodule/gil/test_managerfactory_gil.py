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
Testing that ManagerFactory/ManagerImplementationFactoryInterface
methods release the GIL.
"""
# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=invalid-name,c-extension-no-member
# pylint: disable=missing-class-docstring,missing-function-docstring
from unittest import mock

import pytest

# pylint: disable=no-name-in-module
from openassetio import _openassetio
from openassetio.hostApi import ManagerImplementationFactoryInterface, ManagerFactory
from openassetio.pluginSystem import HybridPluginSystemManagerImplementationFactory


class Test_ManagerImplementationFactoryInterface_gil:
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
        unimplemented = find_unimplemented_test_cases(ManagerImplementationFactoryInterface, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_threaded_manager_impl_factory, mock_manager_impl_factory):
        a_threaded_manager_impl_factory.{method}()
"""
                )

        assert not unimplemented

    def test_identifiers(self, a_threaded_manager_impl_factory, mock_manager_impl_factory):
        mock_manager_impl_factory.mock.identifiers.return_value = []
        a_threaded_manager_impl_factory.identifiers()

    def test_instantiate(
        self,
        a_threaded_manager_impl_factory,
        mock_manager_impl_factory,
        mock_manager_interface,
    ):
        mock_manager_impl_factory.mock.instantiate.return_value = mock_manager_interface
        a_threaded_manager_impl_factory.instantiate("")


class Test_HybridPluginSystemManagerImplementationFactory_gil:
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
            HybridPluginSystemManagerImplementationFactory, self
        )

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_threaded_hybrid_impl_factory, mock_manager_impl_factory):
        a_threaded_hybrid_impl_factory.{method}()
"""
                )

        assert not unimplemented

    def test_identifiers(self, a_threaded_hybrid_impl_factory, mock_manager_impl_factory):
        mock_manager_impl_factory.mock.identifiers.return_value = []
        a_threaded_hybrid_impl_factory.identifiers()

    def test_instantiate(
        self,
        a_threaded_hybrid_impl_factory,
        mock_manager_impl_factory,
        mock_manager_interface,
    ):
        mock_manager_impl_factory.mock.identifiers.return_value = [""]
        mock_manager_impl_factory.mock.instantiate.return_value = mock_manager_interface
        a_threaded_hybrid_impl_factory.instantiate("")


class Test_ManagerFactory_gil:
    """
    ManagerFactory is one of the more complex cases for testing GIL
    release, since it has actual logic inside it, and has multiple
    dependencies.

    However, all we really need is to ensure each method calls at least
    one function that we know for sure will assert on the GIL.

    So here we use the ManagerImplementationFactoryInterface (MIFI)
    dependency. We wire our preconditions to ensure each method under
    test goes down a code path that uses some method of the threaded
    mock MIFI wrapper.

    To be sure the code path we want has been taken, we must
    `.assert_called()` on the relevant MIFI method. Note that the fake
    MIFI we provide has two layers: the threaded wrapper, which does the
    GIL assert, composes and forwards to a mock MIFI, which we can
    manipulate in the tests.

    Also see docstring for similar test under `gil/Test_Manager.py`
    for details on how these tests are structured.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all methods.
        """
        unimplemented = find_unimplemented_test_cases(ManagerFactory, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(
            self, a_threaded_manager_factory, mock_manager_impl_factory, mock_logger,
            mock_host_interface
    ):
        a_threaded_manager_factory.{method}(
                mock_host_interface, a_threaded_manager_impl_factory, mock_logger
        )
"""
                )

        assert not unimplemented

    def test_availableManagers(
        self,
        a_threaded_manager_factory,
        mock_manager_impl_factory,
    ):
        mock_manager_impl_factory.mock.identifiers.return_value = []

        a_threaded_manager_factory.availableManagers()

        mock_manager_impl_factory.mock.identifiers.assert_called()

    def test_createManager(
        self, a_threaded_manager_factory, mock_manager_impl_factory, mock_manager_interface
    ):
        mock_manager_impl_factory.mock.instantiate.return_value = mock_manager_interface

        a_threaded_manager_factory.createManager("")

        mock_manager_impl_factory.mock.instantiate.assert_called()

    def test_createManagerForInterface(
        self,
        a_threaded_manager_impl_factory,
        mock_logger,
        mock_host_interface,
        mock_manager_impl_factory,
        mock_manager_interface,
    ):
        mock_manager_impl_factory.mock.instantiate.return_value = mock_manager_interface

        ManagerFactory.createManagerForInterface(
            "", mock_host_interface, a_threaded_manager_impl_factory, mock_logger
        )

        mock_manager_impl_factory.mock.instantiate.assert_called()

    def test_defaultManagerForInterface(
        self,
        a_threaded_manager_impl_factory,
        mock_logger,
        mock_host_interface,
        mock_manager_impl_factory,
        tmp_path,
        monkeypatch,
        mock_manager_interface,
    ):
        mock_manager_impl_factory.mock.instantiate.return_value = mock_manager_interface
        config_path = tmp_path / "manager.toml"
        config_path.write_text('[manager]\nidentifier = "something"')

        # First overload

        ManagerFactory.defaultManagerForInterface(
            str(config_path),
            mock_host_interface,
            a_threaded_manager_impl_factory,
            mock_logger,
        )

        mock_manager_impl_factory.mock.instantiate.assert_called()

        # Second overload

        mock_manager_impl_factory.mock.instantiate.reset_mock()
        monkeypatch.setenv("OPENASSETIO_DEFAULT_CONFIG", str(config_path))

        ManagerFactory.defaultManagerForInterface(
            mock_host_interface, a_threaded_manager_impl_factory, mock_logger
        )

        mock_manager_impl_factory.mock.instantiate.assert_called()

    def test_identifiers(
        self,
        a_threaded_manager_factory,
        mock_manager_impl_factory,
    ):
        mock_manager_impl_factory.mock.identifiers.return_value = []

        a_threaded_manager_factory.identifiers()

        mock_manager_impl_factory.mock.identifiers.assert_called()


@pytest.fixture
def a_threaded_manager_factory(mock_host_interface, a_threaded_manager_impl_factory, mock_logger):
    return ManagerFactory(mock_host_interface, a_threaded_manager_impl_factory, mock_logger)


@pytest.fixture
def a_threaded_hybrid_impl_factory(a_threaded_manager_impl_factory, mock_logger):
    return HybridPluginSystemManagerImplementationFactory(
        [a_threaded_manager_impl_factory], mock_logger
    )


@pytest.fixture
def a_threaded_manager_impl_factory(mock_manager_impl_factory, mock_logger):
    return _openassetio._testutils.gil.wrapInThreadedManagerImplFactory(
        mock_logger, mock_manager_impl_factory
    )


@pytest.fixture
def mock_manager_impl_factory(mock_logger):
    return MockManagerImplFactoryInterface(mock_logger)


class MockManagerImplFactoryInterface(ManagerImplementationFactoryInterface):
    """
    `ManagerImplementationFactoryInterface` implementation that delegates all
     calls to a public `Mock` instance.
    """

    def __init__(self, logger):
        super().__init__(logger)
        self.mock = mock.create_autospec(
            ManagerImplementationFactoryInterface, spec_set=True, instance=True
        )

    def identifiers(self):
        return self.mock.identifiers()

    def instantiate(self, identifier):
        return self.mock.instantiate(identifier)
