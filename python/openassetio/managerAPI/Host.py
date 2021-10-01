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

from .._core.debug import debugApiCall, Debuggable
from .._core.audit import auditApiCall

from ..hostAPI import HostInterface


__all__ = ['Host']


class Host(Debuggable):
	"""

	The Host object represents the tool or application that created a session with OAIO,
	and wants to query or store information within a @ref manager.

	The Host provides a generalised API to query entities used within a current document
	and its side of the generalised command interface.

	Hosts should never be directly constructed by the Manager's implementation.
	Instead, the @ref HostSession class provided to all manager API entry points
	provides access to the current host through the @ref HostSession.host() method.

	"""
	def __init__(self, hostInterface: HostInterface):
		""""

		@private

		"""
		super(Host, self).__init__()

		self.__impl = hostInterface

		# This can be set to false, to disable API debugging at the per-class level
		self._debugCalls = True

	def __str__(self):
		return self.__impl.getIdentifier()

	def __repr__(self):
		return "Host(%r)" % self.__impl

	def _getInterface(self):
		return self.__impl

	##
	# @name Host Information
	#
	## @{

	@debugApiCall
	@auditApiCall("Host methods")
	def getIdentifier(self):
		"""

		Returns an identifier to uniquely identify the Host.

		The identifier will be different for each tool or application, but common
		to all versions of any one. The identifier will use only alpha-numeric
		characters and '.', '_' or '-', commonly in the form of a 'reverse-DNS'
		style string, for example:

			"uk.co.foundry.katana"

		@return str

		"""
		return self.__impl.getIdentifier()

	@debugApiCall
	@auditApiCall("Host methods")
	def getDisplayName(self):
		"""

		Returns a human readable name to be used to reference this specific host in
		user-facing messaging, for example:

			"Katana"

		"""
		return self.__impl.getDisplayName()

	@debugApiCall
	@auditApiCall("Host methods")
	def getInfo(self):
		"""

		Returns other information that may be useful about the host.
		This can contain arbitrary key/value pairs. There should be no reliance on
		a specific key being supplied by all hosts. The information
		may be more generally useful for diagnostic or debugging purposes.
		For example:

			{ 'version' : '1.1v3' }

		@return Dict[str, pod]

		"""
		return self.__impl.getInfo()

	## @}

	##
	# @name Commands
	#
	# The commands mechanism provides a means for Hosts and asset managers to
	# extend functionality of the API, without requiring any new methods.
	#
	# The  API represents commands via a @ref
	# FnAssetAPI.specifications.CommandSpecification, which maps to a 'name' and some
	# 'arguments'.
	#
	## @{

	@debugApiCall
	@auditApiCall("Host methods")
	def commandSupported(self, command, context):
		"""

		Determines if a specified command is supported by the Host.

		@return bool, True if the Host implements the command, else False.

		@see commandIsSupported()
		@see runCommand()

		"""
		return self.__impl.commandSupported(command, context)

	@debugApiCall
	@auditApiCall("Host methods")
	def commandAvailable(self, command, context):
		"""
		iteritems

		Determines if specified command is permitted or should succeed in the
		current context. This call can be used to test whether a command can
		be carried out, generally to provide some meaningful feedback to a user
		so that they don't perform an action that would consequently error.

		@exception FnAssetAPI.exceptions.InvalidCommand If an un-supported command is
		passed.

		@return (bool, str), True if the command should complete successfully if
		called, False if it is known to fail or is not permitted. The second part
		of the tuple will contain any meaningful information from the host to
		qualify the status.

		@see commandIsSupported()
		@see runCommand()

		"""
		return self.__impl.commandAvailable(command, context)

	@debugApiCall
	@auditApiCall("Host methods")
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
		return self.__impl.runCommand(command, context)

	## @}

	@debugApiCall
	@auditApiCall("Host methods")
	def getDocumentReference(self):
		"""

		The path, or @ref entity_reference of the current document, or
		an empty string if not applicable. If a Host supports multiple concurrent
		documents, it will be the 'frontmost' one. If there is no meaningful
		document reference, then an empty string will be returned.

		@return str

		"""
		return self.__impl.getDocumentReference()

	##
	# @name Entity Reference retrieval
	#
	## @{

	@debugApiCall
	@auditApiCall("Host methods")
	def getKnownEntityReferences(self, specification=None):
		"""

		@return list, An @ref entity_reference for each Entities known by the host
		to be used in the current document, or an empty list if none are known.

		@param specification FnAssetAPI.specifications.Specification [None] If
		supplied, then only entities of the supplied specification will be
		returned.

		"""
		return self.__impl.getKnownEntityReferences(specification=specification)
