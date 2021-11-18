#
#   Copyright 2013-2021 [The Foundry Visionmongers Ltd]
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


kSupportedMetadataTypes = (str, int, float, bool, type(None))

## @name Management States
## @see @ref openassetio.managerAPI.ManagerInterface.ManagerInterface.managementPolicy
## @{

## The Manager has no interest in participating in the management of this kind
## of entity, or a supplied specification is not publishable to a specific
## entity reference
kIgnored = 0

## The Manager would like the opportunity to manage the entity, but the user
## should still be presented with standard Host UI for the type as an option.
kManaged = 1

## The Manager takes exclusive control over this asset type, and any st host
## interfaces/etc... should be suppressed.
kExclusive = 3

# A mask for the state bits
kStateMask = 7

## @}

## @name Path Handling
## @see @ref openassetio.managerAPI.ManagerInterface.ManagerInterface.managementPolicy
## @{

## If False, The manager is not capable of determining the URL for a new @ref entity
## "entity's" data, and will only keep track of existing data. If True, the manager
## will determine the URL to use for writing data for new entities
kWillManagePath = 8

## @}


## @name Batch Processing
## @see openassetio.managerAPI.ManagerInterface.ManagerInterface.preflightMultiple
## @see openassetio.managerAPI.ManagerInterface.ManagerInterface.registerMultiple
## @{

## Some Managers may implement the 'batched' API methods, this flag should be
## set to indicate that the Manage prefers batch operations where possible.
kSupportsBatchOperations = 16

## @}

## @name Field Names
## Field names are to be used whenever data is get or set from a dictionary by
## key, rather than through an accessor in some wrapper class (eg:
## Item/Specification etc...). Bare strings should never be used to help
## protect against inconsistencies and future changes.
##
## These fields should also be used, if necessary, when declaring derived
## classes of a @ref Specification.
## @{

kField_ItemType = 'fnItemType'

# General

kField_DisplayName = 'displayName'
kField_Metadata = 'metadata'
kField_SmallIcon = 'smallIcon'
kField_Icon = 'icon'
kField_ThumbnailPath = 'thumbnailPath'

# Entity Reference Properties

## These fields may be used by the API/Host to optimise queries to
## isEntityReference in situations where bridging languages, etc.. can be
## expensive (particularly in the case of python plug-ins called from
## multi-threaded C). Only one should be set at once.
kField_EntityReferencesMatchPrefix = "entityReferencesMatchPrefix"
kField_EntityReferencesMatchRegex = "entityReferencesMatchRegex"

# Files

kField_FilePath = 'path'
kField_FileExtensions = 'extensions'
kField_FileIsEnumerated = 'enumerated'

# Hints

kField_HintPath = 'pathHint'
kField_HintFilename = 'filenameHint'
kField_HintName = 'nameHint'

# Image data

kField_PixelColorspace = 'colorspace'
kField_PixelAspectRatio = 'aspectRatio'
kField_PixelWidth = 'width'
kField_PixelHeight = 'height'
kField_PixelNumChannels = 'numChannels'
kField_PixelEncoding = 'encoding'
kField_PixelCompression = 'compression'
kField_PixelBitDepth = 'bitDepth'

# Task/Editorial

kField_Status = 'status'

# Sequence

kField_FrameStart = 'startFrame'
kField_FrameEnd = 'endFrame'
kField_FrameIn = 'inFrame'
kField_FrameOut = 'outFrame'
kField_FrameRate = 'frameRate'
kField_DropFrame = 'dropFrame'
kField_FieldDominance = 'fieldDominance'

kField_MediaFrameIn = 'mediaInFrame'
kField_MediaFrameOut = 'mediaOutFrame'

## @}


## @name Thumbnail Defaults
## @{

kThumbnail_DefaultPixelWidth = 360
kThumbnail_DefaultPixelHeight = 270

## @}


## @name Setting Key Names
## Name for keys in the session settings dict, where applicable.
## @{

kSetting_ManagerIdentifier = 'OAIO:managerIdentifier'
kSetting_LoggingSeverity = 'OAIO:loggingSeverity'

## @}


## @name Document actions
## @see DocumentLocale
## @{

kDocumentAction_Save = 'save'
kDocumentAction_SaveAs = 'saveAs'
kDocumentAction_SaveNewVersion = 'saveNewVersion'

## @}


## @name Version dict keys
## @{

kVersionDict_OrderKey = '__order__'

## @}
