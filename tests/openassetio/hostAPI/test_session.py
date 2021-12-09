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
Tests that cover the openassetio.hostAPI.Session class.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest
from unittest import mock

from openassetio import constants, exceptions, logging, Context
from openassetio.specifications import LocaleSpecification
from openassetio.hostAPI import Session, HostInterface, Manager, ManagerFactoryInterface
from openassetio.managerAPI import Host, ManagerInterface


@pytest.fixture
def mock_host_interface():
    return mock.create_autospec(spec=HostInterface)


@pytest.fixture
def mock_manager_interface():
    return mock.create_autospec(spec=ManagerInterface)


@pytest.fixture
def mock_manager_factory(mock_manager_interface):
    factory = mock.create_autospec(spec=ManagerFactoryInterface)
    factory.instantiate.return_value = mock_manager_interface
    return factory


@pytest.fixture
def mock_logger():
    return mock.create_autospec(spec=logging.LoggerInterface)


@pytest.fixture
def a_session(mock_host_interface, mock_logger, mock_manager_factory):
    return Session(mock_host_interface, mock_logger, mock_manager_factory)


class TestSession():

    def test_constructor(self, a_session, mock_logger, mock_manager_factory):
        assert a_session._debugLogFn is mock_logger.log
        with pytest.raises(ValueError):
            Session(None, mock_logger, mock_manager_factory)
        with pytest.raises(ValueError):
            Session(mock_logger, mock_logger, mock_manager_factory)

    def test_host(self, a_session, mock_host_interface):
        host = a_session.host()
        assert isinstance(host, Host)
        assert host._interface() is mock_host_interface
        assert host._debugLogFn is a_session._debugLogFn

    def test_registeredManagers(self, a_session, mock_manager_factory):
        mock_manager_factory.managers.assert_not_called()
        assert a_session.registeredManagers() == mock_manager_factory.managers.return_value
        mock_manager_factory.managers.assert_called_once_with()

    def test_useManager(self, a_session, mock_manager_factory):
        # Not testing lifetime management of manager instances here in too much detail
        # As this isn't set in stone, and will change with the `cpp` implementation.

        # Not testing the EventManager here as this is to be split from the core API.

        an_id = "com.manager"

        # Valid ID

        mock_manager_factory.managerRegistered.return_value = True

        a_session.useManager(an_id)

        mock_manager_factory.managerRegistered.assert_called_once_with(an_id)
        mock_manager_factory.instantiate.assert_not_called()
        mock_manager_factory.managerRegistered.reset_mock()

        # Invalid ID

        mock_manager_factory.managerRegistered.return_value = False

        with pytest.raises(exceptions.ManagerError):
            a_session.useManager(an_id)

        mock_manager_factory.managerRegistered.assert_called_once_with(an_id)
        mock_manager_factory.instantiate.assert_not_called()
        mock_manager_factory.managerRegistered.reset_mock()

    def test_currentManager(self, a_session, mock_manager_factory, mock_manager_interface):
        # Not testing lifetime management of manager instances here in too much detail
        # As this isn't set in stone, and will change with the `cpp` implementation.

        assert a_session.currentManager() is None
        mock_manager_factory.assert_not_called()

        an_id = "com.manager"
        a_session.useManager(an_id)

        # Test first initialisation of new manager id

        manager = a_session.currentManager()

        assert isinstance(manager, Manager)
        assert manager._interface() is mock_manager_interface
        assert manager._debugLogFn is a_session._debugLogFn
        mock_manager_factory.instantiate.assert_called_once_with(an_id)
        mock_manager_interface.initialize.assert_called_once()
        mock_manager_interface.setSettings.assert_not_called()
        mock_manager_factory.reset_mock()

        # Test re-use of previous instance when manager not changed

        assert a_session.currentManager() is manager
        mock_manager_factory.instantiate.assert_not_called()

        # Test changing manager id

        another_id = "com.manager.b"

        a_session.useManager(another_id)

        mock_manager_factory.instantiate.assert_not_called()
        manager_b = a_session.currentManager()
        assert manager_b is not manager
        assert manager_b._interface() is mock_manager_interface
        assert manager_b._debugLogFn is a_session._debugLogFn
        mock_manager_factory.instantiate.assert_called_once_with(another_id)
        mock_manager_interface.initialize.assert_called_once()
        mock_manager_factory.reset_mock()

        # Test changing manager with settings

        some_settings = {"k": "v"}
        a_session.useManager(an_id, settings=some_settings)

        mock_manager_factory.instantiate.assert_not_called()
        mock_manager_interface.setSettings.assert_not_called()

        manager_c = a_session.currentManager()

        mock_manager_factory.instantiate.assert_called_once_with(an_id)
        mock_manager_interface.initialize.assert_called_once()
        mock_manager_interface.setSettings.assert_called_once()
        mock_manager_interface.setSettings.call_args[0][0] is some_settings
        mock_manager_factory.reset_mock()

    def test_createContext(self, a_session, mock_manager_interface):
        # No active manager

        with pytest.raises(RuntimeError):
            some_context = a_session.createContext()

        mock_manager_interface.createState.assert_not_called()

        # With an active manager

        a_session.useManager("com.manager")

        state_a = "state-a"
        mock_manager_interface.createState.return_value = state_a

        context_a = a_session.createContext()

        assert context_a.access == Context.kRead
        assert context_a.retention == Context.kTransient
        assert context_a.managerInterfaceState is state_a
        assert context_a.actionGroupDepth == 0
        assert context_a.locale is None
        mock_manager_interface.createState.assert_called_once()
        mock_manager_interface.reset_mock()

        # Child contexts

        context_a.access = Context.kWrite
        context_a.retention = Context.kSession
        context_a.locale = LocaleSpecification()
        context_a.actionGroupDepth = 3

        state_b = "state-b"
        mock_manager_interface.createState.return_value = state_b
        ## @todo We should spy on the Manager instead of this fudgery
        a_host_session = a_session.currentManager()._Manager__hostSession

        context_b = a_session.createContext(parent=context_a)

        assert context_b is not context_a
        assert context_b.managerInterfaceState is state_b
        assert context_b.access == context_a.access
        assert context_b.retention == context_a.retention
        assert context_b.locale == context_b.locale
        assert context_b.actionGroupDepth == 0
        mock_manager_interface.createState.assert_called_once_with(
            a_host_session, parentState=state_a)

    def test_getSettings(self, a_session, mock_manager_interface):
        settings = a_session.getSettings()
        assert settings == {constants.kSetting_ManagerIdentifier: None}

        an_id = "com.manager"
        some_manager_settings = {"k": "v"}
        mock_manager_interface.getSettings.return_value = some_manager_settings
        expected_settings = dict(some_manager_settings)
        expected_settings.update({constants.kSetting_ManagerIdentifier: an_id})

        a_session.useManager(an_id)

        assert a_session.getSettings() == expected_settings
        mock_manager_interface.getSettings.assert_called_once()

    def test_setSettings(self, a_session, mock_manager_interface, mock_manager_factory):
        an_id = "com.manager"
        manager_settings = {"k": "v"}
        some_settings = {constants.kSetting_ManagerIdentifier: an_id}
        some_settings.update(manager_settings)

        a_session.setSettings(some_settings)

        mock_manager_factory.instantiate.assert_not_called()
        mock_manager_interface.setSettings.assert_not_called()

        _ = a_session.currentManager()

        mock_manager_factory.instantiate.assert_called_once_with(an_id)
        mock_manager_interface.setSettings.assert_called_once()
        assert mock_manager_interface.setSettings.call_args[0][0] == manager_settings
