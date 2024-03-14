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
# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=invalid-name,c-extension-no-member
# pylint: disable=missing-class-docstring,missing-function-docstring
from unittest import mock

import pytest

# pylint: disable=no-name-in-module
from openassetio import _openassetio
from openassetio.pluginSystem import CppPluginSystemPlugin


class Test_CppPluginSystemPlugin_gil:
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
        unimplemented = find_unimplemented_test_cases(CppPluginSystemPlugin, self)

        if unimplemented:
            print("\nSome test cases not implemented. Method templates can be found below:\n")
            for method in unimplemented:
                print(
                    f"""
    def test_{method}(self, a_threaded_cpp_plugin):
        a_threaded_cpp_plugin.{method}()
"""
                )

        assert unimplemented == []

    def test_identifier(self, mock_cpp_plugin, a_threaded_cpp_plugin):
        mock_cpp_plugin.mock.identifier.return_value = "something"
        a_threaded_cpp_plugin.identifier()


@pytest.fixture
def a_threaded_cpp_plugin(mock_cpp_plugin):
    return _openassetio._testutils.gil.wrapInThreadedCppPluginSystemPlugin(mock_cpp_plugin)


@pytest.fixture
def mock_cpp_plugin():
    return MockCppPluginSystemPlugin()


class MockCppPluginSystemPlugin(CppPluginSystemPlugin):
    """
    `CppPluginSystemPlugin` implementation that delegates all
     calls to a public `Mock` instance.
    """

    def __init__(self):
        super().__init__()
        self.mock = mock.create_autospec(CppPluginSystemPlugin, spec_set=True, instance=True)

    def identifier(self):
        return self.mock.identifier()
