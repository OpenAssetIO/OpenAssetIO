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

from .._core.audit import auditApiCall
from ..exceptions import InvalidCommand


__all__ = ['HostInterface']


class HostInterface(object):
  """

  The HostInterface provides an abstraction of the 'caller of the API'.
  Colloquially, we refer to this as the '@ref host'. This may be a simple
  pipeline tool, or a full content creation application.

  The HostInterface provides a generic mechanism for a @ref manager
  to query information about the identity of the host, its available
  documents and the @ref entities they may reference.

  In order for a host to use the API, it must provide an implementation
  of the HostInterface to the @ref openassetio.hostAPI.Session class
  upon construction.

  A @ref manager does not call the HostInterface directly, it is always
  accessed via the @ref openassetio.managerAPI.Host wrapper. This allows the
  API to insert suitable house-keeping and auditing functionality in between.

  """

  def __init__(self):
    super(HostInterface, self).__init__()

  ##
  # @name Host Information
  #
  ## @{

  @auditApiCall("HostInterface")
  def getIdentifier(self):
    """

    Returns an identifier that uniquely identifies the Host.

    This may be used by a Manager's @ref ManagerInterface adjust its behaviour
    accordingly. The identifier should be unique for any application, but
    common to all versions.

    The identifier should use only alpha-numeric characters and '.', '_' or '-'.
    We suggest using the "reverse DNS" style, for example:

        "com.foundry.katana"

    @return str

    """
    raise NotImplementedError


  @auditApiCall("HostInterface")
  def getDisplayName(self):
    """

    Returns a human readable name to be used to reference this specific
    host in user-facing presentations.

        "Katana"

	@return str

    """
    raise NotImplementedError


  @auditApiCall("HostInterface")
  def getInfo(self):
    """

	Returns other information that may be useful about this Host.  This can
	contain arbitrary key/value pairs. Managers never rely directly on any
	particular keys being set here, but the information may be useful for
	diagnostic or debugging purposes. For example:

        { 'version' : '1.1v3' }

    @return Dict[str, pod]

    @todo Definitions for well-known keys such as 'version' etc.

    """
    return {}


  ## @}


  ##
  # @name Commands
  #
  # The commands mechanism provides a means for hosts and managers to
  # extend functionality of the API, without requiring any new methods.
  #
  # The  API represents commands via a @ref
  # FnAssetAPI.specifications.CommandSpecification, which maps to a 'name' and
  # some 'arguments'.
  #
  ## @{

  @auditApiCall("HostInterface")
  def commandSupported(self, command, context):
    """

    Determines if a specified command is supported by the Host.

    @return bool, True if the Host implements the command, else False.

    @see commandIsSupported()
    @see runCommand()

    """
    return False


  @auditApiCall("HostInterface")
  def commandAvailable(self, command, context):
    """

    Determines if specified command is permitted or should succeed in the
    current context. This call can be used to test whether a command can
    be carried out, generally to provide some meaningful feedback to a user
    so that they don't perform an action that would consequently error.

    For example, the 'checkout' command for an asset may return false here
    if that asset is already checked out by another user, or the current
    user is not allowed to check the asset out.

    @exception FnAssetAPI.exceptions.InvalidCommand If an un-supported command is
    passed.

    @return (bool, str), True if the command should complete successfully if
    called, False if it is known to fail or is not permitted. The second part
    of the tuple will contain any meaningful information from the system to
    qualify the status.

    @see commandIsSupported()
    @see runCommand()

    """
    return False, "Unsupported command"


  @auditApiCall("HostInterface")
  def runCommand(self, command, context):
    """

    Instructs the Host to perform the specified command.

    @exception FnAssetAPI.exceptions.InvalidCommand If the command is not
    implemented by the system.

    @exception FnAssetAPI.exceptions.CommandError if any other run-time error
    occurs during execution of the command

    @return Any result of the command.

    @see commandSupported()
    @see commandAvailable()

    """
    raise InvalidCommand

  ## @}


  @auditApiCall("HostInterface")
  def getDocumentReference(self):
    """

    Returns the path, or @ref entity_reference of the current document, or
    an empty string if not applicable. If a Host supports multiple concurrent
    documents, it should be the 'front-most' one. If there is no meaningful
    document reference, then an empty string should be returned.

	@todo Update to properly support multiple documents

    @return str A path or @ref entity_reference.

    """
    return ''


  ##
  # @name Entity Reference retrieval
  #
  ## @{

  @auditApiCall("HostInterface")
  def getKnownEntityReferences(self, specification=None):
    """

    Returns an @ref entity_reference for each Entities known to the host
    that are used in the current document, or an empty list if none are known.

    @param specification FnAssetAPI.specifications.Specification [None] If
    supplied, then only entities of the supplied specification should be
    returned.

    @return List[str] @ref entity_references discovered in the current document.

	@todo Update to support multiple documents

    """
    return []


  @auditApiCall("HostInterface")
  def getEntityReferenceForItem(self, item, allowRelated=False):
    """

    This should be capable of taking any item that may be set in a
    locale/etc... or a Host-native API object and returning an @ref
    entity_reference for it, if applicable.

    @param allowRelated bool, If True, the Host can return a reference for some
    parent or child or relation of the supplied item, if applicable. This can
    be useful for broadening the area of search in less specific cases.

    @return str, An @ref entity_reference of an empty string if no applicable
    Entity Reference could be determined for the supplied item.

    @todo Update to support multiple documents

    """
    return ''

  ## @}
