#
#   Copyright 2013-2022 The Foundry Visionmongers Ltd
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
import inspect
from unittest import mock
import sys

import pytest

from openassetio import Context, EntityReference, TraitsData
from openassetio.log import LoggerInterface
from openassetio.managerApi import ManagerInterface, Host, HostSession
from openassetio.hostApi import HostInterface


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
def mock_manager_interface():
    """
    Fixture for a `ManagerInterface` that asserts parameter types and
    forwards method calls to an internal public `mock.Mock` instance.
    """
    return ValidatingMockManagerInterface()


@pytest.fixture
def create_mock_manager_interface():
    """
    Fixture providing a factory function for creating new
    `ValidatingMockManagerInterface` instances.

    This avoids the need to explicitly import `conftest` in test
    modules.
    """

    def creator():
        return ValidatingMockManagerInterface()

    return creator


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

    def settings(self, hostSession):
        return self.mock.settings(hostSession)

    def flushCaches(self, hostSession):
        return self.mock.flushCaches(hostSession)

    def defaultEntityReference(self, traitSets, context, hostSession):
        self.__assertIsIterableOf(traitSets, set)
        for traitSet in traitSets:
            self.__assertIsIterableOf(traitSet, str)
        self.__assertCallingContext(context, hostSession)
        return self.mock.defaultEntityReference(traitSets, context, hostSession)

    def entityVersion(self, entityRefs, context, hostSession):
        self.__assertIsIterableOf(entityRefs, EntityReference)
        self.__assertCallingContext(context, hostSession)
        return self.mock.entityVersion(entityRefs, context, hostSession)

    def entityVersions(
        self, entityRefs, context, hostSession, includeMetaVersions=False, maxNumVersions=-1
    ):
        self.__assertIsIterableOf(entityRefs, EntityReference)
        self.__assertCallingContext(context, hostSession)
        assert isinstance(includeMetaVersions, bool)
        assert isinstance(maxNumVersions, int)
        return self.mock.entityVersions(
            entityRefs, context, hostSession, includeMetaVersions, maxNumVersions
        )

    def finalizedEntityVersion(self, entityRefs, context, hostSession, overrideVersionName=None):
        self.__assertIsIterableOf(entityRefs, EntityReference)
        self.__assertCallingContext(context, hostSession)
        assert isinstance(overrideVersionName, str) or overrideVersionName is None
        return self.mock.finalizedEntityVersion(
            entityRefs, context, hostSession, overrideVersionName
        )

    def preflight(
        self, targetEntityRefs, traitSet, context, hostSession, successCallback, errorCallback
    ):
        self.__assertIsIterableOf(targetEntityRefs, EntityReference)
        self.__assertIsIterableOf(traitSet, str)
        self.__assertCallingContext(context, hostSession)
        assert callable(successCallback)
        assert callable(errorCallback)
        return self.mock.preflight(
            targetEntityRefs, traitSet, context, hostSession, successCallback, errorCallback
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

    def managementPolicy(self, traitSets, context, hostSession):
        self.__assertIsIterableOf(traitSets, set)
        for traitSet in traitSets:
            self.__assertIsIterableOf(traitSet, str)
        self.__assertCallingContext(context, hostSession)

        return self.mock.managementPolicy(traitSets, context, hostSession)

    def isEntityReferenceString(self, someString, hostSession):
        assert isinstance(someString, str)
        assert isinstance(hostSession, HostSession)
        return self.mock.isEntityReferenceString(someString, hostSession)

    def entityExists(self, entityRefs, context, hostSession):
        self.__assertIsIterableOf(entityRefs, EntityReference)
        self.__assertCallingContext(context, hostSession)
        return self.mock.entityExists(entityRefs, context, hostSession)

    def resolve(self, entityRefs, traitSet, context, hostSession, successCallback, errorCallback):
        self.__assertIsIterableOf(entityRefs, EntityReference)
        self.__assertIsIterableOf(traitSet, str)
        self.__assertCallingContext(context, hostSession)
        assert callable(successCallback)
        assert callable(errorCallback)
        return self.mock.resolve(
            entityRefs, traitSet, context, hostSession, successCallback, errorCallback
        )

    def getWithRelationship(
        self,
        relationshipTraitsData,
        entityReferences,
        context,
        hostSession,
        successCallback,
        errorCallback,
        resultTraitSet=None,
    ):
        assert isinstance(relationshipTraitsData, TraitsData)
        self.__assertIsIterableOf(entityReferences, EntityReference)
        self.__assertCallingContext(context, hostSession)
        if resultTraitSet is not None:
            assert isinstance(resultTraitSet, set)
            self.__assertIsIterableOf(resultTraitSet, str)
        assert callable(successCallback)
        assert callable(errorCallback)
        return self.mock.getWithRelationship(
            relationshipTraitsData,
            entityReferences,
            context,
            hostSession,
            successCallback,
            errorCallback,
            resultTraitSet,
        )

    def getWithRelationships(
        self,
        relationshipTraitsDatas,
        entityReference,
        context,
        hostSession,
        successCallback,
        errorCallback,
        resultTraitSet=None,
    ):
        self.__assertIsIterableOf(relationshipTraitsDatas, TraitsData)
        assert isinstance(entityReference, EntityReference)
        self.__assertCallingContext(context, hostSession)
        assert callable(successCallback)
        assert callable(errorCallback)
        if resultTraitSet is not None:
            assert isinstance(resultTraitSet, set)
            self.__assertIsIterableOf(resultTraitSet, str)
        return self.mock.getWithRelationships(
            relationshipTraitsDatas,
            entityReference,
            context,
            hostSession,
            successCallback,
            errorCallback,
            resultTraitSet,
        )

    def register(
        self,
        targetEntityRefs,
        entityTraitsDatas,
        context,
        hostSession,
        successCallback,
        errorCallback,
    ):
        self.__assertIsIterableOf(targetEntityRefs, EntityReference)
        self.__assertIsIterableOf(entityTraitsDatas, TraitsData)
        self.__assertCallingContext(context, hostSession)
        assert len(targetEntityRefs) == len(entityTraitsDatas)
        assert callable(successCallback)
        assert callable(errorCallback)
        return self.mock.register(
            targetEntityRefs,
            entityTraitsDatas,
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


#
# Python to C++ migration helpers
#


@pytest.fixture
def method_introspector():
    return MethodIntrospector()


class MethodIntrospector:
    """
    Utility function for introspecting methods.

    @todo Remove this class and related tests once C++ migration is
    complete.
    """

    @staticmethod
    def is_defined_in_python(method):
        """
        Returns True if the method is defined in Python (as opposed to
        through a cmodule).

        @param The method of a class to be checked (eg: Manager.info). This
        should be passed from the Class itself, not an instance.
        """
        # The way pybind does its thing™, this returns True for a native
        # Python implementation, False for a C++ method bound to Python
        # (isntancemthod not function). Mildly tenuous, but serves a
        # purpose. getsource and similar raise a TypeError if the supplied
        # object isn't a function, so the flow control is simpler this way.
        return inspect.isfunction(method)

    @staticmethod
    def is_implemented_once(klass, method_name):
        """
        Check if a method is only implemented once in the class hierarchy.

        In particular, this is useful to ensure we aren't hiding a (C++)
        base class method with a (Python) subclass method. I.e. this checks
        that we haven't migrated a method to C++ then forgot to remove the
        Python implementation.

        This acts as a backup check in case we migrate a method then forget
        to update the `is_defined_in_python` assertion.

        @param klass: Class whose base class hierarchy to check.

        @param method_name: Name of method to check.

        @return: True if the method is only defined once in the hierarchy,
        false otherwise.
        """
        # Get class hierarchy, including class itself.
        class_hierarchy = inspect.getmro(klass)
        # C++ instance methods are not hashable, so constructing a `set`,
        # and then checking its length, doesn't work here.
        maybe_impls = (getattr(base, method_name, None) for base in class_hierarchy)
        impls = filter(None, maybe_impls)
        first_impl = next(impls, None)  # Consume first element.
        if first_impl is None:
            # Not even implemented once.
            return False
        return all(impl == first_impl for impl in impls)
