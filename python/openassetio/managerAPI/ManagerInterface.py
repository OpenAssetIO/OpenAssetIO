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
@namespace openassetio.managerAPI.ManagerInterface
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
from .. import exceptions


__all__ = ['ManagerInterface', ]


class ManagerInterface(_openassetio.managerAPI.ManagerInterface):
    """
    @brief This Interface binds a @ref asset_management_system into
    OpenAssetIO. It is not called directly by a @ref host, but by the
    middle-ware that presents a more object-oriented model of this to
    the @ref host - namely, the @ref openassetio.hostAPI.Manager.

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

    The supplied @ref openassetio.managerAPI.HostSession.HostSession
    "HostSession" object provides logging methods that allow messages
    and progress to be reported back to the user. All logging should go
    through these methods otherwise it may not be correctly presented to
    the user. The loose term "user" also covers developers, who may need
    to see log output for debugging and other purposes.

    @warning Your plugin may be hosted out of process, or even on
    another machine, the HostSession bridge takes care of relaying
    messages accordingly. Using custom logging mechanisms may well
    result in output being lost.

    @see @ref openassetio.managerAPI.HostSession.HostSession.log "HostSession.log"
    @see @ref openassetio.managerAPI.HostSession.HostSession.progress "HostSession.progress"

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
    @ref hostAPI.Manager.Manager.createContext "Manager.createContext", the
    @fqref{managerAPI.ManagerInterface.createState} "createState" (or
    @fqref{managerAPI.ManagerInterface.createChildState}
    "createChildState" for @ref hostAPI.Manager.Manager.createChildContext
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
    A @ref openassetio.managerAPI.Host object is available through the
    @ref openassetio.managerAPI.HostSession object passed to each method
    of this class. This provides a standardised interface that all API
    hosts guarantee to implement. This can be used to identify exactly
    which host you are being called for, and query various entity
    related specifics of the hosts data model.

    @see @ref openassetio.managerAPI.Host "Host"

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
       @li @ref getSettings()
       @li @ref setSettings()

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
        read "Release Clip", so you would set the @ref openassetio.hostAPI.terminology.kTerm_Publish
        value to "Release".

        @return `None`

        @see @ref openassetio.constants "constants"
        @see @ref openassetio.hostAPI.terminology.defaultTerminology
        "terminology.defaultTerminology"
        """

    ## @}

    ##
    # @name Initialization
    #
    ## @{

    def getSettings(self, hostSession):
        """
        @todo Document settings mechanism
        """
        return {}

    def setSettings(self, settings, hostSession):
        """
        @todo Document settings mechanism
        """
        if settings != {}:
            raise KeyError(f"{self.displayName} has no settings")

    def prefetch(self, entityRefs, context, hostSession):
        """
        Called by a host to express interest in the supplied @ref
        entity_reference list. This usually means that the host is about
        to make multiple queries to the same references.  This can be
        left unimplemented, but it is advisable to batch request the
        data for resolve here if possible.

        The implementation should ignore any entities to which no action
        is applicable (maybe as they don't exist yet).

        @warning Because the majority of the resolution API itself is
        designated thread safe, it is important to implement any
        pre-fetch mechanism with suitable locks/etc... if required.

        @param entityRefs `List[str]` The entities whose data should be
        prefetched.

        @param context openassetio.Context You may wish to make use of
        the managerState object (if you supplied one on
        construction of the context), to simplify scoping any caching of
        data. Otherwise, it's up to you how to manage the lifetime of
        the data to avoid inconsistencies, but the @ref flushCaches
        method should clear any otherwise sorted data for this call.

        @param hostSession HostSession The host
        session that maps to the caller, this should be used for all
        logging and provides access to the openassetio.managerAPI.Host
        object representing the process that initiated the API session.

        @return `None`
        """

    def flushCaches(self, hostSession):
        """
        Clears any internal caches.  Only applicable if the
        implementation makes use of any caching, otherwise it is a
        no-op. In caching interfaces, this should cause any retained
        data to be discarded to ensure future queries are fresh.
        """

    ## @}

    ##
    # @name Policy
    #
    # @{

    @abc.abstractmethod
    def managementPolicy(self, traitSets, context, hostSession):
        """
        Determines if the asset manager is interested in participating
        in interactions with @ref entity "entities" with the specified
        sets of @ref trait "traits".

        For example, a host may call this in order to see if the manager
        would like to manage the path of a scene file whilst choosing a
        destination to save to.

        This information is then used to determine which options should
        be presented to the user or which workflows may be performed by
        the host. For example, if `kIgnored` was returned for a query as
        to the management of scene files, a Host will hide or disable
        menu items that relate to publish or loading of assetized scene
        files, and not involve the manager in any actions realting to
        scene files.

        @warning The @fqref{Context::access} "access"
        specified in the supplied context should be carefully considered.
        A host will independently query the policy for both read and
        write access to determine if resolution and publishing features
        are applicable to this implementation.

        @note One very important attribute returned as part of this
        policy is the @ref openassetio.constants.kWillManagePath bit. If
        set, this instructs the host that the asset management system
        will manage the path use for the creation of any new assets.
        When set, @ref preflight will be called before any file creation
        to allow the asset management system to determine and prepare
        the work path. If this bit if off, then only @ref register will
        ever be called, and the user will be tasked with determining
        where new files should be located. In many cases, this greatly
        reduces the sophistication of the integration as registering the
        asset becomes a partially manual task, rather than one that can
        be fully automated for new assets.

        For read contexts, kManaged should only be returned if the
        manager can potentially resolve data for all of the supplied
        traits. Hosts are required to deal with the properties for any
        given trait being unset when resolved, as they may not be
        available for existing assets, as long as the traits are
        understood.

        For write contexts, kManaged should only be returned if the
        manager is capable of persisting all traits (and any of their
        property data) when they are registered for an entity, and
        returning that data via resolve.

        @param traitSets `List[Set[str]]` The entity @ref trait "traits"
        to query.

        @param context Context The calling context.

        @param hostSession HostSession The API session.

        @return `List[int]` Bitfields, one for each element in
        `traitSets`. See @ref openassetio.constants.
        """
        raise NotImplementedError

    ## @}

    ##
    # @name Entity Reference inspection
    #
    # Because of the nature of an @ref entity_reference, it is often
    # necessary to determine if some working string is actually an @ref
    # entity_reference or not, to ensure it is handled correctly.
    #
    # @{

    @abc.abstractmethod
    def isEntityReference(self, tokens, hostSession):
        """
        Determines if each supplied token (in its entirety) matches the
        pattern of a valid @ref entity_reference in your system.  It
        does not need to verify that it points to a valid entity in the
        system, simply that the pattern of the token is recognised by
        this implementation.

        If this returns `True`, the token is an @ref entity_reference
        and should be considered usable with the other methods of this
        interface.

        If `False`, this manager should no longer be involved in actions
        relating to the token.

        @warning The result of this call should not depend on the
        context Locale.

        @param tokens `List[str]` The strings to be inspected.

        @param hostSession HostSession The API session.

        @return `List[bool]` `True` if the supplied token should be
        considered as an @ref entity_reference, `False` if the pattern is
        not recognised.

        @note This call should not verify an entity exits, just that
        the format of the string is recognised.

        @see @ref entityExists
        @see @ref resolve
        """
        raise NotImplementedError

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

        @param entityRefs `List[str]` Entity references to query.

        @param context Context The calling context.

        @param hostSession HostSession The API session.

        @return `List[bool]` `True` if the corresponding element in
        entityRefs points to an existing entity, `False` if the entity
        is not known or ready yet.
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

    @abc.abstractmethod
    def resolve(self, entityRefs, traitSet, context, hostSession):
        """
        Returns a @fqref{TraitsData} "TraitsData"
        populated with the available data for the requested set of
        traits for each given @ref entity_reference.

        Any traits that aren't applicable to any particular entity
        reference should not be set in the resulting data. This covers
        any traits that are understood by the implementation, but not
        appliable to the entity in question, or are entirely unknown to
        the manager. Setting a trait in the result is an indication to
        the caller that that entity conceptually has that trait.

        @warning There is no requirement for a manager to populate all
        properties of known traits if appropriate data is not available.
        It is the responsibility of the caller to handle requested data
        being missing in a fashion appropriate to its intended use.

        In summary:
          - Set the trait in the result TraitsData instance for each
            entity if it is known and applicable to that entity, even if
            it has no properties or there is no data available for
            properties it does have.
          - Set the properties of each trait where possible.

        When an @ref entity_reference points to a sequence of files,
        the frame, view, etc substitution tokens should be preserved,
        and in the sprintf compatible syntax.

        This function should attempt to take into account the current
        host/Context to ensure that any other substitution tokens are
        presented in a suitable form. The Context should also be
        carefully considered to ensure that the access does not violate
        any rules of the system - for example, resolving an existing
        entity reference for write.

        The caller will have first called isEntityReference() on the
        supplied strings.

        @param entityRefs `List[str]` Entity references to query.

        @param traitSet `Set[str]` The traits to resolve for the
        supplied list of entity references.

        @param context Context The calling context.

        @param hostSession HostSession The API session.

        @return `List[Union[str,`
            exceptions.EntityResolutionError,
            exceptions.InvalidEntityReference `]]`
        A list containing either a populated TraitsData instance for
        each reference; `EntityResolutionError` if a supplied entity
        reference does not have a meaningful string representation,
        or it is a valid reference format that doesn't exist; or
        `InvalidEntityReference` if a supplied entity reference should
        not be resolved for that context, for example, if the context
        access is `kWrite` and the entity is an existing version.

        @see @ref entityExists
        @see @ref isEntityReference
        """
        raise NotImplementedError

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

        @param hostSession openassetio.managerAPI.HostSession The host
        session that maps to the caller, this should be used for all
        logging and provides access to the openassetio.managerAPI.Host
        object representing the process that initiated the API session.

        @return `List[str]` An @ref entity_reference or empty string for
        each given trait set.
        """
        return ["" for _ in traitSets]

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

    @abc.abstractmethod
    def entityName(self, entityRefs, context, hostSession):
        """
        Returns the name of each entity itself, not including any
        hierarchy or classification.

        For example:

         @li `"Cuttlefish v1"` - for a version of an asset
         @li `"seq003"` - for a sequence in a hierarchy

        @param entityRefs `List[str]` Entity references to query.

        @param context Context The calling context.

        @param hostSession openassetio.managerAPI.HostSession The host
        session that maps to the caller, this should be used for all
        logging and provides access to the openassetio.managerAPI.Host
        object representing the process that initiated the API session.

        @return `List[str]` Strings containing any valid characters for
        the manager's implementation.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def entityDisplayName(self, entityRefs, context, hostSession):
        """
        Returns an unambiguous, humanised display name for each entity.

        The display name may want to consider the host, and any other
        relevant Context information to form a display name for an
        entity that can uniquely identify the entity in that context.

        For example:

         @li `"dive / build / cuttlefish / model / v1"` - for a version
         of an asset in an 'open recent' menu.
         @li `"Sequence 003 [ Dive / Episode 1 ]"` - for a sequence in
         an hierarchy as a window title.

        @param entityRefs `List[str]` Entity references to query.

        @param context Context The calling context.

        @param hostSession openassetio.managerAPI.HostSession The host
        session that maps to the caller, this should be used for all
        logging and provides access to the openassetio.managerAPI.Host
        object representing the process that initiated the API session.

        @return `List[Union[str,` exceptions.InvalidEntityReference `]]`
        For each given entity, either a string containing any valid
        characters for the @ref asset_management_system's
        implementation; or an `InvalidEntityReference` if the supplied
        reference is not recognised by the asset management system.
        """
        raise NotImplementedError

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

        @param entityRefs `List[str]` Entity references to query.

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
        """
        return ["" for _ in entityRefs]

    def entityVersions(
            self, entityRefs, context, hostSession, includeMetaVersions=False, maxNumVersions=-1):
        """
        Retrieves all available versions of each supplied @ref
        entity_reference (including the supplied ref, if it points to a
        specific version).

        @param entityRefs `List[str]` Entity references to query.

        @param context Context The calling context.

        @param hostSession openassetio.managerAPI.HostSession The host
        session that maps to the caller, this should be used for all
        logging and provides access to the openassetio.managerAPI.Host
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

        @param entityRefs `List[str]` The entity references to finalize.

        @param context Context The calling context.

        @param hostSession openassetio.managerAPI.HostSession The host
        session that maps to the caller, this should be used for all
        logging and provides access to the openassetio.managerAPI.Host
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
        `overrideVersionName` does not exist for that entity. For
        example, if the version is missing from a reference to a
        versioned entity, and that behavior is undefined in the
        manager's model, then an `EntityResolutionError` should be
        returned. It may be that it makes sense in the specific asset
        manager to fall back on 'latest' in this case.

        @see @ref entityVersion
        @see @ref entityVersions
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
    # described as 'immediate children' of the location in question. This lay not
    # always be the case (say, for example there is some kind of 'task' structure
    # in place too). Instead we use a request that asks for any 'shots' that
    # relate to the chosen location. It is then up to the implementation of the
    # ManagerInterface to determine how that maps to its own data model.
    # Hopefully this allows Hosts of this API to work with a broader range of
    # asset managements, without providing any requirements of their structure or
    # data model.
    #
    # @{

    @abc.abstractmethod
    def getRelatedReferences(
            self, entityRefs, relationshipTraitsDatas, context, hostSession, resultTraitSet=None):
        """
        Returns related entity references, based on a relationship
        defined by a set of traits and their properties.

        This is an essential function in this API - as it is widely used
        to query organisational hierarchy, etc...

        There are three possible conventions for calling this function,
        to allow for batch optimisations in the implementation and
        prevent excessive query times with high-latency services.

         - a)  A single entity reference, a list of relationships.
         - b)  A list of entity references and a single relationship.
         - c)  Equal length lists of references and relationship.

        In all cases, the return value is a list of lists, for example:

            a)  getRelatedReferences([ r1 ], [ td1, td2, td3 ])

            > [ [ r1td1... ], [ r1td2... ], [ r1td3... ] ]

            b)  getRelatedReferences([ r1, r2, r3 ], [ td1 ])

            > [ [ r1td1... ], [ r2td1... ], [ r3td1... ] ]

            c)  getRelatedReferences([ r1, r2, r3 ], [ td1, td2, td3 ])

            > [ [ r1td1... ], [ r2td2... ], [ r3td3... ] ]

        @note The order of entities in the inner lists of matching
        references will not be considered meaningful, but the outer list
        should match the input order.

        In summary, if only a single entityRef is provided, it should be
        assumed that all relationship definitions should be considered
        for that one entity. If only a single relationship definition is
        provided, then it should be considered for all supplied entity
        references. If lists of both are supplied, then they must be the
        same length, and it should be assumed that it is a 1:1 mapping
        of a relationship definition to an entity. If this is not the
        case, ValueErrors should be thrown.

        If any relationship definition is unknown, then an empty list
        should be returned for that relationship, and no errors should
        be raised.

        @param entityRefs List[str]

        @param relationshipTraitsDatas `List[`
        @fqref{TraitsData} "TraitsData" `]`

        @param context Context The calling context.

        @param hostSession openassetio.managerAPI.HostSession The host
        session that maps to the caller, this should be used for all
        logging and provides access to the openassetio.managerAPI.Host
        object representing the process that initiated the API session.

        @param resultTraitSet `Set[str]` or None, a hint as to what
        traits the caller is expecting the returned entities to have.

        @return List[List[str]] This MUST be the correct length,
        returning an empty outer list is NOT valid. (ie: max(len(refs),
        len(relationships)))

        @exception ValueError If more than one reference and
        relationship are provided, but they lists are not equal in
        length, ie: not a 1:1 mapping of entities to relationships. The
        abstraction of this interface into the Manager class does
        cursory validation that this is the case before calling this
        function.

        @see @ref setRelatedReferences
        """
        raise NotImplementedError

    def setRelatedReferences(
            self, entityRef, relationshipTraitsData, relatedRefs,
            context, hostSession, append=True):
        """
        Creates a new relationship between the referenced entities.

        Though getRelatedReferences is an essential call, there is some
        asymmetry here, as it is not necessarily required to be able to
        setRelatedReferences directly. For example, in the case of a
        'shot' (as illustrated in the docs for getRelatedReferences) -
        any new shots would be created by registering a new entity with
        the traits of a ShotSpecification under the parent, rather than
        using this call. The best way to think of it is that this call
        is reserved for defining relationships between existing assets
        (such as connecting the script used to define a render, with the
        image sequences it creates) and 'register' as being defining the
        relationship between a new asset and some existing one.

        In systems that don't support post-creation adjustment of
        relationships, this can simply be a no-op.

        @param entityRef `str` The entity to which the relationship
        should be established.

        @param relationshipTraitsData @fqref{TraitsData} "TraitsData",
        The type of relationship to establish.

        @param relatedRefs List[str], The related entities for the
        given relationship.

        @param context Context The calling context.

        @param hostSession openassetio.managerAPI.HostSession The host
        session that maps to the caller, this should be used for all
        logging and provides access to the openassetio.managerAPI.Host
        object representing the process that initiated the API session.

        @param append bool, When True (default) new relationships will
        be added to any existing ones. If False, then any existing
        relationships with the supplied traits will first be
        removed.

        @return None

        @see @ref getRelatedReferences
        @see @ref register
        """
        if not self.entityExists(entityRef, context, hostSession):
            raise exceptions.InvalidEntityReference(entityReference=entityRef)

        for ref in relatedRefs:
            if not self.entityExists(ref, context, hostSession):
                raise exceptions.InvalidEntityReference(entityReference=ref)

    ## @}

    ##
    # @name Publishing
    #
    # The publishing functions allow a host create entities within the
    # @ref asset_management_system represented by this implementation. The API
    # is designed to accommodate the broad variety of roles that
    # different asset managers embody. Some are 'librarians' that simply
    # catalog the locations of existing media. Others take an active role
    # in both the temporary and long-term paths to items they manage.
    #
    # There are two key components to publishing within this API.
    #
    # **1 - The Entity Reference**
    #
    # As with the other entry points in this API, it is assumed that an @ref
    # entity_reference is known ahead of time. How this reference is determined
    # is beyond the scope of this layer of the API, and functions exists in
    # higher levels that combine browsing and publishing etc... Here, we simply
    # assert that there must be a meaningful reference given the @ref
    # trait_set of the entity that is being created or published.
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
    # "Traits" and their properties. The resulting @ref trait_set
    # defines the "type" of the entity, and the trait property values
    # hold the data for each specific entity.
    #
    # This means that OpenAssetIO it not just limited to working with
    # file-based data. Traits allow ancillary information to be managed
    # (such as the colorspace for an image), as well as container-like
    # entities such as shots/sequences/etc.
    #
    # For more on the relationship between Entities, Specifications and
    # traits, please see @ref entities_traits_and_specifications
    # "this" page.
    #
    # The action of 'publishing' itself, is split into two parts, depending on
    # the nature of the item to be published.
    #
    #  @li **Preflight** When a Host is about to create some new media/asset.
    #  @li **Registration** When a Host is ready to publish media that exists.
    #
    # For examples of how to correctly call these parts of the
    # API within a host, see the @ref examples page.
    #
    # @note The term '@ref publish' is somewhat loaded. It generally means
    # something different depending on who you are talking to. See the @ref
    # publish "Glossary entry" for more on this, but to help avoid confusion,
    # this API provides the @ref updateTerminology call, in order to allow the
    # implementation to standardize some of the language and terminology used in a
    # Hosts presentation of the asset management system with other integrations
    # of the system.
    #
    # @{

    def preflight(self, targetEntityRefs, traitSet, context, hostSession):
        """
        Prepares for some work to be done to create data for the
        referenced entity. The entity may not yet exist (@ref
        entity_reference). This call is designed to allow sanity
        checking, placeholder creation or any other sundry preparatory
        actions to be carried out.

        Generally, this will be called before register() in any host
        that creates media, where the return to @ref managementPolicy
        has the constants.kWillManagePath bit set.

        @param targetEntityRefs `List[str]` An @ref entity_reference
        for each entity that it is desired to publish the forthcoming
        data to. See the notes in the API documentation for the
        specifics of this.

        @param traitSet `Set(str)` The @ref trait_set of the
        entities that are being published.

        @param context Context The calling context. This is not
        replaced with an array in order to simplify implementation.
        Otherwise, transactional handling has the potential to be
        extremely complex if different contexts are allowed.

        @param hostSession HostSession The API session.

        @return `List[Union[str,`
            exceptions.PreflightError, exceptions.RetryableError `]]`
        The preflight result for each corresponding entity. If
        successful, this should be an @ref entity_reference that the
        host should resolve to determine the path to write media to.
        This may or may not be the same as the input reference. A host
        will resolve this reference to get the working URL before
        writing any files or other data. If preflight was
        unsuccessful, the result for an entity should be either a
        `PreflightError` if some fatal exception happens during
        preflight, indicating the process should be aborted; or
        `RetryableError` if any non-fatal error occurs that means the
        host should retry from the beginning of any given process.

        @note it is important for the implementation to pay attention
        to @fqref{Context::retention} "Context.retention", as not all
        hosts will support the reference changing at this point.

        @see @ref register
        """
        return targetEntityRefs

    def register(self, targetEntityRefs, entityTraitsDatas, context, hostSession):
        """
        Publish entities to the @ref asset_management_system.

        This instructs the implementation to ensure a valid entity
        exists for each given reference and to persist the data provided
        in the @fqref{TraitsData}. This will be called
        either in isolation or after calling preflight, depending on the
        nature of the data being published and the `kWillManagePath` bit
        of the returned @ref managementPolicy for the supplied data's
        @ref trait_set.

        This is an opportunity to do other things in the host as part of
        publishing if required. The context's locale will tell you more
        about the specifics of the calling application. Depending on the
        implementation of your plugin, you can use this opportunity to
        make use of the host-native SDK to extract additional
        information or schedule additional processes to produce
        derivative data.

        @param targetEntityRefs `List[str]` The @ref entity_reference
        of each entity to publish. It is up to the manager to ensure
        that this is meaningful, as it is most likely implementation
        specific. For example, if an entity with the traits of a 'Shot'
        specification is requested to be published to a reference that
        points to a 'Sequence' it makes sense to interpret this as a
        'add a shot of this spec to the sequence'. For other types of
        entity, there may be
        different constraints on what makes sense.

        @param entityTraitsDatas `List[` @fqref{TraitsData} "TraitsData"
        `]` The data for each entity (or 'asset') that is being
        published. The implementation must persist the list of traits,
        and any properties set. Such that a subsequent call to @ref
        resolve for any of these traits contains the same data. It is
        guaranteed that the trait sets of these instances are constant
        across the batch.

        @note Generally speaking, the data within a the supplied
        trait properties should be persisted verbatim. If however, the
        implementation has any specific understanding of any given
        trait, it is free to rewrite this data in any meaningful
        fashion. The simplest example of this is a `file` trait, where a
        path may be updated to the long-term persistent storage location
        of the registered data, after it has been re-located by the
        manager.

        @param context Context The calling context. This is not
        replaced with an array in order to simplify implementation.
        Otherwise, transactional handling has the potential to be
        extremely complex if different contexts are allowed.

        @param hostSession HostSession The API session.

        @return `List[Union[str,`
            exceptions.RegistrationError, exceptions.RetryableError `]]`
        The publish result for each corresponding entity. This is
        either an @ref entity_reference to the 'final' entity created
        by the publish action (which does not need to be the same as
        the corresponding entry in `targetEntityRefs`); a
        `RegistrationError` if some fatal exception happens during
        publishing, indicating the process should be aborted; or
        `RetryableError` if any non-fatal error occurs that means the
        host should retry from the beginning of any given process.

        @note it is important for the implementation to pay attention to
        @fqref{Context::retention} "retention", as not all Hosts will
        support the reference changing at this point.

        @see @fqref{TraitsData} "TraitsData"
        @see @ref preflight
        @see @ref resolve
        """
        raise NotImplementedError

    ## @}


    def persistenceTokenForState(self, state, hostSession):
        """
        Returns a string that encapsulates the current state of the
        ManagerInterface represented by the supplied state object,
        (created by @fqref{managerAPI.ManagerInterface.createState} or
        @fqref{managerAPI.ManagerInterface.createChildState}
        "createChildState") so that can be restored later, or in another
        process.

        @return `str` A string that can be used to restore the stack.

        @see @ref stateFromPersistenceToken
        """
        return ""

    def stateFromPersistenceToken(self, token, hostSession):
        """
        Restores the supplied state object to a previously persisted
        state.

        @return `object` A state object, as per createState(), except
        restored to the previous state encapsulated in the token, which
        is the same string as returned by persistenceTokenForState.

        @exception exceptions.StateError If the supplied token is not
        meaningful, or that a state has already been restored.
        """
        return None
