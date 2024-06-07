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
@namespace openassetio.utils
Provides assorted utility functions to aid library use.
"""

from openassetio import _openassetio  # pylint: disable=no-name-in-module


PathType = _openassetio.utils.PathType

FileUrlPathConverter = _openassetio.utils.FileUrlPathConverter

substitute = _openassetio.utils.substitute
