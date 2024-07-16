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
These tests check the functionality of the hybrid
HybridPluginSystemManagerImplementationFactory implementation.
"""
import inspect
import itertools
from unittest import mock

import pytest
from openassetio import errors, access, Context, EntityReference
from openassetio.trait import TraitsData

# pylint: disable=unused-argument,too-many-lines,too-many-locals
# pylint: disable=invalid-name,redefined-outer-name,
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=too-many-public-methods


from openassetio.hostApi import ManagerImplementationFactoryInterface
from openassetio.managerApi import (
    ManagerInterface,
    ManagerStateBase,
    EntityReferencePagerInterface,
)
from openassetio.pluginSystem import HybridPluginSystemManagerImplementationFactory


class Test_HybridPluginSystemManagerImplementationFactory_init:
    def test_when_None_child_factory_then_raises_error(self, mock_logger, factory_a):
        with pytest.raises(
            errors.InputValidationException,
            match="HybridPluginSystem: Manager implementation factory cannot be None",
        ):
            HybridPluginSystemManagerImplementationFactory([factory_a, None], mock_logger)

    def test_when_empty_child_factories_then_raises_error(self, mock_logger):
        with pytest.raises(
            errors.InputValidationException,
            match=(
                "HybridPluginSystem: At least one child manager implementation factory must be"
                " provided"
            ),
        ):
            HybridPluginSystemManagerImplementationFactory([], mock_logger)


class Test_HybridPluginSystemManagerImplementationFactory_identifiers:

    def test_identifiers_from_all_children_deduplicated(self, mock_logger, factory_a, factory_b):
        factory_a.mock.identifiers.return_value = ["a", "c", "b"]
        factory_b.mock.identifiers.return_value = ["b", "c", "d"]

        factory = HybridPluginSystemManagerImplementationFactory(
            [factory_b, factory_a], mock_logger
        )
        assert factory.identifiers() == ["a", "b", "c", "d"]


class Test_HybridPluginSystemManagerImplementationFactory_instantiate:
    def test_when_no_match_from_multiple_child_factories_then_error_raised(
        self, factory_a, factory_b, mock_logger
    ):
        factory_a.mock.identifiers.return_value = ["bar"]
        factory_b.mock.identifiers.return_value = ["baz"]

        factory = HybridPluginSystemManagerImplementationFactory(
            [factory_a, factory_b], mock_logger
        )

        with pytest.raises(
            errors.InputValidationException,
            match="HybridPluginSystem: No plug-in registered with the identifier 'foo'",
        ):
            factory.instantiate("foo")

    def test_when_single_factory_matches_then_uses_that_factorys_interface(
        self, mock_logger, factory_a, factory_b, the_plugin_identifier
    ):
        factory_a.mock.identifiers.return_value = ["a", the_plugin_identifier]
        factory_b.mock.identifiers.return_value = ["b"]

        factory = HybridPluginSystemManagerImplementationFactory(
            [factory_a, factory_b], mock_logger
        )

        actual_manager_interface = factory.instantiate(the_plugin_identifier)

        factory_a.mock.instantiate.assert_called_once_with(the_plugin_identifier)
        assert not factory_b.mock.instantiate.called
        assert actual_manager_interface is factory_a.mock.instantiate.return_value

    def test_when_many_factories_provided_and_one_matches_then_uses_that_factorys_interface(
        self,
        mock_logger,
        create_mock_manager_interface,
        factory_a,
        factory_b,
        the_plugin_identifier,
    ):
        factory_a.mock.identifiers.return_value = ["a"]
        factory_b.mock.identifiers.return_value = ["b"]
        factory_c = MockManagerImplementationFactory(mock_logger)
        factory_c.mock.identifiers.return_value = ["c"]
        factory_d = MockManagerImplementationFactory(mock_logger)
        factory_d.mock.identifiers.return_value = [the_plugin_identifier]
        factory_d.mock.instantiate.return_value = create_mock_manager_interface()
        factory_e = MockManagerImplementationFactory(mock_logger)
        factory_e.mock.identifiers.return_value = ["e"]

        factory = HybridPluginSystemManagerImplementationFactory(
            [factory_a, factory_b, factory_c, factory_d, factory_e], mock_logger
        )

        actual_manager_interface = factory.instantiate(the_plugin_identifier)

        assert not factory_a.mock.instantiate.called
        assert not factory_b.mock.instantiate.called
        assert not factory_c.mock.instantiate.called
        factory_d.mock.instantiate.assert_called_once_with(the_plugin_identifier)
        assert not factory_e.mock.instantiate.called

        assert actual_manager_interface is factory_d.mock.instantiate.return_value

    def test_when_multiple_factories_match_then_hybrid_interface_used(
        self, mock_logger, factory_a, factory_b, the_plugin_identifier
    ):
        factory = HybridPluginSystemManagerImplementationFactory(
            [factory_a, factory_b], mock_logger
        )

        actual_manager_interface = factory.instantiate(the_plugin_identifier)

        factory_a.mock.instantiate.assert_called_once_with(the_plugin_identifier)
        factory_b.mock.instantiate.assert_called_once_with(the_plugin_identifier)
        assert isinstance(actual_manager_interface, ManagerInterface)
        assert actual_manager_interface is not factory_a.mock.instantiate.return_value
        assert actual_manager_interface is not factory_b.mock.instantiate.return_value

    def test_when_child_factories_go_out_of_scope_then_hybrid_retains_valid_reference(
        self, mock_logger, create_mock_manager_interface, the_plugin_identifier
    ):
        # I.e. test that PyRetainingSharedPtr is used in C++ to refer to
        # the child factories, so the Python facade is kept alive
        # despite going out of scope.

        def make_factory():
            factory_a = MockManagerImplementationFactory(mock_logger)
            factory_a.mock.identifiers.return_value = [the_plugin_identifier]
            factory_a.mock.instantiate.return_value = create_mock_manager_interface()

            factory_b = MockManagerImplementationFactory(mock_logger)
            factory_b.mock.identifiers.return_value = [the_plugin_identifier]
            factory_b.mock.instantiate.return_value = create_mock_manager_interface()

            return HybridPluginSystemManagerImplementationFactory(
                [factory_a, factory_b], mock_logger
            )

        factory = make_factory()

        # Hoping to avoid pybind11 exception "RuntimeError: Tried to
        # call pure virtual function"
        manager_interface = factory.instantiate(the_plugin_identifier)

        assert isinstance(manager_interface, ManagerInterface)


class Test_HybridPluginSystemManagerImplementationFactory_ManagerInterface:

    def test_identifier_uses_first_child_implementation(
        self,
        mock_logger,
        factory_a,
        factory_b,
        the_plugin_identifier,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
    ):
        # Note: in reality we require that plugins and their
        # ManagerInterface instances advertise the same identifier, but
        # just for testing here we vary them.

        manager_interface_a.mock.identifier.return_value = "a"
        manager_interface_b.mock.identifier.return_value = "b"

        identifier = hybrid_manager_interface.identifier()

        assert identifier == "a"

        manager_interface = HybridPluginSystemManagerImplementationFactory(
            [factory_b, factory_a], mock_logger
        ).instantiate(the_plugin_identifier)

        identifier = manager_interface.identifier()

        assert identifier == "b"

    def test_displayName_uses_first_child_implementation(
        self,
        mock_logger,
        factory_a,
        factory_b,
        the_plugin_identifier,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
    ):
        manager_interface_a.mock.displayName.return_value = "A"
        manager_interface_b.mock.displayName.return_value = "B"

        name = hybrid_manager_interface.displayName()

        assert name == "A"

        manager_interface = HybridPluginSystemManagerImplementationFactory(
            [factory_b, factory_a], mock_logger
        ).instantiate(the_plugin_identifier)

        name = manager_interface.displayName()

        assert name == "B"

    def test_info_aggregates_all_implementations_preferring_first(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
    ):
        manager_interface_a.mock.info.return_value = {"x": 1, "y": "i"}
        manager_interface_b.mock.info.return_value = {"y": "k", "z": 1.2}

        assert hybrid_manager_interface.info() == {"x": 1, "y": "i", "z": 1.2}

    def test_settings_aggregates_all_implementations_preferring_first(
        self,
        a_host_session,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
    ):
        manager_interface_a.mock.settings.return_value = {"x": "j", "y": "i"}
        manager_interface_b.mock.settings.return_value = {"y": "k", "z": 1.2}

        assert hybrid_manager_interface.settings(a_host_session) == {"x": "j", "y": "i", "z": 1.2}

    def test_when_not_yet_initialized_then_no_capabilities_available(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        a_host_session,
    ):
        manager_interface_a.mock.hasCapability.return_value = True

        for capability in ManagerInterface.Capability.__members__.values():
            assert not hybrid_manager_interface.hasCapability(capability)

        hybrid_manager_interface.initialize({}, a_host_session)

        for capability in ManagerInterface.Capability.__members__.values():
            assert hybrid_manager_interface.hasCapability(capability)

    @pytest.mark.parametrize(
        "capability",
        # Couple of arbitrary capabilities.
        (
            ManagerInterface.Capability.kPublishing,
            ManagerInterface.Capability.kEntityReferenceIdentification,
        ),
    )
    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_hasCapability_is_aggregated_from_all_child_implementations(
        self,
        capability,
        hasCapability_a,
        hasCapability_b,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        a_host_session,
    ):
        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == capability and hasCapability_b
        )

        hybrid_manager_interface.initialize({}, a_host_session)

        assert hybrid_manager_interface.hasCapability(capability) is (
            hasCapability_a or hasCapability_b
        )

    def test_initialize_initializes_all_child_implementations_forwarding_all_arguments(
        self, manager_interface_a, manager_interface_b, hybrid_manager_interface, a_host_session
    ):
        expected_settings = {"x": 1, "y": "2", "z": False}

        hybrid_manager_interface.initialize(expected_settings, a_host_session)

        manager_interface_a.mock.initialize.assert_called_once_with(
            expected_settings, a_host_session
        )
        manager_interface_b.mock.initialize.assert_called_once_with(
            expected_settings, a_host_session
        )

    def test_flushCaches_flushes_all_child_implementations(
        self, manager_interface_a, manager_interface_b, hybrid_manager_interface, a_host_session
    ):
        hybrid_manager_interface.flushCaches(a_host_session)

        manager_interface_a.mock.flushCaches.assert_called_once_with(a_host_session)
        manager_interface_b.mock.flushCaches.assert_called_once_with(a_host_session)

    #
    # The remaining tests are all rather similar - we ensure that the
    # appropriate child implementation is chosen based on different
    # combinations of capabilities, and that arguments and results
    # are forwarded.
    #

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_updateTerminology(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        a_host_session,
        hasCapability_a,
        hasCapability_b,
    ):
        expected_capability = ManagerInterface.Capability.kCustomTerminology
        some_input_terminology = {"x": "y"}
        expected_output_terminology = {"x": "y", "z": "w"}

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )
        manager_interface_a.mock.updateTerminology.return_value = expected_output_terminology
        manager_interface_b.mock.updateTerminology.return_value = expected_output_terminology

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.updateTerminology(some_input_terminology, a_host_session)
        else:
            # At least one implementation has the capability.
            actual_output_terminology = hybrid_manager_interface.updateTerminology(
                some_input_terminology, a_host_session
            )
            assert actual_output_terminology == expected_output_terminology

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.updateTerminology.assert_called_once_with(
                    some_input_terminology, a_host_session
                )
                manager_interface_b.mock.updateTerminology.assert_not_called()
            else:
                # The second implementation has the capability.
                manager_interface_a.mock.updateTerminology.assert_not_called()
                manager_interface_b.mock.updateTerminology.assert_called_once_with(
                    some_input_terminology, a_host_session
                )

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_managementPolicy(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        a_host_session,
        hasCapability_a,
        hasCapability_b,
        a_context,
    ):
        some_trait_sets = [{"x"}]
        a_policy_access = access.PolicyAccess.kRead

        expected_capability = ManagerInterface.Capability.kManagementPolicyQueries
        expected_policies = [TraitsData({"z"})]

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )
        manager_interface_a.mock.managementPolicy.return_value = expected_policies
        manager_interface_b.mock.managementPolicy.return_value = expected_policies

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.managementPolicy(
                    some_trait_sets, a_policy_access, a_context, a_host_session
                )
        else:
            # At least one implementation has the capability.
            actual_policies = hybrid_manager_interface.managementPolicy(
                some_trait_sets, a_policy_access, a_context, a_host_session
            )
            assert actual_policies == expected_policies

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.managementPolicy.assert_called_once_with(
                    some_trait_sets, a_policy_access, a_context, a_host_session
                )
                manager_interface_b.mock.managementPolicy.assert_not_called()
            else:
                # The second implementation has the capability.
                manager_interface_a.mock.managementPolicy.assert_not_called()
                manager_interface_b.mock.managementPolicy.assert_called_once_with(
                    some_trait_sets, a_policy_access, a_context, a_host_session
                )

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_createState(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        a_host_session,
        hasCapability_a,
        hasCapability_b,
        a_manager_state,
    ):
        expected_capability = ManagerInterface.Capability.kStatefulContexts

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )
        manager_interface_a.mock.createState.return_value = a_manager_state
        manager_interface_b.mock.createState.return_value = a_manager_state

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.createState(a_host_session)
        else:
            # At least one implementation has the capability.
            actual_state = hybrid_manager_interface.createState(a_host_session)
            assert actual_state is a_manager_state

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.createState.assert_called_once_with(a_host_session)
                manager_interface_b.mock.createState.assert_not_called()
            else:
                # The second implementation has the capability.
                manager_interface_a.mock.createState.assert_not_called()
                manager_interface_b.mock.createState.assert_called_once_with(a_host_session)

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_createChildState(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        a_host_session,
        hasCapability_a,
        hasCapability_b,
        a_manager_state,
    ):
        expected_capability = ManagerInterface.Capability.kStatefulContexts

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )

        class ChildManagerState(ManagerStateBase):
            pass

        child_manager_state = ChildManagerState()
        manager_interface_a.mock.createChildState.return_value = child_manager_state
        manager_interface_b.mock.createChildState.return_value = child_manager_state

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.createChildState(a_manager_state, a_host_session)
        else:
            # At least one implementation has the capability.
            actual_state = hybrid_manager_interface.createChildState(
                a_manager_state, a_host_session
            )
            assert actual_state is child_manager_state

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.createChildState.assert_called_once_with(
                    a_manager_state, a_host_session
                )
                manager_interface_b.mock.createChildState.assert_not_called()
            else:
                # The second implementation has the capability.
                manager_interface_a.mock.createChildState.assert_not_called()
                manager_interface_b.mock.createChildState.assert_called_once_with(
                    a_manager_state, a_host_session
                )

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_persistenceTokenForState(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        a_host_session,
        hasCapability_a,
        hasCapability_b,
        a_manager_state,
    ):
        expected_capability = ManagerInterface.Capability.kStatefulContexts

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )

        expected_persistence_token = "some token"
        manager_interface_a.mock.persistenceTokenForState.return_value = expected_persistence_token
        manager_interface_b.mock.persistenceTokenForState.return_value = expected_persistence_token

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.persistenceTokenForState(a_manager_state, a_host_session)
        else:
            # At least one implementation has the capability.
            actual_persistence_token = hybrid_manager_interface.persistenceTokenForState(
                a_manager_state, a_host_session
            )
            assert actual_persistence_token == expected_persistence_token

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.persistenceTokenForState.assert_called_once_with(
                    a_manager_state, a_host_session
                )
                manager_interface_b.mock.persistenceTokenForState.assert_not_called()
            else:
                # The second implementation has the capability.
                manager_interface_a.mock.persistenceTokenForState.assert_not_called()
                manager_interface_b.mock.persistenceTokenForState.assert_called_once_with(
                    a_manager_state, a_host_session
                )

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_stateFromPersistenceToken(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        a_host_session,
        hasCapability_a,
        hasCapability_b,
        a_manager_state,
    ):
        expected_capability = ManagerInterface.Capability.kStatefulContexts

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )

        a_persistence_token = "some token"
        manager_interface_a.mock.stateFromPersistenceToken.return_value = a_manager_state
        manager_interface_b.mock.stateFromPersistenceToken.return_value = a_manager_state

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.stateFromPersistenceToken(
                    a_persistence_token, a_host_session
                )
        else:
            # At least one implementation has the capability.
            actual_state = hybrid_manager_interface.stateFromPersistenceToken(
                a_persistence_token, a_host_session
            )
            assert actual_state is a_manager_state

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.stateFromPersistenceToken.assert_called_once_with(
                    a_persistence_token, a_host_session
                )
                manager_interface_b.mock.stateFromPersistenceToken.assert_not_called()
            else:
                # The second implementation has the capability.
                manager_interface_a.mock.stateFromPersistenceToken.assert_not_called()
                manager_interface_b.mock.stateFromPersistenceToken.assert_called_once_with(
                    a_persistence_token, a_host_session
                )

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_isEntityReferenceString(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        hasCapability_a,
        hasCapability_b,
        a_host_session,
    ):
        expected_capability = ManagerInterface.Capability.kEntityReferenceIdentification

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )

        test_reference = "test_reference"
        manager_interface_a.mock.isEntityReferenceString.return_value = True
        manager_interface_b.mock.isEntityReferenceString.return_value = True

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.isEntityReferenceString(test_reference, a_host_session)
        else:
            # At least one implementation has the capability.
            result = hybrid_manager_interface.isEntityReferenceString(
                test_reference, a_host_session
            )
            assert result is True

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.isEntityReferenceString.assert_called_once_with(
                    test_reference, a_host_session
                )
                manager_interface_b.mock.isEntityReferenceString.assert_not_called()
            else:
                # The second implementation has the capability.
                manager_interface_a.mock.isEntityReferenceString.assert_not_called()
                manager_interface_b.mock.isEntityReferenceString.assert_called_once_with(
                    test_reference, a_host_session
                )

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_entityExists(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        hasCapability_a,
        hasCapability_b,
        a_context,
        a_host_session,
    ):
        expected_capability = ManagerInterface.Capability.kExistenceQueries
        entity_references = [EntityReference("x")]
        expected_success_cb = mock.Mock()
        expected_error_cb = mock.Mock()

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.entityExists(
                    entity_references,
                    a_context,
                    a_host_session,
                    expected_success_cb,
                    expected_error_cb,
                )
        else:
            # At least one implementation has the capability.
            hybrid_manager_interface.entityExists(
                entity_references,
                a_context,
                a_host_session,
                expected_success_cb,
                expected_error_cb,
            )

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.entityExists.assert_called_once_with(
                    entity_references, a_context, a_host_session, mock.ANY, mock.ANY
                )
                manager_interface_b.mock.entityExists.assert_not_called()

                actual_success_cb = manager_interface_a.mock.entityExists.call_args[0][3]
                actual_error_cb = manager_interface_a.mock.entityExists.call_args[0][4]
            else:
                # The second implementation has the capability.
                manager_interface_a.mock.entityExists.assert_not_called()
                manager_interface_b.mock.entityExists.assert_called_once_with(
                    entity_references, a_context, a_host_session, mock.ANY, mock.ANY
                )

                actual_success_cb = manager_interface_b.mock.entityExists.call_args[0][3]
                actual_error_cb = manager_interface_b.mock.entityExists.call_args[0][4]

            # Ensure the callbacks have been passed through. These will
            # be converted to an intermediate representation by
            # pybind11, so we cannot do a naive comparison.

            expected_success_cb_args = (123, True)
            expected_error_cb_args = (
                123,
                errors.BatchElementError(
                    errors.BatchElementError.ErrorCode.kEntityAccessError, "z"
                ),
            )
            actual_success_cb(*expected_success_cb_args)
            actual_error_cb(*expected_error_cb_args)
            expected_success_cb.assert_called_once_with(*expected_success_cb_args)
            expected_error_cb.assert_called_once_with(
                *expected_error_cb_args,
            )

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_entityTraits(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        hasCapability_a,
        hasCapability_b,
        a_context,
        a_host_session,
    ):
        expected_capability = ManagerInterface.Capability.kEntityTraitIntrospection
        entity_references = [EntityReference("x")]
        entity_traits_access = access.EntityTraitsAccess.kRead
        expected_success_cb = mock.Mock()
        expected_error_cb = mock.Mock()

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.entityTraits(
                    entity_references,
                    entity_traits_access,
                    a_context,
                    a_host_session,
                    expected_success_cb,
                    expected_error_cb,
                )
        else:
            # At least one implementation has the capability.
            hybrid_manager_interface.entityTraits(
                entity_references,
                entity_traits_access,
                a_context,
                a_host_session,
                expected_success_cb,
                expected_error_cb,
            )

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.entityTraits.assert_called_once_with(
                    entity_references,
                    entity_traits_access,
                    a_context,
                    a_host_session,
                    mock.ANY,
                    mock.ANY,
                )
                manager_interface_b.mock.entityTraits.assert_not_called()

                actual_success_cb = manager_interface_a.mock.entityTraits.call_args[0][4]
                actual_error_cb = manager_interface_a.mock.entityTraits.call_args[0][5]
            else:
                # The second implementation has the capability.
                manager_interface_a.mock.entityTraits.assert_not_called()
                manager_interface_b.mock.entityTraits.assert_called_once_with(
                    entity_references,
                    entity_traits_access,
                    a_context,
                    a_host_session,
                    mock.ANY,
                    mock.ANY,
                )

                actual_success_cb = manager_interface_b.mock.entityTraits.call_args[0][4]
                actual_error_cb = manager_interface_b.mock.entityTraits.call_args[0][5]

            # Ensure the callbacks have been passed through. These will
            # be converted to an intermediate representation by
            # pybind11, so we cannot do a naive comparison.

            expected_success_cb_args = (123, {"t"})
            expected_error_cb_args = (
                123,
                errors.BatchElementError(
                    errors.BatchElementError.ErrorCode.kEntityAccessError, "z"
                ),
            )
            actual_success_cb(*expected_success_cb_args)
            actual_error_cb(*expected_error_cb_args)
            expected_success_cb.assert_called_once_with(*expected_success_cb_args)
            expected_error_cb.assert_called_once_with(
                *expected_error_cb_args,
            )

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_resolve(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        hasCapability_a,
        hasCapability_b,
        a_context,
        a_host_session,
    ):
        expected_capability = ManagerInterface.Capability.kResolution
        entity_references = [EntityReference("x")]
        trait_set = {"t"}
        resolve_access = access.ResolveAccess.kRead
        expected_success_cb = mock.Mock()
        expected_error_cb = mock.Mock()

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.resolve(
                    entity_references,
                    trait_set,
                    resolve_access,
                    a_context,
                    a_host_session,
                    expected_success_cb,
                    expected_error_cb,
                )
        else:
            # At least one implementation has the capability.
            hybrid_manager_interface.resolve(
                entity_references,
                trait_set,
                resolve_access,
                a_context,
                a_host_session,
                expected_success_cb,
                expected_error_cb,
            )

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.resolve.assert_called_once_with(
                    entity_references,
                    trait_set,
                    resolve_access,
                    a_context,
                    a_host_session,
                    mock.ANY,
                    mock.ANY,
                )
                manager_interface_b.mock.resolve.assert_not_called()

                actual_success_cb = manager_interface_a.mock.resolve.call_args[0][5]
                actual_error_cb = manager_interface_a.mock.resolve.call_args[0][6]

            else:
                # The second implementation has the capability.
                manager_interface_a.mock.resolve.assert_not_called()
                manager_interface_b.mock.resolve.assert_called_once_with(
                    entity_references,
                    trait_set,
                    resolve_access,
                    a_context,
                    a_host_session,
                    mock.ANY,
                    mock.ANY,
                )

                actual_success_cb = manager_interface_b.mock.resolve.call_args[0][5]
                actual_error_cb = manager_interface_b.mock.resolve.call_args[0][6]

            # Ensure the callbacks have been passed through. These will
            # be converted to an intermediate representation by
            # pybind11, so we cannot do a naive comparison.

            expected_success_cb_args = (123, TraitsData({"t"}))
            expected_error_cb_args = (
                123,
                errors.BatchElementError(
                    errors.BatchElementError.ErrorCode.kEntityAccessError, "z"
                ),
            )
            actual_success_cb(*expected_success_cb_args)
            actual_error_cb(*expected_error_cb_args)
            expected_success_cb.assert_called_once_with(*expected_success_cb_args)
            expected_error_cb.assert_called_once_with(
                *expected_error_cb_args,
            )

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_defaultEntityReference(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        hasCapability_a,
        hasCapability_b,
        a_context,
        a_host_session,
    ):
        expected_capability = ManagerInterface.Capability.kDefaultEntityReferences
        trait_sets = [{"t"}]
        default_entity_access = access.DefaultEntityAccess.kRead
        expected_success_cb = mock.Mock()
        expected_error_cb = mock.Mock()

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.defaultEntityReference(
                    trait_sets,
                    default_entity_access,
                    a_context,
                    a_host_session,
                    expected_success_cb,
                    expected_error_cb,
                )
        else:
            # At least one implementation has the capability.
            hybrid_manager_interface.defaultEntityReference(
                trait_sets,
                default_entity_access,
                a_context,
                a_host_session,
                expected_success_cb,
                expected_error_cb,
            )

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.defaultEntityReference.assert_called_once_with(
                    trait_sets,
                    default_entity_access,
                    a_context,
                    a_host_session,
                    mock.ANY,
                    mock.ANY,
                )
                manager_interface_b.mock.defaultEntityReference.assert_not_called()

                actual_success_cb = manager_interface_a.mock.defaultEntityReference.call_args[0][4]
                actual_error_cb = manager_interface_a.mock.defaultEntityReference.call_args[0][5]

            else:
                # The second implementation has the capability.
                manager_interface_a.mock.defaultEntityReference.assert_not_called()
                manager_interface_b.mock.defaultEntityReference.assert_called_once_with(
                    trait_sets,
                    default_entity_access,
                    a_context,
                    a_host_session,
                    mock.ANY,
                    mock.ANY,
                )

                actual_success_cb = manager_interface_b.mock.defaultEntityReference.call_args[0][4]
                actual_error_cb = manager_interface_b.mock.defaultEntityReference.call_args[0][5]

            # Ensure the callbacks have been passed through. These will
            # be converted to an intermediate representation by
            # pybind11, so we cannot do a naive comparison.
            if hasCapability_a:
                actual_success_cb = manager_interface_a.mock.defaultEntityReference.call_args[0][4]
                actual_error_cb = manager_interface_a.mock.defaultEntityReference.call_args[0][5]
            else:
                actual_success_cb = manager_interface_b.mock.defaultEntityReference.call_args[0][4]
                actual_error_cb = manager_interface_b.mock.defaultEntityReference.call_args[0][5]

            expected_success_cb_args = (123, EntityReference("default"))
            expected_error_cb_args = (
                123,
                errors.BatchElementError(
                    errors.BatchElementError.ErrorCode.kEntityAccessError, "z"
                ),
            )
            actual_success_cb(*expected_success_cb_args)
            actual_error_cb(*expected_error_cb_args)
            expected_success_cb.assert_called_once_with(*expected_success_cb_args)
            expected_error_cb.assert_called_once_with(
                *expected_error_cb_args,
            )

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_getWithRelationship(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        hasCapability_a,
        hasCapability_b,
        a_context,
        a_host_session,
        an_entity_reference_pager,
    ):
        expected_capability = ManagerInterface.Capability.kRelationshipQueries
        entity_references = [EntityReference("test")]
        relationship_traits_data = TraitsData({"r"})
        result_trait_set = {"t"}
        page_size = 100
        relations_access = access.RelationsAccess.kRead
        expected_success_cb = mock.Mock()
        expected_error_cb = mock.Mock()

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.getWithRelationship(
                    entity_references,
                    relationship_traits_data,
                    result_trait_set,
                    page_size,
                    relations_access,
                    a_context,
                    a_host_session,
                    expected_success_cb,
                    expected_error_cb,
                )
        else:
            # At least one implementation has the capability.
            hybrid_manager_interface.getWithRelationship(
                entity_references,
                relationship_traits_data,
                result_trait_set,
                page_size,
                relations_access,
                a_context,
                a_host_session,
                expected_success_cb,
                expected_error_cb,
            )

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.getWithRelationship.assert_called_once_with(
                    entity_references,
                    relationship_traits_data,
                    result_trait_set,
                    page_size,
                    relations_access,
                    a_context,
                    a_host_session,
                    mock.ANY,
                    mock.ANY,
                )
                manager_interface_b.mock.getWithRelationship.assert_not_called()
                actual_success_cb = manager_interface_a.mock.getWithRelationship.call_args[0][7]
                actual_error_cb = manager_interface_a.mock.getWithRelationship.call_args[0][8]

            else:
                # The second implementation has the capability.
                manager_interface_a.mock.getWithRelationship.assert_not_called()
                manager_interface_b.mock.getWithRelationship.assert_called_once_with(
                    entity_references,
                    relationship_traits_data,
                    result_trait_set,
                    page_size,
                    relations_access,
                    a_context,
                    a_host_session,
                    mock.ANY,
                    mock.ANY,
                )

                actual_success_cb = manager_interface_b.mock.getWithRelationship.call_args[0][7]
                actual_error_cb = manager_interface_b.mock.getWithRelationship.call_args[0][8]

            # Ensure the callbacks have been passed through. These
            # will be converted to an intermediate representation by
            # pybind11, so we cannot do a naive comparison.

            expected_success_cb_args = (123, an_entity_reference_pager)
            expected_error_cb_args = (
                123,
                errors.BatchElementError(
                    errors.BatchElementError.ErrorCode.kEntityAccessError, "z"
                ),
            )
            actual_success_cb(*expected_success_cb_args)
            actual_error_cb(*expected_error_cb_args)
            expected_success_cb.assert_called_once_with(*expected_success_cb_args)
            expected_error_cb.assert_called_once_with(
                *expected_error_cb_args,
            )

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_getWithRelationships(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        hasCapability_a,
        hasCapability_b,
        a_context,
        a_host_session,
        an_entity_reference_pager,
    ):
        expected_capability = ManagerInterface.Capability.kRelationshipQueries
        entity_reference = EntityReference("test")
        relationship_traits_datas = [TraitsData({"r1"})]
        result_trait_set = {"t"}
        page_size = 100
        relations_access = access.RelationsAccess.kRead
        expected_success_cb = mock.Mock()
        expected_error_cb = mock.Mock()

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.getWithRelationships(
                    entity_reference,
                    relationship_traits_datas,
                    result_trait_set,
                    page_size,
                    relations_access,
                    a_context,
                    a_host_session,
                    expected_success_cb,
                    expected_error_cb,
                )
        else:
            # At least one implementation has the capability.
            hybrid_manager_interface.getWithRelationships(
                entity_reference,
                relationship_traits_datas,
                result_trait_set,
                page_size,
                relations_access,
                a_context,
                a_host_session,
                expected_success_cb,
                expected_error_cb,
            )

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.getWithRelationships.assert_called_once_with(
                    entity_reference,
                    relationship_traits_datas,
                    result_trait_set,
                    page_size,
                    relations_access,
                    a_context,
                    a_host_session,
                    mock.ANY,
                    mock.ANY,
                )
                manager_interface_b.mock.getWithRelationships.assert_not_called()

                actual_success_cb = manager_interface_a.mock.getWithRelationships.call_args[0][7]
                actual_error_cb = manager_interface_a.mock.getWithRelationships.call_args[0][8]

            else:
                # The second implementation has the capability.
                manager_interface_a.mock.getWithRelationships.assert_not_called()
                manager_interface_b.mock.getWithRelationships.assert_called_once_with(
                    entity_reference,
                    relationship_traits_datas,
                    result_trait_set,
                    page_size,
                    relations_access,
                    a_context,
                    a_host_session,
                    mock.ANY,
                    mock.ANY,
                )

                actual_success_cb = manager_interface_b.mock.getWithRelationships.call_args[0][7]
                actual_error_cb = manager_interface_b.mock.getWithRelationships.call_args[0][8]

            # Ensure the callbacks have been passed through. These
            # will be converted to an intermediate representation by
            # pybind11, so we cannot do a naive comparison.

            expected_success_cb_args = (123, an_entity_reference_pager)
            expected_error_cb_args = (
                123,
                errors.BatchElementError(
                    errors.BatchElementError.ErrorCode.kEntityAccessError, "z"
                ),
            )
            actual_success_cb(*expected_success_cb_args)
            actual_error_cb(*expected_error_cb_args)
            expected_success_cb.assert_called_once_with(*expected_success_cb_args)
            expected_error_cb.assert_called_once_with(
                *expected_error_cb_args,
            )

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_preflight(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        hasCapability_a,
        hasCapability_b,
        a_context,
        a_host_session,
    ):
        expected_capability = ManagerInterface.Capability.kPublishing
        entity_references = [EntityReference("x")]
        traits_hints = [TraitsData({"h"})]
        publishing_access = access.PublishingAccess.kWrite
        expected_success_cb = mock.Mock()
        expected_error_cb = mock.Mock()

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.preflight(
                    entity_references,
                    traits_hints,
                    publishing_access,
                    a_context,
                    a_host_session,
                    expected_success_cb,
                    expected_error_cb,
                )
        else:
            # At least one implementation has the capability.
            hybrid_manager_interface.preflight(
                entity_references,
                traits_hints,
                publishing_access,
                a_context,
                a_host_session,
                expected_success_cb,
                expected_error_cb,
            )

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.preflight.assert_called_once_with(
                    entity_references,
                    traits_hints,
                    publishing_access,
                    a_context,
                    a_host_session,
                    mock.ANY,
                    mock.ANY,
                )
                manager_interface_b.mock.preflight.assert_not_called()

                actual_success_cb = manager_interface_a.mock.preflight.call_args[0][5]
                actual_error_cb = manager_interface_a.mock.preflight.call_args[0][6]

            else:
                # The second implementation has the capability.
                manager_interface_a.mock.preflight.assert_not_called()
                manager_interface_b.mock.preflight.assert_called_once_with(
                    entity_references,
                    traits_hints,
                    publishing_access,
                    a_context,
                    a_host_session,
                    mock.ANY,
                    mock.ANY,
                )

                actual_success_cb = manager_interface_b.mock.preflight.call_args[0][5]
                actual_error_cb = manager_interface_b.mock.preflight.call_args[0][6]

            # Ensure the callbacks have been passed through. These will
            # be converted to an intermediate representation by
            # pybind11, so we cannot do a naive comparison.

            expected_success_cb_args = (123, EntityReference("foo"))
            expected_error_cb_args = (
                123,
                errors.BatchElementError(
                    errors.BatchElementError.ErrorCode.kEntityAccessError, "z"
                ),
            )
            actual_success_cb(*expected_success_cb_args)
            actual_error_cb(*expected_error_cb_args)
            expected_success_cb.assert_called_once_with(*expected_success_cb_args)
            expected_error_cb.assert_called_once_with(
                *expected_error_cb_args,
            )

    @pytest.mark.parametrize(
        "hasCapability_a,hasCapability_b", itertools.product((True, False), repeat=2)
    )
    def test_register(
        self,
        manager_interface_a,
        manager_interface_b,
        hybrid_manager_interface,
        hasCapability_a,
        hasCapability_b,
        a_context,
        a_host_session,
    ):
        expected_capability = ManagerInterface.Capability.kPublishing
        entity_references = [EntityReference("x")]
        entity_traits_datas = [TraitsData({"h"})]
        publishing_access = access.PublishingAccess.kWrite
        expected_success_cb = mock.Mock()
        expected_error_cb = mock.Mock()

        manager_interface_a.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_a
        )
        manager_interface_b.mock.hasCapability.side_effect = (
            lambda cap: cap == expected_capability and hasCapability_b
        )

        hybrid_manager_interface.initialize({}, a_host_session)

        if not hasCapability_a and not hasCapability_b:
            # Neither implementation has the capability, so we should
            # get an exception.
            with pytest.raises(errors.NotImplementedException):
                hybrid_manager_interface.register(
                    entity_references,
                    entity_traits_datas,
                    publishing_access,
                    a_context,
                    a_host_session,
                    expected_success_cb,
                    expected_error_cb,
                )
        else:
            # At least one implementation has the capability.
            hybrid_manager_interface.register(
                entity_references,
                entity_traits_datas,
                publishing_access,
                a_context,
                a_host_session,
                expected_success_cb,
                expected_error_cb,
            )

            if hasCapability_a:
                # The first implementation has the capability.
                manager_interface_a.mock.register.assert_called_once_with(
                    entity_references,
                    entity_traits_datas,
                    publishing_access,
                    a_context,
                    a_host_session,
                    mock.ANY,
                    mock.ANY,
                )
                manager_interface_b.mock.register.assert_not_called()

                actual_success_cb = manager_interface_a.mock.register.call_args[0][5]
                actual_error_cb = manager_interface_a.mock.register.call_args[0][6]

            else:
                # The second implementation has the capability.
                manager_interface_a.mock.register.assert_not_called()
                manager_interface_b.mock.register.assert_called_once_with(
                    entity_references,
                    entity_traits_datas,
                    publishing_access,
                    a_context,
                    a_host_session,
                    mock.ANY,
                    mock.ANY,
                )

                actual_success_cb = manager_interface_b.mock.register.call_args[0][5]
                actual_error_cb = manager_interface_b.mock.register.call_args[0][6]

            # Ensure the callbacks have been passed through. These will
            # be converted to an intermediate representation by
            # pybind11, so we cannot do a naive comparison.

            expected_success_cb_args = (123, EntityReference("foo"))
            expected_error_cb_args = (
                123,
                errors.BatchElementError(
                    errors.BatchElementError.ErrorCode.kEntityAccessError, "z"
                ),
            )
            actual_success_cb(*expected_success_cb_args)
            actual_error_cb(*expected_error_cb_args)
            expected_success_cb.assert_called_once_with(*expected_success_cb_args)
            expected_error_cb.assert_called_once_with(
                *expected_error_cb_args,
            )


def test_all_manager_interface_methods_tested(subtests):
    methods_to_test = (
        name
        for (name, obj) in inspect.getmembers(ManagerInterface)
        if not name.startswith("_") and inspect.isroutine(obj)
    )

    test_methods = tuple(
        name
        for (name, obj) in inspect.getmembers(
            Test_HybridPluginSystemManagerImplementationFactory_ManagerInterface
        )
        if not name.startswith("_") and inspect.isroutine(obj)
    )

    for method_to_test in methods_to_test:
        with subtests.test(method_to_test=method_to_test):
            assert any(
                test_method == f"test_{method_to_test}"
                or test_method.startswith(f"test_{method_to_test}_")
                for test_method in test_methods
            )


@pytest.fixture
def a_context():
    return Context(TraitsData({"y"}))


@pytest.fixture
def an_entity_reference_pager():
    class Pager(EntityReferencePagerInterface):
        pass

    return Pager()


@pytest.fixture
def a_manager_state():
    class ManagerState(ManagerStateBase):
        pass

    return ManagerState()


@pytest.fixture
def hybrid_manager_interface(hybrid_factory, the_plugin_identifier):
    return hybrid_factory.instantiate(the_plugin_identifier)


@pytest.fixture
def hybrid_factory(factory_a, factory_b, mock_logger):
    return HybridPluginSystemManagerImplementationFactory([factory_a, factory_b], mock_logger)


@pytest.fixture
def factory_a(manager_interface_a, mock_logger, the_plugin_identifier):
    factory = MockManagerImplementationFactory(mock_logger)
    factory.mock.identifiers.return_value = [the_plugin_identifier]
    factory.mock.instantiate.return_value = manager_interface_a
    return factory


@pytest.fixture
def factory_b(manager_interface_b, mock_logger, the_plugin_identifier):
    factory = MockManagerImplementationFactory(mock_logger)
    factory.mock.identifiers.return_value = [the_plugin_identifier]
    factory.mock.instantiate.return_value = manager_interface_b
    return factory


@pytest.fixture
def manager_interface_a(create_mock_manager_interface):
    return create_mock_manager_interface()


@pytest.fixture
def manager_interface_b(create_mock_manager_interface):
    return create_mock_manager_interface()


@pytest.fixture
def the_plugin_identifier():
    return "org.openassetio.test.plugin"


class MockManagerImplementationFactory(ManagerImplementationFactoryInterface):
    """
    `ManagerImplementationFactoryInterface` that forwards calls to an
    internal mock.
    """

    def __init__(self, logger):
        ManagerImplementationFactoryInterface.__init__(self, logger)
        self.mock = mock.create_autospec(
            ManagerImplementationFactoryInterface, spec_set=True, instance=True
        )

    def identifiers(self):
        return self.mock.identifiers()

    def instantiate(self, identifier):
        return self.mock.instantiate(identifier)
