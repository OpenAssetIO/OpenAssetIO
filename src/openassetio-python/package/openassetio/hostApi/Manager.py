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
@namespace openassetio.hostApi.Manager
A single-class module, providing the Manager class.
"""

# Most of this module is documentation, which hopefully is a good thing.
# pylint: disable=too-many-lines,line-too-long
# We discussed splitting the interface up, but it ends up making most
# implementations more complicated.
# pylint: disable=too-many-public-methods

from openassetio import _openassetio  # pylint: disable=no-name-in-module

from .._core.debug import debugApiCall, Debuggable
from .._core.audit import auditApiCall


__all__ = ["Manager"]


class Manager(_openassetio.hostApi.Manager, Debuggable):
    """
    The Manager is the Host facing representation of an @ref
    asset_management_system. The Manager class shouldn't be directly
    constructed by the host. An instance of the class for any given
    asset management system can be retrieved from a
    @fqref{hostApi.ManagerFactory} "ManagerFactory", using the
    @fqref{hostApi.ManagerFactory.createManager}
    "ManagerFactory.createManager()" method with an appropriate manager
    @needsref identifier.

    @code
    factory = openassetio.hostApi.ManagerFactory(
        hostImpl, consoleLogger, pluginFactory)
    manager = factory.createManager("org.openassetio.test.manager")
    @endcode

    A Manager instance is the single point of interaction with an asset
    management system. It provides methods to uniquely identify the
    underlying implementation, querying and resolving @ref
    entity_reference "entity references" and publishing new data.

    The Manager API is threadsafe and can be called from multiple
    threads concurrently.
    """

    def __init__(self, interfaceInstance, hostSession):
        """
        @private

        A Manager should never be constructed directly by a host,
        instead use the @fqref{hostApi.ManagerFactory} "ManagerFactory"
        class, which takes care of their instantiation.

        @param interfaceInstance openassetio.managerApi.ManagerInterface
        An instance of a Manager Interface to wrap.

        @param hostSession openassetio.managerApi.HostSession the host
        session the manager is part of.
        """

        _openassetio.hostApi.Manager.__init__(self, interfaceInstance, hostSession)
        Debuggable.__init__(self)

        self.__impl = interfaceInstance
        self.__hostSession = hostSession

        # This can be set to false, to disable API debugging at the per-class level
        self._debugCalls = True

    def __str__(self):
        return self.__impl.identifier()

    def __repr__(self):
        return "Manager(%r)" % self.__impl.identifier()

    def _interface(self):
        return self.__impl

    ##
    # @name Asset Management System Information
    #
    # These functions provide general information about the @ref
    # asset_management_system itself. These can all be called before
    # @needsref initialize has been called.
    #
    # @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def updateTerminology(self, stringDict):
        """
        This call gives the Manager a chance to customize certain
        strings that you might want to use in your UI/messages.

        See @ref openassetio.hostApi.terminology "terminology" for
        well-known keys. These keys are updated in-place to the most
        appropriate term for the Manager. You should then use these
        substitutions in any user-facing messages or display text so
        that they feel at home.

        It's rare that you need to call this method directly, the @ref
        openassetio.hostApi.terminology API provides more utility for
        far less effort.

        @see @ref openassetio.hostApi.terminology "terminology"
        @see @ref openassetio.hostApi.terminology.Mapper.replaceTerms "Mapper.replaceTerms"
        @see @ref openassetio.hostApi.terminology.defaultTerminology "terminology.defaultTerminology"

        @param[out] stringDict `Dict[str, str]` Dictionary that is
        modified in-place by the manager if it has any alternate
        terminology.

        @unstable
        """
        self.__impl.updateTerminology(stringDict, self.__hostSession)
        # This is purely so we can see it in the debug log, the
        # return value of this function should be discarded.
        return stringDict

    ## @}

    ##
    # @name Entity Reference inspection
    #
    # @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def entityExists(self, entityRefs, context):
        """
        Called to determine if each @ref entity_reference supplied
        points to an entity that exists in the @ref
        asset_management_system, and that they can be resolved into
        a meaningful string or otherwise queried.

        By 'exist' we mean 'is ready to be read'. For example,
        entityExists may be called before attempting to read from a
        reference that is believed to point to an image sequence, so
        that alternatives can be found.

        In the future, this may need to be extended to cover a more
        complex definition of 'existence' (for example, known to the
        system, but not yet finalized). For now however, it should be
        assumed to simply mean, 'ready to be consumed', and if only a
        placeholder or un-finalized asset is available, `False` should
        be returned.

        The supplied context's locale should be well-configured as it
        may contain information pertinent to disambiguating this subtle
        definition of 'exists' in some cases too, as it better explains
        the use-case of the call.

        @param entityRefs `List[` @fqref{EntityReference}
        "EntityReference" `]` Entity references to query.

        @param context Context The calling context.

        @return `List[bool]` `True` if the corresponding element in
        entityRefs points to an existing entity, `False` if the entity
        is not known or ready yet.

        @unstable
        """
        return self.__impl.entityExists(entityRefs, context, self.__hostSession)

    ## @}

    ##
    # @name Entity Retrieval
    #
    ## @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def defaultEntityReference(self, traitSets, context):
        """
        Returns an @ref entity_reference considered to be a sensible
        default for each of the given entity @ref trait "traits" and
        Context. This can be used to ensure dialogs, prompts or publish
        locations default to some sensible value, avoiding the need for
        a user to re-enter such information. There may be situations
        where there is no meaningful default, so the caller should be
        robust to this situation.

        @param traitSets `List[Set[str]]`
        The relevant trait sets for the type of entities required,
        these will be interpreted in conjunction with the context to
        determine the most sensible default.

        @param context Context The context the resulting reference
        will be used in, particular care should be taken to the access
        pattern as it has great bearing on the resulting reference.

        @return `List[str]` An @ref entity_reference or empty string for
        each given trait set.

        @unstable
        """
        return self.__impl.defaultEntityReference(traitSets, context, self.__hostSession)

    ## @}
