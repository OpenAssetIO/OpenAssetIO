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
@namespace openassetio.access
Provides access mode related constants for use in API functions.
"""

from openassetio import _openassetio  # pylint: disable=no-name-in-module


kAccessNames = _openassetio.access.kAccessNames
PolicyAccess = _openassetio.access.PolicyAccess
ResolveAccess = _openassetio.access.ResolveAccess
EntityTraitsAccess = _openassetio.access.EntityTraitsAccess
PublishingAccess = _openassetio.access.PublishingAccess
RelationsAccess = _openassetio.access.RelationsAccess
DefaultEntityAccess = _openassetio.access.DefaultEntityAccess
