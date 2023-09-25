#
#   Copyright 2013-2023 The Foundry Visionmongers Ltd
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
@namespace openassetio.errors
Provides exception objects to facilitate error handling in OpenAssetIO
"""

from . import _openassetio  # pylint: disable=no-name-in-module

OpenAssetIOException = _openassetio.errors.OpenAssetIOException
InputValidationException = _openassetio.errors.InputValidationException
ConfigurationException = _openassetio.errors.ConfigurationException
NotImplementedException = _openassetio.errors.NotImplementedException
UnhandledException = _openassetio.errors.UnhandledException
BatchElementError = _openassetio.errors.BatchElementError
BatchElementException = _openassetio.errors.BatchElementException
