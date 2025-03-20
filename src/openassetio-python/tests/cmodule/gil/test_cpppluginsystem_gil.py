#
#   Copyright 2024-2025 The Foundry Visionmongers Ltd
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
Testing that CppPluginSystem.* classes' methods release the GIL.
"""
import os

# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=invalid-name,c-extension-no-member
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

from openassetio.managerApi import ManagerInterface
from openassetio.ui.managerApi import UIDelegateInterface
from openassetio.pluginSystem import CppPluginSystem, CppPluginSystemManagerImplementationFactory
from openassetio.ui.pluginSystem import CppPluginSystemUIDelegateImplementationFactory


def noop(_):
    return None


class Test_CppPluginSystem_gil:
    """
    Check that the GIL is released in the CppPluginSystem bindings,
    especially where a method calls out to a virtual method.

    Such a virtual method could be in the plugin itself, or in the
    logger, both of which are mocked such that they throw if the GIL
    is held when they are called.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all methods.
        """
        unimplemented = find_unimplemented_test_cases(CppPluginSystem, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_cpp_plugin_system):
        a_cpp_plugin_system.{method}()
"""
                )

        assert unimplemented == []

    def test_scan(
        self,
        the_cpp_gil_check_manager_plugin_path,
        the_cpp_gil_check_module_hook,
        a_cpp_plugin_system,
    ):
        a_cpp_plugin_system.scan(
            the_cpp_gil_check_manager_plugin_path, "", the_cpp_gil_check_module_hook, noop
        )

    def test_identifiers(
        self,
        the_cpp_gil_check_plugin_identifier,
        the_cpp_gil_check_manager_plugin_path,
        the_cpp_gil_check_module_hook,
        a_cpp_plugin_system,
    ):
        a_cpp_plugin_system.scan(
            the_cpp_gil_check_manager_plugin_path, "", the_cpp_gil_check_module_hook, noop
        )

        assert a_cpp_plugin_system.identifiers() == [the_cpp_gil_check_plugin_identifier]

    def test_reset(
        self,
        the_cpp_gil_check_manager_plugin_path,
        the_cpp_gil_check_module_hook,
        a_cpp_plugin_system,
    ):
        a_cpp_plugin_system.scan(
            the_cpp_gil_check_manager_plugin_path, "", the_cpp_gil_check_module_hook, noop
        )
        a_cpp_plugin_system.reset()

    def test_plugin(
        self,
        the_cpp_gil_check_plugin_identifier,
        the_cpp_gil_check_manager_plugin_path,
        the_cpp_gil_check_module_hook,
        a_cpp_plugin_system,
    ):
        a_cpp_plugin_system.scan(
            the_cpp_gil_check_manager_plugin_path, "", the_cpp_gil_check_module_hook, noop
        )

        _path, _plugin = a_cpp_plugin_system.plugin(the_cpp_gil_check_plugin_identifier)


class Test_CppPluginSystemManagerImplementationFactory_gil:
    """
    Check that the GIL is released in the
    CppPluginSystemManagerImplementationFactory bindings, especially
    where a method calls out to a virtual method.

    Such a virtual method could be in the plugin itself, or in the
    logger, both of which are mocked such that they throw if the GIL
    is held when they are called.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all methods.
        """
        unimplemented = find_unimplemented_test_cases(
            CppPluginSystemManagerImplementationFactory, self
        )

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_cpp_plugin_manager_impl_factory):
        a_cpp_plugin_manager_impl_factory.{method}()
"""
                )

        assert unimplemented == []

    def test_identifiers(
        self,
        the_cpp_gil_check_plugin_identifier,
        a_cpp_plugin_manager_impl_factory,
    ):
        assert a_cpp_plugin_manager_impl_factory.identifiers() == [
            the_cpp_gil_check_plugin_identifier
        ]

    def test_instantiate(
        self,
        the_cpp_gil_check_plugin_identifier,
        a_cpp_plugin_manager_impl_factory,
    ):
        manager_interface = a_cpp_plugin_manager_impl_factory.instantiate(
            the_cpp_gil_check_plugin_identifier
        )
        # Confidence check.
        assert isinstance(manager_interface, ManagerInterface)


class Test_CppPluginSystemUIDelegateImplementationFactory_gil:
    """
    Check that the GIL is released in the
    CppPluginSystemUIDelegateImplementationFactory bindings, especially
    where a method calls out to a virtual method.

    Such a virtual method could be in the plugin itself, or in the
    logger, both of which are mocked such that they throw if the GIL
    is held when they are called.
    """

    def test_all_methods_covered(self, find_unimplemented_test_cases):
        """
        Ensure this test class covers all methods.
        """
        unimplemented = find_unimplemented_test_cases(
            CppPluginSystemUIDelegateImplementationFactory, self
        )

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_cpp_plugin_ui_impl_factory):
        a_cpp_plugin_ui_impl_factory.{method}()
"""
                )

        assert unimplemented == []

    def test_identifiers(
        self,
        the_cpp_gil_check_plugin_identifier,
        a_cpp_plugin_ui_impl_factory,
    ):
        assert a_cpp_plugin_ui_impl_factory.identifiers() == [the_cpp_gil_check_plugin_identifier]

    def test_instantiate(
        self,
        the_cpp_gil_check_plugin_identifier,
        a_cpp_plugin_ui_impl_factory,
    ):
        ui_delegate_interface = a_cpp_plugin_ui_impl_factory.instantiate(
            the_cpp_gil_check_plugin_identifier
        )
        # Confidence check.
        assert isinstance(ui_delegate_interface, UIDelegateInterface)


@pytest.fixture
def a_cpp_plugin_system(a_threaded_logger_interface):
    return CppPluginSystem(a_threaded_logger_interface)


@pytest.fixture
def a_cpp_plugin_manager_impl_factory(
    the_cpp_gil_check_manager_plugin_path, a_threaded_logger_interface
):
    return CppPluginSystemManagerImplementationFactory(
        the_cpp_gil_check_manager_plugin_path, a_threaded_logger_interface
    )


@pytest.fixture
def a_cpp_plugin_ui_impl_factory(the_cpp_gil_check_ui_plugin_path, a_threaded_logger_interface):
    return CppPluginSystemUIDelegateImplementationFactory(
        the_cpp_gil_check_ui_plugin_path, a_threaded_logger_interface
    )


@pytest.fixture(scope="session")
def the_cpp_gil_check_module_hook():
    return "openassetioPlugin"


@pytest.fixture(scope="session")
def the_cpp_gil_check_plugin_identifier():
    return "org.openassetio.test.pluginSystem.resources.python-gil-check"


@pytest.fixture(scope="module")
def the_cpp_gil_check_ui_plugin_path(the_cpp_plugins_root_path):
    return os.path.join(the_cpp_plugins_root_path, "ui", "python-gil-check")


@pytest.fixture(scope="module")
def the_cpp_gil_check_manager_plugin_path(the_cpp_plugins_root_path):
    return os.path.join(the_cpp_plugins_root_path, "python-gil-check")


@pytest.fixture(scope="module", autouse=True)
def skip_if_no_test_plugins_available(the_cpp_plugins_root_path):
    """
    Skip tests in this module if there are no plugins to test against.

    Some test runs may genuinely not have access to the plugins, e.g.
    when building/testing Python wheels, since the test plugins are
    created by CMake when test targets are enabled. In this case, skip
    the tests in this module.

    If we know we are running via CTest (i.e.
    OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR is defined), then the test
    plugins should definitely exist. So in this case, ensure we do _not_
    disable these tests.
    """
    if (
        not os.path.isdir(the_cpp_plugins_root_path)
        and os.environ.get("OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR") is None
    ):
        pytest.skip("Skipping C++ plugin system tests as no test plugins are available")
