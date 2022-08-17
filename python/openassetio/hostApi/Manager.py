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


__all__ = ['Manager']


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

        _openassetio.hostApi.Manager .__init__(self, interfaceInstance, hostSession)
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
        """
        return self.__impl.entityVersions(
            entityRefs, context, self.__hostSession, includeMetaVersions=includeMetaVersions,
            maxNumVersions=maxNumVersions)

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
        """
        return self.__impl.finalizedEntityVersion(
            entityRefs, context, self.__hostSession, overrideVersionName=overrideVersionName)

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
            self, references, relationshipTraitsDataOrDatas, context, resultTraitSet=None):
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

        @todo Implement missing setRelatedReferences()
        """
        if not isinstance(references, (list, tuple)):
            references = [references, ]

        if not isinstance(relationshipTraitsDataOrDatas, (list, tuple)):
            relationshipTraitsDataOrDatas = [relationshipTraitsDataOrDatas, ]

        numEntities = len(references)
        numRelationships = len(relationshipTraitsDataOrDatas)

        if (numEntities > 1 and numRelationships > 1) and numRelationships != numEntities:
            raise ValueError(
                ("You must supply either a single entity and a "
                 + "list of relationships, a single relationship "
                 + "and a list of entities, or an equal number of "
                 + "both... %s entities .vs. %s relationships")
                % (numEntities, numRelationships))

        result = self.__impl.getRelatedReferences(
            references,
            relationshipTraitsDataOrDatas, context, self.__hostSession, resultTraitSet=resultTraitSet)

        return result

    ## @}

    ##
    # @name Entity Resolution
    #
    # The concept of resolution is turning an @ref entity_reference
    # into the data for one or more @ref trait "traits" that are meaningful
    # to the situation. It could be a color space, a directory, a script
    # or a frame range for an image sequence.
    #
    # @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def resolve(self, entityRefs, traitSet, context):
        """
        Returns a @fqref{TraitsData} "TraitsData"
        populated with the available data for the requested set of
        traits for each given @ref entity_reference.

        Any traits that aren't applicable to any particular entity
        reference will not be set in the returned data. Consequently, a
        trait being set in the result is confirmation that an entity has
        that trait.

        There is however, no guarantee that a manager will have data
        for all of a traits properties. It is the responsibility of the
        caller to handle requested data being missing in a fashion
        appropriate to its intended use.

        @note @fqref{EntityReference} "EntityReference" objects _must_
        be constructed using either
        @fqref{hostApi.Manager.createEntityReference}
        "createEntityReference" or
        @fqref{hostApi.Manager.createEntityReferenceIfValid}
        "createEntityReferenceIfValid".

        The API defines that all file paths passed though the API that
        represent file sequences should retain the frame token, and
        use the 'format' syntax, compatible with sprintf (eg.  %04d").

        @param entityRefs `List[` @fqref{EntityReference}
        "EntityReference" `]` Entity references to query.

        @param context Context The calling context.

        @param traitSet `Set[str]` The trait IDs to resolve for the
        supplied list of entity references. Only traits applicable to
        the supplied entity references will be set in the resulting
        data.

        @return `List[Union[`
            @fqref{TraitsData}
            "TraitsData",
            exceptions.EntityResolutionError,
            exceptions.InvalidEntityReference `]]`
        A list containing either a populated TraitsData instance for
        each reference; `EntityResolutionError` if there is any runtime
        error during the resolution of the entity, including internal
        failure modes; or `InvalidEntityReference` if a supplied entity
        reference should not be resolved for that context, for example,
        if the context access is `kWrite` and the entity is an existing
        version - the exception means that it is not a valid action to
        perform on the entity.
        """
        return self.__impl.resolve(entityRefs, traitSet, context, self.__hostSession)

    ## @}

    ##
    # @name Publishing
    #
    # The publishing functions allow the host to create an @ref entity within
    # the @ref asset_management_system represented by the Manager. The API is
    # designed to accommodate the broad variety of roles that different asset
    # managers embody. Some are 'librarians' that simply catalog the locations of
    # existing media. Others take an active role in both the temporary and
    # long-term paths to items they manage.
    #
    # There are two key components to publishing within this API.
    #
    # *1 - The Entity Reference*
    #
    # As with the other entry points in this API, it is assumed that an @ref
    # entity_reference is known ahead of time. How this reference is determined
    # is beyond the scope of this layer of the API, and functions exists in
    # higher levels that combine browsing and publishing etc... Here, we simply
    # assert that there must be a meaningful reference given the
    # @fqref{TraitsData} "TraitsData" of the entity that
    # is being created or published.
    #
    # @note 'Meaningful' is best defined by the asset manager itself. For
    # example, in a system that versions each 'asset' by creating children of the
    # asset for each version, when talking about where to publish an image
    # sequence of a render to, it may make sense to reference to the Asset
    # itself, so that the system can determine the 'next' version number at the
    # time of publish. It may also make sense to reference a specific version of
    # this asset to implicitly state which version it will be written to. Other
    # entity types may not have this flexibility.
    #
    # **2 - TraitsData**
    #
    # The data for an entity is defined by one or more @ref trait
    # "traits" and their properties. The resulting @ref trait_set
    # defines the "type" of the entity, and the trait property values
    # hold the data for each specific entity.
    #
    # This means that OpenAssetIO it not just limited to working with
    # file-based data. Traits allow ancillary information to be managed
    # (such as the colorspace for an image), as well as container-like
    # entities such as shots/sequences/etc..
    #
    # For more on the relationship between Entities, Specifications and
    # traits, please see @ref entities_traits_and_specifications
    # "this" page.
    #
    # The action of 'publishing' itself, is split into two parts, depending on
    # the nature of the item to be published.
    #
    #  @li **Preflight** When you are about to create some new media/asset.
    #  @li **Registration** When you wish to publish media that exists.
    #
    # For examples of how to correctly call these parts of the
    # API, see the @ref examples page.
    #
    # @note The term '@ref publish' is somewhat loaded. It generally means
    # something different depending on who you are talking to. See the @ref
    # publish "Glossary entry" for more on this, but to help avoid confusion,
    # this API provides the @ref updateTerminology call, in order to allow the
    # Manager to standardize some of the language and terminology used in your
    # presentation of the asset management system with other integrations of the
    # system.
    #
    # *3 - Thumbnails*
    #
    # The API provides a mechanism for a manager to request a thumbnail for an
    # entity as it is being published, see: @ref thumbnails.
    #
    # @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def preflight(self, targetEntityRefs, traitSet, context):
        """
        @note This call is only applicable when the manager you are
        communicating with sets the @ref
        openassetio.traits.managementPolicy.WillManagePathTrait
        "WillManagePathTrait" in response to
        @fqref{hostApi.Manager.managementPolicy} "managementPolicy" for
        the traits of entities you are intending to publish.

        It signals your intent as a host application to do some work to
        create data in relation to each supplied @ref entity_reference.
        The entity does not need to exist yet (see @ref
        entity_reference) or it may be a parent entity that you are
        about to create a child of or some other similar relationship
        (it actually doesn't matter really, as this @ref
        entity_reference will ultimately have been determined by
        interaction with the Manager, and it will have returned you
        something meaningful).

        It should be called before register() if you are about to
        create media or write to files. If the file or data already
        exists, then preflight is not needed. It will return a working
        @ref entity_reference for each given entity, which can be
        resolved in order to determine a working path that the files
        should be written to.

        This call is designed to allow sanity checking, placeholder
        creation or any other sundry preparatory actions to be carried
        out by the Manager. In the case of file-based entities,
        the Manager may even use this opportunity to switch to some
        temporary working path or some such.

        @note It's vital that the @ref Context is well configured here,
        in particular the @fqref{Context.retention}
        "Context.retention".

        @warning The working @ref entity_reference returned by this
        method should *always* be used in place of the original
        reference supplied to `preflight` for resolves prior to
        registration, and for the final call to @ref
        register itself. See @ref example_publishing_a_file.

        @param targetEntityRefs `List[` @fqref{EntityReference}
        "EntityReference" `]` The entity references to preflight prior
        to registration.

        @param traitSet `Set[str]` The @ref trait_set of the
        entites that are being published.

        @param context Context The calling context. This is not
        replaced with an array in order to simplify implementation.
        Otherwise, transactional handling has the potential to be
        extremely complex if different contexts are allowed.

        @return `List[Union[str,`
            exceptions.PreflightError, exceptions.RetryableError `]]`
        The preflight result for each corresponding entity. If
        successful, this will be an @ref entity_reference that you
        should resolve to determine the path to write media to. This
        may or may not be the same as the input reference. It should
        be resolved to get a working URL before writing any files or
        other data. If preflight was unsuccessful, the result for an
        entity will be either a `PreflightError` if some fatal exception
        happens during preflight, indicating the process should be
        aborted; or `RetryableError` if any non-fatal error occurs that
        means the host should retry from the beginning of any given
        process.

        @exception `IndexError` If `targetEntityRefs` and `traitSets`
        are not lists of the same length.

        @see @ref register
        """
        return self.__impl.preflight(targetEntityRefs, traitSet, context, self.__hostSession)

    @debugApiCall
    @auditApiCall("Manager methods")
    def register(self, targetEntityRefs, entityTraitsDatas, context):
        """
        Register should be used to register new entities either when
        originating new data within the application process, or
        referencing some existing file, media or information.

        @note The registration call is applicable to all kinds of
        Manager (path managing, or librarian), as long as the @ref
        traits.managementPolicy.ManagedTrait "ManagedTrait" is present
        in the response to @fqref{hostApi.Manager.managementPolicy}
        "managementPolicy" for the traits of the entities you are
        intending to publish. In this case, the Manager is saying it
        doesn't handle entities with those traits, and it should not be
        registered.

        As each @ref entity_reference has (ultimately) come from the
        manager (either in response to delegation of UI/etc... or as a
        return from another call), then it can be assumed that the
        Manager will understand what it means for you to call `register`
        on this reference with the supplied @fqref{TraitsData}
        "TraitsData". The conceptual meaning of the call is:

        "I have this reference you gave me, and I would like to register
        a new entity to it with the traits I told you about before. I
        trust that this is ok, and you will give me back the reference
        that represents the result of this."

        It is up to the manager to understand the correct result for the
        particular trait set in relation to this reference. For example,
        if you received this reference in response to browsing for a
        target to `kWriteMultiple` and the traits of a
        `ShotSpecification`s, then the Manager should have returned you
        a reference that you can then register multiple
        `ShotSpecification` entities to without error. Each resulting
        entity reference should then reference the newly created Shot.

        @warning All supplied TraitsDatas should have the same trait
        sets. If you wish to register different "types" of entity, they
        need to be registered in separate calls.

        @warning When registering files, it should never be assumed
        that the resulting @ref entity_reference will resolve to the
        same path. Managers may freely relocate, copy, move or rename
        files as part of registration.

        @param targetEntityRefs `List[` @fqref{EntityReference}
        "EntityReference" `]` Entity references to publish to.

        @param entityTraitsDatas `List[` @fqref{TraitsData}
        "TraitsData" `]` The data to register for each entity.
        NOTE: All supplied instances should have the same trait set.

        @param context Context The calling context.

        @return `List[Union[str,`
            exceptions.RegistrationError, exceptions.RetryableError `]]`
        The publish result for each corresponding entity. This is
        either an @ref entity_reference to the 'final' entity created
        by the publish action (which is not necessarily the same as
        the corresponding entry in `targetEntityRefs`); a
        `RegistrationError` if some fatal exception happens during
        publishing, indicating the process should be aborted; or
        `RetryableError` if any non-fatal error occurs that means you
        should retry the process later.

        @exception `IndexError` If `targetEntityRefs` and `entityTraitsDatas`
        are not lists of the same length.

        @see @fqref{TraitsData} "TraitsData"
        @see @ref preflight
        """
        if len(targetEntityRefs) != len(entityTraitsDatas):
            raise IndexError("Parameter lists must be of the same length")

        if entityTraitsDatas:
            # Check supplied traitsdata share a trait set
            expectedTraits = entityTraitsDatas[0].traitSet()
            for i, data in enumerate(entityTraitsDatas[1:]):
                traits = data.traitSet()
                if traits != expectedTraits:
                    raise ValueError(
                            f"Mismatched traits at index {i+1}: {traits} != {expectedTraits}")

        return self.__impl.register(targetEntityRefs, entityTraitsDatas, context, self.__hostSession)

    ## @}
