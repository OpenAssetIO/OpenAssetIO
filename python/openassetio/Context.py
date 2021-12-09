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
A single-class module, providing the Context class.
"""

from .specifications import LocaleSpecification
from .constants import kSupportedAttributeTypes


__all__ = ['Context']


class Context(object):
    """
    The Context object is used to convey information about the calling
    environment to a @ref manager. It encapsulates several key access
    properties, as well as providing additional information about the
    @ref host that may be useful to the @ref manager to decorate or
    extend the attributes associated with the stored @ref entity.

    A Manager will also use this information to ensure it presents the
    correct UI, or behavior.

    The Context is passed to many calls in this API, and it may, or may
    not need to be used directly.

    @warning Contexts should never be directly constructed. Hosts should
    use @ref openassetio.hostAPI.Session.Session.createContext. A
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

    def __init__(
            self, access=kRead, retention=kTransient, locale=None,
            managerOptions=None, managerState=None, actionGroupDepth=0):

        super(Context, self).__init__()

        self.__access = access
        self.__retention = retention
        self.__locale = locale

        self.__managerOptions = managerOptions if managerOptions else {}
        self.__managerState = managerState

        self.__actionGroupDepth = actionGroupDepth

    def __getManagerInterfaceState(self):
        """
        The opaque state token owned by the @ref manager, used to
        correlate all API calls made using this context.

        @see @ref stable_resolution
        """
        return self.__managerState

    def __setManagerInterfaceState(self, state):
        self.__managerState = state

    managerInterfaceState = property(__getManagerInterfaceState, __setManagerInterfaceState)

    def __getManagerOptions(self):
        """
        The manager options may contain custom locale data specific to
        your implementation. You should never attempt to set this your
        self, it will not be preserved in many situations by many hosts.
        Instead, the host will ask you for this information on occasions
        that it can be suitable propagated to other API calls. This will
        be generally be done using a @ref
        openassetio-ui.widgets.ManagerOptionsWidget.
        """
        return self.__managerOptions

    def __setManagerOptions(self, options):

        if options is None or not isinstance(options, dict):
            raise ValueError("The managerOptions must be a dict (not %s)" % type(options))

        for key, value in options.items():
            if type(value) not in kSupportedAttributeTypes:
                raise ValueError(
                    ("Manager Options '%s' is not of a " +
                     "supported type '%s' must be %s")
                    % (key, type(value), kSupportedAttributeTypes))

        self.__managerOptions = options

    managerOptions = property(__getManagerOptions, __setManagerOptions)

    def __getActionGroupDepth(self):
        """
        @protected
        Defines the number of action groups in the stack managed by the @ref
        openassetio.hostAPI.transactions.TransactionCoordinator "TransactionCoordinator".
        @todo https://github.com/TheFoundryVisionmongers/OpenAssetIO/issues/135
        """
        return self.__actionGroupDepth

    def __setActionGroupDepth(self, depth):
        self.__actionGroupDepth = depth

    actionGroupDepth = property(__getActionGroupDepth, __setActionGroupDepth)

    def __getAccess(self):
        """
        This covers what the @ref host is intending to do with the data.
        For example, when passed to resolveEntityReference, it infers if
        the @ref host is about to read or write. When configuring a
        BrowserWidget, then it will hint as to whether the Host is
        wanting to choose a new file name to save, or open an existing
        one.
        """
        return self.__access

    def __setAccess(self, access):
        if access not in self.__validAccess:
            raise ValueError(
                "'%s' is not a valid Access Pattern (%s)"
                % (access, ", ".join(self.__validAccess)))
        self.__access = access

    access = property(__getAccess, __setAccess)

    def __getRetention(self):
        """
        This is a concession to the fact that it's not always possible
        to fully implement the spec of this API. For example, @ref
        openassetio.managerAPI.ManagerInterface.ManagerInterface.register
        "Manager.register()" can return an @ref entity_reference that
        points to the newly published @ref entity. This is often not the
        same as the reference that was passed to the call. The Host is
        expected to store this new reference for future use. For example
        in the case of a Scene File added to an 'open recent' menu. A
        Manager may rely on this to ensure a reference that points to a
        specific version is used in the future. In some cases - such as
        batch rendering of an image sequence, it may not be possible to
        store this final reference, due to constraints of the
        distributed natured of such a render. Often, it is not actually
        of consequence. To allow the @ref manager to handle these
        situations correctly, Hosts are required to set this property to
        reflect their ability to persist this information.
        """
        return self.__retention

    def __setRetention(self, retention):
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

    retention = property(__getRetention, __setRetention)

    def __getLocale(self):
        """
        In many situations, the Specification of the desired @ref entity
        itself is not entirely sufficient information to realize many
        functions that a @ref Manager wishes to implement. For example,
        when determining the final file path for an Image that is about
        to be published - knowing it came from a render catalog, rather
        than a 'Write node' from a comp tree could result in different
        behavior.

        The Locale uses a @ref
        openassetio.specifications.LocaleSpecification to describe in
        more detail, what specific part of a @ref host is requesting an
        action. In the case of a file browser for example, it may also
        include information such as whether or not multi-selection is
        required.
        """
        return self.__locale

    def __setLocale(self, locale):
        if locale is not None and not isinstance(locale, LocaleSpecification):
            raise ValueError(
                "Locale must be an instance of %s (not %s)"
                % (LocaleSpecification, type(locale)))
        self.__locale = locale

    locale = property(__getLocale, __setLocale)

    def __str__(self):
        data = (
            ('access', self.__access),
            ('retention', self.kRetentionNames[self.__retention]),
            ('locale', self.__locale),
            ('managerOptions', self.__managerOptions),
            ('managerState', self.__managerState),
            ('actionGroupDepth', self.__actionGroupDepth)
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
