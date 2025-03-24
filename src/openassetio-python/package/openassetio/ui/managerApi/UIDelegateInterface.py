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
@namespace openassetio.ui.hostApi.UIDelegateInterface
A single-class module, providing the UIDelegateInterface class.
"""

from ... import constants
from ... import _openassetio  # pylint: disable=no-name-in-module


__all__ = ["UIDelegateInterface"]


class UIDelegateInterface(_openassetio.ui.managerApi.UIDelegateInterface):
    """
    Python base class augmenting the C++ abstract base class.

    @see @fqref{ui.managerApi.UIDelegateInterface} "UIDelegateInterface".
    """

    def info(self):
        """
        Override base class implementation to add
        @fqref{constants.kInfoKey_IsPython} "kInfoKey_IsPython".

        @see @fqref{ui.managerApi.UIDelegateInterface.info}
        "UIDelegateInterface.info".
        """
        out = super().info()
        out[constants.kInfoKey_IsPython] = True
        return out
