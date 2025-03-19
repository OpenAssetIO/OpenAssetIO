#
#   Copyright 2024 The Foundry Visionmongers Ltd
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
Testing that ManagerFactory/CppPluginSystemPlugin
methods release the GIL.
"""
import os
import sysconfig

# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=invalid-name,c-extension-no-member
# pylint: disable=missing-class-docstring,missing-function-docstring

import openassetio
import pytest

# pylint: disable=no-name-in-module
from openassetio.managerApi import ManagerInterface
from openassetio.pluginSystem import CppPluginSystem, CppPluginSystemManagerImplementationFactory


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
        the_cpp_gil_check_plugin_path,
        a_cpp_plugin_system,
    ):
        a_cpp_plugin_system.scan(the_cpp_gil_check_plugin_path)

    def test_identifiers(
        self,
        the_cpp_gil_check_plugin_identifier,
        the_cpp_gil_check_plugin_path,
        a_cpp_plugin_system,
    ):
        a_cpp_plugin_system.scan(the_cpp_gil_check_plugin_path)

        assert a_cpp_plugin_system.identifiers() == [the_cpp_gil_check_plugin_identifier]

    def test_reset(
        self,
        the_cpp_gil_check_plugin_path,
        a_cpp_plugin_system,
    ):
        a_cpp_plugin_system.scan(the_cpp_gil_check_plugin_path)
        a_cpp_plugin_system.reset()

    def test_plugin(
        self,
        the_cpp_gil_check_plugin_identifier,
        the_cpp_gil_check_plugin_path,
        a_cpp_plugin_system,
    ):
        a_cpp_plugin_system.scan(the_cpp_gil_check_plugin_path)

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
    def test_{method}(self, a_cpp_plugin_impl_factory):
        a_cpp_plugin_impl_factory.{method}()
"""
                )

        assert unimplemented == []

    def test_identifiers(
        self,
        the_cpp_gil_check_plugin_identifier,
        a_cpp_plugin_impl_factory,
    ):
        assert a_cpp_plugin_impl_factory.identifiers() == [the_cpp_gil_check_plugin_identifier]

    def test_instantiate(
        self,
        the_cpp_gil_check_plugin_identifier,
        a_cpp_plugin_impl_factory,
    ):
        manager_interface = a_cpp_plugin_impl_factory.instantiate(
            the_cpp_gil_check_plugin_identifier
        )
        # Confidence check.
        assert isinstance(manager_interface, ManagerInterface)


@pytest.fixture
def a_cpp_plugin_system(a_threaded_logger_interface):
    return CppPluginSystem(a_threaded_logger_interface)


@pytest.fixture
def a_cpp_plugin_impl_factory(the_cpp_gil_check_plugin_path, a_threaded_logger_interface):
    return CppPluginSystemManagerImplementationFactory(
        the_cpp_gil_check_plugin_path, a_threaded_logger_interface
    )


@pytest.fixture(scope="session")
def the_cpp_gil_check_plugin_identifier():
    return "org.openassetio.test.pluginSystem.resources.python-gil-check"


@pytest.fixture(scope="module")
def the_cpp_gil_check_plugin_path():
    scheme = f"{os.name}_user"
    plugin_path = os.path.normpath(
        os.path.join(
            # Top-level __init__.py
            openassetio.__file__,
            # up to openassetio dir
            "..",
            # up to site-packages
            "..",
            # up to install tree root (i.e. posix ../../.., nt ../..)
            os.path.relpath(
                sysconfig.get_path("data", scheme), sysconfig.get_path("platlib", scheme)
            ),
            # down to install location of C++ plugin
            os.getenv("OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR", ""),
            "python-gil-check",
        )
    )
    if (
        not os.path.isdir(plugin_path)
        and os.environ.get("OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR") is None
    ):
        pytest.skip("Skipping C++ plugin system tests as no test plugins are available")
    return plugin_path
