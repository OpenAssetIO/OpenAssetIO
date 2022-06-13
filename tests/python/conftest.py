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
Shared fixtures/code for pytest cases.
"""
# pylint: disable=missing-function-docstring,redefined-outer-name
from unittest import mock
import sys

import pytest

from openassetio import Context, TraitsData
from openassetio.log import LoggerInterface
from openassetio.managerAPI import ManagerInterface, Host, HostSession
from openassetio.hostAPI import HostInterface

# pylint: disable=invalid-name


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
    return mock.create_autospec(spec=LoggerInterface)


@pytest.fixture
def mock_host_interface():
    """
    Fixture for a `HostInterface` that forwards method calls to an
    internal public `mock.Mock` instance.
    """
    return MockHostInterface()


@pytest.fixture
def mock_host_session(mock_host_interface, mock_logger):
    """
    Fixture for a `HostSesssion`, configured with a mock_host_interface,
    that forwards method calls to an internal public `mock.Mock` instance.
    """
    return MockHostSession(Host(mock_host_interface), mock_logger)


@pytest.fixture
def mock_manager_interface():
    """
    Fixture for a `ManagerInterface` that asserts parameter types and
    forwards method calls to an internal public `mock.Mock` instance.
    """
    return ValidatingMockManagerInterface()


class MockHostSession(HostSession):
    """
    `HostSession` that forwards calls to an internal mock.
    @see mock_host_session
    """

    def __init__(self, host, logger):
        super().__init__(host, logger)
        self.mock = mock.create_autospec(HostSession, spec_set=True, instance=True)

    def host(self):
        return self.mock.host()


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

    def getSettings(self, hostSession):
        return self.mock.getSettings(hostSession)

    def setSettings(self, settings, hostSession):
        return self.mock.setSettings(settings, hostSession)

    def prefetch(self, entityRefs, context, hostSession):
        return self.mock.prefetch(entityRefs, context, hostSession)

    def flushCaches(self, hostSession):
        return self.mock.flushCaches(hostSession)

    def defaultEntityReference(self, traitSets, context, hostSession):
        self.__assertIsIterableOf(traitSets, set)
        for traitSet in traitSets:
            self.__assertIsIterableOf(traitSet, str)
        self.__assertCallingContext(context, hostSession)
        return self.mock.defaultEntityReference(traitSets, context, hostSession)

    def entityVersion(self, entityRefs, context, hostSession):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertCallingContext(context, hostSession)
        return self.mock.entityVersion(entityRefs, context, hostSession)

    def entityVersions(
            self, entityRefs, context, hostSession, includeMetaVersions=False, maxNumVersions=-1):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertCallingContext(context, hostSession)
        assert isinstance(includeMetaVersions, bool)
        assert isinstance(maxNumVersions, int)
        return self.mock.entityVersions(
            entityRefs, context, hostSession, includeMetaVersions, maxNumVersions)

    def finalizedEntityVersion(self, entityRefs, context, hostSession, overrideVersionName=None):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertCallingContext(context, hostSession)
        assert isinstance(overrideVersionName, str) or overrideVersionName is None
        return self.mock.finalizedEntityVersion(
            entityRefs, context, hostSession, overrideVersionName)

    def setRelatedReferences(self, entityRef, relationshipTraitsData, relatedRefs, context,
                hostSession, append=True):
        return self.mock.setRelatedReferences(
            entityRef, relationshipTraitsData, relatedRefs, context, hostSession, append=append)

    def preflight(self, targetEntityRefs, traitSet, context, hostSession):
        self.__assertIsIterableOf(targetEntityRefs, str)
        self.__assertIsIterableOf(traitSet, str)
        self.__assertCallingContext(context, hostSession)
        return self.mock.preflight(targetEntityRefs, traitSet, context, hostSession)

    def createState(self, hostSession, parentState=None):
        return self.mock.createState(hostSession, parentState)

    def freezeState(self, state, hostSession):
        return self.mock.freezeState(state, hostSession)

    def thawState(self, token, hostSession):
        return self.mock.thawState(token, hostSession)

    def identifier(self):
        return self.mock.identifier()

    def displayName(self):
        return self.mock.displayName()

    def initialize(self, hostSession):
        return self.mock.initialize(hostSession)

    def managementPolicy(self, traitSets, context, hostSession):
        self.__assertIsIterableOf(traitSets, set)
        for traitSet in traitSets:
            self.__assertIsIterableOf(traitSet, str)
        self.__assertCallingContext(context, hostSession)

        return self.mock.managementPolicy(traitSets, context, hostSession)

    def isEntityReference(self, tokens, hostSession):
        self.__assertIsIterableOf(tokens, str)
        assert isinstance(hostSession, HostSession)
        return self.mock.isEntityReference(tokens, hostSession)

    def entityExists(self, entityRefs, context, hostSession):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertCallingContext(context, hostSession)
        return self.mock.entityExists(entityRefs, context, hostSession)

    def resolve(self, entityRefs, traitSet, context, hostSession):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertIsIterableOf(traitSet, str)
        self.__assertCallingContext(context, hostSession)
        return self.mock.resolve(entityRefs, traitSet, context, hostSession)

    def entityName(self, entityRefs, context, hostSession):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertCallingContext(context, hostSession)
        return self.mock.entityName(entityRefs, context, hostSession)

    def entityDisplayName(self, entityRefs, context, hostSession):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertCallingContext(context, hostSession)
        return self.mock.entityDisplayName(entityRefs, context, hostSession)

    def getRelatedReferences(
            self, entityRefs, relationshipTraitsDatas, context, hostSession, resultTraitSet=None):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertIsIterableOf(relationshipTraitsDatas, TraitsData)
        self.__assertCallingContext(context, hostSession)
        if resultTraitSet is not None:
            assert isinstance(resultTraitSet, set)
            self.__assertIsIterableOf(resultTraitSet, str)
        return self.mock.getRelatedReferences(
            entityRefs, relationshipTraitsDatas, context, hostSession, resultTraitSet)

    def register(self, targetEntityRefs, entityTraitsDatas, context, hostSession):
        self.__assertIsIterableOf(targetEntityRefs, str)
        self.__assertIsIterableOf(entityTraitsDatas, TraitsData)
        self.__assertCallingContext(context, hostSession)
        assert len(targetEntityRefs) == len(entityTraitsDatas)
        return self.mock.register(targetEntityRefs, entityTraitsDatas, context, hostSession)

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
