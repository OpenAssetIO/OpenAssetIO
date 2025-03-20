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
@namespace openassetio.ui.pluginSystem
This module provides a plugin system that can be used to register and
instantiate UI delegate plugins from code that lives outside the
openassetio package.
"""
from ... import _openassetio  # pylint: disable=no-name-in-module

from .PythonPluginSystemUIDelegatePlugin import PythonPluginSystemUIDelegatePlugin
from .PythonPluginSystemUIDelegateImplementationFactory import (
    PythonPluginSystemUIDelegateImplementationFactory,
)

## @see @fqref{ui.pluginSystem.CppPluginSystemUIDelegateImplementationFactory}
## "CppPluginSystemUIDelegateImplementationFactory"
CppPluginSystemUIDelegateImplementationFactory = (
    _openassetio.ui.pluginSystem.CppPluginSystemUIDelegateImplementationFactory
)
## @see @fqref{ui.pluginSystem.HybridPluginSystemUIDelegateImplementationFactory}
## "HybridPluginSystemUIDelegateImplementationFactory"
HybridPluginSystemUIDelegateImplementationFactory = (
    _openassetio.ui.pluginSystem.HybridPluginSystemUIDelegateImplementationFactory
)
