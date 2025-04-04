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
These tests check the structure of the CppPluginSystemPlugin base
class.
"""
# pylint: disable=missing-class-docstring,invalid-name,missing-function-docstring
import inspect

import pytest

from openassetio.pluginSystem import CppPluginSystemPlugin


class Test_CppPluginSystemPlugin_init:
    def test_raises_TypeError(self):
        with pytest.raises(TypeError, match="No constructor defined!"):
            CppPluginSystemPlugin()


class Test_CppPluginSystemPlugin_identifier:
    def test_method_exists(self):
        assert inspect.isroutine(CppPluginSystemPlugin.identifier)
