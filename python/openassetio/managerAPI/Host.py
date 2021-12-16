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

from .._core.debug import debugApiCall, Debuggable
from .._core.audit import auditApiCall


__all__ = ['Host']


class Host(Debuggable):
    """
    The Host object represents the tool or application that created a
    session with OpenAssetIO, and wants to query or store information
    within a @ref manager.

    The Host provides a generalised API to query the identity of the
    caller of the API, as well as which entities are used within the
    current document.

    Hosts should never be directly constructed by the Manager's
    implementation. Instead, the @ref HostSession class provided to all
    manager API entry points provides access to the current host through
    the @ref openassetio.managerAPI.HostSession.HostSession.host
    "HostSession.host" method.
    """

    def __init__(self, hostInterface):
        super(Host, self).__init__()

        self.__impl = hostInterface

        # This can be set to false, to disable API debugging at the per-class level
        self._debugCalls = True

    def __str__(self):
        return self.__impl.identifier()

    def __repr__(self):
        return "Host(%r)" % self.__impl

    def _interface(self):
        return self.__impl

    ##
    # @name Host Information
    #
    ## @{

    @debugApiCall
    @auditApiCall("Host methods")
    def identifier(self):
        """
        Returns an identifier to uniquely identify the Host.

        The identifier will be different for each tool or application,
        but common to all versions of any one. The identifier will use
        only alpha-numeric characters and '.', '_' or '-', commonly in
        the form of a 'reverse-DNS' style string, for example:

            "uk.co.foundry.katana"

        @return str
        """
        return self.__impl.identifier()

    @debugApiCall
    @auditApiCall("Host methods")
    def displayName(self):
        """
        Returns a human readable name to be used to reference this
        specific host in user-facing messaging.
        For example:

            "Katana"
        """
        return self.__impl.displayName()

    @debugApiCall
    @auditApiCall("Host methods")
    def info(self):
        """
        Returns other information that may be useful about the host.
        This can contain arbitrary key/value pairs. There should be no
        reliance on a specific key being supplied by all hosts. The
        information may be more generally useful for diagnostic or
        debugging purposes. For example:

            { 'version' : '1.1v3' }

        @return Dict[str, pod]
        """
        return self.__impl.info()

    ## @}

    @debugApiCall
    @auditApiCall("Host methods")
    def documentReference(self):
        """
        The path, or @ref entity_reference of the current document, or
        an empty string if not applicable. If a Host supports multiple
        concurrent documents, it will be the 'frontmost' one. If there
        is no meaningful document reference, then an empty string will
        be returned.

        @return str
        """
        return self.__impl.documentReference()

    ##
    # @name Entity Reference retrieval
    #
    ## @{

    @debugApiCall
    @auditApiCall("Host methods")
    def knownEntityReferences(self, specification=None):
        """
        @return list, An @ref entity_reference for each Entities known
        by the host to be used in the current document, or an empty list
        if none are known.

        @param specification openassetio.Specification [None] If
        supplied, then only entities of the supplied specification will
        be returned.
        """
        return self.__impl.knownEntityReferences(specification=specification)

    ## @}
