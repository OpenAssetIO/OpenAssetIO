#
#   Copyright 2024 The Foundry Visionmongers Ltd
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
Tests for the SimpleCppManager.

Note that SimpleCppManager is data-driven and tests assume a particular
configuration. See resources/openassetio_config.toml.
"""
import operator

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pathlib

import pytest


from openassetio.trait import TraitsData
from openassetio import access, Context, errors, EntityReference
from openassetio import managerApi
from openassetio.hostApi import HostInterface, ManagerFactory, Manager
from openassetio.pluginSystem import CppPluginSystemManagerImplementationFactory
from openassetio.log import ConsoleLogger


class Test_SimpleCppManager_identifier:

    def test_when_not_overridden_by_env_var_then_identifier_matches_default(
        self, the_host_interface
    ):
        impl_factory = CppPluginSystemManagerImplementationFactory(ConsoleLogger())
        manager_factory = ManagerFactory(the_host_interface, impl_factory, ConsoleLogger())

        available_managers = manager_factory.availableManagers()

        assert list(available_managers.keys()) == [
            "org.openassetio.examples.manager.simplecppmanager"
        ]

        manager = manager_factory.createManager(
            "org.openassetio.examples.manager.simplecppmanager"
        )

        assert manager.identifier() == "org.openassetio.examples.manager.simplecppmanager"

    def test_when_overridden_by_env_var_then_identifier_matches_env_var(
        self, monkeypatch, the_host_interface
    ):
        monkeypatch.setenv("OPENASSETIO_SIMPLECPPMANAGER_IDENTIFIER", "foo.bar")

        impl_factory = CppPluginSystemManagerImplementationFactory(ConsoleLogger())
        manager_factory = ManagerFactory(the_host_interface, impl_factory, ConsoleLogger())

        available_managers = manager_factory.availableManagers()

        assert list(available_managers.keys()) == ["foo.bar"]

        manager = manager_factory.createManager("foo.bar")

        assert manager.identifier() == "foo.bar"


class Test_SimpleCppManager_initialize:
    class StubState(managerApi.ManagerStateBase):
        pass

    def test_when_default_capability_then_default_capability_set_available(
        self, a_fresh_simple_cpp_manager, a_context
    ):
        expected_capability_map = {
            Manager.Capability.kStatefulContexts: False,
            Manager.Capability.kCustomTerminology: False,
            Manager.Capability.kResolution: True,
            Manager.Capability.kPublishing: False,
            Manager.Capability.kRelationshipQueries: False,
            Manager.Capability.kExistenceQueries: False,
            Manager.Capability.kDefaultEntityReferences: False,
        }

        for capability, expected_value in expected_capability_map.items():
            assert a_fresh_simple_cpp_manager.hasCapability(capability) == expected_value

        with pytest.raises(errors.NotImplementedException):
            a_fresh_simple_cpp_manager.updateTerminology({})

        with pytest.raises(errors.NotImplementedException):
            a_fresh_simple_cpp_manager.preflight([], [], access.PublishingAccess.kWrite, a_context)

        with pytest.raises(errors.NotImplementedException):
            a_fresh_simple_cpp_manager.register([], [], access.PublishingAccess.kWrite, a_context)

        with pytest.raises(errors.NotImplementedException):
            a_fresh_simple_cpp_manager.getWithRelationship(
                [], TraitsData(), 1, access.RelationsAccess.kRead, a_context, set()
            )

        with pytest.raises(errors.NotImplementedException):
            a_fresh_simple_cpp_manager.getWithRelationships(
                EntityReference(""),
                [],
                1,
                access.RelationsAccess.kRead,
                a_context,
                set(),
            )

        with pytest.raises(errors.NotImplementedException):
            a_fresh_simple_cpp_manager.entityExists([], a_context)

        with pytest.raises(errors.NotImplementedException):
            a_fresh_simple_cpp_manager.defaultEntityReference(
                [],
                access.DefaultEntityAccess.kRead,
                a_context,
                lambda *a: 0,
                lambda *a: 0,
            )

        with pytest.raises(errors.NotImplementedException):
            a_context.managerState = self.StubState()
            a_fresh_simple_cpp_manager.persistenceTokenForContext(a_context)

        with pytest.raises(errors.NotImplementedException):
            a_fresh_simple_cpp_manager.contextFromPersistenceToken("abc")

    def test_when_capability_is_overridden_then_stub_implementations_available(
        self, a_fresh_simple_cpp_manager, a_context
    ):

        settings = a_fresh_simple_cpp_manager.settings()
        settings["capabilities"] = (
            "entityReferenceIdentification,managementPolicyQueries,statefulContexts,"
            "customTerminology,resolution,publishing,relationshipQueries,existenceQueries,"
            "defaultEntityReferences,entityTraitIntrospection"
        )
        a_fresh_simple_cpp_manager.initialize(settings)

        expected_capability_map = {
            Manager.Capability.kStatefulContexts: True,
            Manager.Capability.kCustomTerminology: True,
            Manager.Capability.kResolution: True,
            Manager.Capability.kPublishing: True,
            Manager.Capability.kRelationshipQueries: True,
            Manager.Capability.kExistenceQueries: True,
            Manager.Capability.kDefaultEntityReferences: True,
        }

        for capability, expected_value in expected_capability_map.items():
            assert a_fresh_simple_cpp_manager.hasCapability(capability) == expected_value

        assert a_fresh_simple_cpp_manager.updateTerminology({}) == {}

        assert a_fresh_simple_cpp_manager.preflight(
            EntityReference("blah"),
            TraitsData(),
            access.PublishingAccess.kWrite,
            a_context,
        ) == EntityReference("blah")

        assert a_fresh_simple_cpp_manager.register(
            EntityReference("blah"),
            TraitsData(),
            access.PublishingAccess.kWrite,
            a_context,
        ) == EntityReference("blah")

        assert (
            a_fresh_simple_cpp_manager.getWithRelationship(
                EntityReference("blah"),
                TraitsData(),
                1,
                access.RelationsAccess.kRead,
                a_context,
                set(),
            )
            is not None
        )

        assert (
            a_fresh_simple_cpp_manager.getWithRelationships(
                EntityReference(""),
                [TraitsData()],
                1,
                access.RelationsAccess.kRead,
                a_context,
                set(),
            )
            is not None
        )

        assert a_fresh_simple_cpp_manager.entityExists(EntityReference("blah"), a_context) is False

        default_refs = [None]

        a_fresh_simple_cpp_manager.defaultEntityReference(
            [set()],
            access.DefaultEntityAccess.kRead,
            a_context,
            lambda idx, ref: operator.setitem(default_refs, idx, ref),
            lambda *a: pytest.fail("Should not be called"),
        )
        assert default_refs == [EntityReference("simplecpp://")]

    def test_when_prefix_overridden_then_entity_reference_format_changed(
        self, a_fresh_simple_cpp_manager
    ):
        assert a_fresh_simple_cpp_manager.isEntityReferenceString("simplecpp://😀")
        assert not a_fresh_simple_cpp_manager.isEntityReferenceString("somethingelse@😀")

        settings = a_fresh_simple_cpp_manager.settings()
        settings["prefix"] = "somethingelse@"
        a_fresh_simple_cpp_manager.initialize(settings)

        assert not a_fresh_simple_cpp_manager.isEntityReferenceString("simplecpp://@😀")
        assert a_fresh_simple_cpp_manager.isEntityReferenceString("somethingelse@😀")

    def test_when_capability_doesnt_exist_then_ConfigurationException_raised(
        self, a_fresh_simple_cpp_manager
    ):
        settings = a_fresh_simple_cpp_manager.settings()
        settings["capabilities"] = "non_existent_capability"
        with pytest.raises(errors.ConfigurationException):
            a_fresh_simple_cpp_manager.initialize(settings)


class Test_SimpleCppManager_isEntityReferenceString:
    def test_when_not_a_reference_then_returns_false(self, a_simple_cpp_manager):
        assert not a_simple_cpp_manager.isEntityReferenceString("not a reference")

    def test_when_is_a_reference_then_returns_true(self, a_simple_cpp_manager):
        assert a_simple_cpp_manager.isEntityReferenceString("simplecpp://😀")


class Test_SimpleCppManager_managementPolicy:
    def test_when_has_entity_trait_then_policy_contains_policy_trait_and_entity_trait(
        self, a_simple_cpp_manager: Manager, a_context: Context
    ):
        expected_policies = [
            TraitsData(),
            TraitsData({"openassetio-mediacreation:managementPolicy.Managed"}),
            TraitsData(
                {
                    "openassetio-mediacreation:content.LocatableContent",
                    "openassetio-mediacreation:managementPolicy.Managed",
                }
            ),
            TraitsData(
                {
                    "openassetio-mediacreation:content.LocatableContent",
                    "openassetio-mediacreation:managementPolicy.Managed",
                }
            ),
            TraitsData(
                {
                    "openassetio-mediacreation:identity.DisplayName",
                    "openassetio-mediacreation:managementPolicy.Managed",
                }
            ),
            TraitsData(
                {
                    "openassetio-mediacreation:content.LocatableContent",
                    "openassetio-mediacreation:identity.DisplayName",
                    "openassetio-mediacreation:managementPolicy.Managed",
                }
            ),
        ]

        actual_policies = a_simple_cpp_manager.managementPolicy(
            [
                set(),
                {"openassetio-mediacreation:usage.Entity"},
                {
                    "openassetio-mediacreation:usage.Entity",
                    "openassetio-mediacreation:content.LocatableContent",
                },
                {"openassetio-mediacreation:content.LocatableContent"},
                {"openassetio-mediacreation:identity.DisplayName"},
                {
                    "openassetio-mediacreation:content.LocatableContent",
                    "openassetio-mediacreation:identity.DisplayName",
                },
            ],
            access.PolicyAccess.kRead,
            a_context,
        )

        assert expected_policies == actual_policies

    @pytest.mark.parametrize(
        "policy_access",
        [
            access.PolicyAccess.kWrite,
            access.PolicyAccess.kManagerDriven,
            access.PolicyAccess.kCreateRelated,
        ],
    )
    def test_when_non_read_policy_then_response_is_empty(
        self, a_simple_cpp_manager, a_context, policy_access
    ):
        [policy] = a_simple_cpp_manager.managementPolicy(
            [{"openassetio-mediacreation:content.LocatableContent"}],
            policy_access,
            a_context,
        )

        assert policy == TraitsData()


class Test_SimpleCppManager_entityTraits:
    def test_when_entity_doesnt_exist_then_EntityResolutionError(
        self, a_simple_cpp_manager, a_context
    ):
        an_entity_reference = a_simple_cpp_manager.createEntityReference("simplecpp://😀")

        with pytest.raises(errors.BatchElementException) as err:
            a_simple_cpp_manager.entityTraits(
                an_entity_reference, access.EntityTraitsAccess.kRead, a_context
            )

        assert err.value.error.code == errors.BatchElementError.ErrorCode.kEntityResolutionError

    def test_when_non_read_access_then_EntityAccessError(self, a_simple_cpp_manager, a_context):
        an_entity_reference = a_simple_cpp_manager.createEntityReference(
            "simplecpp://test/entity/1"
        )
        with pytest.raises(errors.BatchElementException) as err:
            a_simple_cpp_manager.entityTraits(
                [an_entity_reference, an_entity_reference],
                access.EntityTraitsAccess.kWrite,
                a_context,
            )

        assert err.value.error.code == errors.BatchElementError.ErrorCode.kEntityAccessError

    def test_when_entity_exists_for_read_access_then_returns_entity_traits(
        self, a_simple_cpp_manager, a_context
    ):
        an_entity_reference = a_simple_cpp_manager.createEntityReference(
            "simplecpp://test/entity/1"
        )
        expected_entity_traits = {
            "openassetio-mediacreation:usage.Entity",
            "openassetio-mediacreation:identity.DisplayName",
            "openassetio-mediacreation:content.LocatableContent",
        }
        actual_entity_traits = a_simple_cpp_manager.entityTraits(
            an_entity_reference, access.EntityTraitsAccess.kRead, a_context
        )

        assert expected_entity_traits == actual_entity_traits


class Test_SimpleCppManager_resolve:
    def test_when_values_resolved_then_value_types_are_correct(
        self, a_simple_cpp_manager, a_context
    ):
        an_entity_reference = a_simple_cpp_manager.createEntityReference(
            "simplecpp://test/entity/2"
        )

        expeted_trait_data = TraitsData()
        expeted_trait_data.setTraitProperty(
            "openassetio-mediacreation:content.LocatableContent",
            "location",
            "file:///tmp/test2.txt",
        )
        expeted_trait_data.setTraitProperty(
            "openassetio-mediacreation:content.LocatableContent",
            "isTemplated",
            False,
        )
        expeted_trait_data.setTraitProperty(
            "openassetio-mediacreation:timeDomain.FrameRanged", "startFrame", 123
        )
        expeted_trait_data.setTraitProperty(
            "openassetio-mediacreation:timeDomain.FrameRanged", "framesPerSecond", 123.4
        )

        actual_trait_data = a_simple_cpp_manager.resolve(
            an_entity_reference,
            {
                "openassetio-mediacreation:content.LocatableContent",
                "openassetio-mediacreation:timeDomain.FrameRanged",
            },
            access.ResolveAccess.kRead,
            a_context,
        )

        assert expeted_trait_data == actual_trait_data


@pytest.fixture
def a_fresh_simple_cpp_manager(the_args_for_manager_factory):
    return ManagerFactory.defaultManagerForInterface(*the_args_for_manager_factory)


@pytest.fixture(scope="module")
def a_simple_cpp_manager(the_args_for_manager_factory):
    return ManagerFactory.defaultManagerForInterface(*the_args_for_manager_factory)


@pytest.fixture
def a_context(a_simple_cpp_manager):
    return a_simple_cpp_manager.createContext()


@pytest.fixture(scope="module")
def the_args_for_manager_factory(the_host_interface):
    logger = ConsoleLogger()

    impl_factory = CppPluginSystemManagerImplementationFactory(logger)

    config_file_path = pathlib.Path(__file__).parent / "resources" / "openassetio_config.toml"

    return (str(config_file_path), the_host_interface, impl_factory, logger)


@pytest.fixture(scope="module")
def the_host_interface():
    class TestHostInterface(HostInterface):
        def identifier(self):
            return "org.openassetio.examples.SimpleCppManager.test"

        def displayName(self):
            return "Simple C++ Manager Test Host"

    return TestHostInterface()
