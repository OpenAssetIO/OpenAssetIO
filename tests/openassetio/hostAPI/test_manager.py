#
#   Copyright 2013-2021 [The Foundry Visionmongers Ltd]
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
import inspect

import pytest
from unittest import mock

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

    def info(self):
        return mock.DEFAULT

    def updateTerminology(self, stringDict, hostSession):
        return mock.DEFAULT

    def getSettings(self, hostSession):
        return mock.DEFAULT

    def setSettings(self, settings, hostSession):
        return mock.DEFAULT

    def prefetch(self, entitRefs, context, hostSession):
        return mock.DEFAULT

    def flushCaches(self, hostSession):
        return mock.DEFAULT

    def resolveEntityReferences(self, references, context, hostSession):
        return mock.DEFAULT

    def defaultEntityReference(self, specification, context, hostSession):
        return mock.DEFAULT

    def getEntityMetadataEntry(self, entityRef, key, context, hostSession, defaultValue=None):
        return mock.DEFAULT

    def setEntityMetadataEntry(self, entityRef, key, value, context, hostSession):
        return mock.DEFAULT

    def entityVersionName(self, entityRef, context, hostSession):
        return mock.DEFAULT

    def entityVersions(
            self, entityRef, context, hostSession, includeMetaVersions=False, maxResults=-1):
        return mock.DEFAULT

    def finalizedEntityVersion(self, entityRef, context, hostSession, overrideVersionName=None):
        return mock.DEFAULT

    def setRelatedReferences(
            self, entityRef, relationshipSpec, relatedRefs, context, hostSession, append=True):
        return mock.DEFAULT

    def thumbnailSpecification(self, specification, context, options, hostSession):
        return mock.DEFAULT

    def preflight(self, targetEntityRef, entitySpec, context, hostSession):
        return mock.DEFAULT

    def preflightMultiple(self, targetEntityRefs, entitySpecs, context, hostSession):
        return mock.DEFAULT

    def registerMultiple(self, strings, targetEntityRefs, entitySpecs, context, hostSession):
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

    def identifier(self):
        return mock.DEFAULT

    def displayName(self):
        return mock.DEFAULT

    def initialize(self, hostSession):
        return mock.DEFAULT

    def managementPolicy(self, specification, context, hostSession, entityRef=None):
        return mock.DEFAULT

    def isEntityReference(self, token, context, hostSession):
        return mock.DEFAULT

    def entityExists(self, entityRef, context, hostSession):
        return mock.DEFAULT

    def resolveEntityReference(self, entityRef, context, hostSession):
        return mock.DEFAULT

    def entityName(self, entityRef, context, hostSession):
        return mock.DEFAULT

    def entityDisplayName(self, entityRef, context, hostSession):
        return mock.DEFAULT

    def getEntityMetadata(self, entityRef, context, hostSession):
        return mock.DEFAULT

    def setEntityMetadata(self, entityRef, data, context, hostSession, merge=True):
        return mock.DEFAULT

    def getRelatedReferences(
            self, entityRefs, relationshipSpecs, context, hostSession, resultSpec=None):
        return mock.DEFAULT

    def register(self, stringData, targetEntityRef, entitySpec, context, hostSession):
        return mock.DEFAULT


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
def a_context():
    return Context()


@pytest.fixture
def a_ref():
    return "asset://a"


@pytest.fixture
def some_refs():
    return ["asset://a", "asset://b"]


class TestManager():

    # __str__ and __repr__ aren't tested as they're debug tricks that need
    # assessing when this is ported to cpp

    def test__interface(self, mock_manager_interface, host_session):
        a_manager = Manager(mock_manager_interface, host_session)
        assert a_manager._interface() is mock_manager_interface

    def test_identifier(self, manager, mock_manager_interface):
        method = mock_manager_interface.identifier
        assert manager.identifier() == method.return_value
        method.assert_called_once_with()

    def test_updateTerminology(self, manager, mock_manager_interface, host_session):
        method = mock_manager_interface.updateTerminology
        a_dict = {"k", "v"}
        assert manager.updateTerminology(a_dict) is a_dict
        method.assert_called_once_with(a_dict, host_session)

    def test_getSettings(self, manager, mock_manager_interface, host_session):
        method = mock_manager_interface.getSettings
        assert manager.getSettings() == method.return_value
        method.assert_called_once_with(host_session)

    def test_setSettings(self, manager, mock_manager_interface, host_session):
        method = mock_manager_interface.setSettings
        a_dict = {"k", "v"}
        assert manager.setSettings(a_dict) == method.return_value
        method.assert_called_once_with(a_dict, host_session)

    def test_initialize(self, manager, mock_manager_interface, host_session):
        method = mock_manager_interface.initialize
        assert manager.initialize() == method.return_value
        method.assert_called_once_with(host_session)

    def test_prefetch(self, manager, mock_manager_interface, host_session, some_refs, a_context):
        method = mock_manager_interface.prefetch
        # Not testing Entity variant of call as this will be removed shortly
        assert manager.prefetch(some_refs, a_context) == method.return_value
        method.assert_called_once_with(some_refs, a_context, host_session)

    def test_flushCaches(self, manager, mock_manager_interface, host_session):
        method = mock_manager_interface.flushCaches
        assert manager.flushCaches() == method.return_value
        method.assert_called_once_with(host_session)

    def test_isEntityReference(
            self, manager, mock_manager_interface, host_session, a_ref, a_context):
        method = mock_manager_interface.isEntityReference
        assert manager.isEntityReference(a_ref, a_context) == method.return_value
        method.assert_called_once_with(a_ref, a_context, host_session)

    def test_entityExists(self, manager, mock_manager_interface, host_session, a_ref, a_context):
        method = mock_manager_interface.entityExists
        assert manager.entityExists(a_ref, a_context) == method.return_value
        method.assert_called_once_with(a_ref, a_context, host_session)

    # Not testing getEntity as it will be removed

    def test_defaultEntityReference(
            self, manager, mock_manager_interface, host_session, an_entity_spec):
        method = mock_manager_interface.defaultEntityReference
        assert manager.defaultEntityReference(an_entity_spec, a_context) == method.return_value
        method.assert_called_once_with(an_entity_spec, a_context, host_session)

    def test_entityName(self, manager, mock_manager_interface, host_session, a_ref, a_context):
        method = mock_manager_interface.entityName
        assert manager.entityName(a_ref, a_context) == method.return_value
        method.assert_called_once_with(a_ref, a_context, host_session)

    def test_entityDisplayName(
            self, manager, mock_manager_interface, host_session, a_ref, a_context):
        method = mock_manager_interface.entityDisplayName
        assert manager.entityDisplayName(a_ref, a_context) == method.return_value
        method.assert_called_once_with(a_ref, a_context, host_session)

    def test_getEntityMetadata(
            self, manager, mock_manager_interface, host_session, a_ref, a_context):
        method = mock_manager_interface.getEntityMetadata
        assert manager.getEntityMetadata(a_ref, a_context) == method.return_value
        method.assert_called_once_with(a_ref, a_context, host_session)

    def test_setEntityMetadata(
            self, manager, mock_manager_interface, host_session, a_ref, a_context):

        method = mock_manager_interface.setEntityMetadata
        some_data = {"k": "v"}

        assert manager.setEntityMetadata(a_ref, some_data, a_context) == method.return_value
        method.assert_called_once_with(a_ref, some_data, a_context, host_session, merge=True)
        method.reset_mock()

        assert manager.setEntityMetadata(
            a_ref, some_data, a_context, merge=False) == method.return_value
        method.assert_called_once_with(a_ref, some_data, a_context, host_session, merge=False)

    def test_getEntityMetadataEntry(
            self, manager, mock_manager_interface, host_session, a_ref, a_context):

        method = mock_manager_interface.getEntityMetadataEntry
        a_key = "key"
        a_default = 2

        assert manager.getEntityMetadataEntry(a_ref, a_key, a_context) == method.return_value
        method.assert_called_once_with(a_ref, a_key, a_context, host_session, defaultValue=None)
        method.reset_mock()

        assert manager.getEntityMetadataEntry(
            a_ref, a_key, a_context, defaultValue=a_default) == method.return_value
        method.assert_called_once_with(
            a_ref, a_key, a_context, host_session, defaultValue=a_default)

    def test_setEntityMetadataEntry(
            self, manager, mock_manager_interface, host_session, a_ref, a_context):
        a_key = "key"
        a_value = "value"
        method = mock_manager_interface.setEntityMetadataEntry
        assert manager.setEntityMetadataEntry(
            a_ref, a_key, a_value, a_context) == method.return_value
        method.assert_called_once_with(a_ref, a_key, a_value, a_context, host_session)

    def test_entityVersionName(
            self, manager, mock_manager_interface, host_session, a_ref, a_context):
        method = mock_manager_interface.entityVersionName
        assert manager.entityVersionName(a_ref, a_context) == method.return_value
        method.assert_called_once_with(a_ref, a_context, host_session)

    def test_entityVersions(
            self, manager, mock_manager_interface, host_session, a_ref, a_context):

        method = mock_manager_interface.entityVersions

        assert manager.entityVersions(a_ref, a_context) == method.return_value
        method.assert_called_once_with(
            a_ref, a_context, host_session, includeMetaVersions=False, maxResults=-1)
        method.reset_mock()

        max_results = 5
        assert manager.entityVersions(
            a_ref, a_context, maxResults=max_results) == method.return_value
        method.assert_called_once_with(
            a_ref, a_context, host_session, includeMetaVersions=False, maxResults=max_results)
        method.reset_mock()

        include_meta = True
        assert manager.entityVersions(
            a_ref, a_context, maxResults=max_results,
            includeMetaVersions=include_meta) == method.return_value
        method.assert_called_once_with(
            a_ref, a_context, host_session, includeMetaVersions=include_meta,
            maxResults=max_results)
        method.reset_mock()

    def test_finalizedEntityVersion(
            self, manager, mock_manager_interface, host_session, a_ref, a_context):
        method = mock_manager_interface.finalizedEntityVersion
        assert manager.finalizedEntityVersion(a_ref, a_context) == method.return_value
        method.assert_called_once_with(a_ref, a_context, host_session, overrideVersionName=None)
        method.reset_mock()

        a_version_name = "aVersion"
        method = mock_manager_interface.finalizedEntityVersion
        assert manager.finalizedEntityVersion(
            a_ref, a_context, overrideVersionName=a_version_name) == method.return_value
        method.assert_called_once_with(
            a_ref, a_context, host_session, overrideVersionName=a_version_name)

    def test_getRelatedReferences(
            self, manager, mock_manager_interface, host_session, a_ref, an_entity_spec, a_context):

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

    def test_resolveEntityReference(
            self, manager, mock_manager_interface, host_session, a_ref, a_context):
        method = mock_manager_interface.resolveEntityReference
        assert manager.resolveEntityReference(a_ref, a_context) == method.return_value
        method.assert_called_once_with(a_ref, a_context, host_session)

    def test_resolveEntityReferences(
            self, manager, mock_manager_interface, host_session, some_refs, a_context):
        method = mock_manager_interface.resolveEntityReferences
        assert manager.resolveEntityReferences(some_refs, a_context) == method.return_value
        method.assert_called_once_with(some_refs, a_context, host_session)

    def test_managementPolicy(
            self, manager, mock_manager_interface, host_session, an_entity_spec, a_context, a_ref):

        method = mock_manager_interface.managementPolicy
        assert manager.managementPolicy(an_entity_spec, a_context) == method.return_value
        method.assert_called_once_with(an_entity_spec, a_context, host_session, entityRef=None)
        method.reset_mock()

        method = mock_manager_interface.managementPolicy
        assert manager.managementPolicy(
            an_entity_spec, a_context, entityRef=a_ref) == method.return_value
        method.assert_called_once_with(an_entity_spec, a_context, host_session, entityRef=a_ref)

    def test_thumbnailSpecification(
            self, manager, mock_manager_interface, host_session, an_entity_spec, a_context):
        some_options = {"k": "v"}
        method = mock_manager_interface.thumbnailSpecification
        assert manager.thumbnailSpecification(
            an_entity_spec, a_context, some_options) == method.return_value
        method.assert_called_once_with(an_entity_spec, a_context, some_options, host_session)

    def test_preflight(
            self, manager, mock_manager_interface, host_session, a_ref, an_entity_spec, a_context):
        method = mock_manager_interface.preflight
        assert manager.preflight(a_ref, an_entity_spec, a_context) == method.return_value
        method.assert_called_once_with(a_ref, an_entity_spec, a_context, host_session)

    def test_preflightMultiple(
            self, manager, mock_manager_interface, host_session, some_refs, an_entity_spec,
            a_context):
        method = mock_manager_interface.preflightMultiple
        assert manager.preflightMultiple(
            some_refs, an_entity_spec, a_context) == method.return_value
        method.assert_called_once_with(some_refs, an_entity_spec, a_context, host_session)

    def test_register(
            self, manager, mock_manager_interface, host_session, a_ref, an_entity_spec, a_context):

        register_method = mock_manager_interface.register
        setmeta_method = mock_manager_interface.setEntityMetadata

        some_string = "primary string"
        some_meta = {"k": "v"}

        # the return value is used in the setEntityMetadata call so we
        # need it to provide an actual ref we know
        mutated_ref = f"{a_ref}-registered"
        register_method.return_value = mutated_ref

        # Test without metadata

        assert manager.register(
            some_string, a_ref, an_entity_spec, a_context) == register_method.return_value
        register_method.assert_called_once_with(
            some_string, a_ref, an_entity_spec, a_context, host_session)
        setmeta_method.assert_not_called()

        mock_manager_interface.reset_mock()

        # Test with metadata

        assert manager.register(
            some_string, a_ref, an_entity_spec, a_context,
            metadata=some_meta) == register_method.return_value
        register_method.assert_called_once_with(
            some_string, a_ref, an_entity_spec, a_context, host_session)
        setmeta_method.assert_called_once_with(
            mutated_ref, some_meta, a_context, host_session, merge=True)

    def test_registerMultiple(
            self, manager, mock_manager_interface, host_session, a_ref, an_entity_spec, a_context):
        two_strings = ("a", "b")
        two_refs = (a_ref, a_ref)
        two_specs = (an_entity_spec, an_entity_spec)
        method = mock_manager_interface.registerMultiple
        assert manager.registerMultiple(
            two_strings, two_refs, two_specs, a_context) == method.return_value
        method.assert_called_once_with(two_strings, two_refs, two_specs, a_context, host_session)
