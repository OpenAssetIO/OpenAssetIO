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
@namespace openassetio.Context
A single-class module, providing the Context class.
"""

# Import from the cmodule directly to avoid a cyclic dependency on
# openassetio, which also hoists Context.
from ._openassetio import TraitsData # pylint: disable=import-error
from .constants import kSupportedAttributeTypes


__all__ = ['Context']


class Context(object):
    """
    The Context object is used to convey information about the calling
    environment to a @ref manager. It encapsulates several key access
    properties, as well as providing additional information about the
    @ref host that may be useful to the @ref manager.

    A Manager will also use this information to ensure it presents the
    correct UI, or behavior.

    The Context is passed to many calls in this API, and it may, or may
    not need to be used directly.

    @warning Contexts should never be directly constructed. Hosts should
    use @ref openassetio.hostAPI.Manager.Manager.createContext. A
    Manager implementation should never need to create a context of it's
    own, one will always be supplied through the ManagerInterface entry
    points.
    """

    ##
    # @name Access Pattern
    # @{
    kRead = "read"
    kReadMultiple = "readMultiple"
    kWrite = "write"
    kWriteMultiple = "writeMultiple"
    kOther = "other"
    ## @}

    __validAccess = (kRead, kReadMultiple, kWrite, kWriteMultiple, kOther)

    ##
    # @name Data Retention
    # @{

    ## Data will not be used
    kIgnored = 0
    ## Data will be re-used during a particular action
    kTransient = 1
    ## Data will be stored and re-used for the session
    kSession = 2
    ## Data will be permanently stored in the document
    kPermanent = 3

    kRetentionNames = ["ignored", "transient", "session", "permanent"]

    ## @}

    def __init__(self, access=kRead, retention=kTransient, locale=None, managerState=None):

        super(Context, self).__init__()

        self.__access = access
        self.__retention = retention
        self.__locale = locale

        self.__managerState = managerState

    def __getManagerInterfaceState(self):
        # pylint: disable=unused-private-member
        return self.__managerState

    def __setManagerInterfaceState(self, state):
        # pylint: disable=unused-private-member
        self.__managerState = state

    ## @property managerInterfaceState
    ##
    ## The opaque state token owned by the @ref manager, used to
    ## correlate all API calls made using this context.
    ##
    ## @see @ref stable_resolution
    managerInterfaceState = property(__getManagerInterfaceState, __setManagerInterfaceState)

    def __getAccess(self):
        # pylint: disable=unused-private-member
        return self.__access

    def __setAccess(self, access):
        # pylint: disable=unused-private-member
        if access not in self.__validAccess:
            raise ValueError(
                "'%s' is not a valid Access Pattern (%s)"
                % (access, ", ".join(self.__validAccess)))
        self.__access = access

    ## @property access
    ##
    ## Describes what the @ref host is intending to do with the data.
    ##
    ## For example, when passed to resolve, it specifies if the @ref
    ## host is about to read or write. When configuring a BrowserWidget,
    ## then it will hint as to whether the Host is wanting to choose a
    ## new file name to save, or open an existing one.
    access = property(__getAccess, __setAccess)

    def __getRetention(self):
        # pylint: disable=unused-private-member
        return self.__retention

    def __setRetention(self, retention):
        # pylint: disable=unused-private-member
        finalVal = -1
        if isinstance(retention, str):
            if retention in self.kRetentionNames:
                finalVal = self.kRetentionNames.index(retention)
        else:
            finalVal = int(retention)
        if finalVal < self.kIgnored or finalVal > self.kPermanent:
            raise ValueError(
                "%i (%s) is not a valid Retention (%s)"
                % (finalVal, retention, ", ".join(self.kRetentionNames)))
        self.__retention = finalVal

    ## @property retention
    ## A concession to the fact that it's not always possible to fully
    ## implement the spec of this API within a @ref host.
    ##
    ## For example, @ref openassetio.managerAPI.ManagerInterface.ManagerInterface.register
    ## "Manager.register()" can return an @ref entity_reference that
    ## points to the newly published @ref entity. This is often not the
    ## same as the reference that was passed to the call. The Host is
    ## expected to store this new reference for future use. For example
    ## in the case of a Scene File added to an 'open recent' menu. A
    ## Manager may rely on this to ensure a reference that points to a
    ## specific version is used in the future.
    ##
    ## In some cases - such as batch rendering of an image sequence,
    ## it may not be possible to store this final reference, due to
    ## constraints of the distributed natured of such a render.
    ## Often, it is not actually of consequence. To allow the @ref manager
    ## to handle these situations correctly, Hosts are required to set
    ## this property to reflect their ability to persist this information.
    retention = property(__getRetention, __setRetention)

    def __getLocale(self):
        # pylint: disable=unused-private-member
        return self.__locale

    def __setLocale(self, locale):
        # pylint: disable=unused-private-member
        if locale is not None and not isinstance(locale, TraitsData):
            raise ValueError(
                "Locale must be an instance of %s (not %s)"
                % (TraitsData, type(locale)))
        self.__locale = locale

    ## @property locale
    ##
    ## In many situations, the @ref trait_set of the desired @ref entity
    ## itself is not entirely sufficient information to realize many
    ## functions that a @ref manager wishes to implement. For example,
    ## when determining the final file path for an Image that is about
    ## to be published - knowing it came from a render catalog, rather
    ## than a 'Write node' from a comp tree could result in different
    ## behavior.
    ##
    ## The Locale uses a @fqref{TraitsData} "TraitsData" to describe in
    ## more detail, what specific part of a @ref host is requesting an
    ## action. In the case of a file browser for example, it may also
    ## include information such as whether or not multi-selection is
    ## required.
    locale = property(__getLocale, __setLocale)

    def __str__(self):
        data = (
            ('access', self.__access),
            ('retention', self.kRetentionNames[self.__retention]),
            ('locale', self.__locale),
            ('managerState', self.__managerState)
        )
        kwargs = ", ".join(["%s=%r" % (i[0], i[1]) for i in data])
        return "Context(%s)" % kwargs

    def __repr__(self):
        return str(self)

    def isForRead(self):
        """
        @return bool, True if the context is any of the 'Read' based
        access patterns. If the access is unknown (context.kOther), then
        False is returned.
        """
        return self.__access in (self.kRead, self.kReadMultiple)

    def isForWrite(self):
        """
        @return bool, True if the context is any of the 'Write' based
        access patterns. If the access is unknown (context.kOther), then
        False is returned.
        """
        return self.__access in (self.kWrite, self.kWriteMultiple)

    def isForMultiple(self):
        """
        @return bool, True if the context is any of the 'Multiple' based
        access patterns. If the access is unknown (context.kOther), then
        False is returned.
        """
        return self.__access in (self.kReadMultiple, self.kWriteMultiple)
