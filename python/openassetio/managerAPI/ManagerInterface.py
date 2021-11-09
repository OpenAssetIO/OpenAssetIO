#
#   Copyright 2013-2021 [The Foundry Visionmongers Ltd]
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

import abc
from .. import exceptions


__all__ = ['ManagerInterface', ]


class ManagerInterface(object):
    """
    @brief This Interface binds a @ref asset_management_system into
    OpenAssetIO. It is not called directly by a @ref host, but by the
    middle-ware that presents a more object-oriented model of this to
    the @ref host - namely, the @ref openassetio.hostAPI.Manager.

    It is structured around the following principals:

      @li The currency of the API is either data, or an @ref
      entity_reference. objects should not be used to represent an @ref
      entity or its properties.

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

    @important Your plugin may be hosted out of process, or even on
    another machine, the HostSession bridge takes care of relaying
    messages accordingly. Using custom logging mechanisms may well
    result in output being lost.

    @see openassetio.managerAPI.HostSession.HostSession.log
    @see openassetio.managerAPI.HostSession.HostSession.progress

    Exceptions should be thrown to handle any in-flight errors that
    occur.  The error should be mapped to a derived class of
    openassetio.exceptions.BaseException, and thrown.  All exceptions of
    this kind, will be correctly passed across the plug-in C boundary,
    and re-thrown. Other exceptions should not be used.

     @see openassetio.exceptions

    Threading
    ---------
    Any implementation of the ManagerInterface should be thread safe.
    The one exception being Manager::initialize, this will never be
    called concurrently.

    When a @ref openassetio.Context object is constructed by @ref
    openassetio.hostAPI.Session.Session.createContext, the @ref
    createState method will be called, and the resulting state object
    stored in the context. This context will then be re-used across
    related API calls to your implementation of the ManagerInterface.
    You can use this to determine which calls may be part of a specific
    'action' in the same host, or logically grouped processes such as a
    batch render. This should allow you to implement stable resolution
    of @ref meta_version "meta-versions" or other resolve-time concepts.

    One exception to the treading rule is that the transaction managing
    functions won't be called from multiple threads with the same
    transaction object.

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

    @see openassetio.managerAPI.Host

    Initialization
    --------------

    The constructor makes a new instance, but at this point it is not
    ready for use. Instances of this class should be light weight to
    create, but don't have to be lightweight to initialize. The
    informational methods must be available pre-initialization, so that
    UI and other display-type queries can be made relatively cheaply to
    provide users with a list of managers and their settings. None of
    the entity-related methods will be called until after @ref
    initialize has been called. The following methods must be callable
    prior to initialization:

       @li @ref getIdentifier()
       @li @ref getDisplayName()
       @li @ref getInfo()
       @li @ref localizeStrings()
       @li @ref getSettings()
       @li @ref setSettings()

    @todo Finish/Document settings mechanism.
    @see initialize()
    """

    __metaclass__ = abc.ABCMeta

    # Test harness methods.
    #
    # It is difficult to derive generic tests for the API, as they need sample
    # entity references to use in the calls.
    #
    # As such, we introduce optional methods here, that are required to support
    # the various tests in test/TestCases/Core. If this are not implemented, then
    # you will not be able to test the implementation using these tests.

    # def _test_getReference(self, specification):
    #  """
    #
    #  Returns an @ref entity_reference that can be used for testing purposes, the
    #  specification will be a TestEntitySpecification. The current test can be
    #  queried using specification.testName(). Some tests require a reference to
    #  an existing entity, so specification.shouldExist() should be respected.
    #  Additionally specification.embeddable() can be queried to determine if the
    #  ref will be used in isolation, or may be embedded in a more complex
    #  string.
    #
    #  """

    # def _test_cleanup(self, references)
    #  """
    #
    #  Called by the test harness to clean up any references that it requested.
    #  This is called after any test that has requested a reference completes.
    #  You could use this to remove any temporary database entries, etc... that
    #  were necessary to satisfy a request for a reference to an 'existing'
    #  asset.
    #
    #  """

    ##
    # @name Asset Management System Information
    #
    # These functions provide hosts with general information about the @ref
    # asset_management_system itself.
    #
    # @{

    @abc.abstractmethod
    def getIdentifier(self):
        """
        Returns an identifier to uniquely identify a specific asset
        manager. This may be used by a host to persist the users
        preferred manager via a preferences mechanism, or when spawning
        child processes, etc...

        It should match the name used to register the plug-in with the
        plug-in host.  The identifier should use only alpha-numeric
        characters and '.', '_' or '-'.  Generally speaking, we
        recommend using the 'reverse-DNS' convention, for example:

            "org.openassetio.manager.test"

        @return str
        """
        raise NotImplementedError

    @abc.abstractmethod
    def getDisplayName(self):
        """
        Returns a human readable name to be used to reference this
        specific asset manager in UIs or other user-facing messaging.
        One instance of its use may be in a host's preferences UI or
        logging. For example:

            "OpenAssetIO Test Asset Manager"
        """
        raise NotImplementedError

    def getInfo(self):
        """
        Returns other information that may be useful about this @ref
        asset_management_system. This can contain arbitrary key/value
        pairs.For example:

            { 'version' : '1.1v3', 'server' : 'assets.openassetio.org' }

        There are certain optional keys that may be used by a host or
        the API:

          @li openassetio.constants.kField_SmallIcon (upto 32x32)
          @li openassetio.constants.kField_Icon (any size)

        Because it can often be expensive to bridge between languages,
        info can also contain one of two additional fields - a prefix,
        or perl regex compatible string to identify a valid entity
        reference. Only one should be set at once. If supplied, this may
        be used by the API to optimise calls to isEntityReference when
        bridging between C/Python etc... can be slow. If neither of
        these fields are set, then isEntityReference will always be used
        to determine if a string is an @ref entity_reference or not.
        Note, not all hosts support this optimisation, so @ref
        isEntityReference should be implemented regardless.

          @li openassetio.constants.kField_EntityReferencesMatchPrefix
          @li openassetio.constants.kField_EntityReferencesMatchRegex

        @note Keys should always be strings, and values must be
        plain-old-data types (ie: str, int, float, bool).
        """
        return {}

    def localizeStrings(self, stringDict, hostSession):
        """
        This call gives the manager a chance to customise certain
        strings used in a host's UI/messages. @see openassetio.constants
        for known keys. The values in stringDict can be freely updated
        to match the terminology of the asset management system you are
        representing.

        For example, you may way a host's "Publish Clip" menu item to
        read "Release Clip", so you would set the @ref
        kLocalizationKey_Publish value to "Release".

        @return None

        @see @ref openassetio.constants
        @see @ref openassetio.hostAPI.localization.defaultTerminology
        """
        pass

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
        pass

    @abc.abstractmethod
    def initialize(self, hostSession):
        """
        Prepares for interaction with a host.

        This is a good opportunity to initialize any persistent
        connections to a back end implementation, as @ref setSettings
        will have already been called (if applicable). It is fine for
        this call to block for a period of time.

        If an exception is raised by this call, it signifies to the host
        that a fatal error occurred, and this @ref
        asset_management_system is not available with the current
        settings.

        If no exception is raised, it can be assumed that the @ref
        asset_management_system is ready. It is the implementations
        responsibility to deal with transient connection errors (if
        applicable) once initialized.

        The behaviour of calling initialize() on an already initialized
        instance should be a no-op, but if an error was raised
        previously, then initialization should be re-attempted.

        @note This will always be called prior to any Entity-related
        calls. An exception should be raised if this is not the case. It
        is however, the following functions may be called prior to
        initialization:

         @li @ref getIdentifier()
         @li @ref getDisplayName()
         @li @ref getInfo()
         @li @ref localizeStrings()
         @li @ref getSettings()
         @li @ref setSettings()

        @todo We need a 'teardown' method to, before a manager is
        de-activated in a host, to allow any event registrations etc...
        to be removed.
        """
        raise NotImplementedError

    def prefetch(self, entitRefs, context, hostSession):
        """
        Called by a host to express interest in the supplied @ref
        entity_reference list. This usually means that the host is about
        to make multiple queries to the same references.  This can be
        left unimplemented, but it is advisable to batch request the
        data for resolveEntityReference, getEntityMetadata here if
        possible.

        The implementation should ignore any entities to which no action
        is applicable (maybe as they don't exist yet).

        @warning Because the majority of the resolution API itself is
        designated thread safe, it is important to implement any
        pre-fetch mechanism with suitable locks/etc... if required.

        @param context openassetio.Context, You may wish to make use of
        the managerInterfaceState object (if you supplied one on
        construction of the context), to simplify scoping any caching of
        data. Otherwise, it's up to you how to manage the lifetime of
        the data to avoid inconsistencies, but the @ref flushCaches
        method should clear any otherwise sorted data for this call.

        @return None
        """
        pass

    def flushCaches(self, hostSession):
        """
        Clears any internal caches.  Only applicable if the
        implementation makes use of any caching, otherwise it is a
        no-op. In caching interfaces, this should cause any retained
        data to be discarded to ensure future queries are fresh. This
        should have no effect on any open @ref transaction.
        """
        pass

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
    def isEntityReference(self, token, context, hostSession):
        """
        Determines if a supplied token (in its entirety) matches the
        pattern of a valid @ref entity_reference in your system.  It
        does not need to verify that it points to a valid entity in the
        system, simply that the pattern of the token is recognised by
        this implementation.

        If this returns True, the token is an @ref entity_reference and
        should be considered usable with the other methods of this
        interface.

        If false, this manager should no longer be involved in actions
        relating to the token.

        @warning The result of this call should not depend on the
        context Locale.

        @param token The string to be inspected.

        @param context openassetio.Context, The calling context.

        @return bool, True if the supplied token should be considered as
        an @ref entityReference, False if the pattern is not recognised.

        @note This call should not verify the entity exits, just that
        the format of the string is recognised.

        @see entityExists()
        @see resolveEntityReference()
        """
        raise NotImplementedError

    @abc.abstractmethod
    def entityExists(self, entityRef, context, hostSession):
        """
        Called to determine if the supplied @ref entity_reference points
        to an entity that does exist in the @ref
        asset_management_system, and that it can be resolved into a
        meaningful string or otherwise queried.

        By 'exist' we mean 'is ready to be read'. For example,
        entityExists may be called before attempting to read from a
        reference that is believed to point to an image sequence, so
        that alternatives can be found.

        In the future, this may need to be extended to cover a more
        complex definition of 'existence' (for example, known to the
        system, but not yet finalized). For now however, it should be
        assumed to simply mean, 'ready to be consumed', and if only a
        placeholder or un-finalized asset is available, False should be
        returned.

        The supplied context's locale may contain information pertinent
        to disambiguating this subtle definition of 'exists' in some
        cases too, as it better explains the use-case of the call.

        @return bool, True if it points to an existing entity, False if
        the entity is not known or ready yet.
        """
        raise NotImplementedError

    ## @}

    ##
    # @name Entity Reference Resolution
    #
    # The concept of resolution is turning an @ref entity_reference into a
    # 'finalized' string. This, ultimately, is anything meaningful to the
    # situation. It could be a colour space, a directory, a script or image
    # sequence. A rule of thumb is that a resolved @ref entity_reference
    # should be the string that the application would have anyway, in a
    # unmanaged environment. For some kind of Entity - such as a 'Shot', for
    # example, there may not be a meaningful string, though often some sensible
    # value can be returned.
    #
    # @{

    @abc.abstractmethod
    def resolveEntityReference(self, entityRef, context, hostSession):
        """
        Returns the 'finalized' string represented by the @ref
        entity_reference.

        If the string points to some data, then it should always be in
        the form of a valid URL. File paths should be returned as a
        <tt>file</tt> scheme URL.

        When the @ref entity_reference points to a sequence of files,
        the frame token should be preserved, and in the sprintf
        compatible syntax.

        This function should attempt to take into account the current
        host/Context to ensure that any other substitution tokens are
        presented in a suitable form. The Context should also be
        carefully considered to ensure that the access does not violate
        any rules of the system - for example, resolving an existing
        entity reference for write.

        The caller will have first called isEntityReference() on the
        supplied string.

        @note You may need to call getFinalizedEntityVersion() within
        this function to ensure any @ref meta_version "meta-versions"
        are resolved prior to resolution.

        @return str, The string that that is represented by the
        reference.

        @exception openassetio.exceptions.EntityResolutionError If the
        supplied @ref entity_reference does not have a meaningful string
        representation, or it is a valid reference format, that doesn't
        exist.
        @exception openassetio.exceptions.InvalidEntityReference if the
        supplied entity_reference should not be resolved for that
        context, for example, if the context access is kWrite and the
        entity is an existing version - raising will ensure that a Host
        will not attempt to write to that location.

        @see entityExists()
        @see isEntityReference()
        @see resolveEntityReferences()
        """
        raise NotImplementedError

    def resolveEntityReferences(self, references, context, hostSession):
        """
        Batch-resolves a list of @ref entity_reference
        "entity references", following the same pattern as @ref
        resolveEntityReference.

        @return List[str], A list of strings, corresponding to the
        source reference with the same index.

        This will be called by hosts when they wish to batch-resolve
        many references with an eye to performance, or server hits, and
        so should be re-implemented to minimise the number of queries
        over a standard 'for' loop.

        The base class implementation simply calls
        resolveEntityReference repeatedly for each supplied reference.
        """
        resolved = []
        for r in references:
            resolved.append(self.resolveEntityReference(r, context, hostSession))
        return resolved

    def getDefaultEntityReference(self, specification, context, hostSession):
        """
        Returns an @ref entity_reference considered to be a sensible
        default for the given specification and Context. This is often
        used in a host to ensure dialogs, prompts or publish locations
        default to some sensible value, avoiding the need for a user to
        re-enter such information when a Host is being run in some known
        environment.

        For example, a host may request the default ref for
        'ShotSpecification/kWriteMultiple'. If the Manager has some
        concept of the 'current sequence' it may wish to return this so
        that a 'Create Shots' starts somewhere meaningful.

        @return str, A valid @ref entity_reference, or empty string.
        """
        return ''

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
    # @see @ref metadata
    #
    # @{

    @abc.abstractmethod
    def getEntityName(self, entityRef, context, hostSession):
        """
        Returns the name of the entity itself, not including any
        hierarchy or classification.

        For example:

         @li `"Cuttlefish v1"` - for a version of an asset
         @li `"seq003"` - for a sequence in a hierarchy

        @return str, A string containing any valid characters for the
        manager's implementation.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def getEntityDisplayName(self, entityRef, context, hostSession):
        """
        Returns an unambiguous, humanised display name for the entity.

        The display name may want to consider the host, and any other
        relevant Context information to form a display name for an
        entity that can uniquely identify the entity in that context.

        For example:

         @li `"dive / build / cuttlefish / model / v1"` - for a version
         of an asset in an 'open recent' menu.
         @li `"Sequence 003 [ Dive / Episode 1 ]"` - for a sequence in
         an hierarchy as a window title.

        @return str, A string containing any valid characters for the
        @ref asset_management_system's implementation.

        @exception openassetio.exceptions.InvalidEntityReference If any
        supplied reference is not recognised by the asset management
        system.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def getEntityMetadata(self, entityRef, context, hostSession):
        """
        Retrieve @ref metadata for an entity.

        It may be required to bridge between certain 'first-class'
        properties of your asset management system and the well-known
        keys in the metadata dictionary. For example, if the asset
        system represents a 'Shot' with 'cutIn' and 'cutOut' properties
        or accessors, these should be remapped to the @ref
        openassetio.constants.kField_FrameIn/Out metadata keys as
        appropriate.

        @warning See @ref setEntityMetadata for important notes on
        metadata and its role in the system.

        @return Dict[str,primitive], with the entity's metadata. Values
        must be singular plain-old-data types (ie. string, int, float,
        bool), keys must be strings.
        """
        raise NotImplementedError

    def setEntityMetadata(self, entityRef, data, context, hostSession, merge=True):
        """
        Sets an entities metadata.

        @param merge, bool If true, then the entity's existing metadata
        will be merged with the new data (the new data taking
        precedence). If false, its metadata will entirely replaced by
        the new data.

        @note It is a vital that the implementation faithfully stores
        and recalls metadata. It is the underlying mechanism by which
        hosts may round-trip non file-based entities within this API.
        Specific key names and value types should be maintained, even if
        they are re-mapped to an internal name for persistence.

        If any value is 'None' it should be assumed that that key should
        be un-set on the object.

        @exception ValueError if any of the metadata values are of an
        un-storable type. Presently it is only required to store str,
        float, int, bool
        """
        raise NotImplementedError

    def getEntityMetadataEntry(self, entityRef, key, context, hostSession, defaultValue=None):
        """
        Returns the value for the specified metadata key.

        @see getEntityMetadata

        @param key str, The key to look up
        @param defaultValue primitive, If not None, this value will be
        returned in the case of the specified key not being set for the
        entity.

        @return primitive, The value for the specific key.

        @exception KeyError If no defaultValue is supplied, and the
        entity has no metadata for the specified key.

        The default implementation retrieves all metadata for an entity
        and extracts the requested key.
        """
        value = defaultValue
        try:
            value = self.getEntityMetadata(entityRef, context, hostSession)[key]
        except KeyError:
            if defaultValue is None:
                raise
        return value

    def setEntityMetadataEntry(self, entityRef, key, value, context, hostSession):
        self.setEntityMetadata(entityRef, {key: value}, context, hostSession, merge=True)

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

    def getEntityVersionName(self, entityRef, context, hostSession):
        """
        Retrieves the name of the version pointed to by the supplied
        @ref entity_reference.

        @return str, A string representing the version or an empty
        string if the entity was not versioned.

        @note It is not necessarily a requirement that the entity
        exists, if, for example, the version name can be determined from
        the reference itself (in systems that implement a human-readable
        url, for example)

        @see getEntityVersions()
        @see getFinalizedEntityVersion()
        """
        return ""

    def getEntityVersions(
            self, entityRef, context, hostSession, includeMetaVersions=False, maxResults=-1):
        """
        Retrieves all available versions of the supplied @ref
        entity_reference (including the supplied ref, if it points to a
        specific version).

        @param includeMetaVersions bool, if true, @ref meta_version
        "meta-versions" such as 'latest', etc... should be included,
        otherwise, only concrete versions need to be returned.

        @param maxResults int, Limits the number of results collected,
        if more results are available than the limit, then the newest
        versions should be returned. If a value of -1 is used, then all
        results should be returned.

        @return Dict[str,str], Where the keys are string versions, and
        the values are an @ref entity_reference that points to that
        versions entity. Additionally the
        openassetio.constants.kVersionDict_OrderKey can be set to a list
        of the version names (ie: dict keys) in their natural ascending
        order, that may be used by UI elements, etc...

        @see getEntityVersionName()
        @see getFinalizedEntityVersion()
        """
        return {}

    def getFinalizedEntityVersion(self, entityRef, context, hostSession, overrideVersionName=None):
        """
        Retrieves an @ref entity_reference that points to the concrete
        version of a @ref meta_version or otherwise unstable @ref
        entity_reference.

        If the supplied entity reference is not versioned, or already
        has a concrete version, the input reference should be
        passed-through.

        If versioning is unsupported for the given @ref
        entity_reference, then the input reference should be returned.

        @param overrideVersionName str If supplied, then the call should
        return the entity reference for the version of the referenced
        asset that matches the name specified here, ignoring any version
        inferred by the input reference.

        @return str

        @exception openassetio.exceptions.EntityResolutionError should
        be thrown if the entityReference is ambiguously versioned (for
        example if the version is missing from a reference to a
        versioned entity, and that behaviour is undefined in the system
        managers model. It may be that it makes sense in the specific
        asset manager to fall back on 'latest' in this case...)

        @exception openassetio.exceptions.EntityResolutionError if the
        supplied overrideVersionName does not exist for that entity.

        @see getEntityVersionName()
        @see getEntityVersions()
        """
        return entityRef

    ## @}

    ##
    # @name Related Entities
    #
    # A 'related' entity could take many forms. For example:
    #
    #  @li In 3D CGI, Multiple @ref aovs may be related to a 'beauty' render.
    #  @li In Compositing, an image sequence may be related to the script
    #  that created it.
    #  @li An asset may be related to a task that specifies work to be done.
    #  @li Parent/child relationships are also (semantically) covered by
    #  these relationships.
    #
    # In the this API, these relationships are represented by a generic
    # Specification, this may just be a 'type', but can additionally have
    # arbitrary attributes to further define the relationship. For example in
    # the case of @ref aovs, the type might be 'alternate output' and the
    # attributes may be that the 'channel' is 'diffuse'.
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
            self, entityRefs, relationshipSpecs, context, hostSession,
            resultSpec=None):
        """
        Returns related entity references, based on a relationship
        specification.

        This is an essential function in this API - as it is widely used
        to query organisational hierarchy, etc...

        There are three possible conventions for calling this function,
        to allow for batch optimisations in the implementation and
        prevent excessive query times with high-latency services.

         - a)  A single entity reference, a list of specifications.
         - b)  A list of entity references and a single specification.
         - c)  Equal length lists of references and specifications.

        In all cases, the return value is a list of lists, for example:

            a)  getRelatedReferences([ r1 ], [ s1, s2, s3 ])

            > [ [ r1s1... ], [ r1s2... ], [ r1s3... ] ]

            b)  getRelatedReferences([ r1, r2, r3 ], [ s1 ])

            > [ [ r1s1... ], [ r2s1... ], [ r3s1... ] ]

            c)  getRelatedReferences([ r1, r2, r3 ], [ s1, s2, s3 ])

            > [ [ r1s1... ], [ r2s2... ], [ r3s3... ] ]

        @note The order of entities in the inner lists of matching
        references will not be considered meaningful, but the outer list
        should match the input order.

        In summary, if only a single entityRef is provided, it should be
        assumed that all specs should be considered for that one entity.
         If only a single relationshipSpec is provided, then it should
        be considered for all supplied entity references. If lists of
        both are supplied, then they must be the same length, and it
        should be assumed that it is a 1:1 mapping of spec per entity.
        If this is not the case, ValueErrors should be thrown.

        If any specification is unknown, then an empty list should be
        returned for that specification, and no errors should be raised.

        @param entityRefs List[str]

        @param relationshipSpecs List[RelationshipSpecification]

        @param resultSpec openassetio.specifications.EntitySpecification
        or None, a hint as to what kind of entity the caller is
        expecting to be returned. May be None.

        @return List[List[str]] This MUST be the correct length,
        returning an empty outer list is NOT valid. (ie: max(len(refs),
        len(specs)))

        @exception ValueError If more than one reference and
        specification is provided, but they lists are not equal in
        length, ie: not a 1:1 mapping of entities to specs. The
        abstraction of this interface into the Manager class does
        cursory validation that this is the case before calling this
        function.

        @see openassetio.specifications
        @see setRelatedReferences()
        """
        raise NotImplementedError

    def setRelatedReferences(
            self, entityRef, relationshipSpec, relatedRefs,
            context, hostSession, append=True):
        """
        Creates a new relationship between the referenced entities.

        @param append bool, When True (default) new relationships will
        be added to any existing ones. If False, then any existing
        relationships with the supplied specification will first be
        removed.

        Though getRelatedReferences is an essential call, there is some
        asymmetry here, as it is not necessarily required to be able to
        setRelatedReferences directly. For example, in the case of a
        'shot' (as illustrated in the docs for getRelatedReferences) -
        any new shots would be created by registering a new
        ShotSpecification under the parent, rather than using this call.
        The best way to think of it is that this call is reserved for
        defining relationships between existing assets (Such as
        connecting multiple image sequences published under the same
        shot, as being part of the same render.) and 'register' as being
        defining the relationship between a new asset and some existing
        one.

        In systems that don't support post-creation adjustment of
        relationships, this can simply be a no-op.

        @return None

        @see @ref getRelatedReferences()
        @see @ref register()
        """
        if not self.entityExists(entityRef, context, hostSession):
            raise exceptions.InvalidEntityReference(entityReference=entityRef)

        for r in relatedRefs:
            if not self.entityExists(r, context, hostSession):
                raise exceptions.InvalidEntityReference(entityReference=r)

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
    # **2 - The Specification**
    #
    # The Specification allows ancillary information to be provided to help the
    # implementation better interpret what type of entity may be best suited in
    # any given situation. For example, a path to an image will generally be
    # accompanied by with an spec, that details the file type, colour space,
    # resolution etc...
    #
    # @note The Specification should *not* be confused with @ref metadata.  The
    # implementation must not directly store any information contained within the
    # Specification, though it may be used to better define the type of entity.
    # Hosts that wish to persist other properties of the published entity, will
    # call @ref setEntityMetadata() directly instead, and as described in the
    # metadata section, it is assumed that this is the channel for information
    # that needs to persist.
    #
    # For more on the relationship between Entities, Specifications and
    # metadata, please see @ref entities_specifications_and_metadata
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
    # this API provides the @ref localizeStrings call, in order to allow the
    # implementation to standardise some of the language and terminology used in a
    # Hosts presentation of the asset management system with other integrations
    # of the system.
    #
    # @{

    @abc.abstractmethod
    def managementPolicy(self, specification, context, hostSession, entityRef=None):
        """
        Determines if the asset manager is interested in participating
        in interactions with the specified specification of @ref entity.

        For example, a host may call this in order to see if the manager
        would like to manage the path of a scene file whilst choosing a
        destination to save to.

        This information is then used to determine which options should
        be presented to the user. For example, if kIgnored was returned
        for a query as to the management of scene files, a Host will
        hide or disable menu items that relate to publish or loading of
        assetised scene files.

        @warning The @ref openassetio.Context.Context.access "access"
        specified in the supplied context should be carefully considered.
        A host will independently query the policy for both read and
        write access to determine if resolution and publishing features
        are applicable to this implementation.

        Calls with an accompanying @ref entity_reference may be used to
        prevent users from attempting to perform an asset-action that is
        not supported by the asset management system.

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

        Additionally, the @ref
        openassetio.constants.kSupportsBatchOperations bit is important
        if you want hosts to call the *Multiple variants of the @ref
        preflight and @ref register methods.

        @param entityRef str, If supplied, then the call should be
        interpreted as a query as to the applicability of the given
        specification if registered to the supplied entity. For example,
        attempts to register an ImageSpecification to an entity
        reference that refers to the top level project may be
        meaningless, so in this case kIgnored should be returned.

        @return int, a bitfield, see @ref openassetio.constants
        """
        raise NotImplementedError

    def thumbnailSpecification(self, specification, context, options, hostSession):
        """
        This will be called prior to registration of an asset to
        determine if the asset system would like a thumbnail preparing.
        Presently, only JPEG thumbnails will be generated. The arguments
        to this call are the same as those that will be passed to the
        register call.

        If a thumbnail is requested, its path will be set in the
        specification property 'thumbnailPath' passed to a register call
        at a later date if it was possible to create one.

        @param options dict, The thumbnail process can be customised, by
        setting the following keys in the options dict.

          @li kField_PixelWidth ('width') : The pixel width of the
          thumbnail
          @li kField_PixelHeight ('height') : The pixel height of the
          thumbnail

        The keys may be set to the default set by the Host. It will try
        to best match the requested specifications, but it should not be
        assumed that all requested properties are honoured.

        @return bool, If True, a Thumbnail is desired by the manager, if
        False, the host should not waste time making one.
        """
        return False

    def preflight(self, targetEntityRef, entitySpec, context, hostSession):
        """
        Prepares for some work to be done to create data for the
        referenced entity. The entity may not yet exist (@ref
        entity_reference). This call is designed to allow sanity
        checking, placeholder creation or any other sundry preparatory
        actions to be carried out.

        Generally, this will be called before register() in any host
        that creates media, where the return to @ref managementPolicy
        has the @ref openassetio.constants.kWillManagePath bit set.

        @param targetEntityRef str, a @ref entity_reference that it is
        desired to publish the forthcoming data to. See the notes in the
        API documentation for the specifics of this.

        @note it is important for the implementation to pay attention to
        @ref Context.retention, as not all hosts will support the
        reference changing at this point.

        @return str, An @ref entity_reference, that the host should
        resolve to determine the path to write media too. This may or
        may not be the same as the input reference. A host will resolve
        this reference to get the working URL before writing any files
        or other data.

        @exception openassetio.exceptions.PreflightError if some fatal
        exception happens during preflight, indicating the process
        should be aborted.

        @exception openassetio.exceptions.RetryableError If any
        non-fatal error occurs that means the host should re-try from
        the beginning of any given process.

        @see register()
        """
        return targetEntityRef

    def preflightMultiple(self, targetEntityRefs, entitySpecs, context, hostSession):
        """
        A batch version of @ref preflight, where most arguments are
        replaced by arrays of equal length. Exception behaviour, etc...
        is the same as per preflight, and should be thrown mid way
        though preflight if necessary.

        This will be used in preference to calling preflight many times
        in succession to allow the implementation to optimise
        communication with the back end asset management system.

        @param context Context, is not replaced with an array in order
        to simplify implementation. Otherwise, transactional handling
        has the potential to be extremely complex if different contexts
        are allowed.


        @return List[str], A list of working entity references.
        """
        result = []
        for t, s in zip(targetEntityRefs, entitySpecs):
            result.append(self.preflight(t, s, context, hostSession))
        return result

    def register(self, stringData, targetEntityRef, entitySpec, context, hostSession):
        """
        Publish an entity to the @ref asset_management_system.

        This instructs the implementation to ensure a valid entity
        exists for the given reference and spec. This will be called
        either in isolation or after calling preflight, depending on the
        nature of the data being published and the kWillManagePath bit
        of the returned @ref managementPolicy.

        This is an opportunity to do other things in the host as part of
        publishing if required. The context's locale will tell you more
        about the specifics of the calling application. Depending on the
        implementation of your plugin, you can use this opportunity to
        make use of the host-native SDK to extract additional
        information or schedule additional processes to produce
        derivative data.

        @param stringData str, The string that the entity should resolve
        to if passed to a call to resolveEntityReference(). This may be
        left blank, if there is no meaningful string representation of
        that entity (eg: a 'sequence' in a hierarchy). This must be
        stored by the manager and a logically equivalent value returned
        by @ref resolveEntityReference for the same reference. The
        meaning of 'logical' here, is that in the case of an URL, that
        it points to the same data. The manager is free to relocate data
        as required. If stringData is not an URL, then it should be
        returned verbatim.

        @param targetReference The @ref entity_reference to publish to.
        It is up to the manager to ensure that this is meaningful, as it
        is most likely implementation specific. For example, if a 'Shot'
        specification is requested to be published to a reference that
        points to a 'Sequence' it makes sense to interpret this as a
        'add a shot of this spec to the sequence'. For other types of
        entity, there may be different constraints on what makes sense.

        @param entitySpec openassetio.specifications.EntitySpecification
        A description of the Entity (or 'asset') that is being
        published. It is *not* required for the implementation to store
        any information contained in the specification, though it may
        choose to use it if it is meaningful. The host will separately
        call setEntityMetadata() if it wishes to persist any other
        information in the entity.

        @return str, An @ref entity_reference to the 'final' entity
        created by the publish action. It does not need to be the same
        as targetReference.

        @note it is important for the implementation to pay attention to
        openassetio.contexts.Context.retention, as not all Hosts will
        support the reference changing at this point.

        @exception openassetio.exceptions.RegistrationError if some
        fatal exception happens during publishing, indicating the
        process should be aborted.

        @exception openassetio.exceptions.RetryableError If any
        non-fatal error occurs that means the host should re-try from
        the beginning of any given process.

        @see preflight()
        @see resolveEntityReference()
        """
        raise NotImplementedError

    def registerMultiple(self, strings, targetEntityRefs, entitySpecs, context, hostSession):
        """
        A batch version of @ref register, where most arguments are
        replaced by arrays of equal length. Exception behaviour, etc...
        is the same as per register, and should be thrown mid way though
        registration if necessary.

        This will be used in preference to calling register many times
        in succession to allow the implementation to optimise
        communication with the back end asset management system.

        @param context Context, is not replaced with an array in order
        to simplify implementation. Otherwise, transactional handling
        has the potential to be extremely complex if different contexts
        are allowed.


        @return List[str], A list of finalized entity references.
        """
        result = []
        for d, t, s in zip(strings, targetEntityRefs, entitySpecs):
            result.append(self.register(d, t, s, context, hostSession))
        return result

    ## @}

    ##
    # @name Manager State
    #
    # A single 'task' in a host, may require more than one interaction with
    # the asset management system.
    #
    # Because the @ref openassetio.managerAPI.ManagerInterface
    # "ManagerInterface" is effectively state-less. To simplify error
    # handling, and allow an implementation to know which interactions
    # are related, this API supports the concept of a @ref manager_state
    # object. This is contained in every @ref Context and passed to
    # relevant calls.
    #
    # This mechanism may be used for a variety of purposes. For example, it
    # could ensure that queries are made from a coherent time stamp during a
    # render, or to undo the publishing of multiple assets. It can also be used
    # to define 'transactions' - groups of related actions that may be cancelled
    # together/rolled back.
    #
    # @note Not all implementations may support transactions, there is no
    # requirement for any of the functions in this group being implemented.  The
    # defaults are effectively no-ops.
    #
    # @{

    def createState(self, hostSession, parentState=None):
        """
        Create a new object to represent the state of the interface and
        return it (or some handle that can be persisted within the
        context). You are free to implement this however you like, as
        long as it can be uniquely represented by the object returned
        from this function.

        This method is called whenever a new @ref Context is made by a
        @ref openassetio.Session.Session.createContext. The return is
        then stored in the newly created Context, and is consequently
        available to all the API calls in the ManagerInterface that take
        a Context instance via @ref Context.managerInterfaceState. Your
        implementation can then use this to anchor the api call to a
        particular snapshot of the state of the asset inventory.

        This object is also extracted from the context and passed
        directly to any of the 'transactional' calls in this API.  For
        more on the transactional model in this API, and how these will
        be called, see the @ref transactions Page.

        @param parentState obj, If present, it is to be assumed that the
        new state is considered a 'child' of the supplied state. This
        may be used when creating a child Context for persistence
        somewhere in a UI, etc... when further processing may change the
        access/retention of the Context. It is expected that the manager
        will migrate any applicable state components to this child
        context, for example - a timestamp used for 'vlatest'. However
        is it *not* expected to link the new state with any transaction
        that is open in the parent state. So the returned state should
        have any open transactions.

        @return object, Some object that represents self-contained state
        of the ManagerInterface. This will be passed to future calls and
        to the transactional methods. Presently this can be any hashable
        object.

        @exceptions openassetio.exceptions.StateError If for some reason
        creation fails.

        @see startTransaction()
        @see finishTransaction()
        @see cancelTransaction()
        @see freezeState()
        @see thawState()
        @see The @ref transactions page.
        """
        return None

    def startTransaction(self, state, hostSession):
        """
        Called to indicate the start of a series of connected actions.
        The aim of a transaction is to allow undo/cancellation of all
        related actions in one step. Largely to avoid inconsistent state
        in the back end. It is important though that any queries made to
        data that has been created or set within the transaction,
        returns the updated or new data.

        For more on the transactional model in this API, and how these
        functions are called, see the @ref transactions Page.

        This will never be called with the same state from multiple
        threads, but may be called with different state objects.

        This method **must** store any persistent state in the supplied
        state object to ensure the API is stateless. It should not store
        any state relating to the transaction within the
        ManagerInterface instance itself.

        @return None

        @exception openassetio.exceptions.StateError If for some reason
        the action fails.

        @see createState()
        @see finishTransaction()
        @see cancelTransaction()
        @see The @ref transactions page.
        """
        pass

    def finishTransaction(self, state, hostSession):
        """
        Called at the end of a group of actions to inform the
        ManagerInterface that any pending internal management should be
        finalized.

        For more on the transactional model in this API, and how these
        functions will be called, see the @ref transactions Page.

        This will never be called with the same state from  multiple
        threads, but may be called with different state objects.

        This method **must** only use or store any persistent state from
        the supplied state object to ensure the API is stateless.

        @return None

        @exception openassetio.exceptions.StateError If for some reason
        the action fails, or finish is called before start.

        @see createState()
        @see startTransaction()
        @see cancelTransaction()
        @see The @ref transactions page.
        """
        pass

    def cancelTransaction(self, state, hostSession):
        """
        Can be called at any point after @ref startTransaction to undo
        actions and reset the transaction state.

        Generally called in response to some fatal error, in order to
        request the implementation to unroll, or revert any changes made
        since @ref startTransaction

        The state should also be re-configured so that it is then safe
        to call @ref startTransaction

        @return Bool True if roll-back was successful, False in all
        other cases.

        @see createState()
        @see startTransaction()
        @see finishTransaction()
        @see The @ref transactions page.
        """
        return False

    ##
    # @name State Persistence
    #
    # A Host may wish to distribute work. Often the workers may be in a
    # different execution space. As such, it becomes necessary to pass a
    # reference to the current transaction stack along with the work, so that
    # actions can be correctly grouped.
    #
    # The freezeState() call can be made at any point, and
    # The ManagerInterface should return a string that, when
    # passed to thawState() in another process, will restore the
    # state of the context so that future actions will be associated with the
    # same state as before freezing.
    #
    # Included in this is the requirement that if a transaction has been started,
    # this should also be persisted, so that actions on a thawed state are also
    # associated with that transaction.
    #
    # This string could be a serialized representation of some transaction
    # object, or a simple uuid or handle.
    #
    # If an implementation does not support freezing the state, then it should
    # ensure that any outstanding internal tasks pending on @ref
    # finishTransaction are completed prior to thawing, but the 'open' state of
    # the transaction should be persisted to the thawed state - as @ref
    # finishTransaction will most likely still be called.

    def freezeState(self, state, hostSession):
        """
        Returns a string that encapsulates the current state of the
        ManagerInterface represented by the supplied state
        object,(created by @ref createState) so that can be restored
        later, or in another process.

        After calling this, the state should be considered frozen, and
        any further cancel/finish calls should throw a @ref
        openassetio.exceptions.StateError if made without first thawing
        the stack.

        @return A string that can be used to restore the stack.

        @see thawState()
        @see The @ref transactions page.
        """
        return ""

    def thawState(self, token, hostSession):
        """
        Restores the supplied state object to a previously frozen state.

        @return object A state object, as per createState(), except
        restored to the previous state encapsulated in the token, which
        is the same string as returned by freezeState.

        @exception openassetio.exceptions.StateError If the supplied
        token is not meaningful, or that a state has already been
        thawed.
        """
        return None

    ## @}
