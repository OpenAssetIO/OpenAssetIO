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
@namespace openassetio.ui.managerApi
This module contains code relevant to anyone wanting to add UI
delegation support for an asset management system.

If you are a tool or application developer, see @ref
openassetio.ui.hostApi
"""
from ... import _openassetio  # pylint: disable=no-name-in-module

from .UIDelegateInterface import UIDelegateInterface

UIDelegateStateInterface = _openassetio.ui.managerApi.UIDelegateStateInterface
UIDelegateRequest = _openassetio.ui.managerApi.UIDelegateRequest
