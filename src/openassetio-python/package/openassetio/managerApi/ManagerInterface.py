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
@namespace openassetio.managerApi.ManagerInterface
A single-class module, providing the ManagerInterface class.
"""

# Most of this module is documentation, which hopefully is a good thing.
# pylint: disable=too-many-lines,line-too-long
# We discussed splitting the interface up, but it ends up making most
# implementations more complicated.
# pylint: disable=too-many-public-methods
# As this is an abstract base class, there are many of these.
# pylint: disable=unused-argument,no-self-use

import abc

# TODO(DF): Remove pylint disable once CI is fixed.
from openassetio import _openassetio  # pylint: disable=no-name-in-module


__all__ = [
    "ManagerInterface",
]


class ManagerInterface(_openassetio.managerApi.ManagerInterface):
    """
    @brief This Interface binds a @ref asset_management_system into
    OpenAssetIO. It is not called directly by a @ref host, but by the
    middle-ware that presents a more object-oriented model of this to
    the @ref host - namely, the @ref openassetio.hostApi.Manager.

    It is structured around the following principals:

      @li The currency of the API is either data, or an @ref
      entity_reference. objects should not be used to represent an @ref
      entity or its properties.

      @li The manager plugin is expected to be batch-first. That is,
      where relevant, methods expect lists as their primary input
      parameters, and return a list as the result. This means a host
      can batch together multiple items and execute the same command
      on every item in the list in a single call, saving on
      potentially expensive round-trips and allowing the manager to
      use other back-end optimisations.

      @li The interface is stateless as far as the host-facing API is
      concerned. The result of any method should solely depend on its
      inputs. This class could be static. In practice though, in a
      real-world session with a host, there are benefits to having an
      'instance' with a managed lifetime. This can be used to facilitate
      caching etc.

      @li The implementation of this class should have no UI
      dependencies, so that it can be used in command-line only
      hosts/batch process etc...

      @li You generally don't need to call the superclass implementation
      of any methods in this interface, unless you are deriving from your
      own subclass which requires it.

    Logging and Error Handling
    --------------------------

    The supplied @fqref{managerApi.HostSession} "HostSession" object
    provides access to a logger that allows messages and progress to be
    reported back to the user. All logging should go through these
    methods otherwise it may not be correctly presented to the user. The
    loose term "user" also covers developers, who may need to see log
    output for debugging and other purposes.

    @warning Your plugin may be hosted out of process, or even on
    another machine, the HostSession bridge takes care of relaying
    messages accordingly. Using custom logging mechanisms may well
    result in output being lost.

    @see @fqref{managerApi.HostSession.logger} "HostSession.logger"
    @see @fqref{log.LoggerInterface} "LoggerInterface"

    Exceptions should be thrown to handle any in-flight errors that
    occur.  The error should be mapped to a derived class of
    exceptions.OpenAssetIOException, and thrown.  All exceptions of this
    kind, will be correctly passed across the plug-in C boundary,
    and re-thrown. Other exceptions should not be used.

     @see @ref openassetio.exceptions "exceptions"

    Threading
    ---------
    Any implementation of the ManagerInterface should be thread safe.
    The one exception being @needsref initialize, this will
    never be called concurrently.

    When a @fqref{Context} "Context" object is constructed by
    @fqref{hostApi.Manager.createContext} "Manager.createContext", the
    @fqref{managerApi.ManagerInterface.createState} "createState" (or
    @fqref{managerApi.ManagerInterface.createChildState}
    "createChildState" for @fqref{hostApi.Manager.createChildContext}
    "createChildContext") method will be called, and the resulting state
    object stored in the context. This context will then be re-used
    across related API calls to your implementation of the
    ManagerInterface. You can use this to determine which calls may be
    part of a specific 'action' in the same host, or logically grouped
    processes such as a batch render. This should allow you to implement
    stable resolution of @ref meta_version "meta-versions" or other
    resolve-time concepts.

    There should be no persistent state in the implementation, concepts
    such as getError(), etc.. for example should not be used.

    Hosts
    -----

    Sometimes you may need to know more information about the API host.
    A @ref openassetio.managerApi.Host object is available through the
    @ref openassetio.managerApi.HostSession object passed to each method
    of this class. This provides a standardised interface that all API
    hosts guarantee to implement. This can be used to identify exactly
    which host you are being called for, and query various entity
    related specifics of the hosts data model.

    @see @ref openassetio.managerApi.Host "Host"

    Initialization
    --------------

    The constructor makes a new instance, but at this point it is not
    ready for use. Instances of this class should be light weight to
    create, but don't have to be lightweight to initialize. The
    informational methods must be available pre-initialization, so that
    UI and other display-type queries can be made relatively cheaply to
    provide users with a list of managers and their settings. None of
    the entity-related methods will be called until after @needsref
    initialize has been called. The following methods must be callable
    prior to initialization:

       @li @needsref identifier()
       @li @needsref displayName()
       @li @needsref info()
       @li @ref updateTerminology()
       @li @needsref settings()

    @todo Finish/Document settings mechanism.
    @see @needsref initialize
    """

    __metaclass__ = abc.ABCMeta

    ##
    # @name Asset Management System Information
    #
    # These functions provide hosts with general information about the @ref
    # asset_management_system itself.
    #
    # @{

    def updateTerminology(self, stringDict, hostSession):
        """
        This call gives the manager a chance to customize certain
        strings used in a host's UI/messages. See @ref openassetio.constants
        "constants"
        for known keys. The values in stringDict can be freely updated
        to match the terminology of the asset management system you are
        representing.

        For example, you may way a host's "Publish Clip" menu item to
        read "Release Clip", so you would set the @ref openassetio.hostApi.terminology.kTerm_Publish
        value to "Release".

        @return `None`

        @see @ref openassetio.constants "constants"
        @see @ref openassetio.hostApi.terminology.defaultTerminology
        "terminology.defaultTerminology"

        @unstable
        """

    ## @}

    ##
    # @name Initialization
    #
    ## @{

    def flushCaches(self, hostSession):
        """
        Clears any internal caches.  Only applicable if the
        implementation makes use of any caching, otherwise it is a
        no-op. In caching interfaces, this should cause any retained
        data to be discarded to ensure future queries are fresh.

        @unstable
        """

    ## @}

    ##
    # @name Entity Reference inspection
    #
    #
    # @{

    @abc.abstractmethod
    def entityExists(self, entityRefs, context, hostSession):
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

        The supplied context's locale may contain information pertinent
        to disambiguating this subtle definition of 'exists' in some
        cases too, as it better explains the use-case of the call.

        @param entityRefs `List[` @fqref{EntityReference}
        "EntityReference" `]` Entity references to query.

        @param context Context The calling context.

        @param hostSession HostSession The API session.

        @return `List[bool]` `True` if the corresponding element in
        entityRefs points to an existing entity, `False` if the entity
        is not known or ready yet.

        @unstable
        """
        raise NotImplementedError

    ## @}

    ##
    # @name Entity Reference Resolution
    #
    # The concept of resolution is turning an @ref entity_reference into a
    # 'finalized' string. This, ultimately, is anything meaningful to the
    # situation. It could be a color space, a directory, a script or image
    # sequence. A rule of thumb is that a resolved @ref entity_reference
    # should be the string that the application would have anyway, in a
    # unmanaged environment. For some kind of Entity - such as a 'Shot', for
    # example, there may not be a meaningful string, though often some sensible
    # value can be returned.
    #
    # @{

    def defaultEntityReference(self, traitSets, context, hostSession):
        """
        Returns an @ref entity_reference considered to be a sensible
        default for each of the given entity @ref trait "traits" and
        Context. This is often used in a host to ensure dialogs, prompts
        or publish locations default to some sensible value, avoiding
        the need for a user to re-enter such information when a Host is
        being run in some known environment.

        For example, a host may request the default ref for the @ref
        trait_set of a 'ShotSpecification' with access kWriteMultiple'.
        If the Manager has some concept of the 'current sequence' it may
        wish to return this so that a 'Create Shots' action starts
        somewhere meaningful.

        @param traitSets `List[Set[str]]`
        The relevant trait sets for the type of entities a host is
        about to work with. These should be interpreted in conjunction
        with the context to determine the most sensible default.

        @param context Context The context the resulting reference
        will be used in. When determining a suitable reference to
        return, it is important to pay particular attention to the
        access pattern. It differentiates between a reference that
        will be used for reading or writing, and critically single or
        multiple entities.

        @param hostSession openassetio.managerApi.HostSession The host
        session that maps to the caller, this should be used for all
        logging and provides access to the openassetio.managerApi.Host
        object representing the process that initiated the API session.

        @return `List[str]` An @ref entity_reference or empty string for
        each given trait set.

        @unstable
        """
        return ["" for _ in traitSets]

    ## @}

    ##
    # @name Versioning
    #
    # Most @ref asset_management_system "asset management systems" allow
    # multiple revisions of certain entities to be tracked simultaneously.
    # This API exposes this as a generalised concept, and its necessary
    # for the caller to make sure only @ref entity_reference "references"
    # that are meaningfully versioned are queried.
    #
    # @{

    def entityVersion(self, entityRefs, context, hostSession):
        """
        Retrieves the identifier of the version pointed to by each
        supplied @ref entity_reference.

        @param entityRefs `List[` @fqref{EntityReference}
        "EntityReference" `]` Entity references to query.

        @param context Context The calling context.

        @param hostSession HostSession The API session.

        @return `List[str]` A string identifier for each entity
        representing its version, or an empty string  if the entity was
        not versioned. This identifier should be one of the keys in
        @ref entityVersions.

        @note It is not necessarily a requirement that the entity
        exists, if, for example, the version name can be determined from
        the reference itself (in systems that implement a human-readable
        URL, for example)

        @see @ref entityVersions
        @see @ref finalizedEntityVersion

        @unstable
        """
        return ["" for _ in entityRefs]

    def entityVersions(
        self, entityRefs, context, hostSession, includeMetaVersions=False, maxNumVersions=-1
    ):
        """
        Retrieves all available versions of each supplied @ref
        entity_reference (including the supplied ref, if it points to a
        specific version).

        @param entityRefs `List[` @fqref{EntityReference}
        "EntityReference" `]` Entity references to query.

        @param context Context The calling context.

        @param hostSession openassetio.managerApi.HostSession The host
        session that maps to the caller, this should be used for all
        logging and provides access to the openassetio.managerApi.Host
        object representing the process that initiated the API session.

        @param includeMetaVersions `bool` If `True`, @ref meta_version
        "meta-versions" such as 'latest', etc... should be included,
        otherwise, only concrete versions need to be returned.

        @param maxNumVersions `int` Limits the number of versions
        collected for each entity. If more results are available than
        the limit, then the newest versions should be returned. If a
        value of -1 is used, then all results should be returned.

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
        return [{} for _ in entityRefs]

    def finalizedEntityVersion(self, entityRefs, context, hostSession, overrideVersionName=None):
        """
        Retrieves an @ref entity_reference that points to the
        concrete version for each given @ref meta_version or
        otherwise unstable @ref entity_reference.

        If a supplied entity reference is not versioned, or already
        has a concrete version, the input reference should be
        passed-through.

        If versioning is unsupported for a given @ref
        entity_reference, then the input reference should be returned.

        @param entityRefs `List[` @fqref{EntityReference}
        "EntityReference" `]` The entity references to finalize.

        @param context Context The calling context.

        @param hostSession openassetio.managerApi.HostSession The host
        session that maps to the caller, this should be used for all
        logging and provides access to the openassetio.managerApi.Host
        object representing the process that initiated the API session.

        @param overrideVersionName `str` If supplied, then the call
        should return entity references for the version of the
        referenced assets that match the name specified here, ignoring
        any version inferred by the input reference.

        @return `List[Union[str,` exceptions.EntityResolutionError `]]`
        A list where each element is either the concretely versioned
        reference, or `EntityResolutionError`. An
        `EntityResolutionError` should be returned if the entity
        reference is ambiguously versioned or if the supplied
        @p overrideVersionName does not exist for that entity. For
        example, if the version is missing from a reference to a
        versioned entity, and that behavior is undefined in the
        manager's model, then an `EntityResolutionError` should be
        returned. It may be that it makes sense in the specific asset
        manager to fall back on 'latest' in this case.

        @see @ref entityVersion
        @see @ref entityVersions

        @unstable
        """
        return entityRefs

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
    # structure of the asset management system from the Host application in its
    # attempts to provide the user with meaningful functionality. A good example
    # of this is in an editorial example, where it may need to query whether a
    # 'shot' exists in a certain part of the asset system. One approach would be
    # to use a 'getChildren' call, on this part of the system. This has the
    # drawback that is assumes that shots are always something that can be
    # described as 'immediate children' of the location in question. This may not
    # always be the case (say, for example there is some kind of 'task' structure
    # in place too). Instead we use a request that asks for any 'shots' that
    # relate to the chosen location. It is then up to the implementation of the
    # ManagerInterface to determine how that maps to its own data model.
    # Hopefully this allows Hosts of this API to work with a broader range of
    # asset managements, without providing any requirements of their structure or
    # data model.
    #
    # @{

    def getWithRelationship(
        self,
        relationshipTraitsData,
        entityReferences,
        context,
        hostSession,
        successCallback,
        errorCallback,
        resultTraitSet=None,
    ):
        """
        Queries entity references that are related to the input
        references by the relationship defined by a set of traits and
        their properties in @p relationshipTraitsData.

        This is an essential function in this API - as it is widely used
        to query other entities or organisational structure.

        @note Consult the documentation for the relevant relationship
        traits to determine if the order of entities in the inner lists
        of matching references is required to be meaningful.

        If any relationship definition is unknown, then an empty list
        must be returned for that entity, and no errors raised. The
        default implementation returns an empty list for all
        relationships.

        @param relationshipTraitsData @fqref{TraitsData} "TraitsData"
        The traits of the relationship to query.

        @param entityReferences `List[` @fqref{EntityReference} "EntityReference" `]`
        A list of @ref entity_reference "entity references" to query the specified
        relationship for.

        @param context Context The calling context.

        @param hostSession openassetio.managerApi.HostSession The host
        session that maps to the caller, this should be used for all
        logging and provides access to the openassetio.managerApi.Host
        object representing the process that initiated the API session.

        @param successCallback Callback that must be called for each
        successful relationship query for an input entity reference. It
        should be given the corresponding index of the entity reference
        in @p entityReferences along with a list of entity references for
        entities that have the relationship specified by
        @p relationshipTraitsData. If there are no relations, an empty
        list should be passed to the callback. The callback must be
        called on the same thread that initiated the call to
        `getWithRelationship`.

        @param errorCallback Callback that must be called for each
        failed relationship query for an entity reference. It should be
        given the corresponding index of the entity reference in
        @p entityReferences along with a populated
        @fqref{BatchElementError} "BatchElementError" (see
        @fqref{BatchElementError.ErrorCode} "ErrorCodes"). The callback
        must be called on the same thread that initiated the call to
        `getWithRelationship`.

        @param resultTraitSet `Set[str]` or None, a hint as to what
        traits the returned entities should have.

        @return `List[List[`@fqref{EntityReference} "EntityReference"`]]`
        A list of references to related entities, for each input
        reference.

        @note Ensure that your implementation of
        @fqref{managerApi.ManagerInterface.managementPolicy}
        "managementPolicy" responds appropriately when queried with
        relationship trait sets and a read policy to communicate to the
        host whether or not you are capable of handling queries for
        those relationships in this method.
        """
        for i in range(len(entityReferences)):
            successCallback(i, [])

    def getWithRelationships(
        self,
        relationshipTraitsDatas,
        entityReference,
        context,
        hostSession,
        successCallback,
        errorCallback,
        resultTraitSet=None,
    ):
        """
        Queries entity references that are related to the input
        reference by the relationships defined by a set of traits and
        their properties. Each element of @p relationshipTraitsDatas
        defines a specific relationship to query.

        This is an essential function in this API - as it is widely used
        to query other entities or organisational structure.

        @note Consult the documentation for the relevant relationship
        traits to determine if the order of entities in the inner lists
        of matching references is required to be meaningful.

        If any relationship definition is unknown, then an empty list
        must be returned for that relationship, and no errors raised. The
        default implementation returns an empty list for all
        relationships.

        @param relationshipTraitsDatas `List[` @fqref{TraitsData} "TraitsData" `]`
        The traits of the relationships to query.

        @param entityReference @fqref{EntityReference} "EntityReference"
        The @ref entity_reference to query the specified relationships
        for.

        @param hostSession openassetio.managerApi.HostSession The host
        session that maps to the caller, this should be used for all
        logging and provides access to the openassetio.managerApi.Host
        object representing the process that initiated the API session.

        @param context Context The calling context.

        @param successCallback Callback that must be called for each
        successful relationship query for an input relationship. It
        should be given the corresponding index of the relationship
        definition in @p relationshipTraitsDatas along with a list of
        entity references for entities that are related to
        @p entityReference by that relationship. If there are no
        relations, an empty list should be passed to the callback. The
        callback must be called on the same thread that initiated the
        call to `getWithRelationships`.

        @param errorCallback Callback that must be called for each
        failed query for a relationship. It should be given the
        corresponding index of the relationship in
        @p relationshipTraitsDatas along with a populated
        @fqref{BatchElementError} "BatchElementError" (see
        @fqref{BatchElementError.ErrorCode} "ErrorCodes"). The callback
        must be called on the same thread that initiated the call to
        `getWithRelationships`.

        @param resultTraitSet `Set[str]` or None, a hint as to what
        traits the returned entities should have.

        @return `List[List[`@fqref{EntityReference} "EntityReference"`]]`
        A list of references to related entities, for each input
        relationship.

        @note Ensure that your implementation of
        @fqref{managerApi.ManagerInterface.managementPolicy}
        "managementPolicy" responds appropriately when queried with
        relationship trait sets and a read policy to communicate to the
        host whether or not you are capable of handling queries for
        those relationships in this method.
        """
        for i in range(len(relationshipTraitsDatas)):
            successCallback(i, [])

    ## @}
