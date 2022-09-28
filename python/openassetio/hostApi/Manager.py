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
        strings that you might want to use in your UI/messages. See
        @ref openassetio.constants "constants" for well-known keys.
        These keys are updated in-place to the most appropriate term
        for the Manager. You should then use these substitutions in any
        user-facing messages or display text so that they feel at home.

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
    # @name Initialization
    #
    ## @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def flushCaches(self):
        """
        Clears any internal caches.  Only applicable if the manager
        makes use of any caching, otherwise it is a no-op.  In caching
        interfaces, this should cause any retained data to be discarded
        to ensure future queries are fresh.

        @unstable
        """
        return self.__impl.flushCaches(self.__hostSession)

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

    ##
    # @name Entity information
    #
    # There are several common requests for basic, generic information about
    # an entity that is assumed to be valid for all entity types.
    #
    # This suite of methods query information for a supplied @ref
    # entity_reference.
    #
    # @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def entityName(self, entityRefs, context):
        """
        Returns the concise name of each entity itself, not including
        any hierarchy or classification.

        For example:

         @li `"Cuttlefish v1"` - for a versioned asset
         @li `"seq003"` - for a sequence in a hierarchy

        @param entityRefs `List[` @fqref{EntityReference}
        "EntityReference" `]` Entity references to query.

        @param context Context The calling context.

        @return `List[str]` Strings containing any valid characters for
        the manager's implementation.

        @unstable
        """
        return self.__impl.entityName(entityRefs, context, self.__hostSession)

    @debugApiCall
    @auditApiCall("Manager methods")
    def entityDisplayName(self, entityRefs, context):
        """
        Returns an unambiguous, humanised display name for each entity.

        The display name may consider the Host, and any other relevant
        Context information to form a display name for an entity that
        can uniquely identify the entity in that context.

        For example:

         @li `"dive / build / cuttlefish / model / v1"` - for a version
         of an asset in an 'open recent' menu.
         @li `"Sequence 003 [ Dive / Episode 1 ]"` - for a sequence in
         an hierarchy as a window title.

        @param entityRefs `List[` @fqref{EntityReference}
        "EntityReference" `]` Entity references to query.

        @param context Context The calling context.

        @return `List[Union[str,` exceptions.InvalidEntityReference `]]`
        For each given entity, either a string containing any valid
        characters for the @ref asset_management_system's
        implementation; or an `InvalidEntityReference` if the supplied
        reference is not recognised by the asset management system.

        @unstable
        """
        return self.__impl.entityDisplayName(entityRefs, context, self.__hostSession)

    ## @}

    ##
    # @name Versioning
    #
    # Most asset_management_systems allow multiple revisions of certain
    # entities to be tracked simultaneously. This API exposes this as
    # a generalised concept, and its necessary for the caller to make sure
    # only @ref entity_reference "entity references" that are meaningfully
    # versioned are queried.
    #
    # @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def entityVersion(self, entityRefs, context):
        """
        Retrieves the identifier of the version pointed to by each
        supplied @ref entity_reference.

        @param entityRefs `List[` @fqref{EntityReference}
        "EntityReference" `]` Entity references to query.

        @param context Context The calling context.

        @return `List[str]` A string for each entity representing its
        version, or an empty string if the entity was not versioned.
        This identifier will be one of the keys of @ref entityVersions.

        @note It is not necessarily a requirement that the entity
        exists, if, for example, the version name can be determined from
        the reference itself, or is a @ref meta_version.

        @see @ref entityVersions
        @see @ref finalizedEntityVersion

        @unstable
        """
        return self.__impl.entityVersion(entityRefs, context, self.__hostSession)

    @debugApiCall
    @auditApiCall("Manager methods")
    def entityVersions(self, entityRefs, context, includeMetaVersions=False, maxNumVersions=-1):
        """
        Retrieves all available versions of each supplied @ref
        entity_reference (including the supplied ref, if it points to a
        specific version).

        @param entityRefs `List[` @fqref{EntityReference}
        "EntityReference" `]` Entity references to query.

        @param context Context The calling context.

        @param includeMetaVersions `bool` If `True`, @ref meta_version
        "meta-versions" such as 'latest', etc... should be included,
        otherwise, only concrete versions will be retrieved.

        @param maxNumVersions `int` Limits the number of versions
        collected for each entity. If more results are available than
        the limit, then the newest versions will be returned. If a
        value of -1 is used, then all results will be returned.

        @return `List[Dict[str, str]]` A dictionary for each entity,
        where the keys are string version identifiers (as returned by
        @ref entityVersion), and the values are an @ref entity_reference
        that points to its entity. Additionally the
        openassetio.constants.kVersionDict_OrderKey can be set to a list
        of the version names (ie: dict keys) in their natural ascending
        order, that may be used by UI elements, etc.

        @see @ref entityVersion
        @see @ref finalizedEntityVersion

        @unstable
        """
        return self.__impl.entityVersions(
            entityRefs,
            context,
            self.__hostSession,
            includeMetaVersions=includeMetaVersions,
            maxNumVersions=maxNumVersions,
        )

    @debugApiCall
    @auditApiCall("Manager methods")
    def finalizedEntityVersion(self, entityRefs, context, overrideVersionName=None):
        """
        Retrieves an @ref entity_reference that points to the
        concrete version for each given @ref meta_version or
        otherwise unstable @ref entity_reference.

        If a supplied entity reference is not versioned, or already
        has a concrete version, the input reference will be
        passed-through.

        If versioning is unsupported for a given @ref
        entity_reference, then the input reference will be returned.

        @param entityRefs `List[` @fqref{EntityReference}
        "EntityReference" `]` Entity references to query.

        @param context Context The calling context.

        @param overrideVersionName `str` If supplied, then the call
        will return entity references for the version of the
        referenced assets that match the name specified here, ignoring
        any version inferred by the input reference.

        @return `List[Union[str,` exceptions.EntityResolutionError `]]`
        A list where each element is either the concretely versioned
        reference, or `EntityResolutionError`. An
        `EntityResolutionError` will be returned if the entity
        reference is ambiguously versioned or if the supplied
        `overrideVersionName` does not exist for that entity. For
        example, if the version is missing from a reference to a
        versioned entity, and that behavior is undefined in the
        manager's model, then an `EntityResolutionError` will be
        returned. It may be that it makes sense in the specific asset
        manager to fall back on 'latest' in this case.

        @see @ref entityVersion
        @see @ref entityVersions

        @unstable
        """
        return self.__impl.finalizedEntityVersion(
            entityRefs, context, self.__hostSession, overrideVersionName=overrideVersionName
        )

    ## @}

    ##
    # @name Related Entities
    #
    # A 'related' entity could take many forms. For example:
    #
    #  @li In 3D CGI, Multiple AOVs or layers may be related to a 'beauty' render.
    #  @li In Compositing, an image sequence may be related to the script
    #  that created it.
    #  @li An asset may be related to a task that specifies work to be done.
    #  @li Parent/child relationships are also (semantically) covered by
    #  these relationships.
    #
    # In the this API, these relationships are represented by trait data.
    # This may just compose property-less traits as a 'type', or
    # additionally, set trait property values to further define the
    # relationship. For example in the case of AOVs, the type might be
    # 'alternate output' and the attributes may be that the 'channel' is
    # 'diffuse'.
    #
    # Related references form a vital part in the abstraction of the internal
    # structure of the asset management system from the host application in its
    # attempts to provide the user with meaningful functionality. A good example
    # of this is in an editorial workflow, where you may need to query whether a
    # 'shot' exists in a certain part of the asset system. One approach would be
    # to use a 'getChildren' call, on this part of the system. This has the
    # drawback that is assumes that shots are always something that can be
    # described as 'immediate children' of the location in question. This lay not
    # always be the case (say, for example there is some kind of 'task' structure
    # in place too). Instead we use a request that asks for any 'shots' that
    # relate to the chosen location. It is then up to the implementation of the
    # manager to determine how that maps to its own data model. Hopefully this
    # allows a host to work with a broader range of asset management systems,
    # without providing any requirements of their structure or data model within
    # the  system itself.
    #
    # @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def getRelatedReferences(
        self, references, relationshipTraitsDataOrDatas, context, resultTraitSet=None
    ):
        """
        Returns related entity references, based on a relationship
        defined by a set of traits and their properties.

        This is an essential function in this API - as it is widely used
        to query organisational hierarchy, etc...

        There are three possible conventions for calling this function,
        to allow for batch optimisations in the implementation and
        prevent excessive query times with high-latency services.

          a)  A single entity reference, a list of relationships.
          b)  A list of entity references and a single relationship.
          c)  Equal length lists of references and relationships.

        In all cases, the return value is a list of lists, for example:

            a)  getRelatedReferences([ r1 ], [ td1, td2, td3 ])

            > [ [ r1td1... ], [ r1td2... ], [ r1td3... ] ]

            b)  getRelatedReferences([ r1, r2, r3 ], [ td1 ])

            > [ [ r1td1... ], [ r2td1... ], [ r3td1... ] ]

            c)  getRelatedReferences([ r1, r2, r3 ], [ td1, td2, td3 ])

            > [ [ r1td1... ], [ r2td2... ], [ r3td3... ] ]

        @note The order of entities in the inner lists of matching
        references should not be considered meaningful, but the outer
        list should match the input order.

        In summary, if only a single entityRef is provided, it should be
        assumed that all relationships should be considered for that one
        entity. If only a single relationship is provided, then it
        should be considered for all supplied entity references. If
        lists of both are supplied, then they must be the same length,
        and it should be assumed that it is a 1:1 mapping of a
        relationship definition to an entity. If this is not the case,
        ValueErrors will be thrown.

        If any relationship definition is unknown, then an empty list
        will be returned for that relationship, and no errors should be
        raised.

        @param references List[str] A list of @ref entity_reference, see
        the notes on array length above.

        @param relationshipTraitsDataOrDatas `List[`
        @fqref{TraitsData} "TraitsData" `]`

        @param resultTraitSet `Set[str]` or None, a hint as to what
        traits the returned entities should have.

        @param context Context The calling context.

        @return list of str lists The return is *always* a list of lists
        regardless of which form of invocation is used. The outer list
        is for each supplied entity or relationship. The inner lists
        are all the matching entities for that source entity.

        @exception ValueError If more than one reference and
        relationship is provided, but they lists are not equal in
        length, ie: not a 1:1 mapping of entities to relationships.

        @unstable

        @todo Implement missing setRelatedReferences()
        """
        if not isinstance(references, (list, tuple)):
            references = [
                references,
            ]

        if not isinstance(relationshipTraitsDataOrDatas, (list, tuple)):
            relationshipTraitsDataOrDatas = [
                relationshipTraitsDataOrDatas,
            ]

        numEntities = len(references)
        numRelationships = len(relationshipTraitsDataOrDatas)

        if (numEntities > 1 and numRelationships > 1) and numRelationships != numEntities:
            raise ValueError(
                (
                    "You must supply either a single entity and a "
                    + "list of relationships, a single relationship "
                    + "and a list of entities, or an equal number of "
                    + "both... %s entities .vs. %s relationships"
                )
                % (numEntities, numRelationships)
            )

        result = self.__impl.getRelatedReferences(
            references,
            relationshipTraitsDataOrDatas,
            context,
            self.__hostSession,
            resultTraitSet=resultTraitSet,
        )

        return result

    ## @}
