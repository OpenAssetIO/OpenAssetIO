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

kSupportedAttributeTypes = (str, int, float, bool, type(None))

## @name Field Names
## Field names are to be used whenever data is get or set from a dictionary by
## key, rather than through an accessor in some wrapper class (eg:
## Item/Specification etc...). Bare strings should never be used to help
## protect against inconsistencies and future changes.
##
## These fields should also be used, if necessary, when declaring derived
## classes of a @ref Specification.
## @{

kField_ItemType = "fnItemType"

# General

kField_DisplayName = "displayName"
kField_SmallIcon = "smallIcon"
kField_Icon = "icon"

# Entity Reference Properties

## This field may be used by the API to optimize queries to
## isEntityReferenceString in situations where bridging languages, etc.
## can be expensive (particularly in the case of python plug-ins
## called from multi-threaded C++).
kField_EntityReferencesMatchPrefix = "entityReferencesMatchPrefix"

# Files

kField_FilePath = "path"
kField_FileExtensions = "extensions"
kField_FileIsEnumerated = "enumerated"

# Hints

kField_HintPath = "pathHint"
kField_HintFilename = "filenameHint"
kField_HintName = "nameHint"

# Image data

kField_PixelColorspace = "colorspace"
kField_PixelAspectRatio = "aspectRatio"
kField_PixelWidth = "width"
kField_PixelHeight = "height"
kField_PixelNumChannels = "numChannels"
kField_PixelEncoding = "encoding"
kField_PixelCompression = "compression"
kField_PixelBitDepth = "bitDepth"

# Task/Editorial

kField_Status = "status"

# Sequence

kField_FrameStart = "startFrame"
kField_FrameEnd = "endFrame"
kField_FrameIn = "inFrame"
kField_FrameOut = "outFrame"
kField_FrameRate = "frameRate"
kField_DropFrame = "dropFrame"
kField_FieldDominance = "fieldDominance"

kField_MediaFrameIn = "mediaInFrame"
kField_MediaFrameOut = "mediaOutFrame"

## @}


## @name Setting Key Names
## Name for keys in the manager settings dict, where applicable.
## @{

kSetting_ManagerIdentifier = "OpenAssetIO:managerIdentifier"
kSetting_LoggingSeverity = "OpenAssetIO:loggingSeverity"

## @}


## @name Document actions
## @see @needsref DocumentLocale
## @{

kDocumentAction_Save = "save"
kDocumentAction_SaveAs = "saveAs"
kDocumentAction_SaveNewVersion = "saveNewVersion"

## @}


## @name Version dict keys
## @{

kVersionDict_OrderKey = "__order__"

## @}
