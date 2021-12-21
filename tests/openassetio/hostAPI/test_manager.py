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
Tests that cover the openassetio.hostAPI.Manager wrapper class.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import inspect
from unittest import mock

import pytest

from openassetio import Context
from openassetio.specifications import EntitySpecification
from openassetio.hostAPI import Manager
from openassetio.managerAPI import HostSession, ManagerInterface


## @todo Remove comments regarding Entity methods when splitting them from core API


class ValidatingMockManagerInterface(ManagerInterface):
    """
    `ManagerInterface` implementation that asserts parameter types.

    Using this (wrapped in a mock) then allows us to update the API
    test-first, i.e. provide a failing test that gives a starting point
    for TDD.

    @see mock_manager_interface
    """

    # pylint: disable=too-many-public-methods,too-many-arguments

    def info(self):
        return mock.DEFAULT

    def updateTerminology(self, stringDict, hostSession):
        return mock.DEFAULT

    def getSettings(self, hostSession):
        return mock.DEFAULT

    def setSettings(self, settings, hostSession):
        return mock.DEFAULT

    def prefetch(self, entityRefs, context, hostSession):
        return mock.DEFAULT

    def flushCaches(self, hostSession):
        return mock.DEFAULT

    def defaultEntityReference(self, specifications, context, hostSession):
        self.__assertIsIterableOf(specifications, EntitySpecification)
        self.__assertCallingContext(context, hostSession)
        return mock.DEFAULT

    def getEntityAttribute(self, entityRefs, name, context, hostSession, defaultValue=None):
        self.__assertIsIterableOf(entityRefs, str)
        assert isinstance(name, str)
        self.__assertCallingContext(context, hostSession)
        assert isinstance(defaultValue, (str, int, float, bool)) or defaultValue is None
        return mock.DEFAULT

    def setEntityAttribute(self, entityRefs, name, value, context, hostSession):
        self.__assertIsIterableOf(entityRefs, str)
        assert isinstance(name, str)
        assert isinstance(value, (str, bool, int, float))
        self.__assertCallingContext(context, hostSession)
        return mock.DEFAULT

    def entityVersionName(self, entityRefs, context, hostSession):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertCallingContext(context, hostSession)
        return mock.DEFAULT

    def entityVersions(
            self, entityRefs, context, hostSession, includeMetaVersions=False, maxNumVersions=-1):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertCallingContext(context, hostSession)
        assert isinstance(includeMetaVersions, bool)
        assert isinstance(maxNumVersions, int)
        return mock.DEFAULT

    def finalizedEntityVersion(self, entityRefs, context, hostSession, overrideVersionName=None):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertCallingContext(context, hostSession)
        assert isinstance(overrideVersionName, str) or overrideVersionName is None
        return mock.DEFAULT

    def setRelatedReferences(
            self, entityRef, relationshipSpec, relatedRefs, context, hostSession, append=True):
        return mock.DEFAULT

    def preflight(self, targetEntityRefs, entitySpecs, context, hostSession):
        self.__assertIsIterableOf(targetEntityRefs, str)
        self.__assertIsIterableOf(entitySpecs, EntitySpecification)
        self.__assertCallingContext(context, hostSession)
        assert len(targetEntityRefs) == len(entitySpecs)
        return mock.DEFAULT

    def createState(self, hostSession, parentState=None):
        return mock.DEFAULT

    def startTransaction(self, state, hostSession):
        return mock.DEFAULT

    def finishTransaction(self, state, hostSession):
        return mock.DEFAULT

    def cancelTransaction(self, state, hostSession):
        return mock.DEFAULT

    def freezeState(self, state, hostSession):
        return mock.DEFAULT

    def thawState(self, token, hostSession):
        return mock.DEFAULT

    @staticmethod
    def identifier():
        return mock.DEFAULT

    def displayName(self):
        return mock.DEFAULT

    def initialize(self, hostSession):
        return mock.DEFAULT

    def managementPolicy(self, specifications, context, hostSession, entityRef=None):
        self.__assertIsIterableOf(specifications, EntitySpecification)
        self.__assertCallingContext(context, hostSession)
        assert isinstance(entityRef, str) or entityRef is None

        return mock.DEFAULT

    def isEntityReference(self, tokens, context, hostSession):
        self.__assertIsIterableOf(tokens, str)
        self.__assertCallingContext(context, hostSession)
        return mock.DEFAULT

    def entityExists(self, entityRefs, context, hostSession):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertCallingContext(context, hostSession)
        return mock.DEFAULT

    def resolveEntityReference(self, entityRefs, context, hostSession):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertCallingContext(context, hostSession)
        return mock.DEFAULT

    def entityName(self, entityRefs, context, hostSession):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertCallingContext(context, hostSession)
        return mock.DEFAULT

    def entityDisplayName(self, entityRefs, context, hostSession):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertCallingContext(context, hostSession)
        return mock.DEFAULT

    def getEntityAttributes(self, entityRefs, context, hostSession):
        self.__assertIsIterableOf(entityRefs, str)
        self.__assertCallingContext(context, hostSession)
        return mock.DEFAULT

    def setEntityAttributes(self, entityRefs, data, context, hostSession, merge=True):
        self.__assertIsIterableOf(entityRefs, str)
        # TODO(DF): The following fails for `register` since it passes a
        #   list of dicts.
        # assert isinstance(data, dict)
        self.__assertCallingContext(context, hostSession)
        assert isinstance(merge, bool)
        return mock.DEFAULT

    def getRelatedReferences(
            self, entityRefs, relationshipSpecs, context, hostSession, resultSpec=None):
        return mock.DEFAULT

    def register(self, primaryStrings, targetEntityRefs, entitySpecs, context, hostSession):
        self.__assertIsIterableOf(primaryStrings, str)
        self.__assertIsIterableOf(targetEntityRefs, str)
        self.__assertIsIterableOf(entitySpecs, EntitySpecification)
        self.__assertCallingContext(context, hostSession)
        assert len(primaryStrings) == len(targetEntityRefs)
        assert len(primaryStrings) == len(entitySpecs)
        return mock.DEFAULT

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


@pytest.fixture
def mock_manager_interface():
    """
    Fixture for a mock `ManagerInterface` that asserts parameter types.

    Return a mock `autospec`ed to the `ManagerInterface`, with each
    mocked method set up to `side_effect` to the corresponding
    method in `ValidatingMockManagerInterface`.

    This then means method parameter types will be `assert`ed, whilst
    still providing full `MagicMock` functionality.
    """
    interface = ValidatingMockManagerInterface()
    mockInterface = mock.create_autospec(spec=interface, spec_set=True)
    # Set the `side_effect` of each mocked method to call through to
    # the concrete instance.
    methods = inspect.getmembers(interface, predicate=inspect.ismethod)
    for name, method in methods:
        getattr(mockInterface, name).side_effect = method

    return mockInterface


@pytest.fixture
def host_session():
    return mock.create_autospec(HostSession)


@pytest.fixture
def manager(mock_manager_interface, host_session):
    return Manager(mock_manager_interface, host_session)


@pytest.fixture
def an_entity_spec():
    return EntitySpecification()


@pytest.fixture
def some_entity_specs():
    return [EntitySpecification(), EntitySpecification()]


@pytest.fixture
def a_context():
    return Context()


@pytest.fixture
def a_ref():
    return "asset://a"


@pytest.fixture
def some_refs():
    return ["asset://a", "asset://b"]

# __str__ and __repr__ aren't tested as they're debug tricks that need
# assessing when this is ported to cpp

class Test_Manager_init:

    def test_interface_returns_the_constructor_supplied_object(
            self, mock_manager_interface, host_session):

        # pylint: disable=protected-access
        a_manager = Manager(mock_manager_interface, host_session)
        assert a_manager._interface() is mock_manager_interface


class Test_Manager_identifier:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface):

        method = mock_manager_interface.identifier
        assert manager.identifier() == method.return_value
        method.assert_called_once_with()


class Test_Manager_updateTerminology:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session):

        method = mock_manager_interface.updateTerminology
        a_dict = {"k", "v"}
        assert manager.updateTerminology(a_dict) is a_dict
        method.assert_called_once_with(a_dict, host_session)


class Test_Manager_getSettings:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session):

        method = mock_manager_interface.getSettings
        assert manager.getSettings() == method.return_value
        method.assert_called_once_with(host_session)


class Test_Manager_setSettings:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session):

        method = mock_manager_interface.setSettings
        a_dict = {"k", "v"}
        assert manager.setSettings(a_dict) == method.return_value
        method.assert_called_once_with(a_dict, host_session)


class Test_Manager_initialize:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session):

        method = mock_manager_interface.initialize
        assert manager.initialize() == method.return_value
        method.assert_called_once_with(host_session)


class Test_Manager_prefetch:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_refs, a_context):

        method = mock_manager_interface.prefetch
        assert manager.prefetch(some_refs, a_context) == method.return_value
        method.assert_called_once_with(some_refs, a_context, host_session)


class Test_Manager_flushCaches:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session):

        method = mock_manager_interface.flushCaches
        assert manager.flushCaches() == method.return_value
        method.assert_called_once_with(host_session)


class Test_Manager_isEntityReference:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_refs, a_context):

        method = mock_manager_interface.isEntityReference
        assert manager.isEntityReference(some_refs, a_context) == method.return_value
        method.assert_called_once_with(some_refs, a_context, host_session)


class Test_Manager_entityExists:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_refs, a_context):

        method = mock_manager_interface.entityExists
        assert manager.entityExists(some_refs, a_context) == method.return_value
        method.assert_called_once_with(some_refs, a_context, host_session)


class Test_Manager_defaultEntityReference:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, a_context, some_entity_specs):

        method = mock_manager_interface.defaultEntityReference
        assert manager.defaultEntityReference(some_entity_specs, a_context) == method.return_value
        method.assert_called_once_with(some_entity_specs, a_context, host_session)


class Test_Manager_entityName:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_refs, a_context):

        method = mock_manager_interface.entityName
        assert manager.entityName(some_refs, a_context) == method.return_value
        method.assert_called_once_with(some_refs, a_context, host_session)


class Test_Manager_entityDisplayNamer:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_refs, a_context):

        method = mock_manager_interface.entityDisplayName
        assert manager.entityDisplayName(some_refs, a_context) == method.return_value
        method.assert_called_once_with(some_refs, a_context, host_session)


class Test_Manager_getEntityAttributes:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_refs, a_context):

        method = mock_manager_interface.getEntityAttributes
        assert manager.getEntityAttributes(some_refs, a_context) == method.return_value
        method.assert_called_once_with(some_refs, a_context, host_session)


class Test_Manager_setEntityAttributes:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_refs, a_context):

        method = mock_manager_interface.setEntityAttributes
        some_data = [{"k1": "v1"}, {"k2": "v2"}]

        assert manager.setEntityAttributes(some_refs, some_data, a_context) == method.return_value
        method.assert_called_once_with(some_refs, some_data, a_context, host_session, merge=True)
        method.reset_mock()

        assert manager.setEntityAttributes(
            some_refs, some_data, a_context, merge=False) == method.return_value
        method.assert_called_once_with(some_refs, some_data, a_context, host_session, merge=False)


class Test_Manager_getEntityAttribute:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_refs, a_context):

        method = mock_manager_interface.getEntityAttribute
        a_key = "key"
        a_default = 2

        assert manager.getEntityAttribute(some_refs, a_key, a_context) == method.return_value
        method.assert_called_once_with(
            some_refs, a_key, a_context, host_session, defaultValue=None)
        method.reset_mock()

        assert manager.getEntityAttribute(
            some_refs, a_key, a_context, defaultValue=a_default) == method.return_value
        method.assert_called_once_with(
            some_refs, a_key, a_context, host_session, defaultValue=a_default)


class Test_Manager_setEntityAttribute:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_refs, a_context):

        a_key = "key"
        a_value = "value"
        method = mock_manager_interface.setEntityAttribute
        assert manager.setEntityAttribute(
            some_refs, a_key, a_value, a_context) == method.return_value
        method.assert_called_once_with(some_refs, a_key, a_value, a_context, host_session)


class Test_Manager_entityVersionName:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_refs, a_context):

        method = mock_manager_interface.entityVersionName
        assert manager.entityVersionName(some_refs, a_context) == method.return_value
        method.assert_called_once_with(some_refs, a_context, host_session)


class Test_Manager_entityVersions:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_refs, a_context):

        method = mock_manager_interface.entityVersions

        assert manager.entityVersions(some_refs, a_context) == method.return_value
        method.assert_called_once_with(
            some_refs, a_context, host_session, includeMetaVersions=False, maxNumVersions=-1)
        method.reset_mock()

        max_results = 5
        assert manager.entityVersions(
            some_refs, a_context, maxNumVersions=max_results) == method.return_value
        method.assert_called_once_with(
            some_refs, a_context, host_session,
            includeMetaVersions=False, maxNumVersions=max_results)
        method.reset_mock()

        include_meta = True
        assert manager.entityVersions(
            some_refs, a_context, maxNumVersions=max_results,
            includeMetaVersions=include_meta) == method.return_value
        method.assert_called_once_with(
            some_refs, a_context, host_session, includeMetaVersions=include_meta,
            maxNumVersions=max_results)


class Test_Manager_finalizedEntityVersion:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_refs, a_context):

        method = mock_manager_interface.finalizedEntityVersion
        assert manager.finalizedEntityVersion(some_refs, a_context) == method.return_value
        method.assert_called_once_with(
            some_refs, a_context, host_session, overrideVersionName=None)
        method.reset_mock()

        a_version_name = "aVersion"
        method = mock_manager_interface.finalizedEntityVersion
        assert manager.finalizedEntityVersion(
            some_refs, a_context, overrideVersionName=a_version_name) == method.return_value
        method.assert_called_once_with(
            some_refs, a_context, host_session, overrideVersionName=a_version_name)


class Test_Manager_getRelatedReferences:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, a_ref, an_entity_spec, a_context):

        # pylint: disable=too-many-locals

        method = mock_manager_interface.getRelatedReferences

        one_ref = a_ref
        two_refs = [a_ref, a_ref]
        three_refs = [a_ref, a_ref, a_ref]
        one_spec = an_entity_spec
        two_specs = [an_entity_spec, an_entity_spec]
        three_specs = [an_entity_spec, an_entity_spec, an_entity_spec]

        # Check validation that one to many or equal length ref/spec args are required

        for refs_arg, specs_arg in (
                (two_refs, three_specs),
                (three_refs, two_specs)
        ):
            with pytest.raises(ValueError):
                manager.getRelatedReferences(refs_arg, specs_arg, a_context)
            method.assert_not_called()
            method.reset_mock()

        for refs_arg, specs_arg, expected_refs_arg, expected_specs_arg in (
                (one_ref, three_specs, [one_ref], three_specs),
                (three_refs, one_spec, three_refs, [one_spec]),
                (three_refs, three_specs, three_refs, three_specs)
        ):
            assert manager.getRelatedReferences(
                refs_arg, specs_arg, a_context) == method.return_value
            method.assert_called_once_with(
                expected_refs_arg, expected_specs_arg, a_context, host_session, resultSpec=None)
            method.reset_mock()

        # Check optional resultSpec
        assert manager.getRelatedReferences(
            one_ref, one_spec, a_context, resultSpec=an_entity_spec) == method.return_value
        method.assert_called_once_with(
            [one_ref], [one_spec], a_context, host_session, resultSpec=an_entity_spec)


class Test_Manager_resolveEntityReference:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_refs, a_context):

        method = mock_manager_interface.resolveEntityReference
        assert manager.resolveEntityReference(some_refs, a_context) == method.return_value
        method.assert_called_once_with(some_refs, a_context, host_session)


class Test_Manager_managentPolicy:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_entity_specs, a_context,
            a_ref):

        method = mock_manager_interface.managementPolicy
        assert manager.managementPolicy(some_entity_specs, a_context) == method.return_value
        method.assert_called_once_with(some_entity_specs, a_context, host_session, entityRef=None)
        method.reset_mock()

        method = mock_manager_interface.managementPolicy
        assert manager.managementPolicy(
            some_entity_specs, a_context, entityRef=a_ref) == method.return_value
        method.assert_called_once_with(some_entity_specs, a_context, host_session, entityRef=a_ref)


class Test_Manager_preflight:

    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, manager, mock_manager_interface, host_session, some_refs, some_entity_specs,
            a_context):

        method = mock_manager_interface.preflight
        assert manager.preflight(some_refs, some_entity_specs, a_context) == method.return_value
        method.assert_called_once_with(some_refs, some_entity_specs, a_context, host_session)


    def test_when_called_with_mismatched_array_lengths_then_IndexError_is_raised(
            self, manager, some_refs, some_entity_specs, a_context):

        with pytest.raises(IndexError):
            manager.preflight(some_refs, some_entity_specs[1:], a_context)


class Test_Manager_register:

    def test_wraps_the_the_held_interface_register_and_setEntityAttributes_methods(
            self, manager, mock_manager_interface, host_session, some_refs, some_entity_specs,
            a_context):

        register_method = mock_manager_interface.register
        setmeta_method = mock_manager_interface.setEntityAttributes

        some_strings = ["primary string 1", "primary string 2"]
        some_attr = [{"k1": "v1"}, {"k2": "v2"}]

        # the return value is used in the setEntityAttributes call so we
        # need it to provide an actual ref we know
        mutated_refs = [f"{some_refs[0]}-registered", f"{some_refs[1]}-registered"]
        register_method.return_value = mutated_refs

        # Test without attributes

        assert manager.register(
            some_strings, some_refs, some_entity_specs, a_context) == register_method.return_value
        register_method.assert_called_once_with(
            some_strings, some_refs, some_entity_specs, a_context, host_session)
        setmeta_method.assert_not_called()

        mock_manager_interface.reset_mock()

        # Test with attributes

        assert manager.register(
            some_strings, some_refs, some_entity_specs, a_context,
            attributes=some_attr) == register_method.return_value
        register_method.assert_called_once_with(
            some_strings, some_refs, some_entity_specs, a_context, host_session)
        setmeta_method.assert_called_once_with(
            mutated_refs, some_attr, a_context, host_session, merge=True)

    def test_when_called_with_mixed_array_lengths_then_IndexError_is_raised(
            self, manager, some_refs, some_entity_specs, a_context):

        some_strings = ["primary string 1", "primary string 2"]
        some_attr = [{"k1": "v1"}, {"k2": "v2"}]

        with pytest.raises(IndexError):
            manager.register(
                some_strings[1:], some_refs, some_entity_specs, a_context, attributes=some_attr)

        with pytest.raises(IndexError):
            manager.register(
                some_strings, some_refs[1:], some_entity_specs, a_context, attributes=some_attr)

        with pytest.raises(IndexError):
            manager.register(
                some_strings, some_refs, some_entity_specs[1:], a_context, attributes=some_attr)

        with pytest.raises(IndexError):
            manager.register(
                some_strings, some_refs, some_entity_specs, a_context, attributes=some_attr[1:])
