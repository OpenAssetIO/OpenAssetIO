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
@namespace openassetio.hostAPI.HostInterface
A single-class module, providing the HostInterface class.
"""

# As this is an abstract base class, there are many of these.
# pylint: disable=unused-argument,no-self-use

__all__ = ['HostInterface']


class HostInterface(object):
    """
    The HostInterface provides an abstraction of the 'caller of the
    API'. Colloquially, we refer to this as the '@ref host'. This may be
    a simple pipeline tool, or a full content creation application.

    The HostInterface provides a generic mechanism for a @ref manager to
    query information about the identity of the host. In future, this
    interface may be extended to include the ability to retrieve
    information about available documents and their known entity
    references.

    In order for a host to use the API, it must provide an
    implementation of the HostInterface to the @ref
    openassetio.hostAPI.Session class upon construction.

    A @ref manager does not call the HostInterface directly, it is
    always accessed via the @ref openassetio.managerAPI.Host wrapper.
    This allows the API to insert suitable house-keeping and auditing
    functionality in between.
    """

    ##
    # @name Host Information
    #
    ## @{

    def identifier(self):
        """
        Returns an identifier that uniquely identifies the Host.

        This may be used by a Manager's @ref
        openassetio.managerAPI.ManagerInterface "ManagerInterface"
        adjust its behavior accordingly. The identifier should be
        unique for any application, but common to all versions.

        The identifier should use only alpha-numeric characters and '.',
        '_' or '-'. We suggest using the "reverse DNS" style, for
        example:

            "com.foundry.katana"

        @return str
        """
        raise NotImplementedError

    def displayName(self):
        """
        Returns a human readable name to be used to reference this
        specific host in user-facing presentations.

            "Katana"

        @return str
        """
        raise NotImplementedError

    def info(self):
        """
        Returns other information that may be useful about this Host.
        This can contain arbitrary key/value pairs. Managers never rely
        directly on any particular keys being set here, but the
        information may be useful for diagnostic or debugging purposes.
        For example:

            { 'version' : '1.1v3' }

        @return Dict[str, pod]

        @todo Definitions for well-known keys such as 'version' etc.
        """
        return {}

    ## @}
