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
@namespace openassetio.constants
Constants used throughout the OpenAssetIO API.

@todo [tc] Should these live here, or with their owning declarations,
See @ref openassetio.log.LoggerInterface for example.
"""

## @name Info dict field Names
##
## Bare strings should never be used to help protect against
## inconsistencies and future changes.
##
## @{

# General

kField_SmallIcon = "smallIcon"
kField_Icon = "icon"

# Entity Reference Properties

## This field may be used by the API to optimize queries to
## isEntityReferenceString in situations where bridging languages, etc.
## can be expensive (particularly in the case of python plug-ins
## called from multi-threaded C++).
kField_EntityReferencesMatchPrefix = "entityReferencesMatchPrefix"

## @}
