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
@namespace openassetio.hostAPI.Session
A single-class module, providing the Session class.
"""

from .._core.debug import debugApiCall, Debuggable
from .._core.audit import auditApiCall

from .HostInterface import HostInterface
from .Manager import Manager

from ..managerAPI import Host, HostSession

from .. import constants
from ..Context import Context
from ..exceptions import ManagerException


__all__ = ['Session']


class Session(Debuggable):
    """
    The Session is the primary mechanism for managing the lifetime of a
    Manager. A Session should be constructed and persisted for each
    individual Manager a host wishes to communicate with.

    The useManager() function defines which Manager a session should
    use, and allows the current manager to be switched, deallocating the
    old one.

    Session settings can be saved and recalled, this includes the active
    manager and it's settings. This can be useful for persisting the
    configuration across host process invocations.

    @see @ref getSettings
    @see @ref setSettings

    The Session class is suitable for all Hosts, but in cases where a UI
    is presented to the user, it may be desirable to use the UISession
    instead, as it permits access to a Managers widgets etc...

    @see @needsref openassetio-ui.UISession
    """

    def __init__(self, hostInterface, logger, managerFactory):
        # pylint: disable=line-too-long
        """
        @param hostInterface openassetio.hostAPI.HostInterface The current
        HostInterface instance (note: only a single currently active
        HostInterface is supported, so if multiple sessions are created,
        they should all use the same HostInterface instance).

        @param logger openassetio.logging.LoggerInterface The target for
        all logging output from the session API-level or Manager level
        messages will all be routed through this object. No severity
        filtering is performed. Hosts wishing to filter the messages can
        use the @ref openassetio.logging.SeverityFilter wrapper if
        desired.

        @param managerFactory
        openassetio.hostAPI.ManagerFactoryInterface An in stance of some
        factory that will provide instances of a manager's
        ManagerInterface as required by the session.

          @see @ref useManager
          @see @ref currentManager
          @see @ref openassetio.logging "logging"
          @see @ref openassetio.hostAPI.ManagerFactoryInterface
          "ManagerFactoryInterface"
          @see @ref openassetio.pluginSystem.PluginSystemManagerFactory
          "PluginSystemManagerFactory"
        """
        super(Session, self).__init__()

        if not isinstance(hostInterface, HostInterface):
            raise ValueError(
                ("The supplied host must be a HostInterface derived " +
                 "class (%s)") % type(hostInterface))

        self._debugLogFn = logger.log

        ## @todo Should we wrap this here, let the Manager do that? Doing it here
        # as it means that auditing will account any use of the Host, not just via the Manager
        self._host = Host(hostInterface)
        self._host._debugLogFn = logger.log

        self._logger = logger

        self._managerId = None
        self._managerSettings = None

        self._manager = None

        self._factory = managerFactory

    @auditApiCall("Session")
    def host(self):
        """
        @return HostInterface, the HostInterface that the session was
        started by.
        """
        return self._host

    @debugApiCall
    @auditApiCall("Session")
    def registeredManagers(self):
        # pylint: disable=line-too-long
        """
        @see @ref openassetio.pluginSystem.PluginSystemManagerFactory.PluginSystemManagerFactory.managers "managers"
        """
        return self._factory.managers()

    @auditApiCall("Session")
    def useManager(self, identifier, settings=None):
        """
        Configures the session to use the @ref manager with the
        specified identifier. The managerChanged Event is triggered if
        the resulting Manager is different to the previous one.

        @param identifier str The Identifier for the desired manager,
        available from @ref registeredManagers.

        @param settings dict [None], Any settings to pass to the managed
        before calling initialize. This will be shallow-copied and
        retained in order to support deferred initialization of the
        Manager.

        @note The Manager not instantiated until @ref currentManager()
        is actually called. If the supplied identifier matches the
        current manager, then the call is ignored.
        """

        if identifier and not self._factory.managerRegistered(identifier):
            raise ManagerException("Unknown Manager '%s'" % identifier)

        # No need to do anything if its the same
        ## @todo [tc] If we want to keep `settings` as part of this method
        ## (so a deferred constructed manager can have its settings set)
        ## then we should make sure the following does actually apply the
        ## settings:
        ##     useManager(an_id)
        ##     useManager(an_id, setting=some_settings)
        ## Right now, this won't happen, and the settings will be lost.
        if identifier == self._managerId:
            return

        self._managerId = identifier
        self._managerSettings = dict(settings) if settings else None
        self._manager = None

    def currentManager(self):
        """
        @return Manager, an instance of the Manager that has been set
        for this session using @ref useManager(). This will be lazily
        constructed the first time this function is called, then
        retained.
        """
        if not self._managerId:
            return None

        # Cache this internally to avoid double initializations
        if not self._manager:
            interface = self._factory.instantiate(self._managerId)
            self._manager = Manager(interface, self._hostSession())
            self._manager._debugLogFn = self._debugLogFn  # pylint: disable=protected-access
            if self._managerSettings:
                self._manager.setSettings(self._managerSettings)
            self._manager.initialize()

        return self._manager

    @auditApiCall("Session")
    def createContext(self, parent=None):
        """
        Creates a new Context with the Session's current Manager.

        @warning Contexts should never be directly constructed, always
        use this method to create a new one.

        @param parent openassetio.Context If supplied, the new context
        will clone the supplied Context, and the Manager will be given a
        chance to migrate any meaningful state etc... This can be useful
        when certain UI elements need to 'take a copy' of a context in
        its current state. It is not linked to the parent's transaction
        if one has been created in the parent. The lifetime of any
        context's transactions are only ever controlled by the context
        that created them.

        @see @ref openassetio.Context.Context "Context"

        @exception RuntimeError if called when the session has no
        current manager.
        """
        ctx = Context()

        # If we have a parent, copy its setup
        if parent:
            ctx.access = parent.access
            ctx.retention = parent.retention
            ctx.locale = parent.locale
            ctx.managerOptions = parent.managerOptions

        manager = self.currentManager()
        if manager is None:
            raise RuntimeError("Session.createContext called with no current manager")

        parentState = None
        if parent:
            parentState = parent.managerInterfaceState

        # pylint: disable=protected-access
        ctx.managerInterfaceState = manager._createState(parentState)
        ctx.actionGroupDepth = 0

        return ctx

    @auditApiCall("Session")
    def getSettings(self):
        """
        A convenience for persisting a session. It retrieves all session
        settings, and the manager's settings in one dictionary. The @ref
        openassetio.constants.kSetting_ManagerIdentifier key is used to
        hold the identifier of the active manager.

        @return dict
        """
        settings = {}

        manager = self.currentManager()
        if manager:
            settings.update(manager.getSettings())

        settings[constants.kSetting_ManagerIdentifier] = self._managerId
        return settings

    @auditApiCall("Session")
    def setSettings(self, settingsDict):
        """
        A convenience to restore the settings for a Session, the @ref
        openassetio.constants.kSetting_ManagerIdentifier key is used to
        determine which Manager to instantiate. All other keys are
        passed to the Manager prior to initialization. If the Manager
        Identifier key is not present, no manager will be restored.
        """

        managerIdentifier = settingsDict.get(constants.kSetting_ManagerIdentifier, None)
        if managerIdentifier:
            settingsDict = dict(settingsDict)
            del settingsDict[constants.kSetting_ManagerIdentifier]
        self.useManager(managerIdentifier, settingsDict)

    def _hostSession(self):
        """
        @returns a openassetio.managerAPI.HostSession object to proxy
        this session.
        """
        return HostSession(self._host, self._logger)
