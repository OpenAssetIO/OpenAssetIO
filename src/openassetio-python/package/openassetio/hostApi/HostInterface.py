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
@namespace openassetio.hostApi.HostInterface
A single-class module, providing the HostInterface class.
"""

from .. import constants
from .. import _openassetio  # pylint: disable=no-name-in-module


__all__ = ["HostInterface"]


class HostInterface(_openassetio.hostApi.HostInterface):
    """
    Python base class augmenting the C++ abstract base class.

    @see @fqref{hostApi.HostInterface} "HostInterface".
    """

    def info(self):
        """
        Override base class implementation to add
        @fqref{constants.kInfoKey_IsPython} "kInfoKey_IsPython".

        @see @fqref{hostApi.HostInterface.info} "HostInterface.info".
        """
        out = super().info()
        out[constants.kInfoKey_IsPython] = True
        return out
