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
@namespace openassetio.managerAPI.Host
A single-class module, providing the Host class.
"""
from openassetio import _openassetio  # pylint: disable=no-name-in-module

from .._core.debug import Debuggable

__all__ = ['Host']


class Host(_openassetio.managerAPI.Host, Debuggable):
    """
    The Host object represents the tool or application that created a
    session with OpenAssetIO, and wants to query or store information
    within a @ref manager.

    The Host provides a generalised API to query the identity of the
    caller of the API. In the future, this interface may be extended to
    allow retrieval of information about available documents as well as
    which entities are used within these documents.

    Hosts should never be directly constructed by the Manager's
    implementation. Instead, the @ref HostSession class provided to all
    manager API entry points provides access to the current host through
    the @ref openassetio.managerAPI.HostSession.HostSession.host
    "HostSession.host" method.
    """

    def __init__(self, hostInterface):
        _openassetio.managerAPI.Host.__init__(self, hostInterface)
        Debuggable.__init__(self)

        self.__impl = hostInterface

        # This can be set to false, to disable API debugging at the per-class level
        self._debugCalls = True

    def __str__(self):
        return self.__impl.identifier()

    def __repr__(self):
        return "Host(%r)" % self.__impl

    def _interface(self):
        return self.__impl
