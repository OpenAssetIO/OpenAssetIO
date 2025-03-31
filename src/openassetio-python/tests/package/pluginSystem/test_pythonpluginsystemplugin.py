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
These tests check the structure of the PythonPluginSystemPlugin base
class.
"""
# pylint: disable=missing-class-docstring,invalid-name,missing-function-docstring
import pytest

from openassetio.errors import NotImplementedException
from openassetio.pluginSystem import PythonPluginSystemPlugin


class Test_PythonPluginSystemPlugin_identifier:
    def test_raises_NotImplementedException(self):
        with pytest.raises(NotImplementedException):
            PythonPluginSystemPlugin.identifier()
