#
#   Copyright 2013-2024 The Foundry Visionmongers Ltd
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
OpenAssetIO
===========

An open-source interoperability standard for tools and content
management systems used in media production.

OpenAssetIO defines a common set of interactions between a host of the
API (eg: a Digital Content Creation tool or pipeline script) and an
Asset Management System.

It aims to reduce the integration effort and maintenance overhead of
modern CGI pipelines, and pioneer new, standardized asset-centric
workflows in post-production tooling.

OpenAssetIO enabled tools and asset management systems can freely
communicate with each other, without needing to know any specifics of
their respective implementations.

The API has no inherent functionality. It exists as a bridge - at the
boundary between a process that consumes or produces data (the host),
and the systems that provide data coordination and version management
functionality.

Scope
-----

The API covers the following areas:

- Resolution of asset references (URIs) into locatable data (URLs).

- Publishing and retrieval of data for file-based and non-file-based
  assets.

- Discovery and registration of related assets.

The API, by design, does not:

- Define any standardized data structures for the storage or description
  of assets or asset hierarchies.

- Dictate any aspect of how an asset management system operates,
  organizes, locates or manages asset data and versions.

- The API builds upon the production-tested Katana Asset API, addressing
  several common integration challenges and adding support for a wider
  range of asset types and publishing workflows.

API documentation
-----------------

The documentation for OpenAssetIO can be found here:
   https://openassetio.github.io/OpenAssetIO.
"""

# pylint: disable=wrong-import-position,import-error,no-name-in-module
from ._openassetio import (
    constants,
    Context,
    EntityReference,
    majorVersion,
    minorVersion,
    patchVersion,
    betaMajorVersion,
    betaMinorVersion,
    versionString,
)


#
# Deprecated: https://github.com/OpenAssetIO/OpenAssetIO/issues/1127
#
from ._openassetio import trait

TraitsData = trait.TraitsData
del trait


from ._openassetio import errors as _errors

BatchElementError = _errors.BatchElementError


class BatchElementException(_errors.BatchElementException):
    """
    @deprecated See openassetio.errors.BatchElementException
    """

    def __init__(self, index, error):
        super().__init__(index, error, error.message)


UnknownBatchElementException = _errors.BatchElementException
InvalidEntityReferenceBatchElementException = _errors.BatchElementException
MalformedEntityReferenceBatchElementException = _errors.BatchElementException
EntityAccessErrorBatchElementException = _errors.BatchElementException
EntityResolutionErrorBatchElementException = _errors.BatchElementException
InvalidPreflightHintBatchElementException = _errors.BatchElementException
InvalidTraitSetBatchElementException = _errors.BatchElementException

del _errors
