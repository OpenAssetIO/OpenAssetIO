#
#   Copyright 2022 The Foundry Visionmongers Ltd
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
Tests of the C++ Python hostApi helper library.

This is really a C++ test, but bound to Python to make use of pytest
niceties. The test must be run in a Python environment anyway, so this
approach just avoids some unnecessary boilerplate.
"""
# pylint: disable=invalid-name,missing-class-docstring,no-self-use
# pylint: disable=missing-function-docstring
from openassetio import _openassetio_test, log  # pylint: disable=no-name-in-module
from openassetio.pluginSystem import PythonPluginSystemManagerImplementationFactory


class Test_createPythonPluginSystemManagerImplementationFactory:
    def test_is_instance_of_plugin_factory(self):
        factory = _openassetio_test.callCreatePythonPluginSystemManagerImplementationFactory(
            log.ConsoleLogger())

        assert isinstance(factory, PythonPluginSystemManagerImplementationFactory)
