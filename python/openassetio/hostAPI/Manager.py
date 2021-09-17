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

from ..managerAPI.HostSession import HostSession
from ..managerAPI.ManagerInterface import ManagerInterface

from .._core.debug import debugApiCall, Debuggable
from .._core.audit import auditApiCall


__all__ = ['Manager']


class Manager(Debuggable):
  """

  The Manager is the Host facing representation of the @ref
  asset_management_system it wishes to communicate with. Hosts should never use
  the ManagerInterface directly.

  The Manager is the port of call for 'house keeping' and the retrieval of an
  @ref Entity. Often, you may retrieve an Entity and interact with it directly,
  but to get it in the first place, you need the Manager.

  The Manager also provides means to query information about the asset system
  itself, as well as one-liners for resolving one or more @ref entity_reference
  into its @pref primary_string.

  The Manager API is threadsafe and should be callable from multiple threads
  concurrently.

  Managers are light weight to construct, but not necessarily light weight to
  initialize. The informational methods are available pre-initialization, so
  that UI and other display-type queries can be made relatively cheaply. None
  of the Entity-related calls are available until after @ref initialize has
  been called. The following functions may be called prior to initialization:

     @li @ref getIdentifier()
     @li @ref getDisplayName()
     @li @ref getInfo()
     @li @ref localizeStrings()
     @li @ref getSettings()
     @li @ref setSettings()

  @see @ref Entity

  """

  def __init__(self, interfaceInstance, hostSession: HostSession):
    """

    It's rare that a Manager would ever be constructed directly by a Host,
    instead the @ref Session class takes care of their instantiation.

    @param interfaceInstance FnAssetAPI.implementation.ManagerInterface An
    instance of a Manager Interface to wrap.

    @param hostSession FnAssetAPI.implementation.HostSession the host session
    the manager is part of.

    """
    super(Manager, self).__init__()

    if not isinstance(interfaceInstance, ManagerInterface):
      raise ValueError(("A manager can only be instantiated with a "+
        "instance of the ManagerInterface or a derived class (%s)")
        % type(interfaceInstance))

    self.__impl = interfaceInstance
    self.__hostSession = hostSession

    # This can be set to false, to disable API debugging at the per-class level
    self._debugCalls = True


  def __str__(self):
    return self.__impl.getIdentifier()


  def __repr__(self):
    return "Manager(%r)" % self.__impl.getIdentifier()


  def _getInterface(self):
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
  def getIdentifier(self):
    """

    Returns an identifier to uniquely identify the Manager. This identifier is
    used with the Session class to select which Manager to initialize, and so
    can be used as in preferences etc... to persist the chosen Manager.
    The identifier will use only alpha-numeric characters and '.', '_' or '-'.
    For example:

        "uk.co.foundry.beams"

    @return str

    """
    return self.__impl.getIdentifier()


  @debugApiCall
  @auditApiCall("Manager methods")
  def getDisplayName(self):
    """

    Returns a human readable name to be used to reference this specific
    asset manager. This can be useful for user-display purposes.
    For example:

        "The Foundry Better Example Asset Management System"

    """
    return self.__impl.getDisplayName()


  @debugApiCall
  @auditApiCall("Manager methods")
  def getInfo(self):
    """

    Returns other information that may be useful about this @ref
    asset_management_system.  This can contain arbitrary key/value pairs.For
    example:

        { 'version' : '1.1v3', 'server' : 'beams.thefoundry.co.uk' }

    There is no requirement to use any of the information in the info dict, but
    it may be useful for optimisations of display customisation.

    There are certain well-known keys that may be set by the Manager. They
    include things such as:

      @li FnAssetAPI.constants.kField_SmallIcon (upto 32x32)
      @li FnAssetAPI.constants.kField_Icon (any size)
      @li FnAssetAPI.constants.kField_EntityRefrencesMatchPrefix
      @li FnAssetAPI.constants.kField_EntityRefrencesMatchRegex

    Keys will always be UTF8 strings, and Values will be int, bool, float or
    str.

    """
    return self.__impl.getInfo()


  @debugApiCall
  @auditApiCall("Manager methods")
  def localizeStrings(self, stringDict):
    """

    This call gives the Manager a chance to customise certain strings that you
    might want to use in your UI/messages. @see FnAssetAPI.constants for known
    keys. These keys are updated in-place to the most appropriate term for the
    Manager. You should then use these substitutions in any user-facing
    messages or display text so that they feel at home.

    It's rare that you need to call this method as part of Host implementation
    as usually the convenience methods on a Session object should be used
    instead.

    @see @ref FnAssetAPI.localization
    @see @ref FnAssetAPI.localization.Localizer.localizeString
    @see @ref FnAssetAPI.localization.defaultTerminology

    """

    self.__impl.localizeStrings(stringDict, self.__hostSession)
    # So we can see it in the debug log
    return stringDict

  ## @}


  ##
  # @name Initialization
  #
  ## @{

  @debugApiCall
  @auditApiCall("Manager methods")
  def getSettings(self):
    return self.__impl.getSettings(self.__hostSession)

  @debugApiCall
  @auditApiCall("Manager methods")
  def setSettings(self, settings):
    return self.__impl.setSettings(settings, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def initialize(self):
    """

    Prepares the Manager for interaction with a Host. In order to provide light
    weight inspection of available Managers, initial construction is cheap.
    However most system require some kind of handshake or back-end setup in
    order to make Entity-related queries. As such, the @ref initialize method
    is the instruction to the Manager to prepare itself for full interaction.

    If an exception is raised by this call, its is safe to assume that a fatal
    error occurred, and this @ref asset_management_system is not available, and
    should be retried later.

    If no exception is raised, it can be assumed that the @ref
    asset_management_system is ready. It is the implementations responsibility
    to deal with transient connection errors (if applicable) once initialized.

    The behaviour of calling initialize() on an already initialized
    Manager should be a no-op, but if an error was raised previously, then
    initialization will be re-attempted.

    @note This must be called prior to any Entity-related calls or an Exception
    will be raised.

    """
    return self.__impl.initialize(self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def prefetch(self, references, context):
    """

    Because query latency may be high with certain Managers, it is often
    desirable to 'batch' requests. However, in many cases, it is not always
    practical or desirable to adjust the flow of a host application in order to
    facilitate this. The preflight call is designed for these situations. It
    should be called wherever possible by a Host before it makes a series of
    calls to query information about multiple Entities in close proximity. It
    gives the Manager a change to retrieve information in advance.

    The prefetch calls instructs the Manager to retrieve any information needed
    to either resolve, or get metadata from the list of supplied Entities.

    The lifetime of the data is managed by the Manager, as it may have
    mechanisms to auto-dirty any caches. It is *highly* recommended to supply a
    suitably managed Context to this call, as it can be used as the cache, so
    that the cache lifetime is inherently well-managed by your persistence (or
    not) of the context.

    @param references list A list of Entites or @ref entity_reference to
    prefetch data for.

    @param context FnAssetAPI.contexts.Context

    @return None

    """
    if not isinstance(references, (list, tuple)):
      references = [references, ]
    return self.__impl.prefetch(references, context, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def flushCaches(self):
    """

    Clears any internal caches.  Only applicable if the Manager makes use of
    any caching, otherwise it is a no-op.  In caching interfaces, this should
    cause any retained data to be discarded to ensure future queries are fresh.
    This should have no effect on any open @ref transaction.

    """
    return self.__impl.flushCaches(self.__hostSession)

  ## @}


  ##
  # @name Entity Reference inspection
  #
  # Because of the nature of an @ref entity_reference, it is often
  # necessary to determine if some working string is actually an @ref
  # entityReference or not, to ensure it is handled correctly.
  #
  # @{

  @debugApiCall
  @auditApiCall("Manager methods")
  def isEntityReference(self, token, context):
    """

    Determines if a supplied token (in its entirety) matches the pattern of
    an @ref entity_reference.
    It does not verify that it points to a valid entity in the system,
    simply that the pattern of the token is recognised by the Manager.

    If it returns True, the token is an @ref entity_reference and should
    be considered as a managed Entity. Consequently, it should be resolved
    before use. It also confirms that it can be passed to any other
    method that requires an @ref entity_reference.

    If False, this Manager should no longer be involved in actions relating
    to the token.

    @param token The UTF-8 ASCII string to be inspected.

    @return bool, True if the supplied token should be considered as an @ref
    entity_reference, False if the pattern is not recognised.

    @note This call does not verify the entity exits, just that the format of
    the string is recognised.

    @see containsEntityReference
    @see entityExists
    @see resolveEntityReference

    @todo Make use of FnAssetAPI.constants.kField_EntityReferenceMatchPrefix or
    FnAssetAPI.constants.kField_EntityReferenceMatchRegex if supplied,
    especially when bridging between C/FnAssetAPI.

    """
    # We need to add support here for using the supplied prefix match string,
    # or regex, if supplied, instead of calling the manager, this is less
    # relevant in python though, more in C, but the note is here to remind us.
    return self.__impl.isEntityReference(token, context, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def containsEntityReference(self, string, context=None):
    """

    Determines if the string contains a @ref entity_reference.

    There may be occasion to operate on a more complex input string, that
    combines one or more @ref entity_reference and free-form text. It is not
    possible as a Host to isolate these references as the format is not known.
    For example, the following strings should cause isEntityReference()
    to return false, but this function to return true:

    @li `{fnasset://job?t=scriptsDir}/fileInDirectory.nk`
    @li `source fnasset://myScript?v=1 fnasset://myOtherScript?v=2`

    Positive matches here indicate that the string may need to
    be resolved using resolveEntityReferences() prior to use.

    @param str The input to parse for @ref entity_reference occurrences

    @return bool, True if one or more @ref entity_reference is found within the
    string, otherwise False.

    @note This call does not verify that any of the referenced entities exit,
    just that the string contains one or more @ref entity_reference. Often

    @see resolveEntityReferences()

    """
    return self.__impl.containsEntityReference(string, context, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def entityExists(self, reference, context):
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

    The supplied context's locale should be well-configured as it may contain
    information pertinent to disambiguating this subtle definition of 'exists'
    in some cases too, as it better explains the use-case of the call.

    @return bool, True if it points to an existing entity, False if the Entity
    is not known or ready yet.

    @exception FnAssetAPI.exceptions.InvalidEntityReference If the input string is
    not a valid entity reference.

    """
    return self.__impl.entityExists(reference, context, self.__hostSession)

  ## @}


  ##
  # @name Entity Retrieval
  #
  ## @{

  @debugApiCall
  @auditApiCall("Manager methods")
  def getDefaultEntityReference(self, specification, context):
    """

    Returns an @ref entity_reference considered to be a sensible default for
    the given Specification and Context. This can be used to ensure
    dialogs, prompts or publish locations default to some sensible value,
    avoiding the need for a user to re-enter such information.

    @param specification FnAssetAPI.specifications.Specification.Specification The
    relevant specification for an applicable Entity, this will be interpreted
    in conjunction with the context to determine the most sensible default.

    @param context FnAssetAPI.Context.Context The context the resulting reference
    will be used in, particular care should be taken to the access pattern as
    it has great bearing on the resulting meaning.

    @return str, An @ref entity_reference or empty string.

    """
    return self.__impl.getDefaultEntityReference(specification, context, self.__hostSession)

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

  @debugApiCall
  @auditApiCall("Manager methods")
  def getEntityName(self, reference, context):
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
    return self.__impl.getEntityName(reference, context, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def getEntityDisplayName(self, reference, context):
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
    return self.__impl.getEntityDisplayName(reference, context, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def getEntityMetadata(self, reference, context):
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
    return self.__impl.getEntityMetadata(reference, context, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def setEntityMetadata(self, reference, data, context, merge=True):
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
    return self.__impl.setEntityMetadata(reference, data, context, self.__hostSession, merge=merge)


  @debugApiCall
  @auditApiCall("Manager methods")
  def getEntityMetadataEntry(self, reference, key, context, defaultValue=None):
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
    return self.__impl.getEntityMetadataEntry(reference, key, context, self.__hostSession, defaultValue=defaultValue)


  @debugApiCall
  @auditApiCall("Manager methods")
  def setEntityMetadataEntry(self, reference, key, value, context):
    return self.__impl.setEntityMetadataEntry(reference, key, value, context, self.__hostSession)

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

  @debugApiCall
  @auditApiCall("Manager methods")
  def getEntityVersionName(self, reference, context):
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
    return self.__impl.getEntityVersionName(reference, context, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def getEntityVersions(self, reference, context, includeMetaVersions=False, maxResults=-1):
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
    return self.__impl.getEntityVersions(reference, context, self.__hostSession, includeMetaVersions=includeMetaVersions, maxResults=maxResults)


  @debugApiCall
  @auditApiCall("Manager methods")
  def getFinalizedEntityVersion(self, reference, context, overrideVersionName=None):
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
    return self.__impl.getFinalizedEntityVersion(reference, context, self.__hostSession, overrideVersionName=overrideVersionName)

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
  # of this is in an editorial example, where you may need to query whether a
  # 'shot' exists in a certain part of the asset system. One approach would be
  # to use a 'getChildren' call, on this part of the system. This has the
  # drawback that is assumes that shots are always something that can be
  # described as 'immediate children' of the location in question. This lay not
  # always be the case (say, for example there is some kind of 'task' structure
  # in place too). Instead we use a request that asks for any 'shots' that
  # relate to the chosen location. It is then up to the implementation of the
  # ManagerInterface to determine how that maps to its own data model.
  # Hopefully this allows you to work with a broader range of asset
  # managements, without providing any requirements of their structure or data
  # model within the asset system itself.
  #
  # @{

  @debugApiCall
  @auditApiCall("Manager methods")
  def getRelatedEntities(self, references, relationshipSpecOrSpecs, context, resultSpec=None):
    """

    Returns related Entities, based on a relationship specification.

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

    @note The order of entities in the inner lists of matching references
    should not be considered meaningful, but the outer list should match the
    input order.

    In summary, if only a single entityRef is provided, it should be assumed
    that all specs should be considered for that one entity.  If only a single
    relationshipSpec is provided, then it should be considered for all supplied
    entity references. If lists of both are supplied, then they must be the
    same length, and it should be assumed that it is a 1:1 mapping of spec per
    entity. If this is not the case, ValueErrors will be thrown.

    If any specification is unknown, then an empty list will be returned for
    that specificaion, and no errors should be raised.

    @param references list(str) A list of @ref entity_reference,
    see the notes on array length above.

    @param relationshipSpecs FnAssetAPI.specifications.Specification or
    FnAssetAPI.specifications.RelationshipSpecification list

    @param resultSpec FnAssetAPI.specifications.EntitySpecification or None, a hint
    as to what kind of entity the caller is expecting to be returned. May be
    None.

    @return list of str lists The return is *always* a list of lists
    regardless of which form of invocation is used. The outer list is for each
    supplied entity or specification. The inner lists are all the matching
    Entities for that source entity.

    @exception FnAssetAPI.exceptions.InvalidEntityReference If any supplied
    reference is not known by the @ref asset_management_system. However, no
    exception will be thrown if it is a recognised reference, but has no
    applicable relations.

    @exception ValueError If more than one reference and specification is
    provided, but they lists are not equal in length, ie: not a 1:1 mapping of
    entities to specs.

    @see FnAssetAPI.specifications
    @see setRelatedReferences()

    """
    if not isinstance(references, (list, tuple)):
      references = [ references, ]

    if not isinstance(relationshipSpecOrSpecs, (list, tuple)):
      relationshipSpecOrSpecs = [ relationshipSpecOrSpecs, ]

    numEntities = len(references)
    numSpecs = len(relationshipSpecOrSpecs)

    if (numEntities > 1 and numSpecs > 1) and numSpecs != numEntities:
      raise ValueError(("You must supply either a single entity and a "
        +"list of specs, a single spec and a list of entities, or an equal "
        +"number of both... %s entities .vs. %s specs")
            % (numEntities, numSpecs))

    result = self.__impl.getRelatedReferences(references,
        relationshipSpecOrSpecs, context, self.__hostSession, resultSpec=resultSpec)

    return result

  ## @}

  ##
  # @name Entity Resolution
  #
  # The concept of resolution is turning an @ref Entity into a 'finalized' or
  # 'primary' string. This, ultimately, is anything meaningful to the
  # situation. It could be a colour space, a directory, a script or image
  # sequence. A rule of thumb is that a resolved @ref Entity should be the
  # string you would have anyway, in a unmanaged environment. For some kind of
  # Entity - such as a 'Shot', for example, there may not be a meaningful
  # string, though often some sensible return can be made. In these cases its
  # generally unlikely that you would be resolving the Entity in the first
  # place.
  #
  # @{

  @debugApiCall
  @auditApiCall("Manager methods")
  def resolveEntityReference(self, reference, context):
    """

    Returns the primary string held by the Entity pointed to by the supplied
    @ref entity_reference. In general, any substitutions tokens - such as frame
    numbers, views, etc... will remain intact and need handling as if the Asset
    API was never there..

    @note You should always call isEntityReference first if there is any doubt
    as to whether or not the string you have contains a reference, and only
    call resolve if it is a reference recognised by the Mangaer.

    The API defines that all file paths passed though the API that represent
    file sequences should use the 'format' syntax, compatible with sprintf,
    etc... (eg.  %04d").

    @return str, The UTF-8 ASCII compatible string that that is represented by
    the entity.

    @exception FnAssetAPI.exceptions.InvalidEntityReference If the @ref
    entity_reference is not known by the Manager.
    @exception FnAssetAPI.exceptions.EntityResolutionError If the @ref
    entity_reference does not have a meaningful string representation, or if it
    is a valid entity but it does not logically exist in a way required to
    resolve.
    @exception FnAssetAPI.exceptions.InvalidEntityReference if the \ref
    entity_reference should not be resolved for that context, for example, if
    the context access is kWrite and the entity is an existing version - the
    exception means that it is not a valid action to perform on the entity.

    """
    return self.__impl.resolveEntityReference(reference, context, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def resolveEntityReferences(self, refrences, context):
    """

    As-per resolveEntityReference but it will resolve all of the references in
    the supplied list.

    @param references list(str) A list of one or more @ref entity_reference

    @return list(str) A list of resolved references with the same length as the
    input list.

    @see resolveEntityReference for exceptions, etc...

    """
    return self.__impl.resolveEntityReferences(refrences, context, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def resolveInlineEntityReferences(self, string, context):
    """

    Returns a copy of the input string will all references resolved in-place.
    The same rules of resolution apply for each @ref entity_reference in the
    input string as noted in resolveEntityReference().

    If no entity references are present, the input string will be returned.

    @return str

    @exception FnAssetAPI.exceptions.InvalidEntityReference If any supplied
    @ref entity_reference is not recognised by the asset management system.

    @exception FnAssetAPI.exceptions.EntityResolutionError If any supplied @ref
    entity_reference does not have a meaningful string representation, or any
    supplied reference points to a non-existent entity.

    @see resolveEntityReference()
    @see containsEntityReference()

    """
    return self.__impl.resolveInlineEntityReferences(string, context, self.__hostSession)

  ## @}


  ##
  # @name Publishing
  #
  # The publishing functions allow a your application to create entities within
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
  # accompanied by with an spec, that details the file type, colour space,
  # resolution etc...
  #
  # @note The Specification should *not* be confused with @ref metadata.  The
  # Manager will not directly store any information contained within the
  # Specification, though it may be used to better define the type of entity.
  # If you wish to persist other properties of the published entity, you must
  # call @ref setEntityMetadata() directly instead, and as described in the
  # metadata section, this is assumed that this is the channel for information
  # that needs to be stored by the Manager.
  #
  # For more on the relationship between Entities, Specifications and
  # Meta-data, please see @ref entities_specifications_and_metadata
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
  # this API provides the @ref localizeStrings call, in order to allow the
  # Manager to standardise some of the language and terminology used in your
  # presentation of the asset management system with other integrations of the
  # system.
  #
  # *3 - Thumbnails*
  #
  # The API provides a mechanism for a Manager to request a thumbnail for an
  # entity as it is being published. If as a Host you are capable of making a
  # suitable thumbnail for whatever it is you are wanting to publish, you
  # should call @ref thumbnailSpecification. If this returns True, then a
  # thumbnail should be prepared, and saved to disk in some temporary location.
  # It's path should then be set in the 'thumbnailPath' field of the
  # EntitySpecification that you pass to the final register call. If it was not
  # possible to make one, simply leave this field blank.
  #
  # @{

  @debugApiCall
  @auditApiCall("Manager methods")
  def managementPolicy(self, specification, context, entityRef=None):
    """

    Determines if the Manager is interested in participating in
    interactions with the specified type of @ref Entity. It is *vital* to call
    this before attempting to publish/etc... to the Manager, as the entity you
    desire to work with may not be supported.

    For example, a you would call this in order to see if the Manager would
    like to manage the path of a scene file whilst choosing a destination to
    save to.

    This information should then be used to determine which options should be
    presented to the user. For example, if kIgnored was returned for a query as
    to the management of scene files, a you should hide or disable menu items
    that relate to publish or loading of assetised scene files.

    Calls with an accompanying @ref entity_reference should be used when one is
    known, to ensure that the Manager has the opportunity to prohibit users
    from attempting to perform an asset-specific action that is not supported
    by the asset management system.

    @note One very important attribute returned as part of this policy is the
    @ref FnAssetAPI.constants.kWillManagePath bit. If set, you can assume the asset
    management system will manage the path to use for the creation of any new
    assets. you must then always call @ref preflight before any file creation to
    allow the asset management system to determine and prepare the work path,
    and then use this path to write data to, prior to calling @ref register..
    If this bit if off, then you should take care of writing data yourself
    (maybe prompting the user for a location on disk), and then only call @ref
    register to create the new Entity.

    Additionally, if you are ever dealing with multiple assets at one, the @ref
    FnAssetAPI.constants.kSupportsBatchOperations bit is important as it indicates
    that it is beneficial to call the *Multiple variants of the @ref preflight
    and @ref register methods.

    @param entityRef str, If supplied, then the call should be interpreted as a
    query as to the applicability of the given specification if registered to
    the supplied entity. For example, attempts to register an ImageSpecification
    to an entity reference that refers to the top level project may be
    meaningless, so in this case kIgnored would be returned.

    @return int, a bitfield, see @ref FnAssetAPI.constants

    """
    return self.__impl.managementPolicy(specification, context, self.__hostSession, entityRef=entityRef)


  @debugApiCall
  @auditApiCall("Manager methods")
  def thumbnailSpecification(self, specification, context, options):
    """

    This should be called prior to registration of an asset to determine if the
    asset system would like a thumbnail preparing. Presently, only JPEG
    thumbnails will be generated. The arguments to this call should be the same
    as those that will be passed to the register call.

    @param specification FnAssetAPI.specifications.Specification The spec of the
    Entity that is about to be published, etc...

    @param context FnAssetAPI.Context.Context the Context in which the publishing
    will occur.

    @param options dict, A dictionary that will be modifier in place by the
    Manager to reflect the desired thumbnail specification. You may set
    suitable 'defaults' that best fit the host application before making the
    call.

      @li kField_PixelWidth ('width') : The pixel width of the thumbnail
      @li kField_PixelHeight ('height') : The pixel height of the thumbnail

    Best attempts should be made to satisfy the specifications as requested, but
    if it is not possible, return the best possible match.

    @return bool, If True, a Thumbnail is desired by the Manager, if False, the
    host should not waste time making one.

    """
    return self.__impl.thumbnailSpecification(specification, context, options, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def preflight(self, targetEntityRef, entitySpec, context):
    """

    @note This call is only applicable when this Manager you are communicating
    with sets the @ref FnAssetAPI.constants.kWillManagePath bit in response to a
    @ref FnAssetAPI.Manager.Manager.managementPolicy for the Specification of
    Entity you are intending to publish.

    It signals your intent as a Host application to do some work to create a
    file in relation to the supplied @ref entity_reference. This entity does
    not need to exist yet (see @ref entity_reference) or it may be a parent
    entity that you are about to create a child of or some other similar
    relationship (it actually doesn't matter really, as this @ref
    entity_reference will ultimately have been determined by interaction with
    the Manager, and it will have returned you something meaningful).

    It should be called before register() if you are about to create media or
    write to files. If the file or data already exists, then preflight is not
    needed. It will return a working @ref entity_reference that can be
    resolved/etc... in order to determine a working path that the files should
    be written to.

    This call is designed to allow sanity checking, placeholder creation or any
    other sundry preparatory actions to be carried out by the Manager. In the
    case of file-based entites, the Manage may even use this opportunity to
    switch to some temporary working path or some such.

    \note Its vital that the \ref Context is well configured here, in
    particular the 'ref FnAssetAPI.Context.Context.retention "Context.retention".
    See @ref examples_save, but the importance of using the working @ref
    entity_reference, rather than the initial @ref entity_reference is
    essential to proper behaviour.

    @return str, A working @ref entity_reference, that the you should resolve
    to determine the path to write media too. This may or may not be the same
    as the input reference. It should be resolved to get a working file path
    before writing any files.

    @exception FnAssetAPI.exceptions.InvalidEntityReference If the refrence is not
    recognised by the Manager.

    @exception FnAssetAPI.exceptions.PreflightError if some fatal exception happens
    during preflight, this Exception indicates the process should be aborted.

    @exception FnAssetAPI.exceptions.RetryableError If any non-fatal error occurs
    that means the call can be re-tried.

    @see preflightMultiple
    @see register
    @see registerMultiple

    """
    return self.__impl.preflight(targetEntityRef, entitySpec, context, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def preflightMultiple(self, targetReferences, specifications, context):
    """

    A batch version of preflight, taking an array of targets and specs, instead
    of a single pair, and returning an array of references.

    @note It is advisable to only call this if the Manager has set the
    kSupportsBatchOperations bit in the managementPolicy bitfield for the
    applicable EntitySpecification.

    """
    return self.__impl.preflightMultiple(targetReferences, specifications, context, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def register(self, stringData, targetEntityRef, entitySpec, context, metadata=None):
    """

    Register should be used to register a new entity either when originating new
    data within the application process, or referencing some existing file,
    media or information.

    @note The registration call is applicable to all kinds of Manager, as long
    as the @ref FnAssetAPI.constants.kIgnored bit is not set in response to a @ref
    FnAssetAPI.Manager.Manager.managementPolicy for the Specification of entity you
    are intending to publish. In this case, the Manager is saying it doesn't
    handle that Specification of entity, and it should not be registered.

    As the @ref entity_reference has (ultimately) come from the Manager (either
    in response to delegation of UI/etc... or as a return from another call),
    then it can be assumed that the Manager will understand what it means for
    you to call 'register' on this refrence with the supplied Specification. The
    conceptual meaning of the call is:

    "I have this reference you gave me, and I would like to register a new
    entity to it with this Specification, to hold the supplied stringData. I
    trust that this is ok, and you will give me back the reference that
    represents the result of this."

    It is up to the manager to understand the correct result for the particular
    Specification in relation to this reference. For example, if you received
    this reference in response to browsing for a target to 'kWriteMultiple'
    ShotSpecifications, then the Manager should have returned you a reference
    that you can then call register() on multiple times with a
    ShotSpecification without error. Each resulting entity reference should then
    reference the newly created Shot.

    @warning When registering files, it should never be assumed that the
    resulting @ref entity_reference will resolve to the same path. Managers may
    freely relocate, copy move or rename files as part of registration.

    @param stringData str, The @ref primary_string for this entity. It is the
    string the resulting @ref entity_reference will resolve to. In the case of
    file-based entites, this is the file path, and may be further modified by
    Managers that take care of relocating or managing the storage of files. The
    API defines that in the case of paths representing file sequences, frame
    tokens should be left un-subsituted, in a sprintf compatible format, eg.
    "%04d", rather than say, the #### based method. If your application uses
    hashes, or some other scheme, it should be converted to/from the sprintf
    format as part of your integration.

    @param spec FnAssetAPI.specifications.Specfication the EntitySpecification for
    the new registration.

    @see FnAssetAPI.specifications
    @see registerMultiple
    @see preflight
    @see preflightMultiple

    """
    ## At the mo, metatdata is deliberately not passed to register in the
    ## ManagerInterface. This helps ensure that no Manager ever places a
    ## requirement that metadata is known on creation. This is a bad state to
    ## be in, as it places severe limitations on a host so its worth leaving it
    ## this way so people will moan at us if its a problem.
    ## @todo ... but conversely, setMetadata doesn't allow that data to be versioned
    ## This needs revisitiong, as its not even really 'metadata' as we encourage
    ## hosts to treat it as first-class asset data.
    entityRef = self.__impl.register(stringData, targetEntityRef, entitySpec, context, self.__hostSession)
    if metadata and entityRef:
      self.__impl.setEntityMetadata(entityRef, metadata, context, self.__hostSession, merge=True)
    return entityRef


  @debugApiCall
  @auditApiCall("Manager methods")
  def registerMultiple(self, strings, targetReferences, specifications, context):
    """

    A batch version of register - taking equal length arrays of strings,
    targets and specs, returning a list with each @ref entity_reference

    @note It is advisable to only call this if the Manager has set the
    kSupportsBatchOperations bit in the managementPolicy bitfield for the
    applicable EntitySpecification.

    """
    return self.__impl.registerMultiple(strings, targetReferences, specifications, context, self.__hostSession)

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
  # @{

  @debugApiCall
  @auditApiCall("Manager methods")
  def commandSupported(self, command, context):
    """

    Determines if a specified command is supported by the Manager.

    @return bool, True if the Manager implements the command, else False.

    @see commandIsSupported()
    @see runCommand()

    """
    return self.__impl.commandSupported(command, context, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def commandAvailable(self, command, context):
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
    return self.__impl.commandAvailable(command, context, self.__hostSession)


  @debugApiCall
  @auditApiCall("Manager methods")
  def runCommand(self, command, context):
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
    return self.__impl.runCommand(command, context, self.__hostSession)

  ## @}

  ##
  # @name Transaction managemenet
  # These methods should not be used directly outside of the core API code.
  # Always use a @ref FnAssetAPI.transactions.TransactionCoordinator instead.
  ## @{

  @debugApiCall
  @auditApiCall("Manager methods")
  def _startTransaction(self, state):
    """
    @see FnAssetAPI.implementation.ManagerInterface._startTransaction
    """
    return self.__impl.startTransaction(state, self.__hostSession)

  @debugApiCall
  @auditApiCall("Manager methods")
  def _finishTransaction(self, state):
    """
    @see FnAssetAPI.implementation.ManagerInterface._finishTransaction
    """
    return self.__impl.finishTransaction(state, self.__hostSession)

  @debugApiCall
  @auditApiCall("Manager methods")
  def _cancelTransaction(self, state):
    """
	@see FnAssetAPI.implementation.ManagerInterface._cancelTransaction
	"""
    return self.__impl.cancelTransaction(state, self.__hostSession)

  ## @}

  ##
  # @name State Management
  # These methods should not be used directly outside of the core API code.
  # Always use a @ref FnAssetAPI.transactions.TransactionCoordinator instead.
  ## @{

  @debugApiCall
  @auditApiCall("Manager methods")
  def _createState(self, parentState=None):
    """
    @see FnAssetAPI.implementation.ManagerInterface.createState
    """
    return self.__impl.createState(self.__hostSession, parentState=parentState)

  @debugApiCall
  @auditApiCall("Manager methods")
  def _freezeState(self, state):
    """
    @see FnAssetAPI.implementation.ManagerInterface.freezeState
    """
    return self.__impl.freezeState(state, self.__hostSession)

  @debugApiCall
  @auditApiCall("Manager methods")
  def _thawState(self, token):
    """
    @see FnAssetAPI.implementation.ManagerInterface.thawState
    """
    return self.__impl.thawState(token, self.__hostSession)

  ## @}