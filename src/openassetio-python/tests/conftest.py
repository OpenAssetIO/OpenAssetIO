#
#   Copyright 2013-2025 The Foundry Visionmongers Ltd
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
Shared fixtures/code for pytest cases.
"""
# pylint: disable=missing-function-docstring,redefined-outer-name
from unittest import mock
import sys
import os
import sysconfig
import re

import pytest

import openassetio
from openassetio import Context, EntityReference
from openassetio.access import (
    PolicyAccess,
    ResolveAccess,
    RelationsAccess,
    PublishingAccess,
    DefaultEntityAccess,
    EntityTraitsAccess,
)
from openassetio.log import LoggerInterface
from openassetio.managerApi import (
    ManagerInterface,
    Host,
    HostSession,
    EntityReferencePagerInterface,
)
from openassetio.hostApi import HostInterface
from openassetio.trait import TraitsData
from openassetio.ui.managerApi import UIDelegateInterface

# pylint: disable=invalid-name


@pytest.fixture(scope="session")
def regex_matcher():
    return RegexMatch


@pytest.fixture
def unload_openassetio_modules():
    """
    Temporarily removes openassetio modules from the sys.modules cache
    that otherwise mask cyclic dependencies or bleed state from a
    previous test case.

    We restore them afterwards to avoid issues where module-level
    imports in preceding tests end up with references to the deleted
    module. This causes `isinstance` and others to fail as the compared
    classes are at different addresses.
    """
    to_delete = {
        name: module for name, module in sys.modules.items() if name.startswith("openassetio")
    }
    # Remove the target modules from the cache
    for name in to_delete.keys():
        del sys.modules[name]
    # Yield to allow the target test to run
    yield
    # Restore the previously imported modules
    for name, module in to_delete.items():
        sys.modules[name] = module


@pytest.fixture
def mock_logger():
    """
    Fixture providing a mock that conforms to the LoggerInterface.
    """
    return MockLogger()


@pytest.fixture
def mock_host_interface():
    """
    Fixture for a `HostInterface` that forwards method calls to an
    internal public `mock.Mock` instance.
    """
    return MockHostInterface()


@pytest.fixture
def a_host(mock_host_interface):
    """
    Fixture for a `Host` that wraps the mock_host_interface.
    """
    return Host(mock_host_interface)


@pytest.fixture
def a_host_session(a_host, mock_logger):
    """
    Fixture for a `HostSession`, configured with a mock_host_interface,
    (via a_host) and a mock_logger.
    """
    return HostSession(a_host, mock_logger)


@pytest.fixture
def mock_entity_reference_pager_interface():
    """
    Fixture for an `EntityReferencePagerInterface` that forwards method
    calls to an internal public `mock.Mock` instance.
    """
    return MockEntityReferencePagerInterface()


@pytest.fixture
def mock_entity_reference_pager_interface_2():
    """
    Fixture for an `EntityReferencePagerInterface` that forwards method
    calls to an internal public `mock.Mock` instance.
    """
    return MockEntityReferencePagerInterface()


@pytest.fixture
def mock_manager_interface(create_mock_manager_interface):
    """
    Fixture for a `ManagerInterface` that asserts parameter types and
    forwards method calls to an internal public `mock.Mock` instance.
    """
    return create_mock_manager_interface()


@pytest.fixture
def create_mock_manager_interface():
    """
    Fixture providing a factory function for creating new
    `ValidatingMockManagerInterface` instances.

    This avoids the need to explicitly import `conftest` in test
    modules.
    """

    def creator():
        manager_interface = ValidatingMockManagerInterface()
        manager_interface.mock.info.return_value = {}
        return manager_interface

    return creator


@pytest.fixture
def mock_ui_delegate_interface(create_mock_ui_delegate_interface):
    return create_mock_ui_delegate_interface()


@pytest.fixture
def create_mock_ui_delegate_interface():

    def creator():
        return MockUIDelegateInterface()

    return creator


@pytest.fixture
def plugin_a_identifier():
    return "org.openassetio.test.pluginSystem.resources.pluginA"


@pytest.fixture
def a_cpp_plugin_path(the_cpp_plugins_root_path):
    return os.path.join(the_cpp_plugins_root_path, "pathA")


@pytest.fixture(scope="session")
def the_cpp_plugins_root_path():
    """
    Assume C++ plugins are installed in
    $<INSTALL_PREFIX>/${OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR}
    """
    scheme = f"{os.name}_user"
    return os.path.normpath(
        os.path.join(
            # Top-level __init__.py
            openassetio.__file__,
            # up to openassetio dir
            "..",
            # up to site-packages
            "..",
            # up to install tree root (i.e. posix ../../.., nt ../..)
            os.path.relpath(
                sysconfig.get_path("data", scheme), sysconfig.get_path("platlib", scheme)
            ),
            # down to install location of C++ plugins. Environment
            # variable set automatically if running pytest via CMake's
            # ctest. Default value provides a valid path to check (and
            # fail) in consuming fixtures - see
            # `skip_if_no_test_plugins_available`.
            os.getenv("OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR", "plugin-env-var-not-set"),
        )
    )


class RegexMatch:
    """
    Argument matcher to match strings by regular expression.
    """

    def __init__(self, pattern):
        self.__pattern = pattern

    def __eq__(self, text):
        return bool(re.search(self.__pattern, text))


class ValidatingMockManagerInterface(ManagerInterface):
    """
    `ManagerInterface` implementation that asserts parameter types then
    calls an internal mock.

    All method calls first have their parameter types validated, then
    are forwarded to an internal `mock.Mock` instance, which is
    `autospec`ed to `ManagerInterface` and accessible as a public `mock`
    member variable, so that expectations can be configured.

    @see mock_manager_interface
    """

    # pylint: disable=too-many-public-methods,too-many-arguments

    def __init__(self):
        super().__init__()
        self.mock = mock.create_autospec(ManagerInterface, spec_set=True, instance=True)

    def info(self):
        return self.mock.info()

    def updateTerminology(self, stringDict, hostSession):
        return self.mock.updateTerminology(stringDict, hostSession)

    def hasCapability(self, capability):
        return self.mock.hasCapability(capability)

    def settings(self, hostSession):
        return self.mock.settings(hostSession)

    def flushCaches(self, hostSession):
        return self.mock.flushCaches(hostSession)

    def defaultEntityReference(
        self, traitSets, defaultEntityAccess, context, hostSession, successCallback, errorCallback
    ):
        self.__assertIsIterableOf(traitSets, set)
        for traitSet in traitSets:
            self.__assertIsIterableOf(traitSet, str)
        assert isinstance(defaultEntityAccess, DefaultEntityAccess)
        self.__assertCallingContext(context, hostSession)
        assert callable(successCallback)
        assert callable(errorCallback)
        return self.mock.defaultEntityReference(
            traitSets, defaultEntityAccess, context, hostSession, successCallback, errorCallback
        )

    def preflight(
        self,
        targetEntityRefs,
        traitsDatas,
        publishingAccess,
        context,
        hostSession,
        successCallback,
        errorCallback,
    ):
        self.__assertIsIterableOf(targetEntityRefs, EntityReference)
        self.__assertIsIterableOf(traitsDatas, TraitsData)
        assert isinstance(publishingAccess, PublishingAccess)
        self.__assertCallingContext(context, hostSession)
        assert callable(successCallback)
        assert callable(errorCallback)
        return self.mock.preflight(
            targetEntityRefs,
            traitsDatas,
            publishingAccess,
            context,
            hostSession,
            successCallback,
            errorCallback,
        )

    def createState(self, hostSession):
        return self.mock.createState(hostSession)

    def createChildState(self, hostSession, parentState):
        return self.mock.createChildState(hostSession, parentState)

    def persistenceTokenForState(self, state, hostSession):
        return self.mock.persistenceTokenForState(state, hostSession)

    def stateFromPersistenceToken(self, token, hostSession):
        return self.mock.stateFromPersistenceToken(token, hostSession)

    def identifier(self):
        return self.mock.identifier()

    def displayName(self):
        return self.mock.displayName()

    def initialize(self, managerSettings, hostSession):
        return self.mock.initialize(managerSettings, hostSession)

    def managementPolicy(self, traitSets, policyAccess, context, hostSession):
        self.__assertIsIterableOf(traitSets, set)
        assert isinstance(policyAccess, PolicyAccess)
        for traitSet in traitSets:
            self.__assertIsIterableOf(traitSet, str)
        self.__assertCallingContext(context, hostSession)

        return self.mock.managementPolicy(traitSets, policyAccess, context, hostSession)

    def isEntityReferenceString(self, someString, hostSession):
        assert isinstance(someString, str)
        assert isinstance(hostSession, HostSession)
        return self.mock.isEntityReferenceString(someString, hostSession)

    def entityExists(self, entityRefs, context, hostSession, successCallback, errorCallback):
        self.__assertIsIterableOf(entityRefs, EntityReference)
        self.__assertCallingContext(context, hostSession)
        assert callable(successCallback)
        assert callable(errorCallback)
        return self.mock.entityExists(
            entityRefs, context, hostSession, successCallback, errorCallback
        )

    def entityTraits(
        self,
        entityRefs,
        entityTraitsAccess,
        context,
        hostSession,
        successCallback,
        errorCallback,
    ):
        self.__assertIsIterableOf(entityRefs, EntityReference)
        assert isinstance(entityTraitsAccess, EntityTraitsAccess)
        self.__assertCallingContext(context, hostSession)
        assert callable(successCallback)
        assert callable(errorCallback)
        return self.mock.entityTraits(
            entityRefs,
            entityTraitsAccess,
            context,
            hostSession,
            successCallback,
            errorCallback,
        )

    def resolve(
        self,
        entityRefs,
        traitSet,
        resolveAccess,
        context,
        hostSession,
        successCallback,
        errorCallback,
    ):
        self.__assertIsIterableOf(entityRefs, EntityReference)
        self.__assertIsIterableOf(traitSet, str)
        assert isinstance(resolveAccess, ResolveAccess)
        self.__assertCallingContext(context, hostSession)
        assert callable(successCallback)
        assert callable(errorCallback)
        return self.mock.resolve(
            entityRefs,
            traitSet,
            resolveAccess,
            context,
            hostSession,
            successCallback,
            errorCallback,
        )

    def getWithRelationship(
        self,
        entityReferences,
        relationshipTraitsData,
        resultTraitSet,
        pageSize,
        relationsAccess,
        context,
        hostSession,
        successCallback,
        errorCallback,
    ):
        assert isinstance(relationshipTraitsData, TraitsData)
        self.__assertIsIterableOf(entityReferences, EntityReference)
        assert isinstance(relationsAccess, RelationsAccess)
        self.__assertCallingContext(context, hostSession)
        assert isinstance(resultTraitSet, set)
        self.__assertIsIterableOf(resultTraitSet, str)
        assert isinstance(pageSize, int)
        assert pageSize > 0
        assert callable(successCallback)
        assert callable(errorCallback)
        return self.mock.getWithRelationship(
            entityReferences,
            relationshipTraitsData,
            resultTraitSet,
            pageSize,
            relationsAccess,
            context,
            hostSession,
            successCallback,
            errorCallback,
        )

    def getWithRelationships(
        self,
        entityReference,
        relationshipTraitsDatas,
        resultTraitSet,
        pageSize,
        relationsAccess,
        context,
        hostSession,
        successCallback,
        errorCallback,
    ):
        self.__assertIsIterableOf(relationshipTraitsDatas, TraitsData)
        assert isinstance(entityReference, EntityReference)
        assert isinstance(relationsAccess, RelationsAccess)
        self.__assertCallingContext(context, hostSession)
        assert isinstance(pageSize, int)
        assert pageSize > 0
        assert callable(successCallback)
        assert callable(errorCallback)
        assert isinstance(resultTraitSet, set)
        self.__assertIsIterableOf(resultTraitSet, str)
        return self.mock.getWithRelationships(
            entityReference,
            relationshipTraitsDatas,
            resultTraitSet,
            pageSize,
            relationsAccess,
            context,
            hostSession,
            successCallback,
            errorCallback,
        )

    def register(
        self,
        targetEntityRefs,
        entityTraitsDatas,
        publishingAccess,
        context,
        hostSession,
        successCallback,
        errorCallback,
    ):
        self.__assertIsIterableOf(targetEntityRefs, EntityReference)
        self.__assertIsIterableOf(entityTraitsDatas, TraitsData)
        assert isinstance(publishingAccess, PublishingAccess)
        self.__assertCallingContext(context, hostSession)
        assert len(targetEntityRefs) == len(entityTraitsDatas)
        assert callable(successCallback)
        assert callable(errorCallback)
        return self.mock.register(
            targetEntityRefs,
            entityTraitsDatas,
            publishingAccess,
            context,
            hostSession,
            successCallback,
            errorCallback,
        )

    @staticmethod
    def __assertIsIterableOf(iterable, expectedElemType):
        # We want to assert that `iterable` is any reasonable container.
        # Unfortunately there doesn't seem to be a catch-all for this.
        # E.g. if we expect a collection containing str elements, then a
        # str itself fits this criteria since we could iterate over it
        # and each element (character) would be a str. So just be
        # explicit on the types that we accept.
        assert isinstance(iterable, (list, tuple, set))
        for elem in iterable:
            assert isinstance(elem, expectedElemType)

    @staticmethod
    def __assertCallingContext(context, hostSession):
        assert isinstance(context, Context)
        assert isinstance(hostSession, HostSession)


class MockHostInterface(HostInterface):
    """
    `HostInterface` implementation that delegates all calls to a public
    `Mock` instance.
    """

    def __init__(self):
        super().__init__()
        self.mock = mock.create_autospec(HostInterface, spec_set=True, instance=True)

    def identifier(self):
        return self.mock.identifier()

    def displayName(self):
        return self.mock.displayName()

    def info(self):
        return self.mock.info()


class MockLogger(LoggerInterface):
    """
    `LoggerInterface` implementation that delegates all calls to a
    public `Mock` instance.
    """

    def __init__(self):
        LoggerInterface.__init__(self)
        self.mock = mock.create_autospec(LoggerInterface, spec_set=True, instance=True)

    def log(self, severity, message):
        self.mock.log(severity, message)

    def isSeverityLogged(self, severity):
        return self.mock.isSeverityLogged(severity)


class MockEntityReferencePagerInterface(EntityReferencePagerInterface):
    """
    `EntityReferencePagerInterface` implementation that delegates all
     calls to a public `Mock` instance.
    """

    def __init__(self):
        super().__init__()
        self.mock = mock.create_autospec(
            EntityReferencePagerInterface, spec_set=True, instance=True
        )

    def hasNext(self, hostSession):
        return self.mock.hasNext(hostSession)

    def get(self, hostSession):
        return self.mock.get(hostSession)

    def next(self, hostSession):
        self.mock.next(hostSession)

    def close(self, hostSession):
        self.mock.close(hostSession)


class MockUIDelegateInterface(UIDelegateInterface):
    """
    `UIDelegateInterface` implementation that delegates all calls to a
    public `Mock` instance.
    """

    def __init__(self):
        super().__init__()
        self.mock = mock.create_autospec(UIDelegateInterface, spec_set=True, instance=True)

    def identifier(self):
        return self.mock.identifier()

    def displayName(self):
        return self.mock.displayName()

    def info(self):
        return self.mock.info()

    def settings(self, hostSession):
        return self.mock.settings(hostSession)

    def initialize(self, uiDelegateSettings, hostSession):
        return self.mock.initialize(uiDelegateSettings, hostSession)

    # TODO(DF): fill out remaining details
