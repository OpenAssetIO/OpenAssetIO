#
#   Copyright 2013-2023 The Foundry Visionmongers Ltd
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
Tests for the default implementations of ManagerInterface methods.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

from openassetio import EntityReference, Context, errors, access
from openassetio.managerApi import (
    ManagerInterface,
    ManagerStateBase,
    EntityReferencePagerInterface,
)
from openassetio.trait import TraitsData


class Test_ManagerInterface_identifier:
    def test_is_pure_virtual(self, manager_interface, pure_virtual_error_msg):
        with pytest.raises(RuntimeError, match=pure_virtual_error_msg.format("identifier")):
            manager_interface.identifier()


class Test_ManagerInterface_displayName:
    def test_is_pure_virtual(self, manager_interface, pure_virtual_error_msg):
        with pytest.raises(RuntimeError, match=pure_virtual_error_msg.format("displayName")):
            manager_interface.displayName()


class Test_ManagerInterface_info:
    def test_when_not_overridden_then_returns_empty_dict(self):
        info = ManagerInterface().info()

        assert isinstance(info, dict)
        assert info == {}


class Test_ManagerInterface_Capability:
    def test_has_expected_values(self):
        assert len(ManagerInterface.Capability.__members__.values()) == 10
        assert ManagerInterface.Capability.kEntityReferenceIdentification.value == 0
        assert ManagerInterface.Capability.kManagementPolicyQueries.value == 1
        assert ManagerInterface.Capability.kStatefulContexts.value == 2
        assert ManagerInterface.Capability.kCustomTerminology.value == 3
        assert ManagerInterface.Capability.kResolution.value == 4
        assert ManagerInterface.Capability.kPublishing.value == 5
        assert ManagerInterface.Capability.kRelationshipQueries.value == 6
        assert ManagerInterface.Capability.kExistenceQueries.value == 7
        assert ManagerInterface.Capability.kDefaultEntityReferences.value == 8
        assert ManagerInterface.Capability.kEntityTraitIntrospection.value == 9


class Test_ManagerInterface_kCapabilityNames:
    def test_names_indices_match_constants(self):
        assert (
            ManagerInterface.kCapabilityNames[
                int(ManagerInterface.Capability.kEntityReferenceIdentification)
            ]
            == "entityReferenceIdentification"
        )
        assert (
            ManagerInterface.kCapabilityNames[
                int(ManagerInterface.Capability.kManagementPolicyQueries)
            ]
            == "managementPolicyQueries"
        )
        assert (
            ManagerInterface.kCapabilityNames[int(ManagerInterface.Capability.kStatefulContexts)]
            == "statefulContexts"
        )
        assert (
            ManagerInterface.kCapabilityNames[int(ManagerInterface.Capability.kCustomTerminology)]
            == "customTerminology"
        )
        assert (
            ManagerInterface.kCapabilityNames[int(ManagerInterface.Capability.kResolution)]
            == "resolution"
        )
        assert (
            ManagerInterface.kCapabilityNames[int(ManagerInterface.Capability.kPublishing)]
            == "publishing"
        )
        assert (
            ManagerInterface.kCapabilityNames[
                int(ManagerInterface.Capability.kRelationshipQueries)
            ]
            == "relationshipQueries"
        )
        assert (
            ManagerInterface.kCapabilityNames[int(ManagerInterface.Capability.kExistenceQueries)]
            == "existenceQueries"
        )
        assert (
            ManagerInterface.kCapabilityNames[
                int(ManagerInterface.Capability.kDefaultEntityReferences)
            ]
            == "defaultEntityReferences"
        )
        assert (
            ManagerInterface.kCapabilityNames[
                int(ManagerInterface.Capability.kEntityTraitIntrospection)
            ]
            == "entityTraitIntrospection"
        )


class Test_ManagerInterface_hasCapability:
    def test_is_pure_virtual(self, manager_interface, pure_virtual_error_msg):
        with pytest.raises(RuntimeError, match=pure_virtual_error_msg.format("hasCapability")):
            manager_interface.hasCapability(ManagerInterface.Capability.kManagementPolicyQueries)


class Test_ManagerInterface_settings:
    def test_when_not_overridden_then_returns_empty_dict(self, manager_interface, a_host_session):
        settings = manager_interface.settings(a_host_session)

        assert isinstance(settings, dict)
        assert settings == {}


class Test_ManagerInterface_managementPolicy:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_host_session, a_context, unimplemented_method_error_msg
    ):
        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format(
                "managementPolicy", "managementPolicyQueries"
            ),
        ):
            manager_interface.managementPolicy(
                [set()], access.PolicyAccess.kRead, a_context, a_host_session
            )


class Test_ManagerInterface_isEntityReferenceString:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_host_session, unimplemented_method_error_msg
    ):
        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format(
                "isEntityReferenceString", "entityReferenceIdentification"
            ),
        ):
            manager_interface.isEntityReferenceString("", a_host_session)


class Test_ManagerInterface_initialize:
    def test_when_settings_not_provided_then_default_implementation_ok(
        self, manager_interface, a_host_session
    ):
        # Lack of exception means all good.
        manager_interface.initialize({}, a_host_session)

    def test_when_settings_provided_then_default_implementation_raises(
        self, manager_interface, a_host_session
    ):
        expected_error_message = (
            "Settings provided but are not supported. "
            "The initialize method has not been implemented by the manager."
        )

        with pytest.raises(errors.InputValidationException, match=expected_error_message):
            manager_interface.initialize({"some": "setting"}, a_host_session)


class Test_ManagerInterface_updateTerminology:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_host_session, unimplemented_method_error_msg
    ):
        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format("updateTerminology", "customTerminology"),
        ):
            manager_interface.updateTerminology({}, a_host_session)


class Test_ManagerInterface_flushCaches:
    def test_default_implementation_exists(self, a_host_session):
        ManagerInterface().flushCaches(a_host_session)


class Test_ManagerInterface_createState:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_host_session, unimplemented_method_error_msg
    ):
        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format("createState", "statefulContexts"),
        ):
            manager_interface.createState(a_host_session)


class Test_ManagerInterface_createChildState:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_host_session, unimplemented_method_error_msg
    ):
        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format("createChildState", "statefulContexts"),
        ):
            manager_interface.createChildState(ManagerStateBase(), a_host_session)

    def test_when_none_is_supplied_then_TypeError_is_raised(self, a_host_session):
        with pytest.raises(TypeError):
            ManagerInterface().createChildState(None, a_host_session)


class Test_ManagerInterface_persistenceTokenForState:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_host_session, unimplemented_method_error_msg
    ):
        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format(
                "persistenceTokenForState", "statefulContexts"
            ),
        ):
            manager_interface.persistenceTokenForState(ManagerStateBase(), a_host_session)

    def test_when_none_is_supplied_then_TypeError_is_raised(self, a_host_session):
        with pytest.raises(TypeError):
            ManagerInterface().persistenceTokenForState(None, a_host_session)


class Test_ManagerInterface_stateFromPersistenceToken:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_host_session, unimplemented_method_error_msg
    ):
        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format(
                "stateFromPersistenceToken", "statefulContexts"
            ),
        ):
            manager_interface.stateFromPersistenceToken("", a_host_session)

    def test_when_none_is_supplied_then_TypeError_is_raised(self, a_host_session):
        with pytest.raises(TypeError):
            ManagerInterface().stateFromPersistenceToken(None, a_host_session)


class Test_ManagerInterface_defaultEntityReference:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_context, a_host_session, unimplemented_method_error_msg
    ):
        def fail(*_):
            pytest.fail("No callbacks should be called")

        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format(
                "defaultEntityReference", "defaultEntityReferences"
            ),
        ):
            manager_interface.defaultEntityReference(
                [], access.DefaultEntityAccess.kRead, a_context, a_host_session, fail, fail
            )


class Test_ManagerInterface_entityExists:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_context, a_host_session, unimplemented_method_error_msg
    ):
        def fail(*_):
            pytest.fail("No callbacks should be called")

        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format("entityExists", "existenceQueries"),
        ):
            manager_interface.entityExists([], a_context, a_host_session, fail, fail)


class Test_ManagerInterface_entityTraits:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_context, a_host_session, unimplemented_method_error_msg
    ):
        def fail(*_):
            pytest.fail("No callbacks should be called")

        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format(
                "entityTraits", "entityTraitIntrospection"
            ),
        ):
            manager_interface.entityTraits(
                [], access.EntityTraitsAccess.kRead, a_context, a_host_session, fail, fail
            )


class Test_ManagerInterface_resolve:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_context, a_host_session, unimplemented_method_error_msg
    ):
        def fail(*_):
            pytest.fail("No callbacks should be called")

        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format("resolve", "resolution"),
        ):
            manager_interface.resolve(
                [], set(), access.ResolveAccess.kRead, a_context, a_host_session, fail, fail
            )


class Test_ManagerInterface_getWithRelationship:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_context, a_host_session, unimplemented_method_error_msg
    ):
        def fail(*_):
            pytest.fail("No callbacks should be called")

        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format(
                "getWithRelationship", "relationshipQueries"
            ),
        ):
            manager_interface.getWithRelationship(
                [],
                TraitsData(),
                set(),
                1,
                access.RelationsAccess.kRead,
                a_context,
                a_host_session,
                fail,
                fail,
            )


class Test_ManagerInterface_getWithRelationships:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_context, a_host_session, unimplemented_method_error_msg
    ):
        def fail(*_):
            pytest.fail("No callbacks should be called")

        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format(
                "getWithRelationships", "relationshipQueries"
            ),
        ):
            manager_interface.getWithRelationships(
                EntityReference(""),
                [],
                set(),
                1,
                access.RelationsAccess.kRead,
                a_context,
                a_host_session,
                fail,
                fail,
            )


def assert_is_default_pager(a_host_session, pager):
    # The default pager behaviour is to return no data and
    # report no new pages.
    assert isinstance(pager, EntityReferencePagerInterface)
    assert pager.hasNext(a_host_session) is False
    assert pager.get(a_host_session) == []
    pager.next(a_host_session)
    assert pager.hasNext(a_host_session) is False
    assert pager.get(a_host_session) == []


class Test_ManagerInterface__createEntityReference:
    def test_when_input_is_string_then_wrapped_in_entity_reference(self, manager_interface):
        a_string = "some string"
        # pylint: disable=protected-access
        actual = manager_interface._createEntityReference(a_string)
        assert isinstance(actual, EntityReference)
        assert actual.toString() == a_string

    def test_when_input_is_none_then_typeerror_raised(self, manager_interface):
        with pytest.raises(TypeError):
            manager_interface._createEntityReference(None)  # pylint: disable=protected-access

    def test_when_input_is_not_a_string_then_typeerror_raised(self, manager_interface):
        with pytest.raises(TypeError):
            manager_interface._createEntityReference(1)  # pylint: disable=protected-access

    def test_is_entity_reference_string_is_not_called(self, mock_manager_interface):
        # pylint: disable=protected-access
        _ = mock_manager_interface._createEntityReference("some string")
        mock_manager_interface.mock.isEntityReferenceString.assert_not_called()


class Test_ManagerInterface_preflight:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_context, a_host_session, unimplemented_method_error_msg
    ):
        def fail(*_):
            pytest.fail("No callbacks should be called")

        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format("preflight", "publishing"),
        ):
            manager_interface.preflight(
                [], [], access.PublishingAccess.kWrite, a_context, a_host_session, fail, fail
            )


class Test_ManagerInterface_register:
    def test_default_implementation_raises_NotImplementedException(
        self, manager_interface, a_context, a_host_session, unimplemented_method_error_msg
    ):
        def fail(*_):
            pytest.fail("No callbacks should be called")

        with pytest.raises(
            errors.NotImplementedException,
            match=unimplemented_method_error_msg.format("register_", "publishing"),
        ):
            manager_interface.register(
                [], [], access.PublishingAccess.kWrite, a_context, a_host_session, fail, fail
            )


@pytest.fixture
def manager_interface():
    return ManagerInterface()


@pytest.fixture
def a_context():
    return Context()


@pytest.fixture
def pure_virtual_error_msg():
    return 'Tried to call pure virtual function "ManagerInterface::{}"'


@pytest.fixture
def unimplemented_method_error_msg():
    return (
        "The '{}' method has not been implemented by the manager. "
        "Check manager capability for {} by calling `manager.hasCapability`"
    )
