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
@namespace openassetio.hostApi
This module contains code relevant to anyone hosting the API in a
tool or application, wanting to communicate with some asset management
system.

If you are wanting to provide support for an asset management system,
see @ref openassetio.managerApi.
"""

from .. import _openassetio  # pylint: disable=no-name-in-module

Manager = _openassetio.hostApi.Manager
ManagerFactory = _openassetio.hostApi.ManagerFactory
HostInterface = _openassetio.hostApi.HostInterface
ManagerImplementationFactoryInterface = _openassetio.hostApi.ManagerImplementationFactoryInterface
EntityReferencePager = _openassetio.hostApi.EntityReferencePager
