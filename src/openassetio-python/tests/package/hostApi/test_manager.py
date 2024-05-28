#
#   Copyright 2013-2024 The Foundry Visionmongers Ltd
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
Tests that cover the openassetio.hostApi.Manager wrapper class.
"""
import itertools
from typing import Callable, Any

# pylint: disable=invalid-name,redefined-outer-name,unused-argument
# pylint: disable=too-many-lines,too-many-locals
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=too-many-instance-attributes
from unittest import mock
import re

import pytest

from openassetio import (
    Context,
    EntityReference,
    managerApi,
    constants,
    access,
)
from openassetio.access import kAccessNames
from openassetio.errors import (
    BatchElementException,
    BatchElementError,
    InputValidationException,
    ConfigurationException,
)
from openassetio.hostApi import Manager, EntityReferencePager
from openassetio.managerApi import EntityReferencePagerInterface, ManagerInterface
from openassetio.trait import TraitsData


## @todo Remove comments regarding Entity methods when splitting them from core API

# __str__ and __repr__ aren't tested as they're debug tricks that need
# assessing when this is ported to cpp


class BatchFirstMethodTest:
    """
    Assertion helpers for testing batch-first methods and their
    "convenience" method signatures.

    Many Manager methods have multiple overloads that present signatures
    friendlier for specific workflows, i.e. exception vs. error object,
    singular vs. batch.

    Convenience signatures all follow a similar pattern across the
    Manager API, as does their expected behaviour under corner cases.
    This base class factors out the common assertion logic for all such
    methods.
    """

    subtests: Any
    method: Callable
    invoke_success_cb: Callable
    invoke_error_cb: Callable
    mock_interface_method: mock.Mock

    a_batch_element_error: BatchElementError
    a_context: Context
    a_host_session: managerApi.HostSession

    batch_element_error_codes = list(BatchElementError.ErrorCode.__members__.values())

    batch_element_error_codes_names = [
        "unknown",
        "invalidEntityReference",
        "malformedEntityReference",
        "entityAccessError",
        "entityResolutionError",
        "invalidPreflightHint",
        "invalidTraitSet",
    ]

    def assert_callback_overload_wraps_the_corresponding_method_of_the_held_interface(
        self, method_specific_args_for_batch_of_two, one_success_result
    ):
        success_callback = mock.Mock()
        error_callback = mock.Mock()

        def call_callbacks(*_args):
            self.invoke_success_cb(123, one_success_result)
            self.invoke_error_cb(456, self.a_batch_element_error)

        self.mock_interface_method.side_effect = call_callbacks

        self.method(
            *method_specific_args_for_batch_of_two,
            self.a_context,
            success_callback,
            error_callback,
        )

        self.mock_interface_method.assert_called_once_with(
            *method_specific_args_for_batch_of_two,
            self.a_context,
            self.a_host_session,
            mock.ANY,
            mock.ANY,
        )

        success_callback.assert_called_once_with(123, one_success_result)
        error_callback.assert_called_once_with(456, self.a_batch_element_error)

    def assert_callback_overload_errors_with_mixed_array_lengths(
        self,
        batched_method_specific_args_for_batch_of_two,
        nonbatched_remaining_method_specific_args,
        expected_message_pattern,
    ):
        for idx, arg in enumerate(batched_method_specific_args_for_batch_of_two):
            idx_plus_one = idx + 1
            mismatched_args = (
                *batched_method_specific_args_for_batch_of_two[:idx],
                arg[1:],
                *batched_method_specific_args_for_batch_of_two[idx_plus_one:],
            )

            arg_lengths = tuple(map(len, mismatched_args))

            with pytest.raises(
                InputValidationException,
                match=expected_message_pattern.format(*arg_lengths),
            ):
                self.method(
                    *mismatched_args,
                    *nonbatched_remaining_method_specific_args,
                    self.a_context,
                    mock.Mock(),
                    mock.Mock(),
                )

    def assert_callback_overload_errors_with_invalid_batch_element(
        self, method_specific_args_for_batch_of_two_with_invalid_element
    ):
        with pytest.raises(InputValidationException):
            self.method(
                *method_specific_args_for_batch_of_two_with_invalid_element,
                self.a_context,
                mock.Mock(),
                mock.Mock(),
            )

    def assert_singular_overload_success(
        self,
        method_specific_args,
        batched_method_specific_args,
        expected_result,
        assert_result_identity=True,
    ):
        def call_callbacks(*_args):
            self.invoke_success_cb(0, expected_result)

        self.mock_interface_method.side_effect = call_callbacks

        for tag in (
            [],
            [Manager.BatchElementErrorPolicyTag.kException],
            [Manager.BatchElementErrorPolicyTag.kVariant],
        ):
            with self.subtests.test(tag=tag):

                actual_result = self.method(*method_specific_args, self.a_context, *tag)

                self.mock_interface_method.assert_called_once_with(
                    *batched_method_specific_args,
                    self.a_context,
                    self.a_host_session,
                    mock.ANY,
                    mock.ANY,
                )
                self.mock_interface_method.reset_mock()

                assert actual_result == expected_result
                if assert_result_identity:
                    assert actual_result is expected_result

    def assert_batch_overload_success(
        self,
        method_specific_args_for_batch_of_two,
        expected_results,
        assert_result_identity=True,
    ):
        def call_callbacks(*_args):
            self.invoke_success_cb(0, expected_results[0])
            self.invoke_success_cb(1, expected_results[1])

        self.mock_interface_method.side_effect = call_callbacks

        for tag in (
            [],
            [Manager.BatchElementErrorPolicyTag.kException],
            [Manager.BatchElementErrorPolicyTag.kVariant],
        ):
            with self.subtests.test(tag=tag):
                actual_results = self.method(
                    *method_specific_args_for_batch_of_two, self.a_context, *tag
                )

                self.mock_interface_method.assert_called_once_with(
                    *method_specific_args_for_batch_of_two,
                    self.a_context,
                    self.a_host_session,
                    mock.ANY,
                    mock.ANY,
                )
                self.mock_interface_method.reset_mock()

                assert actual_results == expected_results

                if assert_result_identity:
                    for actual, expected in zip(actual_results, expected_results):
                        assert actual is expected

    def assert_batch_overload_success_out_of_order(
        self,
        method_specific_args_for_batch_of_two,
        expected_results,
        assert_result_identity=True,
    ):
        def call_callbacks(*_args):
            self.invoke_success_cb(1, expected_results[1])
            self.invoke_success_cb(0, expected_results[0])

        self.mock_interface_method.side_effect = call_callbacks

        for tag in (
            [],
            [Manager.BatchElementErrorPolicyTag.kException],
            [Manager.BatchElementErrorPolicyTag.kVariant],
        ):
            with self.subtests.test(tag=tag):

                actual_results = self.method(
                    *method_specific_args_for_batch_of_two, self.a_context, *tag
                )

                self.mock_interface_method.assert_called_once_with(
                    *method_specific_args_for_batch_of_two,
                    self.a_context,
                    self.a_host_session,
                    mock.ANY,
                    mock.ANY,
                )
                self.mock_interface_method.reset_mock()

                assert actual_results == expected_results

                if assert_result_identity:
                    for actual, expected in zip(actual_results, expected_results):
                        assert actual is expected

    def assert_singular_variant_overload_error(
        self,
        method_specific_args,
        batched_method_specific_args,
    ):
        expected_result = BatchElementError(
            BatchElementError.ErrorCode.kInvalidEntityReference, "some string ✨"
        )

        def call_callbacks(*_args):
            self.invoke_error_cb(123, expected_result)

        self.mock_interface_method.side_effect = call_callbacks

        actual_result = self.method(
            *method_specific_args,
            self.a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        self.mock_interface_method.assert_called_once_with(
            *batched_method_specific_args,
            self.a_context,
            self.a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert actual_result == expected_result

    def assert_batch_variant_overload_mixed_output(
        self,
        method_specific_args_for_batch_of_two,
        one_success_result,
    ):
        expected_error_result = BatchElementError(
            BatchElementError.ErrorCode.kInvalidEntityReference, "some string ✨"
        )

        def call_callbacks(*_args):
            self.invoke_success_cb(0, one_success_result)
            self.invoke_error_cb(1, expected_error_result)

        self.mock_interface_method.side_effect = call_callbacks

        actual_success_result_and_error = self.method(
            *method_specific_args_for_batch_of_two,
            self.a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        self.mock_interface_method.assert_called_once_with(
            *method_specific_args_for_batch_of_two,
            self.a_context,
            self.a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert len(actual_success_result_and_error) == 2
        assert actual_success_result_and_error[0] == one_success_result
        assert actual_success_result_and_error[1] == expected_error_result

    def assert_batch_variant_overload_mixed_output_out_of_order(
        self, method_specific_args_for_batch_of_four, two_success_results
    ):
        expected_results = [
            BatchElementError(
                BatchElementError.ErrorCode.kEntityResolutionError, "0 some string ✨"
            ),
            two_success_results[0],
            BatchElementError(
                BatchElementError.ErrorCode.kEntityResolutionError, "2 some string ✨"
            ),
            two_success_results[1],
        ]

        def call_callbacks(*_args):
            self.invoke_success_cb(1, expected_results[1])
            self.invoke_error_cb(0, expected_results[0])
            self.invoke_success_cb(3, expected_results[3])
            self.invoke_error_cb(2, expected_results[2])

        self.mock_interface_method.side_effect = call_callbacks

        actual_results = self.method(
            *method_specific_args_for_batch_of_four,
            self.a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        self.mock_interface_method.assert_called_once_with(
            *method_specific_args_for_batch_of_four,
            self.a_context,
            self.a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert actual_results == expected_results

    def assert_singular_throwing_overload_raises(
        self,
        method_specific_args,
        batched_method_specific_args,
        batch_element_error,
        expected_error_message,
    ):
        expected_index = 0

        def call_callbacks(*_args):
            self.invoke_error_cb(expected_index, batch_element_error)
            pytest.fail("Singular method shouldn't invoke multiple callbacks")

        self.mock_interface_method.side_effect = call_callbacks

        for tag in ([], [Manager.BatchElementErrorPolicyTag.kException]):
            with self.subtests.test(tag=tag):
                with pytest.raises(
                    BatchElementException,
                    match=re.escape(expected_error_message),
                ) as exc:
                    self.method(
                        *method_specific_args,
                        self.a_context,
                        *tag,
                    )

                # Remember this is the managerInterface, always takes a list
                # regardless of convenience called.
                self.mock_interface_method.assert_called_once_with(
                    *batched_method_specific_args,
                    self.a_context,
                    self.a_host_session,
                    mock.ANY,
                    mock.ANY,
                )
                self.mock_interface_method.reset_mock()

                assert exc.value.index == expected_index
                assert exc.value.error == batch_element_error

    def assert_batched_throwing_overload_raises(
        self,
        method_specific_args_for_batch_of_two,
        batch_element_error,
        expected_error_message,
    ):
        expected_index = 0

        def call_callbacks(*_args):
            self.invoke_error_cb(expected_index, batch_element_error)
            pytest.fail("Exception should have short-circuited this")

        self.mock_interface_method.side_effect = call_callbacks

        for tag in ([], [Manager.BatchElementErrorPolicyTag.kException]):
            with self.subtests.test(tag=tag):
                with pytest.raises(
                    BatchElementException,
                    match=re.escape(expected_error_message),
                ) as exc:
                    self.method(
                        *method_specific_args_for_batch_of_two,
                        self.a_context,
                        *tag,
                    )

                self.mock_interface_method.assert_called_once_with(
                    *method_specific_args_for_batch_of_two,
                    self.a_context,
                    self.a_host_session,
                    mock.ANY,
                    mock.ANY,
                )
                self.mock_interface_method.reset_mock()

                assert exc.value.index == expected_index
                assert exc.value.error == batch_element_error

    def _make_expected_err_msg(self, batch_element_error, access, entityRef):
        error_type_name = self.batch_element_error_codes_names[
            self.batch_element_error_codes.index(batch_element_error.code)
        ]
        return (
            f"{error_type_name}: {batch_element_error.message} [index=0]"
            f" [access={kAccessNames[access]}] [entity={entityRef}]"
        )


class Test_Manager_init:
    def test_when_constructed_with_ManagerInterface_as_None_then_raises_TypeError(
        self, a_host_session
    ):
        # Check the message is both helpful and that the bindings
        # were loaded in the correct order such that types are
        # described correctly.
        matchExpr = (
            r".+The following argument types are supported:[^(]+"
            r"Manager\([^,]+managerApi.ManagerInterface,[^,]+managerApi.HostSession.+"
        )

        with pytest.raises(TypeError, match=matchExpr):
            Manager(None, a_host_session)


class Test_Manager_identifier:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.identifier)
        assert method_introspector.is_implemented_once(Manager, "identifier")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface
    ):
        expected = "stub.manager"
        mock_manager_interface.mock.identifier.return_value = expected

        actual = manager.identifier()

        assert actual == expected

    def test_when_interface_provides_wrong_type_then_raises_RuntimeError(
        self, manager, mock_manager_interface
    ):
        mock_manager_interface.mock.identifier.return_value = 123

        with pytest.raises(RuntimeError) as err:
            manager.identifier()

        # Pybind error messages vary between release and debug mode:
        # "Unable to cast Python instance of type <class 'int'> to C++
        # type 'std::string'"
        # vs.
        # "Unable to cast Python instance to C++ type (compile in debug
        # mode for details)"
        assert str(err.value).startswith("Unable to cast Python instance")


class Test_Manager_displayName:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.displayName)
        assert method_introspector.is_implemented_once(Manager, "displayName")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface
    ):
        expected = "stub.manager"
        mock_manager_interface.mock.displayName.return_value = expected

        actual = manager.displayName()

        assert actual == expected

    def test_when_interface_provides_wrong_type_then_raises_RuntimeError(
        self, manager, mock_manager_interface
    ):
        mock_manager_interface.mock.displayName.return_value = 123

        with pytest.raises(RuntimeError) as err:
            manager.displayName()

        # Note: pybind error messages vary between release and debug mode.
        assert str(err.value).startswith("Unable to cast Python instance")


class Test_Manager_info:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.info)
        assert method_introspector.is_implemented_once(Manager, "info")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface
    ):
        expected = {"an int": 123}
        mock_manager_interface.mock.info.return_value = expected

        actual = manager.info()

        assert actual == expected

    def test_when_interface_provides_wrong_type_then_raises_RuntimeError(
        self, manager, mock_manager_interface
    ):
        mock_manager_interface.mock.info.return_value = {123: 123}

        with pytest.raises(RuntimeError) as err:
            manager.info()

        # Note: pybind error messages vary between release and debug mode.
        assert str(err.value).startswith("Unable to cast Python instance")


class Test_Manager_updateTerminology:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.updateTerminology)
        assert method_introspector.is_implemented_once(Manager, "updateTerminology")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface, a_host_session
    ):
        a_dict = {"k": "v"}
        method = mock_manager_interface.mock.updateTerminology
        method.return_value = a_dict

        ret = manager.updateTerminology(a_dict)
        assert ret == a_dict
        assert ret is not a_dict
        method.assert_called_once_with(a_dict, a_host_session)

    def test_input_not_modified(self, manager, mock_manager_interface, a_host_session):
        input_dict = {"k": "v"}
        method = mock_manager_interface.mock.updateTerminology
        method.return_value = {"k": "v", "l": "b"}

        _ret = manager.updateTerminology(input_dict)
        assert input_dict == {"k": "v"}


class Test_Manager_settings:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.settings)
        assert method_introspector.is_implemented_once(Manager, "settings")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface, a_host_session
    ):
        expected = {"some": "setting"}
        method = mock_manager_interface.mock.settings
        method.return_value = expected

        actual = manager.settings()

        method.assert_called_once_with(a_host_session)
        assert actual == expected


class Test_Manager_initialize:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.initialize)
        assert method_introspector.is_implemented_once(Manager, "initialize")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface, a_host_session
    ):
        a_dict = {"k": "v"}

        manager.initialize(a_dict)

        mock_manager_interface.mock.initialize.assert_called_once_with(a_dict, a_host_session)

    def test_when_entity_ref_prefix_given_then_debug_log_printed(
        self, manager, mock_manager_interface, mock_logger
    ):
        mock_manager_interface.mock.info.return_value = {
            constants.kInfoKey_EntityReferencesMatchPrefix: "someprefix:"
        }

        manager.initialize({})

        mock_logger.mock.log.assert_called_once_with(
            mock_logger.Severity.kDebugApi,
            "Entity reference prefix 'someprefix:' provided by manager's info() dict."
            " Subsequent calls to isEntityReferenceString will use this prefix rather"
            " than call the manager's implementation.",
        )

    def test_when_entity_ref_prefix_type_invalid_then_debug_log_printed(
        self, manager, mock_manager_interface, mock_logger
    ):
        mock_manager_interface.mock.info.return_value = {
            constants.kInfoKey_EntityReferencesMatchPrefix: 123
        }

        manager.initialize({})

        mock_logger.mock.log.assert_called_once_with(
            mock_logger.Severity.kWarning,
            "Entity reference prefix given but is an invalid type: should be a string.",
        )


required_capabilities = [
    ManagerInterface.Capability.kEntityReferenceIdentification,
    ManagerInterface.Capability.kManagementPolicyQueries,
    ManagerInterface.Capability.kEntityTraitIntrospection,
]

# The powerset (set of all subsets) of capabilities, minus the empty
# set. Adapted from https://docs.python.org/3/library/itertools.html#itertools-recipes
required_capabilities_powerset = list(
    itertools.chain.from_iterable(
        itertools.combinations(required_capabilities, r)
        for r in range(1, len(required_capabilities) + 1)
    )
)


class Test_Manager_initialize_capablility_check:
    def test_has_capability_called_after_initialize(
        self, manager, a_host_session, mock_manager_interface
    ):
        mock_manager_interface.mock.hasCapability.return_value = True

        manager.initialize({})

        assert mock_manager_interface.mock.method_calls[0:4] == [
            mock.call.initialize({}, a_host_session),
            mock.call.hasCapability(ManagerInterface.Capability.kEntityReferenceIdentification),
            mock.call.hasCapability(ManagerInterface.Capability.kManagementPolicyQueries),
            mock.call.hasCapability(ManagerInterface.Capability.kEntityTraitIntrospection),
        ]

    def test_when_manager_has_capabilities_then_no_error(self, manager, mock_manager_interface):
        mock_manager_interface.mock.hasCapability.return_value = True
        manager.initialize({})

    @pytest.mark.parametrize("missing_capabilities", required_capabilities_powerset)
    def test_when_manager_does_not_have_capability_then_ConfigurationException_raised(
        self, manager, mock_manager_interface, missing_capabilities
    ):
        def mock_has_capability(capability):
            return capability not in missing_capabilities

        mock_manager_interface.mock.hasCapability.side_effect = mock_has_capability
        mock_manager_interface.mock.identifier.return_value = "expected.identifier"

        capability_names = ", ".join(
            [ManagerInterface.kCapabilityNames[c] for c in missing_capabilities]
        )
        expected_msg = (
            f"Manager implementation for '{manager.identifier()}' does not "
            + f"support the required capabilities: {capability_names}"
        )

        with pytest.raises(ConfigurationException, match=expected_msg):
            manager.initialize({})


manager_capabilities = [
    (Manager.Capability.kStatefulContexts, ManagerInterface.Capability.kStatefulContexts),
    (Manager.Capability.kCustomTerminology, ManagerInterface.Capability.kCustomTerminology),
    (Manager.Capability.kResolution, ManagerInterface.Capability.kResolution),
    (Manager.Capability.kPublishing, ManagerInterface.Capability.kPublishing),
    (Manager.Capability.kRelationshipQueries, ManagerInterface.Capability.kRelationshipQueries),
    (Manager.Capability.kExistenceQueries, ManagerInterface.Capability.kExistenceQueries),
    (
        Manager.Capability.kDefaultEntityReferences,
        ManagerInterface.Capability.kDefaultEntityReferences,
    ),
]


class Test_Manager_Capability:
    def test_has_expected_number_of_values(self):
        assert len(Manager.Capability.__members__.values()) == 7

    @pytest.mark.parametrize(
        "manager_capability,managerinterface_capability", manager_capabilities
    )
    def test_values_match_managerinterface(self, manager_capability, managerinterface_capability):
        assert manager_capability.value == managerinterface_capability.value


class Test_Manager_hasCapability:
    @pytest.mark.parametrize(
        "manager_capability,managerinterface_capability", manager_capabilities
    )
    @pytest.mark.parametrize("return_value", (True, False))
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        manager,
        mock_manager_interface,
        manager_capability,
        managerinterface_capability,
        return_value,
    ):
        method = mock_manager_interface.mock.hasCapability

        mock_manager_interface.mock.hasCapability.return_value = return_value
        actual_return_value = manager.hasCapability(manager_capability)

        method.assert_called_once_with(managerinterface_capability)
        assert actual_return_value == return_value


class Test_Manager_flushCaches:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.flushCaches)
        assert method_introspector.is_implemented_once(Manager, "flushCaches")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface, a_host_session
    ):
        method = mock_manager_interface.mock.flushCaches
        manager.flushCaches()
        method.assert_called_once_with(a_host_session)


class Test_Manager_isEntityReferenceString:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.isEntityReferenceString)
        assert method_introspector.is_implemented_once(Manager, "isEntityReferenceString")

    @pytest.mark.parametrize("expected", (True, False))
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface, a_host_session, a_ref_string, expected
    ):
        method = mock_manager_interface.mock.isEntityReferenceString
        method.return_value = expected

        assert manager.isEntityReferenceString(a_ref_string) == expected
        method.assert_called_once_with(a_ref_string, a_host_session)

    @pytest.mark.parametrize(
        "prefix,entity_ref,expected",
        (
            ("asset://", "asset://my_asset", True),
            ("asset://", "/home/user/my_asset", False),
            ("a", "asset://my_asset", True),
            ("asset://my_asset", "asset://my_asset", True),
            ("asset://my_asset/long_prefix/", "asset://my_asset", False),
            ("my📹manager⚡", "my📹manager⚡my_asset⚡", True),
            ("my📹manager⚡", "my📹manager☁️my_asset⚡", False),
        ),
    )
    def test_when_prefix_given_in_info_then_prefix_used_and_interface_not_called(
        self, manager, mock_manager_interface, prefix, entity_ref, expected
    ):
        mock_manager_interface.mock.info.return_value = {
            constants.kInfoKey_EntityReferencesMatchPrefix: prefix
        }
        manager.initialize({})

        actual = manager.isEntityReferenceString(entity_ref)

        assert not mock_manager_interface.mock.isEntityReferenceString.called
        assert actual is expected


class Test_Manager_createEntityReference:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.createEntityReference)
        assert method_introspector.is_implemented_once(Manager, "createEntityReference")

    def test_when_invalid_then_raises_InputValidationException(
        self, manager, mock_manager_interface, a_ref_string, a_host_session
    ):
        mock_manager_interface.mock.isEntityReferenceString.return_value = False

        with pytest.raises(InputValidationException) as err:
            manager.createEntityReference(a_ref_string)

        mock_manager_interface.mock.isEntityReferenceString.assert_called_once_with(
            a_ref_string, a_host_session
        )
        assert str(err.value) == f"Invalid entity reference: {a_ref_string}"

    def test_when_valid_then_returns_configured_EntityReference(
        self, manager, mock_manager_interface, a_ref_string, a_host_session
    ):
        mock_manager_interface.mock.isEntityReferenceString.return_value = True

        entity_reference = manager.createEntityReference(a_ref_string)

        mock_manager_interface.mock.isEntityReferenceString.assert_called_once_with(
            a_ref_string, a_host_session
        )
        assert isinstance(entity_reference, EntityReference)
        assert entity_reference.toString() == a_ref_string


class Test_Manager_createEntityReferenceIfValid:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.createEntityReferenceIfValid)
        assert method_introspector.is_implemented_once(Manager, "createEntityReferenceIfValid")

    def test_when_invalid_then_returns_None(
        self, manager, mock_manager_interface, a_ref_string, a_host_session
    ):
        mock_manager_interface.mock.isEntityReferenceString.return_value = False

        entity_reference = manager.createEntityReferenceIfValid(a_ref_string)

        mock_manager_interface.mock.isEntityReferenceString.assert_called_once_with(
            a_ref_string, a_host_session
        )
        assert entity_reference is None

    def test_when_valid_then_returns_configured_EntityReference(
        self, manager, mock_manager_interface, a_ref_string, a_host_session
    ):
        mock_manager_interface.mock.isEntityReferenceString.return_value = True

        entity_reference = manager.createEntityReferenceIfValid(a_ref_string)

        mock_manager_interface.mock.isEntityReferenceString.assert_called_once_with(
            a_ref_string, a_host_session
        )
        assert isinstance(entity_reference, EntityReference)
        assert entity_reference.toString() == a_ref_string


class Test_Manager_entityExists:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.entityExists)
        assert method_introspector.is_implemented_once(Manager, "entityExists")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        a_context,
        a_batch_element_error,
        invoke_entityExists_success_cb,
        invoke_entityExists_error_cb,
    ):
        success_callback = mock.Mock()
        error_callback = mock.Mock()

        method = mock_manager_interface.mock.entityExists

        def call_callbacks(*_args):
            invoke_entityExists_success_cb(123, False)
            invoke_entityExists_error_cb(456, a_batch_element_error)

        method.side_effect = call_callbacks

        manager.entityExists(some_refs, a_context, success_callback, error_callback)

        method.assert_called_once_with(some_refs, a_context, a_host_session, mock.ANY, mock.ANY)

        success_callback.assert_called_once_with(123, False)
        error_callback.assert_called_once_with(456, a_batch_element_error)


class Test_Manager_defaultEntityReference:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.defaultEntityReference)
        assert method_introspector.is_implemented_once(Manager, "defaultEntityReference")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_context,
        some_entity_trait_sets,
        a_ref,
        a_batch_element_error,
        invoke_defaultEntityReference_success_cb,
        invoke_defaultEntityReference_error_cb,
    ):
        success_callback = mock.Mock()
        error_callback = mock.Mock()

        method = mock_manager_interface.mock.defaultEntityReference

        def call_callbacks(*_args):
            invoke_defaultEntityReference_success_cb(1, None)
            invoke_defaultEntityReference_success_cb(0, a_ref)
            invoke_defaultEntityReference_error_cb(2, a_batch_element_error)

        method.side_effect = call_callbacks

        manager.defaultEntityReference(
            some_entity_trait_sets,
            access.DefaultEntityAccess.kCreateRelated,
            a_context,
            success_callback,
            error_callback,
        )
        method.assert_called_once_with(
            some_entity_trait_sets,
            access.DefaultEntityAccess.kCreateRelated,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        success_callback.assert_has_calls([mock.call(1, None), mock.call(0, a_ref)])
        error_callback.assert_called_once_with(2, a_batch_element_error)


class FakeEntityReferencePagerInterface(EntityReferencePagerInterface):
    """
    Throwaway pager interface def, so we can create a temporary
    interface intended to fall out of scope.

    See `test_pager_kept_alive_by_retaining_shared_ptr`.
    """

    def __init__(self):
        EntityReferencePagerInterface.__init__(self)

    def hasNext(self, hostSession):
        return False

    def get(self, hostSession):
        return []

    def next(self, hostSession):
        pass


# The getWithRelationship tests are more repetitive than most tests
# in this suite. They are unable to make use of the test
# automation that we have written for the conveniences signatures, as
# the arguments for getWithRelationship are not in the standard format.


class Test_Manager_getWithRelationship_with_callback_signiature:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        manager,
        a_ref,
        mock_manager_interface,
        mock_entity_reference_pager_interface,
        a_host_session,
        a_batch_element_error,
        an_empty_traitsdata,
        an_entity_trait_set,
        an_entity_reference_pager,
        a_context,
        invoke_getWithRelationship_success_cb,
        invoke_getWithRelationship_error_cb,
    ):
        # pylint: disable=too-many-locals

        two_refs = [a_ref, a_ref]
        page_size = 3

        success_callback = mock.Mock()
        error_callback = mock.Mock()

        method = mock_manager_interface.mock.getWithRelationship

        def call_callbacks(*_args):
            invoke_getWithRelationship_success_cb(0, mock_entity_reference_pager_interface)
            invoke_getWithRelationship_error_cb(1, a_batch_element_error)

        method.side_effect = call_callbacks

        manager.getWithRelationship(
            two_refs,
            an_empty_traitsdata,
            page_size,
            access.RelationsAccess.kWrite,
            a_context,
            success_callback,
            error_callback,
            resultTraitSet=an_entity_trait_set,
        )

        method.assert_called_once_with(
            two_refs,
            an_empty_traitsdata,
            an_entity_trait_set,
            page_size,
            access.RelationsAccess.kWrite,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )
        success_callback.assert_called_once_with(0, mock.ANY)

        # Additional assert to check cpp constructed Pager object is as
        # expected.
        pager = success_callback.call_args[0][1]
        assert isinstance(pager, EntityReferencePager)
        pager.next()
        mock_entity_reference_pager_interface.mock.next.assert_called_once_with(a_host_session)

        error_callback.assert_called_once_with(1, a_batch_element_error)

        mock_manager_interface.mock.reset_mock()

        # Check optional resultTraitSet

        manager.getWithRelationship(
            two_refs,
            an_empty_traitsdata,
            page_size,
            access.RelationsAccess.kWrite,
            a_context,
            success_callback,
            error_callback,
            resultTraitSet=an_entity_trait_set,
        )

        method.assert_called_once_with(
            two_refs,
            an_empty_traitsdata,
            an_entity_trait_set,
            page_size,
            access.RelationsAccess.kWrite,
            a_context,
            a_host_session,
            mock.ANY,  # success
            mock.ANY,  # error
        )

    def test_pager_kept_alive_by_retaining_shared_ptr(
        self,
        manager,
        a_ref,
        mock_manager_interface,
        a_host_session,
        a_batch_element_error,
        an_empty_traitsdata,
        an_entity_trait_set,
        a_context,
        invoke_getWithRelationship_success_cb,
        invoke_getWithRelationship_error_cb,
    ):
        # pylint: disable=too-many-locals

        two_refs = [a_ref, a_ref]
        page_size = 3

        error_callback = mock.Mock()

        method = mock_manager_interface.mock.getWithRelationship

        def call_callbacks(*_args):
            invoke_getWithRelationship_success_cb(0, FakeEntityReferencePagerInterface())
            invoke_getWithRelationship_error_cb(1, a_batch_element_error)

        method.side_effect = call_callbacks

        pagers = []
        manager.getWithRelationship(
            two_refs,
            an_empty_traitsdata,
            page_size,
            access.RelationsAccess.kWrite,
            a_context,
            lambda _idx, pager: pagers.append(pager),
            error_callback,
            resultTraitSet=an_entity_trait_set,
        )

        # Without PyRetainingSharedPtr, will raise
        # > Tried to call pure virtual function
        # > "EntityReferencePagerInterface::get"
        pagers[0].get()

    def test_when_zero_pageSize_then_InputValidationException_is_raised(
        self, manager, a_ref, an_empty_traitsdata, an_entity_trait_set, a_context
    ):
        two_refs = [a_ref, a_ref]
        page_size = 0

        success_callback = mock.Mock()
        error_callback = mock.Mock()

        with pytest.raises(InputValidationException):
            manager.getWithRelationship(
                two_refs,
                an_empty_traitsdata,
                page_size,
                access.RelationsAccess.kWrite,
                a_context,
                success_callback,
                error_callback,
                resultTraitSet=an_entity_trait_set,
            )


class Test_Manager_getWithRelationship_singular_convenience:
    @pytest.mark.parametrize(
        "error_mode",
        [
            None,
            Manager.BatchElementErrorPolicyTag.kException,
            Manager.BatchElementErrorPolicyTag.kVariant,
        ],
    )
    def test_when_success_then_entityReferencePager_returned(
        self,
        manager,
        a_ref,
        mock_manager_interface,
        a_host_session,
        an_empty_traitsdata,
        an_entity_trait_set,
        a_context,
        mock_entity_reference_pager_interface,
        invoke_getWithRelationship_success_cb,
        error_mode,
    ):
        page_size = 3
        method = mock_manager_interface.mock.getWithRelationship

        def call_callbacks(*_args):
            invoke_getWithRelationship_success_cb(0, mock_entity_reference_pager_interface)

        method.side_effect = call_callbacks

        args = {
            "entityReference": a_ref,
            "relationshipTraitsData": an_empty_traitsdata,
            "pageSize": page_size,
            "relationsAccess": access.RelationsAccess.kRead,
            "context": a_context,
            "resultTraitSet": an_entity_trait_set,
        }

        if error_mode is not None:
            args["errorPolicyTag"] = error_mode

        actual_pager = manager.getWithRelationship(**args)

        method.assert_called_once_with(
            [a_ref],
            an_empty_traitsdata,
            an_entity_trait_set,
            page_size,
            access.RelationsAccess.kRead,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert isinstance(actual_pager, EntityReferencePager)

    @pytest.mark.parametrize(
        "error_mode",
        [
            None,
            Manager.BatchElementErrorPolicyTag.kException,
            Manager.BatchElementErrorPolicyTag.kVariant,
        ],
    )
    def test_when_fail_then_error_emitted(
        self,
        manager,
        a_ref,
        mock_manager_interface,
        a_host_session,
        an_empty_traitsdata,
        an_entity_trait_set,
        a_context,
        a_batch_element_error,
        invoke_getWithRelationship_error_cb,
        error_mode,
    ):
        page_size = 3
        method = mock_manager_interface.mock.getWithRelationship

        def call_callbacks(*_args):
            invoke_getWithRelationship_error_cb(0, a_batch_element_error)

        method.side_effect = call_callbacks

        args = {
            "entityReference": a_ref,
            "relationshipTraitsData": an_empty_traitsdata,
            "pageSize": page_size,
            "relationsAccess": access.RelationsAccess.kRead,
            "context": a_context,
            "resultTraitSet": an_entity_trait_set,
        }

        if error_mode is not None:
            args["errorPolicyTag"] = error_mode

        if error_mode is None or error_mode is Manager.BatchElementErrorPolicyTag.kException:
            with pytest.raises(BatchElementException) as exc_info:
                manager.getWithRelationship(**args)

            assert exc_info.value.error == a_batch_element_error
            assert (
                exc_info.value.message
                == "unknown: some message [index=0] [access=read] [entity=asset://a]"
            )
        else:
            variant_error = manager.getWithRelationship(**args)
            assert variant_error == a_batch_element_error


class Test_Manager_getWithRelationship_batch_convenience:

    @pytest.mark.parametrize(
        "error_mode",
        [
            None,
            Manager.BatchElementErrorPolicyTag.kException,
            Manager.BatchElementErrorPolicyTag.kVariant,
        ],
    )
    def test_when_success_then_entityReferencePagers_returned(
        self,
        manager,
        a_ref,
        mock_manager_interface,
        a_host_session,
        an_empty_traitsdata,
        an_entity_trait_set,
        a_context,
        mock_entity_reference_pager_interface,
        mock_entity_reference_pager_interface_2,
        invoke_getWithRelationship_success_cb,
        error_mode,
    ):

        two_refs = [a_ref, a_ref]
        page_size = 3
        method = mock_manager_interface.mock.getWithRelationship

        def call_callbacks(*_args):
            mock_entity_reference_pager_interface.mock.hasNext.return_value = True
            invoke_getWithRelationship_success_cb(0, mock_entity_reference_pager_interface)
            mock_entity_reference_pager_interface_2.mock.hasNext.return_value = False
            invoke_getWithRelationship_success_cb(1, mock_entity_reference_pager_interface_2)

        method.side_effect = call_callbacks

        args = {
            "entityReferences": two_refs,
            "relationshipTraitsData": an_empty_traitsdata,
            "pageSize": page_size,
            "relationsAccess": access.RelationsAccess.kRead,
            "context": a_context,
            "resultTraitSet": an_entity_trait_set,
        }

        if error_mode is not None:
            args["errorPolicyTag"] = error_mode

        actual_pagers = manager.getWithRelationship(**args)

        method.assert_called_once_with(
            two_refs,
            an_empty_traitsdata,
            an_entity_trait_set,
            page_size,
            access.RelationsAccess.kRead,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert len(actual_pagers) == 2
        assert actual_pagers[0].hasNext() is True
        assert actual_pagers[1].hasNext() is False

    @pytest.mark.parametrize(
        "error_mode",
        [
            None,
            Manager.BatchElementErrorPolicyTag.kException,
            Manager.BatchElementErrorPolicyTag.kVariant,
        ],
    )
    def test_when_fail_then_error_emitted(
        self,
        manager,
        a_ref,
        mock_manager_interface,
        a_host_session,
        an_empty_traitsdata,
        an_entity_trait_set,
        a_context,
        a_batch_element_error,
        a_batch_element_error_2,
        invoke_getWithRelationship_error_cb,
        error_mode,
    ):

        two_refs = [a_ref, a_ref]
        page_size = 3
        method = mock_manager_interface.mock.getWithRelationship

        def call_callbacks(*_args):
            invoke_getWithRelationship_error_cb(0, a_batch_element_error)
            invoke_getWithRelationship_error_cb(1, a_batch_element_error_2)

        method.side_effect = call_callbacks

        args = {
            "entityReferences": two_refs,
            "relationshipTraitsData": an_empty_traitsdata,
            "pageSize": page_size,
            "relationsAccess": access.RelationsAccess.kRead,
            "context": a_context,
            "resultTraitSet": an_entity_trait_set,
        }

        if error_mode is not None:
            args["errorPolicyTag"] = error_mode

        if error_mode is None or error_mode is Manager.BatchElementErrorPolicyTag.kException:
            with pytest.raises(BatchElementException) as exc_info:
                manager.getWithRelationship(**args)

            assert exc_info.value.error == a_batch_element_error
            assert (
                exc_info.value.message
                == "unknown: some message [index=0] [access=read] [entity=asset://a]"
            )
        else:
            variant_error = manager.getWithRelationship(**args)
            assert variant_error == [a_batch_element_error, a_batch_element_error_2]


class Test_Manager_getWithRelationships_with_callback_signature:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        a_batch_element_error,
        an_empty_traitsdata,
        an_entity_trait_set,
        mock_entity_reference_pager_interface,
        an_entity_reference_pager,
        a_context,
        invoke_getWithRelationships_success_cb,
        invoke_getWithRelationships_error_cb,
    ):
        two_datas = [an_empty_traitsdata, an_empty_traitsdata]
        page_size = 3

        success_callback = mock.Mock()
        error_callback = mock.Mock()

        method = mock_manager_interface.mock.getWithRelationships

        def call_callbacks(*_args):
            invoke_getWithRelationships_success_cb(0, mock_entity_reference_pager_interface)
            invoke_getWithRelationships_error_cb(1, a_batch_element_error)

        method.side_effect = call_callbacks

        manager.getWithRelationships(
            a_ref,
            two_datas,
            page_size,
            access.RelationsAccess.kWrite,
            a_context,
            success_callback,
            error_callback,
            resultTraitSet=an_entity_trait_set,
        )

        method.assert_called_once_with(
            a_ref,  # entityref,
            two_datas,
            an_entity_trait_set,
            page_size,
            access.RelationsAccess.kWrite,
            a_context,
            a_host_session,
            mock.ANY,  # success
            mock.ANY,  # error
        )

        success_callback.assert_called_once_with(0, mock.ANY)

        # Additional assert to check cpp constructed Pager object is as
        # expected.
        pager = success_callback.call_args[0][1]
        assert isinstance(pager, EntityReferencePager)
        pager.next()
        mock_entity_reference_pager_interface.mock.next.assert_called_once_with(a_host_session)
        error_callback.assert_called_once_with(1, a_batch_element_error)

        mock_manager_interface.mock.reset_mock()

        # Check optional resultTraitSet

        manager.getWithRelationships(
            a_ref,
            two_datas,
            page_size,
            access.RelationsAccess.kWrite,
            a_context,
            success_callback,
            error_callback,
            resultTraitSet=an_entity_trait_set,
        )

        method.assert_called_once_with(
            a_ref,  # entityref
            two_datas,
            an_entity_trait_set,
            page_size,
            access.RelationsAccess.kWrite,
            a_context,
            a_host_session,
            mock.ANY,  # success
            mock.ANY,  # error
        )

    def test_pager_kept_alive_by_retaining_shared_ptr(
        self,
        manager,
        mock_manager_interface,
        a_ref,
        a_batch_element_error,
        an_empty_traitsdata,
        an_entity_trait_set,
        a_context,
        invoke_getWithRelationships_success_cb,
        invoke_getWithRelationships_error_cb,
    ):
        two_datas = [an_empty_traitsdata, an_empty_traitsdata]
        page_size = 3

        error_callback = mock.Mock()

        method = mock_manager_interface.mock.getWithRelationships

        def call_callbacks(*_args):
            invoke_getWithRelationships_success_cb(0, FakeEntityReferencePagerInterface())
            invoke_getWithRelationships_error_cb(1, a_batch_element_error)

        method.side_effect = call_callbacks

        pagers = []
        manager.getWithRelationships(
            a_ref,
            two_datas,
            page_size,
            access.RelationsAccess.kWrite,
            a_context,
            lambda _idx, pager: pagers.append(pager),
            error_callback,
            resultTraitSet=an_entity_trait_set,
        )

        # Without PyRetainingSharedPtr, will raise
        # > Tried to call pure virtual function
        # > "EntityReferencePagerInterface::get"
        pagers[0].get()

    def test_when_zero_pageSize_then_InputValidationException_is_raised(
        self, manager, a_ref, an_empty_traitsdata, an_entity_trait_set, a_context
    ):
        two_datas = [an_empty_traitsdata, an_empty_traitsdata]
        page_size = 0

        success_callback = mock.Mock()
        error_callback = mock.Mock()

        with pytest.raises(InputValidationException):
            manager.getWithRelationships(
                a_ref,
                two_datas,
                page_size,
                access.RelationsAccess.kWrite,
                a_context,
                success_callback,
                error_callback,
                resultTraitSet=an_entity_trait_set,
            )


# GetWithRelationships have no singular conveniences, as they would just be
# duplicates of GetWithRelationship


class Test_Manager_getWithRelationships_with_batch_convenience:
    @pytest.mark.parametrize(
        "error_mode",
        [
            None,
            Manager.BatchElementErrorPolicyTag.kException,
            Manager.BatchElementErrorPolicyTag.kVariant,
        ],
    )
    def test_when_success_then_entityReferencePagers_returned(
        self,
        manager,
        a_ref,
        mock_manager_interface,
        a_host_session,
        an_empty_traitsdata,
        an_entity_trait_set,
        a_context,
        mock_entity_reference_pager_interface,
        mock_entity_reference_pager_interface_2,
        invoke_getWithRelationships_success_cb,
        error_mode,
    ):

        two_traitsdatas = [an_empty_traitsdata, an_empty_traitsdata]
        page_size = 3
        method = mock_manager_interface.mock.getWithRelationships

        def call_callbacks(*_args):
            mock_entity_reference_pager_interface.mock.hasNext.return_value = True
            invoke_getWithRelationships_success_cb(0, mock_entity_reference_pager_interface)
            mock_entity_reference_pager_interface_2.mock.hasNext.return_value = False
            invoke_getWithRelationships_success_cb(1, mock_entity_reference_pager_interface_2)

        method.side_effect = call_callbacks

        args = {
            "entityReference": a_ref,
            "relationshipTraitsDatas": two_traitsdatas,
            "pageSize": page_size,
            "relationsAccess": access.RelationsAccess.kRead,
            "context": a_context,
            "resultTraitSet": an_entity_trait_set,
        }

        if error_mode is not None:
            args["errorPolicyTag"] = error_mode

        actual_pagers = manager.getWithRelationships(**args)

        method.assert_called_once_with(
            a_ref,
            two_traitsdatas,
            an_entity_trait_set,
            page_size,
            access.RelationsAccess.kRead,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert len(actual_pagers) == 2
        assert actual_pagers[0].hasNext() is True
        assert actual_pagers[1].hasNext() is False

    @pytest.mark.parametrize(
        "error_mode",
        [
            None,
            Manager.BatchElementErrorPolicyTag.kException,
            Manager.BatchElementErrorPolicyTag.kVariant,
        ],
    )
    def test_when_fail_then_error_emitted(
        self,
        manager,
        a_ref,
        mock_manager_interface,
        an_empty_traitsdata,
        an_entity_trait_set,
        a_context,
        a_batch_element_error,
        a_batch_element_error_2,
        invoke_getWithRelationships_error_cb,
        error_mode,
    ):

        two_traitsdatas = [an_empty_traitsdata, an_empty_traitsdata]
        page_size = 3
        method = mock_manager_interface.mock.getWithRelationships

        def call_callbacks(*_args):
            invoke_getWithRelationships_error_cb(0, a_batch_element_error)
            invoke_getWithRelationships_error_cb(1, a_batch_element_error_2)

        method.side_effect = call_callbacks

        args = {
            "entityReference": a_ref,
            "relationshipTraitsDatas": two_traitsdatas,
            "pageSize": page_size,
            "relationsAccess": access.RelationsAccess.kRead,
            "context": a_context,
            "resultTraitSet": an_entity_trait_set,
        }

        if error_mode is not None:
            args["errorPolicyTag"] = error_mode

        if error_mode is None or error_mode is Manager.BatchElementErrorPolicyTag.kException:
            with pytest.raises(BatchElementException) as exc_info:
                manager.getWithRelationships(**args)

            assert exc_info.value.error == a_batch_element_error
            assert (
                exc_info.value.message
                == "unknown: some message [index=0] [access=read] [entity=asset://a]"
            )
        else:
            variant_error = manager.getWithRelationships(**args)
            assert variant_error == [a_batch_element_error, a_batch_element_error_2]


class Test_Manager_BatchElementErrorPolicyTag:
    def test_unique(self):
        assert (
            Manager.BatchElementErrorPolicyTag.kVariant
            is not Manager.BatchElementErrorPolicyTag.kException
        )


class Test_Manager_resolve(BatchFirstMethodTest):
    @pytest.fixture(autouse=True)
    def constructor(
        self,
        subtests,
        invoke_resolve_success_cb,
        invoke_resolve_error_cb,
        a_batch_element_error,
        a_context,
        a_host_session,
        manager,
        mock_manager_interface,
    ):
        self.subtests = subtests
        self.invoke_success_cb = invoke_resolve_success_cb
        self.invoke_error_cb = invoke_resolve_error_cb
        self.a_batch_element_error = a_batch_element_error
        self.a_context = a_context
        self.a_host_session = a_host_session

        self.method = manager.resolve
        self.mock_interface_method = mock_manager_interface.mock.resolve

    def test_callback_overload_wraps_the_corresponding_method_of_the_held_interface(
        self, two_refs, an_entity_trait_set, a_traitsdata
    ):
        self.assert_callback_overload_wraps_the_corresponding_method_of_the_held_interface(
            method_specific_args_for_batch_of_two=(
                two_refs,
                an_entity_trait_set,
                access.ResolveAccess.kRead,
            ),
            one_success_result=a_traitsdata,
        )

    def test_singular_overload_success(self, a_ref, an_entity_trait_set, a_traitsdata):
        self.assert_singular_overload_success(
            method_specific_args=(
                a_ref,
                an_entity_trait_set,
                access.ResolveAccess.kRead,
            ),
            batched_method_specific_args=(
                [a_ref],
                an_entity_trait_set,
                access.ResolveAccess.kRead,
            ),
            expected_result=a_traitsdata,
        )

    def test_batch_overload_success(self, two_refs, an_entity_trait_set, two_entity_traitsdatas):
        self.assert_batch_overload_success(
            method_specific_args_for_batch_of_two=(
                two_refs,
                an_entity_trait_set,
                access.ResolveAccess.kRead,
            ),
            expected_results=two_entity_traitsdatas,
        )

    def test_when_batch_overload_receives_output_out_of_order_then_results_reordered(
        self, two_refs, an_entity_trait_set, two_entity_traitsdatas
    ):
        self.assert_batch_overload_success_out_of_order(
            method_specific_args_for_batch_of_two=(
                two_refs,
                an_entity_trait_set,
                access.ResolveAccess.kRead,
            ),
            expected_results=two_entity_traitsdatas,
        )

    def test_when_singular_variant_overload_errors_then_error_returned(
        self, a_ref, an_entity_trait_set
    ):
        self.assert_singular_variant_overload_error(
            method_specific_args=(
                a_ref,
                an_entity_trait_set,
                access.ResolveAccess.kRead,
            ),
            batched_method_specific_args=(
                [a_ref],
                an_entity_trait_set,
                access.ResolveAccess.kRead,
            ),
        )

    def test_when_batch_variant_overload_receives_mixed_output_then_mixed_results_returned(
        self, two_refs, an_entity_trait_set, a_traitsdata
    ):
        self.assert_batch_variant_overload_mixed_output(
            method_specific_args_for_batch_of_two=(
                two_refs,
                an_entity_trait_set,
                access.ResolveAccess.kRead,
            ),
            one_success_result=a_traitsdata,
        )

    def test_when_batch_variant_overload_receives_mixed_output_out_of_order_then_results_reordered(
        self, four_refs, an_entity_trait_set, two_entity_traitsdatas
    ):
        self.assert_batch_variant_overload_mixed_output_out_of_order(
            method_specific_args_for_batch_of_four=(
                four_refs,
                an_entity_trait_set,
                access.ResolveAccess.kRead,
            ),
            two_success_results=two_entity_traitsdatas,
        )

    @pytest.mark.parametrize(
        "access_mode", [access.ResolveAccess.kRead, access.ResolveAccess.kManagerDriven]
    )
    @pytest.mark.parametrize("error_code", BatchFirstMethodTest.batch_element_error_codes)
    def test_when_singular_throwing_overload_errors_then_raises(
        self, a_ref, an_entity_trait_set, a_traitsdata, access_mode, error_code
    ):
        batch_element_error = BatchElementError(error_code, "some error")
        expected_error_message = self._make_expected_err_msg(
            batch_element_error,
            access_mode,
            a_ref,
        )

        self.assert_singular_throwing_overload_raises(
            method_specific_args=(
                a_ref,
                an_entity_trait_set,
                access_mode,
            ),
            batched_method_specific_args=(
                [a_ref],
                an_entity_trait_set,
                access_mode,
            ),
            batch_element_error=batch_element_error,
            expected_error_message=expected_error_message,
        )

    @pytest.mark.parametrize(
        "access_mode", [access.ResolveAccess.kRead, access.ResolveAccess.kManagerDriven]
    )
    @pytest.mark.parametrize("error_code", BatchFirstMethodTest.batch_element_error_codes)
    def test_when_batched_throwing_overload_errors_then_raises(
        self, two_refs, an_entity_trait_set, access_mode, error_code
    ):
        batch_element_error = BatchElementError(error_code, "some error")
        expected_error_message = self._make_expected_err_msg(
            batch_element_error,
            access_mode,
            two_refs[0],
        )

        self.assert_batched_throwing_overload_raises(
            method_specific_args_for_batch_of_two=(
                two_refs,
                an_entity_trait_set,
                access_mode,
            ),
            batch_element_error=batch_element_error,
            expected_error_message=expected_error_message,
        )


class Test_Manager_entityTraits(BatchFirstMethodTest):
    @pytest.fixture(autouse=True)
    def constructor(
        self,
        subtests,
        invoke_entityTraits_success_cb,
        invoke_entityTraits_error_cb,
        a_batch_element_error,
        a_context,
        a_host_session,
        manager,
        mock_manager_interface,
    ):
        self.subtests = subtests
        self.invoke_success_cb = invoke_entityTraits_success_cb
        self.invoke_error_cb = invoke_entityTraits_error_cb
        self.a_batch_element_error = a_batch_element_error
        self.a_context = a_context
        self.a_host_session = a_host_session

        self.method = manager.entityTraits
        self.mock_interface_method = mock_manager_interface.mock.entityTraits

    def test_callback_overload_wraps_the_corresponding_method_of_the_held_interface(
        self, two_refs, an_entity_trait_set
    ):
        self.assert_callback_overload_wraps_the_corresponding_method_of_the_held_interface(
            method_specific_args_for_batch_of_two=(
                two_refs,
                access.EntityTraitsAccess.kRead,
            ),
            one_success_result=an_entity_trait_set,
        )

    def test_singular_overload_success(self, a_ref, an_entity_trait_set):
        self.assert_singular_overload_success(
            method_specific_args=(
                a_ref,
                access.EntityTraitsAccess.kRead,
            ),
            batched_method_specific_args=(
                [a_ref],
                access.EntityTraitsAccess.kRead,
            ),
            expected_result=an_entity_trait_set,
            assert_result_identity=False,
        )

    def test_batch_overload_success(self, two_refs, two_entity_trait_sets):
        self.assert_batch_overload_success(
            method_specific_args_for_batch_of_two=(
                two_refs,
                access.EntityTraitsAccess.kRead,
            ),
            expected_results=two_entity_trait_sets,
            assert_result_identity=False,
        )

    assert_result_identity = (False,)

    def test_when_batch_overload_receives_output_out_of_order_then_results_reordered(
        self, two_refs, two_entity_trait_sets
    ):
        self.assert_batch_overload_success_out_of_order(
            method_specific_args_for_batch_of_two=(
                two_refs,
                access.EntityTraitsAccess.kRead,
            ),
            expected_results=two_entity_trait_sets,
            assert_result_identity=False,
        )

    def test_when_singular_variant_overload_errors_then_error_returned(self, a_ref):
        self.assert_singular_variant_overload_error(
            method_specific_args=(
                a_ref,
                access.EntityTraitsAccess.kRead,
            ),
            batched_method_specific_args=(
                [a_ref],
                access.EntityTraitsAccess.kRead,
            ),
        )

    def test_when_batch_variant_overload_receives_mixed_output_then_mixed_results_returned(
        self, two_refs, an_entity_trait_set
    ):
        self.assert_batch_variant_overload_mixed_output(
            method_specific_args_for_batch_of_two=(
                two_refs,
                access.EntityTraitsAccess.kRead,
            ),
            one_success_result=an_entity_trait_set,
        )

    def test_when_batch_variant_overload_receives_mixed_output_out_of_order_then_results_reordered(
        self, four_refs, two_entity_trait_sets
    ):
        self.assert_batch_variant_overload_mixed_output_out_of_order(
            method_specific_args_for_batch_of_four=(
                four_refs,
                access.EntityTraitsAccess.kRead,
            ),
            two_success_results=two_entity_trait_sets,
        )

    @pytest.mark.parametrize(
        "access_mode", [access.EntityTraitsAccess.kRead, access.EntityTraitsAccess.kWrite]
    )
    @pytest.mark.parametrize("error_code", BatchFirstMethodTest.batch_element_error_codes)
    def test_when_singular_throwing_overload_errors_then_raises(
        self, a_ref, access_mode, error_code
    ):
        batch_element_error = BatchElementError(error_code, "some error")
        expected_error_message = self._make_expected_err_msg(
            batch_element_error,
            access_mode,
            a_ref,
        )

        self.assert_singular_throwing_overload_raises(
            method_specific_args=(
                a_ref,
                access_mode,
            ),
            batched_method_specific_args=(
                [a_ref],
                access_mode,
            ),
            batch_element_error=batch_element_error,
            expected_error_message=expected_error_message,
        )

    @pytest.mark.parametrize(
        "access_mode", [access.EntityTraitsAccess.kRead, access.EntityTraitsAccess.kWrite]
    )
    @pytest.mark.parametrize("error_code", BatchFirstMethodTest.batch_element_error_codes)
    def test_when_batched_throwing_overload_errors_then_raises(
        self, two_refs, access_mode, error_code
    ):
        batch_element_error = BatchElementError(error_code, "some error")
        expected_error_message = self._make_expected_err_msg(
            batch_element_error,
            access_mode,
            two_refs[0],
        )

        self.assert_batched_throwing_overload_raises(
            method_specific_args_for_batch_of_two=(
                two_refs,
                access_mode,
            ),
            batch_element_error=batch_element_error,
            expected_error_message=expected_error_message,
        )


class Test_Manager_managementPolicy:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.managementPolicy)
        assert method_introspector.is_implemented_once(Manager, "managementPolicy")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface, a_host_session, some_entity_trait_sets, a_context
    ):
        data1 = TraitsData()
        data1.setTraitProperty("t1", "p1", 1)
        data2 = TraitsData()
        data2.setTraitProperty("t2", "p2", 2)
        expected = [data1, data2]
        method = mock_manager_interface.mock.managementPolicy
        method.return_value = expected

        actual = manager.managementPolicy(
            some_entity_trait_sets, access.PolicyAccess.kWrite, a_context
        )

        assert actual == expected
        method.assert_called_once_with(
            some_entity_trait_sets, access.PolicyAccess.kWrite, a_context, a_host_session
        )


class Test_Manager_preflight(BatchFirstMethodTest):
    @pytest.fixture(autouse=True)
    def constructor(
        self,
        subtests,
        invoke_preflight_success_cb,
        invoke_preflight_error_cb,
        a_batch_element_error,
        a_context,
        a_host_session,
        manager,
        mock_manager_interface,
    ):
        self.subtests = subtests
        self.invoke_success_cb = invoke_preflight_success_cb
        self.invoke_error_cb = invoke_preflight_error_cb
        self.a_batch_element_error = a_batch_element_error
        self.a_context = a_context
        self.a_host_session = a_host_session

        self.method = manager.preflight
        self.mock_interface_method = mock_manager_interface.mock.preflight

    def test_callback_overload_wraps_the_corresponding_method_of_the_held_interface(
        self, two_refs, two_entity_traitsdatas, a_ref
    ):
        self.assert_callback_overload_wraps_the_corresponding_method_of_the_held_interface(
            method_specific_args_for_batch_of_two=(
                two_refs,
                two_entity_traitsdatas,
                access.PublishingAccess.kWrite,
            ),
            one_success_result=a_ref,
        )

    def test_when_callback_overload_given_mixed_array_lengths_then_raises(
        self, two_refs, two_entity_traitsdatas
    ):
        self.assert_callback_overload_errors_with_mixed_array_lengths(
            batched_method_specific_args_for_batch_of_two=(two_refs, two_entity_traitsdatas),
            nonbatched_remaining_method_specific_args=(access.PublishingAccess.kWrite,),
            expected_message_pattern=(
                "Parameter lists must be of the same length: {} entity references vs."
                " {} traits hints."
            ),
        )

    def test_when_callback_overload_given_invalid_batch_element_then_raises(
        self, two_refs, a_traitsdata
    ):
        self.assert_callback_overload_errors_with_invalid_batch_element(
            method_specific_args_for_batch_of_two_with_invalid_element=(
                two_refs,
                [a_traitsdata, None],
                access.PublishingAccess.kWrite,
            )
        )

    def test_singular_overload_success(self, a_ref, a_different_ref, a_traitsdata):
        self.assert_singular_overload_success(
            method_specific_args=(
                a_ref,
                a_traitsdata,
                access.PublishingAccess.kWrite,
            ),
            batched_method_specific_args=(
                [a_ref],
                [a_traitsdata],
                access.PublishingAccess.kWrite,
            ),
            expected_result=a_different_ref,
            assert_result_identity=False,
        )

    def test_batch_overload_success(self, two_refs, two_entity_traitsdatas, two_different_refs):
        self.assert_batch_overload_success(
            method_specific_args_for_batch_of_two=(
                two_refs,
                two_entity_traitsdatas,
                access.PublishingAccess.kWrite,
            ),
            expected_results=two_different_refs,
            assert_result_identity=False,
        )

    def test_when_batch_overload_receives_output_out_of_order_then_results_reordered(
        self, two_refs, two_entity_traitsdatas, two_different_refs
    ):
        self.assert_batch_overload_success_out_of_order(
            method_specific_args_for_batch_of_two=(
                two_refs,
                two_entity_traitsdatas,
                access.PublishingAccess.kWrite,
            ),
            expected_results=two_different_refs,
            assert_result_identity=False,
        )

    def test_when_singular_variant_overload_errors_then_error_returned(self, a_ref, a_traitsdata):
        self.assert_singular_variant_overload_error(
            method_specific_args=(
                a_ref,
                a_traitsdata,
                access.PublishingAccess.kWrite,
            ),
            batched_method_specific_args=(
                [a_ref],
                [a_traitsdata],
                access.PublishingAccess.kWrite,
            ),
        )

    def test_when_batch_variant_overload_receives_mixed_output_then_mixed_results_returned(
        self, two_refs, two_entity_traitsdatas, a_ref
    ):
        self.assert_batch_variant_overload_mixed_output(
            method_specific_args_for_batch_of_two=(
                two_refs,
                two_entity_traitsdatas,
                access.PublishingAccess.kWrite,
            ),
            one_success_result=a_ref,
        )

    def test_when_batch_variant_overload_receives_mixed_output_out_of_order_then_results_reordered(
        self, four_refs, four_entity_traitsdatas, two_refs
    ):
        self.assert_batch_variant_overload_mixed_output_out_of_order(
            method_specific_args_for_batch_of_four=(
                four_refs,
                four_entity_traitsdatas,
                access.PublishingAccess.kWrite,
            ),
            two_success_results=two_refs,
        )

    @pytest.mark.parametrize(
        "access_mode", [access.PublishingAccess.kWrite, access.PublishingAccess.kCreateRelated]
    )
    @pytest.mark.parametrize("error_code", BatchFirstMethodTest.batch_element_error_codes)
    def test_when_singular_throwing_overload_errors_then_raises(
        self, a_ref, a_traitsdata, access_mode, error_code
    ):
        batch_element_error = BatchElementError(error_code, "some error")
        expected_error_message = self._make_expected_err_msg(
            batch_element_error,
            access_mode,
            a_ref,
        )

        self.assert_singular_throwing_overload_raises(
            method_specific_args=(
                a_ref,
                a_traitsdata,
                access_mode,
            ),
            batched_method_specific_args=(
                [a_ref],
                [a_traitsdata],
                access_mode,
            ),
            batch_element_error=batch_element_error,
            expected_error_message=expected_error_message,
        )

    @pytest.mark.parametrize(
        "access_mode", [access.PublishingAccess.kWrite, access.PublishingAccess.kCreateRelated]
    )
    @pytest.mark.parametrize("error_code", BatchFirstMethodTest.batch_element_error_codes)
    def test_when_batched_throwing_overload_errors_then_raises(
        self, two_refs, two_entity_traitsdatas, access_mode, error_code
    ):
        batch_element_error = BatchElementError(error_code, "some error")
        expected_error_message = self._make_expected_err_msg(
            batch_element_error,
            access_mode,
            two_refs[0],
        )

        self.assert_batched_throwing_overload_raises(
            method_specific_args_for_batch_of_two=(
                two_refs,
                two_entity_traitsdatas,
                access_mode,
            ),
            batch_element_error=batch_element_error,
            expected_error_message=expected_error_message,
        )


class Test_Manager_register(BatchFirstMethodTest):
    @pytest.fixture(autouse=True)
    def constructor(
        self,
        subtests,
        invoke_register_success_cb,
        invoke_register_error_cb,
        a_batch_element_error,
        a_context,
        a_host_session,
        manager,
        mock_manager_interface,
    ):
        self.subtests = subtests
        self.invoke_success_cb = invoke_register_success_cb
        self.invoke_error_cb = invoke_register_error_cb
        self.a_batch_element_error = a_batch_element_error
        self.a_context = a_context
        self.a_host_session = a_host_session

        self.method = manager.register
        self.mock_interface_method = mock_manager_interface.mock.register

    def test_callback_overload_wraps_the_corresponding_method_of_the_held_interface(
        self, two_refs, two_entity_traitsdatas, a_ref
    ):
        self.assert_callback_overload_wraps_the_corresponding_method_of_the_held_interface(
            method_specific_args_for_batch_of_two=(
                two_refs,
                two_entity_traitsdatas,
                access.PublishingAccess.kWrite,
            ),
            one_success_result=a_ref,
        )

    def test_when_callback_overload_given_mixed_array_lengths_then_raises(
        self, two_refs, two_entity_traitsdatas
    ):
        self.assert_callback_overload_errors_with_mixed_array_lengths(
            batched_method_specific_args_for_batch_of_two=(two_refs, two_entity_traitsdatas),
            nonbatched_remaining_method_specific_args=(access.PublishingAccess.kWrite,),
            expected_message_pattern=(
                "Parameter lists must be of the same length: {} entity references vs."
                " {} traits datas."
            ),
        )

    def test_when_callback_overload_given_invalid_batch_element_then_raises(
        self, two_refs, a_traitsdata
    ):
        self.assert_callback_overload_errors_with_invalid_batch_element(
            method_specific_args_for_batch_of_two_with_invalid_element=(
                two_refs,
                [a_traitsdata, None],
                access.PublishingAccess.kWrite,
            )
        )

    def test_singular_overload_success(self, a_ref, a_different_ref, a_traitsdata):
        self.assert_singular_overload_success(
            method_specific_args=(
                a_ref,
                a_traitsdata,
                access.PublishingAccess.kWrite,
            ),
            batched_method_specific_args=(
                [a_ref],
                [a_traitsdata],
                access.PublishingAccess.kWrite,
            ),
            expected_result=a_different_ref,
            assert_result_identity=False,
        )

    def test_batch_overload_success(self, two_refs, two_entity_traitsdatas, two_different_refs):
        self.assert_batch_overload_success(
            method_specific_args_for_batch_of_two=(
                two_refs,
                two_entity_traitsdatas,
                access.PublishingAccess.kWrite,
            ),
            expected_results=two_different_refs,
            assert_result_identity=False,
        )

    def test_when_batch_overload_receives_output_out_of_order_then_results_reordered(
        self, two_refs, two_entity_traitsdatas, two_different_refs
    ):
        self.assert_batch_overload_success_out_of_order(
            method_specific_args_for_batch_of_two=(
                two_refs,
                two_entity_traitsdatas,
                access.PublishingAccess.kWrite,
            ),
            expected_results=two_different_refs,
            assert_result_identity=False,
        )

    def test_when_singular_variant_overload_errors_then_error_returned(self, a_ref, a_traitsdata):
        self.assert_singular_variant_overload_error(
            method_specific_args=(
                a_ref,
                a_traitsdata,
                access.PublishingAccess.kWrite,
            ),
            batched_method_specific_args=(
                [a_ref],
                [a_traitsdata],
                access.PublishingAccess.kWrite,
            ),
        )

    def test_when_batch_variant_overload_receives_mixed_output_then_mixed_results_returned(
        self, two_refs, two_entity_traitsdatas, a_ref
    ):
        self.assert_batch_variant_overload_mixed_output(
            method_specific_args_for_batch_of_two=(
                two_refs,
                two_entity_traitsdatas,
                access.PublishingAccess.kWrite,
            ),
            one_success_result=a_ref,
        )

    def test_when_batch_variant_overload_receives_mixed_output_out_of_order_then_results_reordered(
        self, four_refs, four_entity_traitsdatas, two_refs
    ):
        self.assert_batch_variant_overload_mixed_output_out_of_order(
            method_specific_args_for_batch_of_four=(
                four_refs,
                four_entity_traitsdatas,
                access.PublishingAccess.kWrite,
            ),
            two_success_results=two_refs,
        )

    @pytest.mark.parametrize(
        "access_mode", [access.PublishingAccess.kWrite, access.PublishingAccess.kCreateRelated]
    )
    @pytest.mark.parametrize("error_code", BatchFirstMethodTest.batch_element_error_codes)
    def test_when_singular_throwing_overload_errors_then_raises(
        self, a_ref, a_traitsdata, access_mode, error_code
    ):
        batch_element_error = BatchElementError(error_code, "some error")
        expected_error_message = self._make_expected_err_msg(
            batch_element_error,
            access_mode,
            a_ref,
        )

        self.assert_singular_throwing_overload_raises(
            method_specific_args=(
                a_ref,
                a_traitsdata,
                access_mode,
            ),
            batched_method_specific_args=(
                [a_ref],
                [a_traitsdata],
                access_mode,
            ),
            batch_element_error=batch_element_error,
            expected_error_message=expected_error_message,
        )

    @pytest.mark.parametrize(
        "access_mode", [access.PublishingAccess.kWrite, access.PublishingAccess.kCreateRelated]
    )
    @pytest.mark.parametrize("error_code", BatchFirstMethodTest.batch_element_error_codes)
    def test_when_batched_throwing_overload_errors_then_raises(
        self, two_refs, two_entity_traitsdatas, access_mode, error_code
    ):
        batch_element_error = BatchElementError(error_code, "some error")
        expected_error_message = self._make_expected_err_msg(
            batch_element_error,
            access_mode,
            two_refs[0],
        )

        self.assert_batched_throwing_overload_raises(
            method_specific_args_for_batch_of_two=(
                two_refs,
                two_entity_traitsdatas,
                access_mode,
            ),
            batch_element_error=batch_element_error,
            expected_error_message=expected_error_message,
        )


class Test_Manager_createContext:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.createContext)
        assert method_introspector.is_implemented_once(Manager, "createContext")

    def test_context_is_created_with_locale(self, manager, mock_manager_interface, a_host_session):
        mock_manager_interface.mock.hasCapability.return_value = False

        context_a = manager.createContext()

        assert isinstance(context_a.locale, TraitsData)
        assert context_a.locale.traitSet() == set()

    def test_when_custom_state_not_supported_then_create_state_not_called(
        self, manager, mock_manager_interface, a_host_session
    ):
        mock_manager_interface.mock.hasCapability.return_value = False

        context_a = manager.createContext()

        assert context_a.managerState is None
        mock_manager_interface.mock.createState.assert_not_called()

    def test_when_custom_state_supported_then_returned_context_contains_state(
        self, manager, mock_manager_interface, a_host_session
    ):
        # setup

        mock_manager_interface.mock.hasCapability.return_value = True
        state_a = managerApi.ManagerStateBase()
        mock_manager_interface.mock.createState.return_value = state_a

        # action

        context_a = manager.createContext()

        # confirm

        assert context_a.managerState is state_a
        mock_manager_interface.mock.createState.assert_called_once_with(a_host_session)


class Test_Manager_createChildContext:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.createChildContext)
        assert method_introspector.is_implemented_once(Manager, "createChildContext")

    def test_when_called_with_parent_then_props_copied_and_createState_called_with_parent_state(
        self, manager, mock_manager_interface, a_host_session
    ):
        state_a = managerApi.ManagerStateBase()
        mock_manager_interface.mock.createState.return_value = state_a
        context_a = manager.createContext()
        context_a.locale = TraitsData()
        mock_manager_interface.mock.reset_mock()

        state_b = managerApi.ManagerStateBase()
        mock_manager_interface.mock.createChildState.return_value = state_b

        context_b = manager.createChildContext(context_a)

        assert context_b is not context_a
        assert context_b.managerState is state_b
        assert context_b.locale == context_a.locale
        mock_manager_interface.mock.createChildState.assert_called_once_with(
            state_a, a_host_session
        )
        mock_manager_interface.mock.createState.assert_not_called()

    def test_when_called_with_parent_then_locale_is_deep_copied(
        self, manager, mock_manager_interface, a_host_session
    ):
        original_locale = TraitsData()
        original_locale.setTraitProperty("a", "v", 1)

        state_a = managerApi.ManagerStateBase()
        mock_manager_interface.mock.createState.return_value = state_a
        mock_manager_interface.mock.createChildState.return_value = state_a
        context_a = manager.createContext()
        context_a.locale = original_locale

        context_b = manager.createChildContext(context_a)

        assert context_b.locale == context_a.locale
        original_locale.setTraitProperty("a", "v", 2)
        assert context_b.locale != context_a.locale

    def test_when_called_with_parent_with_no_managerState_then_createChildState_is_not_called(
        self, manager, mock_manager_interface
    ):
        context_a = Context()
        context_a.locale = TraitsData()
        context_b = manager.createChildContext(context_a)

        assert context_b.locale == context_b.locale
        mock_manager_interface.mock.createChildState.assert_not_called()


class Test_Manager_persistenceTokenForContext:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.persistenceTokenForContext)
        assert method_introspector.is_implemented_once(Manager, "persistenceTokenForContext")

    def test_when_called_then_the_managers_persistence_token_is_returned(
        self, manager, mock_manager_interface, a_host_session
    ):
        expected_token = "a_persistence_token"
        mock_manager_interface.mock.persistenceTokenForState.return_value = expected_token

        initial_state = managerApi.ManagerStateBase()
        a_context = Context()
        a_context.managerState = initial_state

        actual_token = manager.persistenceTokenForContext(a_context)

        assert actual_token == expected_token

        mock_manager_interface.mock.persistenceTokenForState.assert_called_once_with(
            initial_state, a_host_session
        )

    def test_when_no_state_then_return_is_empty_and_persistenceTokenForState_is_not_called(
        self, manager, mock_manager_interface
    ):
        a_context = Context()

        assert manager.persistenceTokenForContext(a_context) == ""
        mock_manager_interface.mock.persistenceTokenForState.assert_not_called()


class Test_Manager_contextFromPersistenceToken:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.contextFromPersistenceToken)
        assert method_introspector.is_implemented_once(Manager, "contextFromPersistenceToken")

    def test_when_called_then_the_managers_restored_state_is_set_in_the_context(
        self, manager, mock_manager_interface, a_host_session
    ):
        expected_state = managerApi.ManagerStateBase()
        mock_manager_interface.mock.stateFromPersistenceToken.return_value = expected_state

        a_token = "a_persistence_token"
        a_context = manager.contextFromPersistenceToken(a_token)

        assert a_context.managerState is expected_state

        mock_manager_interface.mock.stateFromPersistenceToken.assert_called_once_with(
            a_token, a_host_session
        )

    def test_when_empty_then_no_state_and_stateFromPersistenceToken_is_not_called(
        self, manager, mock_manager_interface
    ):
        a_context = manager.contextFromPersistenceToken("")
        assert a_context.managerState is None
        mock_manager_interface.mock.stateFromPersistenceToken.assert_not_called()


@pytest.fixture
def manager(mock_manager_interface, a_host_session):
    # Default to accepting anything as an entity reference string, to
    # make constructing EntityReference objects a bit easier.
    mock_manager_interface.mock.isEntityReferenceString.return_value = True
    return Manager(mock_manager_interface, a_host_session)


@pytest.fixture
def an_entity_reference_pager(mock_entity_reference_pager_interface, a_host_session):
    return EntityReferencePager(mock_entity_reference_pager_interface, a_host_session)


@pytest.fixture
def an_empty_traitsdata():
    return TraitsData(set())


@pytest.fixture
def four_entity_traitsdatas(two_entity_traitsdatas):
    first = TraitsData({"another_trait"})
    second = TraitsData({"another_trait", "another_different_trait"})
    first.setTraitProperty("another_trait", "another_prop", 123)
    second.setTraitProperty("another_trait", "another_prop", 456)
    return [first, second] + two_entity_traitsdatas


@pytest.fixture
def two_entity_traitsdatas(some_entity_traitsdatas):
    return some_entity_traitsdatas


@pytest.fixture
def some_entity_traitsdatas():
    first = TraitsData({"a_trait"})
    second = TraitsData({"a_trait", "a_different_trait"})
    first.setTraitProperty("a_trait", "a_prop", 123)
    second.setTraitProperty("a_trait", "a_prop", 456)
    return [first, second]


@pytest.fixture
def a_traitsdata():
    return TraitsData(set())


@pytest.fixture
def a_batch_element_error():
    return BatchElementError(BatchElementError.ErrorCode.kUnknown, "some message")


@pytest.fixture
def a_batch_element_error_2():
    return BatchElementError(
        BatchElementError.ErrorCode.kInvalidEntityReference, "another message"
    )


@pytest.fixture
def two_entity_trait_sets():
    return [{"blob", "lolcat"}, {"lolcat", "dog"}]


@pytest.fixture
def an_entity_trait_set():
    return {"blob", "lolcat"}


@pytest.fixture
def some_entity_trait_sets():
    return [{"blob"}, {"blob", "image"}]


@pytest.fixture
def a_context():
    return Context()


@pytest.fixture
def a_ref_string():
    return "asset://a"


@pytest.fixture
def a_ref(manager):
    return manager.createEntityReference("asset://a")


@pytest.fixture
def a_different_ref(manager):
    return manager.createEntityReference("asset://b")


@pytest.fixture
def two_refs(some_refs):
    return some_refs


@pytest.fixture
def two_different_refs(some_different_refs):
    return some_different_refs


@pytest.fixture
def four_refs(some_refs, some_different_refs):
    return some_refs + some_different_refs


@pytest.fixture
def some_refs(manager):
    return [manager.createEntityReference("asset://c"), manager.createEntityReference("asset://d")]


@pytest.fixture
def some_different_refs(manager):
    return [manager.createEntityReference("asset://e"), manager.createEntityReference("asset://f")]


@pytest.fixture
def invoke_entityExists_success_cb(mock_manager_interface):
    def invoke(idx, exists):
        callback = mock_manager_interface.mock.entityExists.call_args[0][3]
        callback(idx, exists)

    return invoke


@pytest.fixture
def invoke_entityExists_error_cb(mock_manager_interface):
    def invoke(idx, batch_element_error):
        callback = mock_manager_interface.mock.entityExists.call_args[0][4]
        callback(idx, batch_element_error)

    return invoke


@pytest.fixture
def invoke_defaultEntityReference_success_cb(mock_manager_interface):
    def invoke(idx, entity_ref):
        callback = mock_manager_interface.mock.defaultEntityReference.call_args[0][4]
        callback(idx, entity_ref)

    return invoke


@pytest.fixture
def invoke_defaultEntityReference_error_cb(mock_manager_interface):
    def invoke(idx, batch_element_error):
        callback = mock_manager_interface.mock.defaultEntityReference.call_args[0][5]
        callback(idx, batch_element_error)

    return invoke


@pytest.fixture
def invoke_getWithRelationship_success_cb(mock_manager_interface):
    def invoke(idx, entityReferencesPagerInterface):
        callback = mock_manager_interface.mock.getWithRelationship.call_args[0][7]
        callback(idx, entityReferencesPagerInterface)

    return invoke


@pytest.fixture
def invoke_getWithRelationships_error_cb(mock_manager_interface):
    def invoke(idx, batch_element_error):
        callback = mock_manager_interface.mock.getWithRelationships.call_args[0][8]
        callback(idx, batch_element_error)

    return invoke


@pytest.fixture
def invoke_getWithRelationships_success_cb(mock_manager_interface):
    def invoke(idx, entityReferencesPagerInterface):
        callback = mock_manager_interface.mock.getWithRelationships.call_args[0][7]
        callback(idx, entityReferencesPagerInterface)

    return invoke


@pytest.fixture
def invoke_getWithRelationship_error_cb(mock_manager_interface):
    def invoke(idx, batch_element_error):
        callback = mock_manager_interface.mock.getWithRelationship.call_args[0][8]
        callback(idx, batch_element_error)

    return invoke


@pytest.fixture
def invoke_resolve_success_cb(mock_manager_interface):
    def invoke(idx, traits_data):
        callback = mock_manager_interface.mock.resolve.call_args[0][5]
        callback(idx, traits_data)

    return invoke


@pytest.fixture
def invoke_resolve_error_cb(mock_manager_interface):
    def invoke(idx, batch_element_error):
        callback = mock_manager_interface.mock.resolve.call_args[0][6]
        callback(idx, batch_element_error)

    return invoke


@pytest.fixture
def invoke_entityTraits_success_cb(mock_manager_interface):
    def invoke(idx, traits_data):
        callback = mock_manager_interface.mock.entityTraits.call_args[0][4]
        callback(idx, traits_data)

    return invoke


@pytest.fixture
def invoke_entityTraits_error_cb(mock_manager_interface):
    def invoke(idx, batch_element_error):
        callback = mock_manager_interface.mock.entityTraits.call_args[0][5]
        callback(idx, batch_element_error)

    return invoke


@pytest.fixture
def invoke_preflight_success_cb(mock_manager_interface):
    def invoke(idx, traits_data):
        callback = mock_manager_interface.mock.preflight.call_args[0][5]
        callback(idx, traits_data)

    return invoke


@pytest.fixture
def invoke_preflight_error_cb(mock_manager_interface):
    def invoke(idx, batch_element_error):
        callback = mock_manager_interface.mock.preflight.call_args[0][6]
        callback(idx, batch_element_error)

    return invoke


@pytest.fixture
def invoke_register_success_cb(mock_manager_interface):
    def invoke(idx, traits_data):
        callback = mock_manager_interface.mock.register.call_args[0][5]
        callback(idx, traits_data)

    return invoke


@pytest.fixture
def invoke_register_error_cb(mock_manager_interface):
    def invoke(idx, batch_element_error):
        callback = mock_manager_interface.mock.register.call_args[0][6]
        callback(idx, batch_element_error)

    return invoke
