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

## @todo Should we just assume all validation of supplied entity references,
## etc is taken care of in the Manager/Entity abstraction, to avoid doubling
## the work, if a host already tests whether or not something is a ref before
## acting upon it.


__all__ = ['ManagerInterface', ]


class ManagerInterface(object):
  """

  @brief This Interface binds a @ref asset_management_system into the
  Asset API. It is not called directly by a @ref host, but by the
  middle-ware that presents a more object-oriented model of this the a @ref
  host - namely, the @ref FnAssetAPI.Manager.Manager and @ref
  FnAssetAPI.Entity.Entity classes.

  It is structured around the following principals:

    @li The currency of the API is either data, or an @ref entity_reference.
    objects should not be used to represent an Entity or its properties.

    @li All calls should be atomic, to facilitate concurrency (see the @ref
    threading section for more details).

    @li The implementation of this class should have no UI dependencies, so
    that it can be used in command-line only hosts/batch process etc...

    @li You generally don't need to call the superclass implementation of any
    methods in this interface, unless you are deriving from your own subclass
    which requires it.

  Logging and Error Handling
  --------------------------

  The supplied @ref FnAssetAPI.implementation.HostSession object provides
  logging methods that allow messages and progress to be reported back to
  the user. All logging should go through these methods otherwise it may
  not be correctly presented to the user. The loose term "user" also covers
  developers, who may need to see log output for debugging and other purposes.

  @important Your plugin may be hosted out of process, or even on another
  machine, the HostSession bridge takes care of relaying messages accordingly.
  Using custom logging mechanisms may well result in output being lost.

  @see FnAssetAPI.implementation.HostSession.log
  @see FnAssetAPI.implementation.HostSession.progress

  Exceptions should be thrown to handle any in-flight errors that occur.
  The error should be mapped to a derived class of
  FnAssetAPI.exceptions.BaseException, and thrown.  All exceptions of this kind,
  will be correctly passed across the plug-in C boundary, and re-thrown. Other
  exceptions should not be used.

   @see python::exceptions

  Threading
  ---------
  Any implementation of the ManagerInterface should be thread safe. The one
  exception being Manager::initialize, this will never be called
  concurrently.

  When a @ref FnAssetAPI.Context.Context object is constructed by @ref
  FnAssetAPI.Session.Session.createContext, the createState method will be called,
  and the resulting state object stored in the context.
  This context will then be re-used across related API calls to the
  ManagerInterface implementation. You can use this to determine which
  calls may be part of a specific 'action' in the Host, or to store any
  transaction-persistent data.

  One exception to the treading rule is that the transaction managing functions
  won't be called from multiple threads with the same transaction object.

  There should be no persistent state in the implementation, concepts such
  as getError(), etc.. for example should not be used.


  Context
  -------

  The Context object is passed to many methods of this class.  Though in the
  majority of situations this will be well defined, it should not cause an
  error if this is ever None.


  Hosts
  -----

  Sometimes you may need to know more information about the API host. A
  @ref FnAssetAPI.implementation.Host object is available through the
  @ref FnAssetAPI.implementation.HostSession object passed to each
  method of this class. This provides a standardised interface that
  all API hosts guarantee to implement. This can be used to identify
  exactly which host you are being called for, and query various
  entity related specifics of the hosts data model.

  @see FnAssetPI.implementation.Host


  Initialization
  --------------

  The constructor makes a new instance, but at this point it is not ready for use.
  The implementation shouldn't do any work in the constructor, so that it is
  its is cheap to create one. This means that only the informational
  methods need to be available until initialize() has been called.

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
  #  Returns an entityReference that can be used for testing purposes, the
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
  #  You could use this to remove any temporary database entires, etc... that
  #  were necessary to satisfy a request for a reference to an 'existing'
  #  asset.
  #
  #  """


  ##
  # @name Asset Management System Information
  #
  # These functions provide general information about the @ref asset_management_system itself.
  #
  # @{

  @abc.abstractmethod
  def getIdentifier(self):
    """

    Returns an identifier to uniquely identify a specific asset manager.
    This may be used by a Host to persist the users preferred manager via a
    preferences mechanism, or when spawning child processes, etc...
    It should match the name used to register the plug-in with the plug-in host.
    The identifier should use only alpha-numeric characters and '.', '_' or '-'.
    For example:

        "uk.co.foundry.asset.testAssetManager"

    @return str

    """
    raise NotImplementedError


  @abc.abstractmethod
  def getDisplayName(self):
    """

    Returns a human readable name to be used to reference this specific
    asset manager.
    Once instance of its use may be in a Host's Preferences UI or logging.
    For example:

        "The Foundry Test Asset Manager"

    """
    raise NotImplementedError


  def getInfo(self):
    """

    Returns other information that may be useful about this @ref
    asset_management_system.  This can contain arbitrary key/value pairs.For
    example:

        { 'version' : '1.1v3',
          'server' : 'am.thefoundry.co.uk' }

    There are certain optional keys that may be used by a host or the API:

      @li FnAssetAPI.constants.kField_SmallIcon (upto 32x32)
      @li FnAssetAPI.constants.kField_Icon (any size)

    Because it can often be expensive to bridge between languages, info can
    also contain one of two additional fields - a prefix, or perl regex
    compatible string to identify a valid entity reference. Only one should be
    set at once. If supplied, this may be used by the API to optimise calls to
    isEntityReference when bridging between C/Python etc... can be slow. If
    neither of these fields are set, then isEntityReference will always be used
    to determine if a string is an entityReference or not. Note, not all hosts
    support this optimisation, so @ref isEntityReference should be implemented
    regardless.

      @li FnAssetAPI.constants.kField_EntityReferencesMatchPrefix
      @li FnAssetAPI.constants.kField_EntityReferencesMatchRegex

    @note Keys should always be UTF-8 stings, and values must be
    plain-old-data types (ie: str, int, float, bool).

    """
    return {}


  def localizeStrings(self, stringDict, hostSession):
    """

    This call gives the Host a chance to customise certain strings used in it's
    UI/messages. @see FnAssetAPI.constants for known keys. The values in stringDict
    can be freely updated to match the terminology of the asset management
    system you are representing.

    For example, you may way a Host's "Publish Clip" menu item to read "Release
    Clip", so you would set the kLocalizationKey_Publish value to "Release".

    @return None

    @see @ref FnAssetAPI.constants
    @see @ref FnAssetAPI.Session.Session.__terminology

    """
    pass

  ## @}


  ##
  # @name Initialization
  #
  ## @{

  def getSettings(self, hostSession):
    return {}

  def setSettings(self, settings, hostSession):
    pass

  @abc.abstractmethod
  def initialize(self, hostSession):
    """

    Prepares for interaction with a Host.

    This is a good opportunity to initialize connections to a back end
    implementation, as @ref setSettings will have already been called (if
    applicable). This may result in this call blocking for a period of time.

    If an exception is raised by this call, its is safe to assume that a fatal
    error occurred, and this @ref asset_management_system is not available, and
    should be retried later.

    If no exception is raised, it can be assumed that the @ref asset_management_system is
    ready. It is the implementations responsibility to deal with transient
    connection errors (if applicable) once initialized.

    The behaviour of calling initialize() on an already initialized
    Manager should be a no-op, but if an error was raised previously, then
    initialization should be re-attempted.

    @note This will always be called prior to any Entity-related calls.
    An exception should be raised if this is not the case. It is however,
    the following functions may be called prior to initialization:

     @li @ref getIdentifier()
     @li @ref getDisplayName()
     @li @ref getInfo()
     @li @ref localizeStrings()
     @li @ref getSettings()
     @li @ref setSettings()

    @todo We need a 'teardown' method to, before a manager is de-activated in a
    host, to allow any event registrations etc... to be removed.

    """
    raise NotImplementedError


  def prefetch(self, entitRefs, context, hostSession):
    """

    Called by a Host to express interest in the supplied @ref
    entity_reference list. This usually means that the Host is about to make
    multiple queries to the same references.  This can be left unimplemented,
    but it is advisable to batch request the data for resolveEntityReference,
    getEntityMetadata here if possible to minimize server load.

    The implementation should ignore any unrecognised strings, or any entities
    to which no action is applicable (maybe as they don't exist yet).

    @warning Because the majority of the resolution API itself is designated
    thread stafe, it is important to implement any pre-fetch mechanism with
    suitable locks/etc... if required.

    @param context FnAssetAPI.contexts.Context, may be None, but if present, you
    may wish to make use of the managerInterfaceState object (if you supplied
    one on construction of the context), to simplify scoping any caching of
    data. Otherwise, it's up to you how to manage the lifetime of the data to
    avoid inconsistencies, but the @ref flushCaches method should clear any
    otherwise sorted data for this call.

    @return None

    """
    pass


  def flushCaches(self, hostSession):
    """

    Clears any internal caches.  Only applicable if the implementation makes
    use of any caching, otherwise it is a no-op.  In caching interfaces, this
    should cause any retained data to be discarded to ensure future queries are
    fresh.  This should have no effect on any open @ref transaction.

    """
    pass


  ## @}


  ##
  # @name Entity Reference inspection
  #
  # Because of the nature of an @ref entity_reference, it is often
  # necessary to determine if some working string is actually an @ref
  # entityReference or not, to ensure it is handled correctly.
  #
  # @{

  @abc.abstractmethod
  def isEntityReference(self, token, context, hostSession):
    """

    Determines if a supplied token (in its entirety) matches the pattern of
    an @ref entity_reference.
    It does not verify that it points to a valid entity in the system,
    simply that the pattern of the token is recognised by this implementation.

    If this returns True, the token is an @ref entity_reference and should
    be considered as a managed entity. Consequently, it should be resolved
    before use. It also confirms that it can be passed to any other
    method that requires an @ref entity_reference.

    If false, this manager should no longer be involved in actions relating
    to the token.

    @warning The result of this call should not depend on the context Locale,
    as these results may be cached by access pattern.

    @param token The string to be inspected.

    @param context, The calling context, this may be None.

    @return bool, True if the supplied token should be considered as an @ref
    entityReference, False if the pattern is not recognised.

    @note This call does not verify the entity exits, just that the format of
    the string is recognised.

    @see entityExists()
    @see resolveEntityReference()

    """
    raise NotImplementedError


  @abc.abstractmethod
  def entityExists(self, entityRef, context, hostSession):
    """

    Called to determine if the supplied @ref entity_reference points to an
    Entity that exists in the @ref asset_management_system, and that it can be
    resolved into a meaningful string.

    By 'Exist' we mean 'is ready to be read'. For example, entityExists may be
    called before attempting to read from a reference that is believed to point
    to an image sequence, so that alternatives can be found.

    In the future, this may need to be extended to cover a more complex
    definition of 'existence' (for example, known to the system, but not yet
    finalized). For now however, it should be assumed to simply mean, 'ready to
    be consumed', and if only a placeholder or un-finalized asset is available,
    False should be returned.

    The supplied context's locale may contain information pertinent to
    disambiguating this subtle definition of 'exists' in some cases too, as it
    better explains the use-case of the call.

    @return bool, True if it points to an existing entity, False if the Entity
    is not known or ready yet.

    @exception FnAssetAPI.exceptions.InvalidEntityReference If the input string is
    not a valid entity reference.

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

    Returns the 'finalized' string represented by the @ref entity_reference.

    When the @ref entity_reference points to a sequence of files, the frame
    token should be preserved, and in the sptintf compatible syntax.

    This function should attempt to take into account the current Host/Context
    to ensure that any other substitution tokens are presented in a suitable
    form. The Context should also be carefully considered to ensure that the
    access does not violate any rules of the system - for example, resolving an
    existing entity reference for write.

    The caller should have first called isEntityReference() on the supplied
    string.

    @note You may need to call getFinalizedEntityVersion() within this function
    to ensure any @ref meta_versions are resolved prior to resolution.

    @return str, The UTF-8 ASCII compatible string that that is represented by
    the reference.

    @exception FnAssetAPI.exceptions.InvalidEntityReference If the supplied @ref
    entity_reference is not known by the asset management system.
    @exception FnAssetAPI.exceptions.EntityResolutionError If the supplied @ref
    entity_reference does not have a meaningful string representation, or it is
    a valid reference format, that doesn't exist.
    @exception FnAssetAPI.exceptions.InvalidEntityReference if the supplied
    entity_reference should not be resolved for that context, for example, if
    the context access is kWrite and the entity is an existing version -
    raising will ensure that a Host will not attempt to write to that location.

    @see entityExists()
    @see isEntityReference()
    @see resolveEntityReferences()

    """
    raise NotImplementedError


  def resolveEntityReferences(self, references, context, hostSession):
    """

    Batch-resolves a list of entityReferences, following the same pattern as
    @ref resolveEntityReference.

    @return list, A list of strings, corresponding to the source reference
    with the same index.

    This will be called by hosts when they wish to batch-resolve many
    references with an eye to performance, or server hits, and so should be
    re-implemented to minimise the number of queries over a standard 'for'
    loop.

    The base class implementation simply calls resolveEntityReference
    repeatedly for each suppled reference.

    """
    resolved = []
    for r in references:
      resolved.append(self.resolveEntityReference(r, context, hostSession))
    return resolved


  def getDefaultEntityReference(self, specification, context, hostSession):
    """

    Returns an @ref entity_reference considered to be a sensible default for
    the given Specification and Context. This is often used in a host to ensure
    dialogs, prompts or publish locations default to some sensible value,
    avoiding the need for a user to re-enter such information when a Host is
    being run in some known environment.

    For example, a Host may request the default ref for
    'ShotSpecification/kWriteMultiple'. If the Manager has some concept of the
    'current sqeuence' it may wish to return this so that a 'Create Shots'
    starts somewhere meaningful.

    @return str, A valid entity reference, or empty string.

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

    Returns the name of the entity itself, not including any hierarchy or
    classification.

    For example:

     @li `"1"` - for a version of an asset
     @li `"seq003"` - for a sequence in a hierarchy

    @return str, An UTF-8 ASCII string containing any valid characters for the
    manager's implementation.

    @exception FnAssetAPI.exceptions.InvalidEntityReference If any supplied
    reference is not recognised by the asset management system.

    """
    raise NotImplementedError



  @abc.abstractmethod
  def getEntityDisplayName(self, entityRef, context, hostSession):
    """

    Returns an unambiguous, humanised display name for the entity.

    The display name may consider the Host, and any other relevant Context
    information to form a display name for an entity that can uniquely
    identify the entity in that context.

    For example:

     @li `"dive / build / cuttlefish / model / v1"` - for a version of an
     asset in an 'open recent' menu.
     @li `"Sequence 003 [ Dive / Episode 1 ]"` - for a sequence in
     an hierarchy as a window title.

    @return str, an ASCII string containing any valid characters for the
    @ref asset_management_system's implementation.

    @exception FnAssetAPI.exceptions.InvalidEntityReference If any supplied
    reference is not recognised by the asset management system.

    """
    raise NotImplementedError


  @abc.abstractmethod
  def getEntityMetadata(self, entityRef, context, hostSession):
    """

    Retrieve @ref metadata for an entity.

    It may be required here to bridge between certain perhaps 'first-class'
    properties of the asset management system in question, and keys in the
    metadata dictionary. For example, if the asset system represents a 'Shot'
    with 'cutIn' and 'cutOut' properties or accessors, these should be remapped to the
    @ref FnAssetAPI.kField_FrameIn/Out metadata keys as appropriate.

    @warning See @ref setEntityMetadata for important notes on metadata and its
    role in the system.

    @return dict, with the entities meta-data. Values must be P.O.D types, keys
    must be UTF-8 ASCII strings.

    @exception FnAssetAPI.exceptions.InvalidEntityReference If any supplied
    reference is not recognised by the asset management system.

    """
    raise NotImplementedError


  @abc.abstractmethod
  def setEntityMetadata(self, entityRef, data, context, hostSession, merge=True):
    """

    Sets an entities metadata.

    @param merge, bool If true, then the entity's existing metadata will be
    merged with the new data (the new data taking precedence). If false,
    its metadata will entirely replaced by the new data.

    @note It is a vital that the implementation faithfully stores and recalls
    metadata. It is the underlying binding to any stronger Entity types within
    this API, that simply wrap the metadata dictionary to allow hosts a more
    sophisticated interaction. Specific key named and value types should be
    maintained. To ensure entities created by other facilities of the asset
    sysetem, It may also be necessary to bridge data between its native
    representation in the system, and well-known keys here, based on the
    Entity's type.

    If any value is 'None' it should be assumed that that key should be un-set
    on the object.

    @exception FnAssetAPI.exceptions.InvalidEntityReference If any supplied
    reference is not recognised by the asset management system.

    @exception ValueError if any of the metadata values are of an un-storable
    type. Presently it is only required to store str, float, int, bool

    @exception KeyError if any of the metadata keys are non-strings.

    """
    raise NotImplementedError


  def getEntityMetadataEntry(self, entityRef, key, context, hostSession, defaultValue=None):
    """

    Returns the value for the specified metadata key.

    @param key str, The key to look up
    @param defaultValue p.o.d If not None, this value will be returned in the
    case of the specified key not being set for the entity.

    @return p.o.d, The value for the specific key.

    @exception FnAssetAPI.exceptions.InvalidEntityReference If any supplied
    reference is not recognised by the asset management system.

    @exception KeyError If no defaultValue is supplied, and the entity has no
    metadata for the specified key.

    """
    value = defaultValue
    try:
      value = self.getEntityMetadata(entityRef, context, hostSession)[key]
    except KeyError:
      if defaultValue is None:
        raise
    return value

  def setEntityMetadataEntry(self, entityRef, key, value, context, hostSession):
    self.setEntityMetadata(entityRef, {key : value}, context, hostSession, merge=True)


  ## @}

  ##
  # @name Versioning
  #
  # Most asset_management_systems allow multiple revisions of certain
  # entities to be tracked simultaneously. This API exposes this as
  # a generalised concept, and its necessary for the caller to make sure
  # only @ref entity_references that are meaningfully versioned are
  # queried.
  #
  # @{

  def getEntityVersionName(self, entityRef, context, hostSession):
    """

    Retrieves the name of the version pointed to by the supplied @ref
    entity_reference.

    @return str, A UTF-8 ASCII string representing the version or an empty
    string if the entity was not versioned.

    @note It is not necessarily a requirement that the entity exists, if, for
    example, the version name can be determined from the reference itself (in
    systems that implement a human-readable url, for example)

    @exception FnAssetAPI.exceptions.InvalidEntityReference If any supplied
    reference is not recognised by the asset management system.

    @see getEntityVersions()
    @see getFinalizedEntityVersion()

    """
    return ""


  def getEntityVersions(self, entityRef, context, hostSession, includeMetaVersions=False, maxResults=-1):
    """

    Retrieves all available versions of the supplied @ref entity_reference
    (including the supplied ref, if it points to a specific version).

    @param includeMetaVersions bool, if true, @ref meta_versions such as
    'latest', etc... should be included, otherwise, only concrete versions
    will be retrieved.

    @param maxResults int, Limits the number of results collected, if more
    results are available than the limit, then the newest versions will be
    returned. If a value of -1 is used, then all results will be returned.

    @return dict, Where the keys are ASCII string versions, and the values are
    an @ref entity_reference that points to its entity. Additionally the
    FnAssetAPI.constants.kVersionDict_OrderKey can be set to a list of the
    version names (ie: dict keys) in their natural ascending order, that may be
    used by UI elements, etc...

    @exception FnAssetAPI.exceptions.InvalidEntityReference If any supplied
    reference is not recognised by the asset management system.

    @see getEntityVersionName()
    @see getFinalizedEntityVersion()

    """
    return {}


  def getFinalizedEntityVersion(self, entityRef, context, hostSession, overrideVersionName=None):
    """

    Retrieves a @ref entity_reference that points to the concrete version
    of a @ref meta-version @ref entity_reference.

    If the supplied entity reference is not versioned, or already has a
    concrete version, the input reference is passed-through.

    If versioning is unsupported for the given @ref entity_reference, then the
    input reference is returned.

    @param overrideVersionName str If supplied, then the call should return the
    entity reference for the version of the referenced asset that matches the
    name specified here, ignoring any version inferred by the input reference.

    @return str

    @exception FnAssetAPI.exceptions.InvalidEntityReference If any supplied
    reference is not recognised by the asset management system.

    @exception FnAssetAPI.exceptions.EntityResolutionError should be thrown if the
    entityReference is ambiguously versioned (for example if the version is
    missing from a reference to a versioned entity, and that behaviour is
    undefined in the system managers model. It may be that it makes sense in
    the specific asset manager to fall back on 'latest' in this case...)

    @exception FnAssetAPI.exception.EntityResolutionError if the supplied
    overrideVersionName does not exist for that entity.

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
  def getRelatedReferences(self, entityRefs, relationshipSpecs, context, hostSession,
      resultSpec=None):
    """

    Returns related entity references, based on a relationship specification.

    This is an essential function in this API - as it is widely used to query
    organisational hierarchy, etc...

    There are three possible conventions for calling this function, to allow
    for batch optimisations in the implementation and prevent excessive query
    times with high-latency services.

      a)  A single entity reference, a list of specifications.
      b)  A list of entity references and a single specification.
      c)  Equal length lists of references and specifications.

    In all cases, the return value is a list of lists, for example:

    a)  getRelatedReferencess( [ r1 ], [ s1, s2, s3 ] )

    > [ [ r1-s1-matches, ... ], [ r1-s2-matches, ... ], [ r1-s3-matches, ... ] ]

    b)  getRelatedReferences( [ r1, r2, r3 ], [ s1 ] )

    > [ [ r1-s1-matches, ... ], [ r2-s1-matches, ... ], [ r3-s1-matches, ... ] ]

    c)  getRelatedReferences( [ r1, r2, r3 ], [ s1, s2, s3 ] )

    > [ [ r1-s1-matches, ... ], [ r2-s2-matches, ... ], [ r3-s3-matches, ... ] ]

    @note The order of entities in the inner lists of matching references will
    not be considered meaningful, but the outer list should match the input
    order.

    In summary, if only a single entityRef is provided, it should be assumed
    that all specs should be considered for that one entity.  If only a single
    relationshipSpec is provided, then it should be considered for all supplied
    entity references. If lists of both are supplied, then they must be the
    same length, and it should be assumed that it is a 1:1 mapping of spec per
    entity. If this is not the case, ValueErrors should be thrown.

    If any specification is unknown, then an empty list should be returned for
    that specificaion, and no errors should be raised.

    @param entityRefs str list

    @param relationshipSpecs FnAssetAPI.specifications.Specification or
    FnAssetAPI.specifications.RelationshipSpecification list

    @param resultSpec FnAssetAPI.specifications.EntitySpecification or None, a hint
    as to what kind of entity the caller is expecting to be returned. May be
    None.

    @return list of str lists, this MUST be the correct length, returning an
    empty outer list is NOT valid. (ie: max(len(refs), len(specs)))

    @exception FnAssetAPI.exceptions.InvalidEntityReference If any supplied
    reference is not known by the @ref asset_management_system. However, no exception should be
    thrown if it is a recognised reference, but has no applicable relations.

    @exception ValueError If more than one reference and specification is
    provided, but they lists are not equal in length, ie: not a 1:1 mapping of
    entities to specs. The abstraction of this interface into the Manager
    class does cursory validation that this is the case before calling this
    function.

    @see FnAssetAPI.specifications
    @see setRelatedReferences()

    """
    raise NotImplementedError


  def setRelatedReferences(self, entityRef, relationshipSpec, relatedRefs,
      context, hostSession, append=True):
    """

    Creates a new relationship between the referenced entities.

    @param append bool, When True (default) new relationships will be added to
    any existing ones. If False, then any existing relationships with the
    supplied specification will first be removed.

    Though getRelatedReferences is an essential call, there is some asymetry
    here, as it is not neccesarily required to be able to setRelatedReferences
    directly. For example, in the case of a 'shot' (as illustrated in the docs
    for getRelatedReferences) - any new shots would be created by registering a
    new @ref FnAssetAPI.specifications.ShotSpecification under the parent, rather
    than using this call. The best way to think of it is that this call is
    reserved for defining relationships between existing assets (Such as
    connecting multiple image sequences published under the same shot, as being
    part of the same render.) and 'register' as being defining the relationship
    between a new asset and some existing one.

    In systems that don't support post-creation adjustment of relationships,
    this can simply be a no-op.

    @exception FnAssetAPI.exceptions.InvalidEntityReference If any supplied
    reference is not recognised by the asset management system.

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
  # The publishing functions allow a Host create entities within the
  # @ref asset_management_system represented by this impementation. The API
  # is designed to accommodate the broad variety of roles that
  # different asset managers embody. Some are 'librarians' that simply
  # catalog the locations of existing media. Others take an active role
  # in both the temporary and long-term paths to items they manage.
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
  # Meta-data, please see @ref entities_specifications_and_metadata
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

    Determines if the asset manager is interested in participating in
    interactions with the specified type of @ref Entity.

    For example, a Host may call this in order to see if it would
    like to manage the path of a scene file whilst choosing a destination to
    save to.

    This information is then used to determine which options should be
    presented to the user. For example, if kIgnored was returned for a query as
    to the management of scene files, a Host will hide or disable menu items
    that relate to publish or loading of assetised scene files.

    Calls with an accompanying @ref entity_reference may be used to prevent
    users from attempting to perform an asset-action that is not supported by
    the asset management system.

    @note One very important attribute returned as part of this policy is the
    @ref FnAssetAPI.constants.kWillManagePath bit. If set, this instructs the Host
    that the asset management system will manage the path use for the creation
    of any new assets. When set, @ref preflight will be called before any file
    creation to allow the asset management system to determine and prepare the
    work path. If this bit if off, then only @ref register will ever be called,
    and the user will be tasked with determining where new files should be
    located. In many cases, this greatly reduces the sophisticaion of the
    integration as registering the asset becomes a partially manual task,
    rather than one that can be fully automated for new assets.

    Additionally, the @ref FnAssetAPI.constants.kSupportsBatchOperations bit is
    important if you want Hosts to call the *Multiple variants of the
    @ref preflight and @ref register methods.

    @param entityRef str, If supplied, then the call should be interpreted as a
    query as to the applicability of the given specification if registered to
    the supplied entity. For example, attempts to register an ImageSpecification
    to an entity reference that refers to the top level project may be
    meaningless, so in this case kIgnored should be returned.

    @return int, a bitfield, see @ref FnAssetAPI.constants

    """
    raise NotImplementedError


  def thumbnailSpecification(self, specification, context, options, hostSession):
    """

    This will be called prior to registration of an asset to determine if the
    asset system would like a thumbnail preparing. Presently, only JPEG
    thumbnails will be generated. The arguments to this call are the same as
    those that will be passed to the register call.

    If a thumbnail is requested, its path will be set in the specfication
    property 'thumbnailPath' passed to a register call at a later date if it
    was possible to create one.

    @param options dict, The thumbnail process can be customised, by setting
    the following keys in the options dict.

      @li kField_PixelWidth ('width') : The pixel width of the thumbnail
      @li kField_PixelHeight ('height') : The pixel height of the thumbnail

    The keys may be set to the default set by the Host. It will try to best
    match the requested specfications, but it should not be assumed that all
    requested properties are honoured.

    @return bool, If True, a Thumbnail is desired by the Manager, if False, the
    host should not waste time making one.

    """
    return False


  def preflight(self, targetEntityRef, entitySpec, context, hostSession):
    """

    Prepares for some work to be done, to the referenced entity.
    The entity referenced may not yet exist (@ref entity_reference). This
    call is designed to allow sanity checking, placeholder creation or
    any other sundry preparatory actions to be carried out.

    Generally, this will be called before register() in any Host that
    creates media, where the return to @ref managementPolicy has the @ref
    FnAssetAPI.constants.kWillManagePath bit set.

    @param targetEntityRef str, a @ref entity_reference that it is desired to
    pubish the forthcoming media to. See the notes in the API documentation for
    the specifics of this.

    @note it is important for the implementation to pay attention to
    FnAssetAPI.contexts.Context.retention, as not all Hosts will support the
    reference changing at this point.

    @return str, An @ref entity_reference, that the host should resolve to
    determine the path to write media too. This may or may not be the same as
    the input reference. A Host should resolve this reference to get the
    working filepath before writing any files.

    @exception FnAssetAPI.exceptions.InvalidEntityReference If any supplied
    reference is not suitable for the supplied specification.

    @exception FnAssetAPI.exceptions.PreflightError if some fatal exception happens
    during preflight, indicating the process should be aborted.

    @exception FnAssetAPI.exceptions.RetryableError If any non-fatal error occurs
    that means the host should re-try from the beginning of any given process.

    @see register()

    """
    return targetEntityRef


  def preflightMultiple(self, targetEntityRefs, entitySpecs, context, hostSession):
    """

    A batch version of @ref preflight, where most arguments are replaced by
    arrays of equal length. Exception behaviour, etc... is the same as per
    preflight, and should be thrown mid way though preflight if necessary.

    This will be used in preference to calling preflight many times in
    succession to allow the implementation to optimise communication with the
    back end asset management system.

    @param context Context, is not replaced with an array in order to
    simplify implementation. Otherwise, transactional handling has the
    potential to be extremely complex if different contexts are allowed.


    @return list str, A list of working entity references.

    """
    result = []
    for t,s in zip(targetEntityRefs, entitySpecs):
      result.append(self.preflight(t, s, context, hostSession))
    return result


  @abc.abstractmethod
  def register(self, stringData, targetEntityRef, entitySpec, context, hostSession):
    """

    Publish an entity to the @ref asset_management_system
    Instructs the implementation to ensure a valid entity exists for the given
    reference and spec. This will be called either in isolation or after
    calling preflight, depending on the nature of the data being published and
    the kWillManagePath bit of the returned @ref managementPolicy.

    @param stringData str, The string that the entity should resolve to if
    passed to a call to resolveEntityReference(). This may be left blank, if
    there is no meaningful string representation of that entity (eg: a
    'sequence' in a hierarchy). This must be stored by the Manager.

    @param targetReference The @ref entity_reference to publish to. It is
    up to the Manager to ensure that this is meaningful, as it is most
    likely implementation specific. For example, if a 'Shot' specification
    is requested to be published to a reference that points to a 'Sequence'
    it makes sense to interpret this as a 'add a shot of this spec to the
    sequence'. For other types of entity, there may be different
    constraints on what makes sense.

    @param entitySpec FnAssetAPI.specifications.EntitySpecification A description
    of the Entity (or 'asset') that is being published. It is *not* required
    for the implementation to store any information contained in the specification,
    though it may choose to use it if it is meaningful. A Host will separately
    call setEntityMetadata() if it wishes to persist any other information in
    the entity.

    @return str, An @ref entity_reference to the 'final' entity created by the
    publish action. It may or may not be the same as targetReference.

    @note it is important for the implementation to pay attention to
    FnAssetAPI.contexts.Context.retention, as not all Hosts will support the
    reference changing at this point.

    @exception FnAssetAPI.exceptions.InvalidEntityReference If any supplied
    reference is not suitable for the supplied specification.

    @exception FnAssetAPI.exceptions.RegistrationError if some fatal exception happens
    during publishing, indicating the process should be aborted.

    @exception FnAssetAPI.exceptions.RetryableError If any non-fatal error occurs
    that means the host should re-try from the beginning of any given process.

    @see preflight()
    @see resolveEntityReference()

    """
    raise NotImplementedError


  def registerMultiple(self, strings, targetEntityRefs, entitySpecs, context, hostSession):
    """

    A batch version of @ref register, where most arguments are replaced by
    arrays of equal length. Exception behaviour, etc... is the same as per
    register, and should be thrown mid way though registration if necessary.

    This will be used in preference to calling register many times in
    succession to allow the implementation to optimise communication with the
    back end asset management system.

    @param context Context, is not replaced with an array in order to
    simplify implementation. Otherwise, transactional handling has the
    potential to be extremely complex if different contexts are allowed.


    @return list str, A list of finalized entity references.

    """
    result = []
    for d,t,s in zip(strings, targetEntityRefs, entitySpecs):
      result.append(self.register(d, t, s, context, hostSession))
    return result


  ## @}


  ##
  # @name Commands
  #
  # The commands mechanism provides a means for Hosts and asset managers to
  # extend functionality of the API, without requiring any new methods.
  #
  # The API represents commands via a @ref
  # FnAssetAPI.specifications.CommandSpecification, which maps to a 'name' and some
  # 'arguments'.
  #
  # @todo Reference any core module commands
  #
  # @{

  def commandSupported(self, commandSpec, context, hostSession):
    """

    Determines if a specified command is supported by the system.

    @return bool, True if the system implements the command, else False.

    @see commandIsSupported()
    @see runCommand()

    """
    return False

  def commandAvailable(self, commandSpec, context, hostSession):
    """

    Determines if specified command is permitted or should succeed in the
    current context.  This call can be used to test whether a command can
    be carried out, generally to provide some meaningful feedback to a user
    so that they don't perform an action that would consequently error.

    For example, the 'checkout' command for an asset may return false here
    if that asset is already checked out by another user, or the current
    user is not allowed to check the asset out.

    @exception FnAssetAPI.exceptions.InvalidCommand If an un-supported command is
    passed.

    @return (bool, str), True if the command should complete stressfully if
    called, False if it is known to fail or is not permitted. The second part
    of the tuple will contain any meaningful information from the system to
    qualify the status.

    @see commandIsSupported()
    @see runCommand()

    """
    msg = "The command '%s' is not supported by the Asset Manager." % commandSpec
    return False, msg

  def runCommand(self, commandSpec, context, hostSession):
    """

    Instructs the asset system to perform the specified command.

    @exception FnAssetAPI.exceptions.InvalidCommand If the command is not
    implemented by the system.

    @exception FnAssetAPI.exceptions.CommandError if any other run-time error
    occurs during execution of the command

    @return Any result of the command.

    @see commandSupported()
    @see commandAvailable()

    """
    msg = "The command '%s' is not supported by this Asset Manager." % commandSpec
    raise exceptions.InvalidCommand(msg)

  ## @}


  ##
  # @name Manager State
  #
  # A single 'task' in a Host, may require more than one interaction with
  # the asset management system.
  #
  # Because the @ref ManagerInterface is largely state-less. To simplify error
  # handling, and allow an implementation to know which interactions are
  # related, this API supports the concept of a @ref manager_state
  # object. This is contained in every @ref Context and passed to relevant
  # calls.
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

    Create a new object to represent the state of the interface and return it
    (or some handle that can be persisted within the context). You are free to
    implement this however you like, as long as it can be uniquely represented
    by the object returned from this function.

    A new state object is created whenever a @ref Context is made by a @ref
    FnAssetAPI.Session.Session.

    This object is then stored in the newly created Context, and is
    consequently available to all the API calls in the ManagerInterface that
    take a Context instance.  The implementation of a ManagerInterface can
    then use this internally to control its behaviour.

    This object is also extracted from the context and passed directly to any
    of the 'transactional' calls in this API.  For more on the transactional
    model in this API, and how these will be called, see the @ref transactions
    Page.

    @param parentState obj, If present, it is to be assumed that the new state
    is considered a 'child' of the supplied state. This may be used when
    creating a child Context for persistence somewhere in a UI, etc... when
    further processing may change the access/retention of the Context. It is
    expected that the Manager will migrate any applicable state components to
    this child context, for example - a timestamp used for 'vlatest'. Hoewver
    is it *not* expected to link the new state with any transaction that is
    open in the parent state. So the returned state should have any open
    transactions.

    @return object, Some object that represents self-contained state of the
    ManagerInterface. This will be passed to future calls and to the
    transactional methods. Presently this can be any hashable object.

    @exceptions FnAssetAPI.exceptions.StateError If for some reason creation
    fails.

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

    Called to indicate the start of a series of connected actions. The aim of a
    transaction is to allow undo/cancellation of all related actions in one
    step. Largely to avoid inconsistent state in the back end. It is important
    though that any queries made to data that has been created or set within
    the transaction, returns the updated or new data.

    For more on the transactional model in this API, and how these functions are
    called, see the @ref transactions Page.

    This will never be called with the same state from multiple
    threads, but may be called with different state objects.

    This method **must** store any persistent state in the supplied
    state object to ensure the API is stateless. It should not store any
    state relating to the transaction within the ManagerInterface instance
    itself.

    @return None

    @exception FnAssetAPI.exceptions.StateError If for some reason the
    action fails.

    @see createState()
    @see finishTransaction()
    @see cancelTransaction()
    @see The @ref transactions page.

    """
    pass


  def finishTransaction(self, state, hostSession):
    """

    Called at the end of a group of actions to inform the ManagerInterface
    that any pending internal management should be finalized.

    For more on the transactional model in this API, and how these functions
    will be called, see the @ref transactions Page.

    This will never be called with the same state from  multiple
    threads, but may be called with different state objects.

    This method **must** only use or store any persistent state from the
    supplied state object to ensure the API is stateless.

    @return None

    @exception FnAssetAPI.exceptions.StateError If for some reason the
    action fails, or finish is called before start.

    @see createState()
    @see startTransaction()
    @see cancelTransaction()
    @see The @ref transactions page.

    """
    pass


  def cancelTransaction(self, state, hostSession):
    """

    Can be called at any point after @ref startTransaction to undo actions and
    reset the transaction state.

    Generally called in response to some fatal error, in order to request
    the implementation to unroll, or revert any changes made since @ref
    startTransaction

    The state should also be re-configured so that it is then safe to
    call @ref startTransaction

    @return Bool True if roll-back was successful, False in all other cases.

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
    ManagerInterface represented by the supplied state object, so that
    can be restored later, or in another process.

    After calling this, the state should be considered frozen, and any further
    cancel/finish calls should throw a @ref FnAssetAPI.exceptions.StateError if
    made without first thawing the stack.

    @return An ASCII compatible string that can be used to restore the
    stack.

    @see thawState()
    @see The @ref transactions page.

    """
    return ""


  def thawState(self, token, hostSession):
    """

    Restores the supplied state object to a previously frozen state.

    @return object A state object, as per createState(), except restored to the
    previous state encapsulated in the token, which is the same string as
    returned by freezeState.

    @exception FnAssetAPI.exceptions.StateError If the supplied token is not
    meaningful, or that a state has already been thawed.

    """
    return None

  ## @}




