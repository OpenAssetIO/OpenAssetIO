#
#   Copyright 2013-2021 The Foundry Visionmongers Ltd
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
@namespace openassetio.pluginSystem
This module provides a plugin system that can be used to register and
instantiate manager plugins from code that lives outside of the
openassetio package.
"""
from .PythonPluginSystemManagerPlugin import PythonPluginSystemManagerPlugin
from .PythonPluginSystem import PythonPluginSystem
from .PythonPluginSystemPlugin import PythonPluginSystemPlugin
from .PythonPluginSystemManagerImplementationFactory import (
    PythonPluginSystemManagerImplementationFactory,
)

from .. import _openassetio  # pylint: disable=no-name-in-module

CppPluginSystem = _openassetio.pluginSystem.CppPluginSystem
CppPluginSystemPlugin = _openassetio.pluginSystem.CppPluginSystemPlugin
CppPluginSystemManagerImplementationFactory = (
    _openassetio.pluginSystem.CppPluginSystemManagerImplementationFactory
)
