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

from ..managerAPI.ManagerInterface import ManagerInterface

from .._core.debug import debugApiCall, Debuggable
from .._core.audit import auditApiCall


__all__ = ['Manager']


class Manager(Debuggable):
    """
    The Manager is the Host facing representation of an @ref
    asset_management_system. The Manager class shouldn't be directly
    constructed by the host.  An instance of the class for any given
    asset management system can be retrieved from an API @ref Session,
    using the @ref openassetio.hostAPI.Session.Session.currentManager
    "Session.currentManager" method, after configuring the session with
    the appropriate manager @ref identifier.

    @code
    session = openassetio.hostAPI.Session(
        hostImpl, consoleLogger, pluginFactory)
    session.useManager("org.openassetio.test")
    manager = session.currentManager()
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
        instead use the @ref Session class, which takes care of their
        instantiation.

        @param interfaceInstance openassetio.managerAPI.ManagerInterface
        An instance of a Manager Interface to wrap.

        @param hostSession openassetio.managerAPI.HostSession the host
        session the manager is part of.
        """
        super(Manager, self).__init__()

        if not isinstance(interfaceInstance, ManagerInterface):
            raise ValueError(
                ("A manager can only be instantiated with a " +
                 "instance of the ManagerInterface or a derived class (%s)")
                % type(interfaceInstance))

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
    # asset_management_system itself. These can all be called before @ref
    # initialize has been called.
    #
    # @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def identifier(self):
        """
        Returns an identifier to uniquely identify the Manager. This
        identifier is used with the Session class to select which
        Manager to initialize, and so can be used as in preferences
        etc... to persist the chosen Manager. The identifier will use
        only alpha-numeric characters and '.', '_' or '-'. They
        generally follow the 'reverse-DNS' style, for example:

            "org.openassetio.manager.test"

        @return `str`
        """
        return self.__impl.identifier()

    @debugApiCall
    @auditApiCall("Manager methods")
    def displayName(self):
        """
        Returns a human readable name to be used to reference this
        specific asset manager in user-facing displays.
        For example:

            "OpenAssetIO Test Manager"

        @return `str`
        """
        return self.__impl.displayName()

    @debugApiCall
    @auditApiCall("Manager methods")
    def info(self):
        """
        Returns other information that may be useful about this @ref
        asset_management_system.  This can contain arbitrary key/value
        pairs.For example:

            { 'version' : '1.1v3', 'server' : 'assets.openassetio.org' }

        There is no requirement to use any of the information in the
        info dict, but it may be useful for optimisations or display
        customisation.

        There are certain well-known keys that may be set by the
        Manager. They include things such as:

          @li openassetio.constants.kField_SmallIcon (upto 32x32)
          @li openassetio.constants.kField_Icon (any size)
          @li openassetio.constants.kField_EntityReferencesMatchPrefix

        Keys will always be str, and Values will be int, bool, float or
        str.
        """
        return self.__impl.info()

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
        openassetio.hostAPI.terminology API provides more utility for
        far less effort.

        @see @ref openassetio.hostAPI.terminology "terminology"
        @see @ref openassetio.hostAPI.terminology.Mapper.replaceTerms "Mapper.replaceTerms"
        @see @ref openassetio.hostAPI.terminology.defaultTerminology "terminology.defaultTerminology"

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
    # @note Manager initialization is generally managed by the @ref Session
    # and these methods generally don't need to be called directly by
    # host code.
    #
    ## @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def getSettings(self):
        """
        @protected
        """
        return self.__impl.getSettings(self.__hostSession)

    @debugApiCall
    @auditApiCall("Manager methods")
    def setSettings(self, settings):
        """
        @protected
        """
        return self.__impl.setSettings(settings, self.__hostSession)

    @debugApiCall
    @auditApiCall("Manager methods")
    def initialize(self):
        """
        Prepares the Manager for interaction with a host. In order to
        provide light weight inspection of available Managers, initial
        construction must be cheap. However most system require some
        kind of handshake or back-end setup in order to make
        entity-related queries. As such, the @ref initialize method is
        the instruction to the Manager to prepare itself for full
        interaction.

        If an exception is raised by this call, its is safe to assume
        that a fatal error occurred, and this @ref
        asset_management_system is not available, and should be retried
        later.

        If no exception is raised, it can be assumed that the @ref
        asset_management_system is ready. It is the implementations
        responsibility to deal with transient connection errors (if
        applicable) once initialized.

        The behavior of calling initialize() on an already initialized
        Manager should be a no-op, but if an error was raised
        previously, then initialization will be re-attempted.

        @note This must be called prior to any entity-related calls or
        an Exception will be raised.

        @note This method may block for extended periods of time.

        @protected
        """
        return self.__impl.initialize(self.__hostSession)

    @debugApiCall
    @auditApiCall("Manager methods")
    def prefetch(self, references, context):
        """
        Because query latency may be high with certain managers, it is
        often desirable to 'batch' requests. However, in many cases, it
        is not always practical or desirable to adjust the flow of your
        application in order to facilitate this. The preflight call is
        designed for these situations. It should be called wherever
        possible before you make a series of calls to query information
        about multiple entities in close proximity. It gives the manager
        a chance to retrieve information in advance.

        The prefetch calls instructs the manager to retrieve any
        information needed to either resolve, or populate attributes for
        the supplied list of entities.

        The lifetime of the data is managed by the manager, as it may
        have mechanisms to auto-dirty any caches. It is *highly*
        recommended to supply a suitably managed @ref Context to this
        call, as it can be used as a cache key, so that the cache
        lifetime is inherently well-managed by your persistence (or not)
        of the context.

        @param references `List[` @ref entity_reference `]` A list of
        references to prefetch data for.

        @param context Context

        @return `None`
        """
        if not isinstance(references, (list, tuple)):
            references = [references, ]
        return self.__impl.prefetch(references, context, self.__hostSession)

    @debugApiCall
    @auditApiCall("Manager methods")
    def flushCaches(self):
        """
        Clears any internal caches.  Only applicable if the manager
        makes use of any caching, otherwise it is a no-op.  In caching
        interfaces, this should cause any retained data to be discarded
        to ensure future queries are fresh. This should have no effect
        on any open @ref transaction.
        """
        return self.__impl.flushCaches(self.__hostSession)

    ## @}

    ##
    # @name Policy
    #
    # @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def managementPolicy(self, specifications, context, entityRef=None):
        """
        Determines if the manager is interested in participating in
        interactions with the specified types of @ref entity, either
        for resolution or publishing. It is *vital* to call this before
        attempting to publish data to the manager, as the entity
        specification you desire to work with may not be supported.

        For example, you would call this in order to see if the
        manager would like to manage the path of a scene file whilst
        choosing a destination to save to.

        This information should then be used to determine which options
        should be presented to the user. For example, if kIgnored was
        returned for a query as to the management of scene files, you
        should hide or disable menu items that relate to publish or
        loading of assetized scene files.

        @warning The @ref openassetio.Context.Context.access "access"
        of the supplied context will be considered by the manager. If
        it is set to read, then it's response applies to resolution
        and @ref attributes queries. If write, then it applies to
        publishing. Ignored reads can allow optimisations in a host as
        there is no longer a need to test/resolve applicable strings.

        Calls with an accompanying @ref entity_reference should be used
        when one is known, to ensure that the manager has the
        opportunity to prohibit users from attempting to perform an
        asset-specific action that is not supported by the asset
        management system.

        @note One very important attribute returned as part of this
        policy is the @ref openassetio.constants.kWillManagePath bit. If
        set, you can assume the asset management system will manage the
        path to use for the creation of any new assets. you must then
        always call @ref preflight before any file creation to allow the
        asset management system to determine and prepare the work path,
        and then use this path to write data to, prior to calling @ref
        register. If this bit is off, then you should take care of
        writing data yourself (maybe prompting the user for a location
        on disk), and then only call @ref register to create the new
        entity.

        @param specifications `List[Specification]` Specifications to
        query.

        @param context Context The calling context.

        @param entityRef `str` If supplied, then the call should be
        interpreted as a query as to the applicability of the given
        specification if registered to the supplied entity. For example,
        attempts to register an ImageSpecification to an entity
        reference that refers to the top level project may be
        meaningless, so in this case `kIgnored` would be returned.

        @return `List[int]` Bitfields, one for each element in
        `specifications`. See @ref openassetio.constants.
        """
        return self.__impl.managementPolicy(
            specifications, context, self.__hostSession, entityRef=entityRef)

    ## @}

    ##
    # @name Entity Reference inspection
    #
    # Because of the nature of an @ref entity_reference, it is often
    # necessary to determine if some working string is actually an @ref
    # entity_reference or not, to ensure it is handled correctly.
    #
    # @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def isEntityReference(self, tokens, context):
        """
        @warning It is essential, as a host, that only valid
        references are supplied to Manager API calls. Before any
        reference is passed to any other methods of this class, they
        must first be validated through this method.

        Determines if each supplied token (in its entirety) matches the
        pattern of an @ref entity_reference.  It does not verify that it
        points to a valid entity in the system, simply that the pattern
        of the token is recognised by the manager.

        If it returns `True`, the token is an @ref entity_reference and
        should be considered as a managed entity (or a future one).
        Consequently, it should be resolved before use. It also confirms
        that it can be passed to any other method that requires an @ref
        entity_reference.

        If `False`, this manager should no longer be involved in actions
        relating to the token.

        @param tokens `List[str]` The strings to be inspected.

        @param context openassetio.Context The calling context.

        @return `List[bool]` `True` if a supplied token should be
        considered as an @ref entity_reference, `False` if the pattern
        is not recognised.

        @note This call does not verify an entity exits, just that the
        format of the string is recognised.

        @see @ref entityExists
        @see @ref resolveEntityReference

        @todo Make use of
        openassetio.constants.kField_EntityReferencesMatchPrefix if
        supplied, especially when bridging between C/python.
        """
        # We need to add support here for using the supplied prefix match string,
        # or regex, if supplied, instead of calling the manager, this is less
        # relevant in python though, more in C, but the note is here to remind us.
        return self.__impl.isEntityReference(tokens, context, self.__hostSession)

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

        @param entityRefs `List[str]` Entity references to query.

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
    def defaultEntityReference(self, specifications, context):
        """
        Returns an @ref entity_reference considered to be a sensible
        default for each of the given Specifications and Context. This
        can be used to ensure dialogs, prompts or publish locations
        default to some sensible value, avoiding the need for a user to
        re-enter such information. There may be situations where there
        is no meaningful default, so the caller should be robust to this
        situation.

        @param specifications `List[`
            specifications.EntitySpecification `]`
        The relevant specifications for the type of entities required,
        these will be interpreted in conjunction with the context to
        determine the most sensible default.

        @param context Context The context the resulting reference
        will be used in, particular care should be taken to the access
        pattern as it has great bearing on the resulting reference.

        @return `List[str]` An @ref entity_reference or empty string for
        each given specification.
        """
        return self.__impl.defaultEntityReference(specifications, context, self.__hostSession)

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
    # @see @ref attributes
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

        @param entityRefs `List[str]` Entity references to query.

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

        @param entityRefs `List[str]` Entity references to query.

        @param context Context The calling context.

        @return `List[Union[str,` exceptions.InvalidEntityReference `]]`
        For each given entity, either a string containing any valid
        characters for the @ref asset_management_system's
        implementation; or an `InvalidEntityReference` if the supplied
        reference is not recognised by the asset management system.
        """
        return self.__impl.entityDisplayName(entityRefs, context, self.__hostSession)

    @debugApiCall
    @auditApiCall("Manager methods")
    def getEntityAttributes(self, entityRefs, context):
        """
        Retrieve @ref attributes for each given entity. This may contain
        well-known attributes that you can then use to further customize
        your handling of the entity. Some types of entity may only have
        attributes, and no meaningful @ref primary_string.

        There are some well-known attribute names defined in the core
        API - see @ref openassetio.constants "constants". These have
        universally agreed meaning.

        As a host, you can also advertize well-known attribute names of
        your own as part of any first-class asset based workflows you
        may have. For example, a compositor may choose to consume the
        `colorspace` attribute (if present) and adjust the input space
        of an image reader node accordingly.

        These new attribute names should be clearly explained in your
        documentation. A manager may then be able to provide this
        information, based on introspection of your identifier (see
        @ref openassetio.managerAPI.Host.Host.identifier "Host.identifier").

        @warning See @ref setEntityAttributes for important notes on
        attributes and their role in the system.

        @param entityRefs `List[str]` Entity references to query.

        @param context Context The calling context.

        @return `List[Dict[str, primitive]]` Attributes for each entity.
        Values will be singular plain-old-data types (ie. string,
        int, float, bool), keys will be strings.
        """
        return self.__impl.getEntityAttributes(entityRefs, context, self.__hostSession)

    @debugApiCall
    @auditApiCall("Manager methods")
    def setEntityAttributes(self, entityRefs, data, context, merge=True):
        """
        Sets the supplied attributes for each given entity.

        A Manager guarantees that it will round-trip attributes, such that
        the return of @ref getEntityAttributes for attributes with those names
        will be the same as set. Managers may remap attributes internally to
        their own native names, but a set/get should be transparent.

        If any value is 'None' it should be assumed that that attribute should
        be un-set on the object.

        @param entityRefs List[str] Entity references to update.

        @param data List[dict] The attributes to set for each referenced
        entity.

        @param context Context The calling context.

        @param merge bool If true, then each entity's existing attributes
        will be merged with the new data (the new data taking
        precedence). If false, its attributes will entirely replaced by
        the new data.

        @exception ValueError if any of the attributes values are of an
        un-storable type. Presently it is only required to store str,
        float, int, bool

        @exception KeyError if any of the data keys are non-strings.
        """
        return self.__impl.setEntityAttributes(
            entityRefs, data, context, self.__hostSession, merge=merge)

    @debugApiCall
    @auditApiCall("Manager methods")
    def getEntityAttribute(self, entityRefs, name, context, defaultValue=None):
        """
        Retrieve the value of the given attribute for each given entity.

        @see @ref getEntityAttributes

        @param entityRefs `List[str]` Entity references to query.

        @param name `str` The attribute name to look up

        @param defaultValue `primitive` If not `None`, this value will
        be returned in the case of the specified name not being set for
        an entity.

        @param context Context The calling context.

        @return `Union[primitive, KeyError]` The value for the specific
        attribute, or `KeyError` if not found and no defaultValue is
        supplied.
        """
        return self.__impl.getEntityAttribute(
            entityRefs, name, context, self.__hostSession, defaultValue=defaultValue)

    @debugApiCall
    @auditApiCall("Manager methods")
    def setEntityAttribute(self, entityRefs, name, value, context):
        return self.__impl.setEntityAttribute(
            entityRefs, name, value, context, self.__hostSession)

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
    def entityVersionName(self, entityRefs, context):
        """
        Retrieves the name of the version pointed to by each supplied
        @ref entity_reference.

        @param entityRefs `List[str]` Entity references to query.

        @param context Context The calling context.

        @return `List[str]` A string for each entity representing its
        version, or an empty string if the entity was not versioned.

        @note It is not necessarily a requirement that the entity
        exists, if, for example, the version name can be determined from
        the reference itself, or is a @ref meta_version.

        @see @ref entityVersions
        @see @ref finalizedEntityVersion
        """
        return self.__impl.entityVersionName(entityRefs, context, self.__hostSession)

    @debugApiCall
    @auditApiCall("Manager methods")
    def entityVersions(self, entityRefs, context, includeMetaVersions=False, maxNumVersions=-1):
        """
        Retrieves all available versions of each supplied @ref
        entity_reference (including the supplied ref, if it points to a
        specific version).

        @param entityRefs `List[str]` Entity references to query.

        @param context Context The calling context.

        @param includeMetaVersions `bool` If `True`, @ref meta_version
        "meta-versions" such as 'latest', etc... should be included,
        otherwise, only concrete versions will be retrieved.

        @param maxNumVersions `int` Limits the number of versions
        collected for each entity. If more results are available than
        the limit, then the newest versions will be returned. If a
        value of -1 is used, then all results will be returned.

        @return `List[Dict[str, str]]` A dictionary for each entity,
        where the keys are string versions, and the values are an
        @ref entity_reference that points to its entity. Additionally
        the openassetio.constants.kVersionDict_OrderKey can be set to
        a list of the version names (ie: dict keys) in their natural
        ascending order, that may be used by UI elements, etc.

        @see @ref entityVersionName
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

        @param entityRefs `List[str]` Entity references to query.

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

        @see @ref entityVersionName
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
    # In the this API, these relationships are represented by a generic
    # Specification, this may just be a 'type', but can additionally have
    # arbitrary attributes to further define the relationship. For example in
    # the case of AOVs, the type might be 'alternate output' and the
    # attributes may be that the 'channel' is 'diffuse'.
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
    def getRelatedReferences(self, references, relationshipSpecOrSpecs, context, resultSpec=None):
        """
        Returns related entity references, based on a relationship
        specification.

        This is an essential function in this API - as it is widely used
        to query organisational hierarchy, etc...

        There are three possible conventions for calling this function,
        to allow for batch optimisations in the implementation and
        prevent excessive query times with high-latency services.

          a)  A single entity reference, a list of specifications.
          b)  A list of entity references and a single specification.
          c)  Equal length lists of references and specifications.

        In all cases, the return value is a list of lists, for example:

            a)  getRelatedReferences([ r1 ], [ s1, s2, s3 ])

            > [ [ r1s1... ], [ r1s2... ], [ r1s3... ] ]

            b)  getRelatedReferences([ r1, r2, r3 ], [ s1 ])

            > [ [ r1s1... ], [ r2s1... ], [ r3s1... ] ]

            c)  getRelatedReferences([ r1, r2, r3 ], [ s1, s2, s3 ])

            > [ [ r1s1... ], [ r2s2... ], [ r3s3... ] ]

        @note The order of entities in the inner lists of matching
        references should not be considered meaningful, but the outer
        list should match the input order.

        In summary, if only a single entityRef is provided, it should be
        assumed that all specs should be considered for that one entity.
         If only a single relationshipSpec is provided, then it should
        be considered for all supplied entity references. If lists of
        both are supplied, then they must be the same length, and it
        should be assumed that it is a 1:1 mapping of spec per entity.
        If this is not the case, ValueErrors will be thrown.

        If any specification is unknown, then an empty list will be
        returned for that specification, and no errors should be raised.

        @param references List[str] A list of @ref entity_reference, see
        the notes on array length above.

        @param relationshipSpecOrSpecs
        List[openassetio.specifications.RelationshipSpecification]

        @param resultSpec openassetio.specifications.EntitySpecification
        or None, a hint as to what kind of entity you want to be
        returned. May be None.

        @param context Context The calling context.

        @return list of str lists The return is *always* a list of lists
        regardless of which form of invocation is used. The outer list
        is for each supplied entity or specification. The inner lists
        are all the matching entities for that source entity.

        @exception ValueError If more than one reference and
        specification is provided, but they lists are not equal in
        length, ie: not a 1:1 mapping of entities to specs.

        @see @ref openassetio.specifications "specifications"
        @todo Implement missing setRelatedReferences()
        """
        if not isinstance(references, (list, tuple)):
            references = [references, ]

        if not isinstance(relationshipSpecOrSpecs, (list, tuple)):
            relationshipSpecOrSpecs = [relationshipSpecOrSpecs, ]

        numEntities = len(references)
        numSpecs = len(relationshipSpecOrSpecs)

        if (numEntities > 1 and numSpecs > 1) and numSpecs != numEntities:
            raise ValueError(
                ("You must supply either a single entity and a "
                 + "list of specs, a single spec and a list of entities, or an equal "
                 + "number of both... %s entities .vs. %s specs")
                % (numEntities, numSpecs))

        result = self.__impl.getRelatedReferences(
            references,
            relationshipSpecOrSpecs, context, self.__hostSession, resultSpec=resultSpec)

        return result

    ## @}

    ##
    # @name Entity Resolution
    #
    # The concept of resolution is turning an @ref entity_reference into a
    # 'finalized' or 'primary' string. This, ultimately, is anything meaningful
    # to the situation. It could be a color space, a directory, a script or
    # image sequence. A rule of thumb is that a resolved @ref entity_reference
    # should be the string you would have anyway, in a unmanaged environment.
    #
    # Some kinds of entity - for example, a 'Shot' - may not have a meaningful
    # @ref primary_string, and so an empty string will be returned.
    # In these cases, it is more likely that the information required (eg.
    # a working frame range) is obtained through calling @ref getEntityAttributes.
    # The dictionary returned from this method should then contain well-known
    # keys for this information.
    #
    # @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def resolveEntityReference(self, entityRefs, context):
        """
        Returns the @ref primary_string represented by each given @ref
        entity_reference.

        When an @ref entity_reference points to a sequence of files,
        the frame, view, etc substitution tokens will be preserved
        and need handling as if OpenAssetIO was never involved.

        @note You should always call @ref isEntityReference first if
        there is any doubt as to whether or not a string you have is a
        valid reference for the manager, and only call resolve, or any
        other methods, if it is a reference recognised by the manager.

        The API defines that all file paths passed though the API that
        represent file sequences should use the 'format' syntax,
        compatible with sprintf (eg.  %04d").

        @param entityRefs `List[str]` Entity references to query.

        @param context Context The calling context.

        @return `List[Union[str,`
            exceptions.EntityResolutionError,
            exceptions.InvalidEntityReference `]]`
        A list containing either the primary string for each
        reference; `EntityResolutionError` if a supplied entity
        reference does not have a meaningful string representation,
        or it is a valid reference format that doesn't exist; or
        `InvalidEntityReference` if a supplied entity reference should
        not be resolved for that context, for example, if the context
        access is `kWrite` and the entity is an existing version  - the
        exception means that it is not a valid action to perform on
        the entity.
        """
        return self.__impl.resolveEntityReference(entityRefs, context, self.__hostSession)

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
    # assert that there must be a meaningful reference given the @ref
    # Specification of the entity that is being created or published.
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
    # *2 - The Specification*
    #
    # The Specification allows ancillary information to be provided to help the
    # implementation better interpret what type of entity may be best suited in
    # any given situation. For example, a path to an image will generally be
    # accompanied by with an spec, that details the file type, color space,
    # resolution etc...
    #
    # @note The Specification should *not* be confused with @ref attributes.  The
    # manager will not directly store any information contained within the
    # Specification, though it may be used to better define the type of entity.
    # If you wish to persist other properties of the published entity, you must
    # call @ref setEntityAttributes() directly instead, and as described in the
    # attributes section, this is assumed that this is the channel for information
    # that needs to be stored by the manager.
    #
    # For more on the relationship between Entities, Specifications and
    # attributes, please see @ref entities_specifications_and_attributes
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
    def preflight(self, targetEntityRefs, entitySpecs, context):
        """
        @note This call is only applicable when the manager you are
        communicating with sets the constants.kWillManagePath bit in
        response to a @ref Manager.managementPolicy for the
        specification of entity you are intending to publish.

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
        in particular the @ref openassetio.Context.Context.retention
        "Context.retention".

        @warning The working @ref entity_reference returned by this
        method should *always* be used in place of the original
        reference supplied to `preflight` for resolves or attributes
        queries prior to registration, and for the final call to @ref
        register itself. See @ref example_publishing_a_file.

        @param targetEntityRefs `List[str]` The entity references to
        preflight prior to registration.

        @param entitySpecs `List[`
            specifications.EntitySpecification `]`
        A description of each entity that is being published.

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

        @exception `IndexError` If `targetEntityRefs` and `entitySpecs`
        are not lists of the same length.

        @see @ref register
        """
        if len(targetEntityRefs) != len(entitySpecs):
            raise IndexError("Parameter lists must be of the same length")

        return self.__impl.preflight(targetEntityRefs, entitySpecs, context, self.__hostSession)

    @debugApiCall
    @auditApiCall("Manager methods")
    def register(self, primaryStrings, targetEntityRefs, entitySpecs, context, attributes=None):
        """
        Register should be used to register new entities either when
        originating new data within the application process, or
        referencing some existing file, media or information.

        @note The registration call is applicable to all kinds of
        Manager, as long as the @ref constants.kIgnored bit is not set
        in response to a @ref Manager.managementPolicy for the
        Specification of entity you are intending to publish. In this
        case, the Manager is saying it doesn't handle that
        Specification of entity, and it should not be registered.

        As each @ref entity_reference has (ultimately) come from the
        manager (either in response to delegation of UI/etc... or as a
        return from another call), then it can be assumed that the
        Manager will understand what it means for you to call `register`
        on this reference with the supplied Specification. The
        conceptual meaning of the call is:

        "I have this reference you gave me, and I would like to
        register a new entity to it with this Specification, to hold
        the supplied primary string. I trust that this is ok, and you
        will give me back the reference that represents the result of
        this."

        It is up to the manager to understand the correct result for the
        particular Specification in relation to this reference. For
        example, if you received this reference in response to browsing
        for a target to `kWriteMultiple` `ShotSpecification`s, then the
        Manager should have returned you a reference that you can then
        call register() on multiple times with a `ShotSpecification`
        without error. Each resulting entity reference should then
        reference the newly created Shot.

        @warning When registering files, it should never be assumed
        that the resulting @ref entity_reference will resolve to the
        same path. Managers may freely relocate, copy, move or rename
        files as part of registration.

        @param targetEntityRefs `List[str]` Entity references to publish.

        @param primaryStrings `List[str]` The @ref primary_string for
        each entity. It is the string the resulting @ref
        entity_reference will resolve to. In the case of file-based
        entities, this is the file path, and may be further modified
        by Managers that take care of relocating or managing the
        storage of files. The API defines that in the case of paths
        representing file sequences, frame tokens should be left
        un-substituted, in a sprintf compatible format, eg. "%04d",
        rather than say, the #### based method. If your application
        uses hashes, or some other scheme, it should be converted
        to/from the sprintf format as part of your integration.

        @param entitySpecs `List[`
            specifications.EntitySpecification `]`
        The `EntitySpecification` for each new registration.

        @param context Context The calling context.

        @param attributes `List[Union[Dict[str, primitive], None]`
        Optional attributes to set during publish.

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

        @exception `IndexError` If `primaryStrings`, `targetEntityRefs`
        and `entitySpecs` are not lists of the same length.

        @see @ref openassetio.specifications "specifications"
        @see @ref preflight
        @see @ref setEntityAttributes
        """
        ## At the mo, attributes are deliberately not passed to register in the
        ## ManagerInterface. This helps ensure that no Manager ever places a
        ## requirement that attributes is known on creation. This is a bad state to
        ## be in, as it places severe limitations on a host so its worth leaving it
        ## this way so people will moan at us if its a problem.
        ## @todo ... but conversely, setAttributes doesn't allow that data to be versioned
        ## This needs revisiting, as its not even really 'attributes' as we encourage
        ## hosts to treat it as first-class asset data.
        if (len(primaryStrings) != len(targetEntityRefs) or
                len(primaryStrings) != len(entitySpecs) or
                attributes is not None and len(primaryStrings) != len(attributes)):
            raise IndexError("Parameter lists must be of the same length")

        entityRefs = self.__impl.register(
            primaryStrings, targetEntityRefs, entitySpecs, context, self.__hostSession)
        if attributes and entityRefs:
            self.__impl.setEntityAttributes(
                entityRefs, attributes, context, self.__hostSession, merge=True)
        return entityRefs

    ## @}

    ##
    # @name Transaction management
    # These methods should not be used directly outside of the core API code.
    # Always use a @ref openassetio.hostAPI.transactions.TransactionCoordinator
    # instead.
    ## @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def _startTransaction(self, state):
        """
        @see @ref openassetio.managerAPI.ManagerInterface.ManagerInterface.startTransaction "startTransaction"
        """
        return self.__impl.startTransaction(state, self.__hostSession)

    @debugApiCall
    @auditApiCall("Manager methods")
    def _finishTransaction(self, state):
        """
        @see @ref openassetio.managerAPI.ManagerInterface.ManagerInterface.finishTransaction "finishTransaction"
        """
        return self.__impl.finishTransaction(state, self.__hostSession)

    @debugApiCall
    @auditApiCall("Manager methods")
    def _cancelTransaction(self, state):
        """
        @see @ref openassetio.managerAPI.ManagerInterface.ManagerInterface.cancelTransaction "cancelTransaction"
        """
        return self.__impl.cancelTransaction(state, self.__hostSession)

    ## @}

    ##
    # @name State Management
    # These methods should not be used directly outside of the core API code.
    # Always use a @ref openassetio.hostAPI.transactions.TransactionCoordinator
    # instead.
    ## @{

    @debugApiCall
    @auditApiCall("Manager methods")
    def _createState(self, parentState=None):
        """
        @see @ref openassetio.managerAPI.ManagerInterface.ManagerInterface.createState "ManagerInterface.createState"
        """
        return self.__impl.createState(self.__hostSession, parentState=parentState)

    @debugApiCall
    @auditApiCall("Manager methods")
    def _freezeState(self, state):
        """
        @see @ref openassetio.managerAPI.ManagerInterface.ManagerInterface.freezeState "ManagerInterface.freezeState"
        """
        return self.__impl.freezeState(state, self.__hostSession)

    @debugApiCall
    @auditApiCall("Manager methods")
    def _thawState(self, token):
        """
        @see @ref openassetio.managerAPI.ManagerInterface.ManagerInterface.thawState "ManagerInterface.thawState"
        """
        return self.__impl.thawState(token, self.__hostSession)

    ## @}
