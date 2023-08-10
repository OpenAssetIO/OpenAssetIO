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
        strings used in a host's UI/messages.

        See @ref openassetio.hostApi.terminology "terminology" for known
        keys. The values in stringDict can be freely updated to match
        the terminology of the asset management system you are
        representing.

        For example, you may way a host's "Publish Clip" menu item to
        read "Release Clip", so you would set the @ref openassetio.hostApi.terminology.kTerm_Publish
        value to "Release".

        @return `None`

        @see @ref openassetio.hostApi.terminology.defaultTerminology
        "terminology.defaultTerminology"

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
        trait_set of a 'ShotSpecification' with access 'kWrite'.
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
