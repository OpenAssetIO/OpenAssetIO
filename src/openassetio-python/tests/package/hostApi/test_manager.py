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
Tests that cover the openassetio.hostApi.Manager wrapper class.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
from unittest import mock

import pytest

from openassetio import (
    UnknownBatchElementException,
    InvalidEntityReferenceBatchElementException,
    MalformedEntityReferenceBatchElementException,
    EntityAccessErrorBatchElementException,
    EntityResolutionErrorBatchElementException,
    BatchElementError,
    Context,
    EntityReference,
    TraitsData,
    managerApi,
)
from openassetio.hostApi import Manager


## @todo Remove comments regarding Entity methods when splitting them from core API

# __str__ and __repr__ aren't tested as they're debug tricks that need
# assessing when this is ported to cpp


class Test_Manager_init:
    def test_interface_returns_the_constructor_supplied_object(
        self, mock_manager_interface, a_host_session
    ):
        # pylint: disable=protected-access
        a_manager = Manager(mock_manager_interface, a_host_session)
        assert a_manager._interface() is mock_manager_interface

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
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(Manager.updateTerminology)
        assert method_introspector.is_implemented_once(Manager, "updateTerminology")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface, a_host_session
    ):
        method = mock_manager_interface.mock.updateTerminology
        a_dict = {"k", "v"}
        assert manager.updateTerminology(a_dict) is a_dict
        method.assert_called_once_with(a_dict, a_host_session)


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


class Test_Manager_flushCaches:
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(Manager.flushCaches)
        assert method_introspector.is_implemented_once(Manager, "flushCaches")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface, a_host_session
    ):
        method = mock_manager_interface.mock.flushCaches
        assert manager.flushCaches() == method.return_value
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


class Test_Manager_createEntityReference:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.createEntityReference)
        assert method_introspector.is_implemented_once(Manager, "createEntityReference")

    def test_when_invalid_then_raises_ValueError(
        self, manager, mock_manager_interface, a_ref_string, a_host_session
    ):
        mock_manager_interface.mock.isEntityReferenceString.return_value = False

        with pytest.raises(ValueError) as err:
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
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(Manager.entityExists)
        assert method_introspector.is_implemented_once(Manager, "entityExists")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface, a_host_session, some_refs, a_context
    ):
        method = mock_manager_interface.mock.entityExists
        assert manager.entityExists(some_refs, a_context) == method.return_value
        method.assert_called_once_with(some_refs, a_context, a_host_session)


class Test_Manager_defaultEntityReference:
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(Manager.defaultEntityReference)
        assert method_introspector.is_implemented_once(Manager, "defaultEntityReference")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface, a_host_session, a_context, some_entity_trait_sets
    ):
        method = mock_manager_interface.mock.defaultEntityReference
        assert (
            manager.defaultEntityReference(some_entity_trait_sets, a_context)
            == method.return_value
        )
        method.assert_called_once_with(some_entity_trait_sets, a_context, a_host_session)


class Test_Manager_entityVersion:
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(Manager.entityVersion)
        assert method_introspector.is_implemented_once(Manager, "entityVersion")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface, a_host_session, some_refs, a_context
    ):
        method = mock_manager_interface.mock.entityVersion
        assert manager.entityVersion(some_refs, a_context) == method.return_value
        method.assert_called_once_with(some_refs, a_context, a_host_session)


class Test_Manager_entityVersions:
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(Manager.entityVersions)
        assert method_introspector.is_implemented_once(Manager, "entityVersions")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface, a_host_session, some_refs, a_context
    ):
        method = mock_manager_interface.mock.entityVersions

        assert manager.entityVersions(some_refs, a_context) == method.return_value
        method.assert_called_once_with(
            some_refs, a_context, a_host_session, includeMetaVersions=False, maxNumVersions=-1
        )
        method.reset_mock()

        max_results = 5
        assert (
            manager.entityVersions(some_refs, a_context, maxNumVersions=max_results)
            == method.return_value
        )
        method.assert_called_once_with(
            some_refs,
            a_context,
            a_host_session,
            includeMetaVersions=False,
            maxNumVersions=max_results,
        )
        method.reset_mock()

        include_meta = True
        assert (
            manager.entityVersions(
                some_refs, a_context, maxNumVersions=max_results, includeMetaVersions=include_meta
            )
            == method.return_value
        )
        method.assert_called_once_with(
            some_refs,
            a_context,
            a_host_session,
            includeMetaVersions=include_meta,
            maxNumVersions=max_results,
        )


class Test_Manager_finalizedEntityVersion:
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(Manager.finalizedEntityVersion)
        assert method_introspector.is_implemented_once(Manager, "finalizedEntityVersion")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, manager, mock_manager_interface, a_host_session, some_refs, a_context
    ):
        method = mock_manager_interface.mock.finalizedEntityVersion
        assert manager.finalizedEntityVersion(some_refs, a_context) == method.return_value
        method.assert_called_once_with(
            some_refs, a_context, a_host_session, overrideVersionName=None
        )
        method.reset_mock()

        a_version_name = "aVersion"
        method = mock_manager_interface.mock.finalizedEntityVersion
        assert (
            manager.finalizedEntityVersion(
                some_refs, a_context, overrideVersionName=a_version_name
            )
            == method.return_value
        )
        method.assert_called_once_with(
            some_refs, a_context, a_host_session, overrideVersionName=a_version_name
        )


class Test_Manager_getWithRelationship:
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(Manager.getWithRelationship)
        assert method_introspector.is_implemented_once(Manager, "getWithRelationship")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        a_different_ref,
        a_batch_element_error,
        an_empty_traitsdata,
        an_entity_trait_set,
        a_context,
        invoke_getWithRelationship_success_cb,
        invoke_getWithRelationship_error_cb,
    ):
        # pylint: disable=too-many-locals

        two_refs = [a_ref, a_ref]
        two_different_refs = [a_different_ref, a_different_ref]

        success_callback = mock.Mock()
        error_callback = mock.Mock()

        method = mock_manager_interface.mock.getWithRelationship

        def call_callbacks(*_args):
            invoke_getWithRelationship_success_cb(0, two_different_refs)
            invoke_getWithRelationship_error_cb(1, a_batch_element_error)

        method.side_effect = call_callbacks

        manager.getWithRelationship(
            an_empty_traitsdata, two_refs, a_context, success_callback, error_callback
        )

        method.assert_called_once_with(
            an_empty_traitsdata,
            two_refs,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
            resultTraitSet=None,
        )

        success_callback.assert_called_once_with(0, two_different_refs)
        error_callback.assert_called_once_with(1, a_batch_element_error)

        mock_manager_interface.mock.reset_mock()

        # Check optional resultTraitSet

        manager.getWithRelationship(
            an_empty_traitsdata,
            two_refs,
            a_context,
            success_callback,
            error_callback,
            resultTraitSet=an_entity_trait_set,
        )

        method.assert_called_once_with(
            an_empty_traitsdata,
            two_refs,
            a_context,
            a_host_session,
            success_callback,
            error_callback,
            resultTraitSet=an_entity_trait_set,
        )


class Test_Manager_getWithRelationships:
    def test_method_defined_in_python(self, method_introspector):
        assert method_introspector.is_defined_in_python(Manager.getWithRelationships)
        assert method_introspector.is_implemented_once(Manager, "getWithRelationships")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        a_different_ref,
        a_batch_element_error,
        an_empty_traitsdata,
        an_entity_trait_set,
        a_context,
        invoke_getWithRelationships_success_cb,
        invoke_getWithRelationships_error_cb,
    ):
        two_datas = [an_empty_traitsdata, an_empty_traitsdata]
        two_different_refs = [a_different_ref, a_different_ref]

        success_callback = mock.Mock()
        error_callback = mock.Mock()

        method = mock_manager_interface.mock.getWithRelationships

        def call_callbacks(*_args):
            invoke_getWithRelationships_success_cb(0, two_different_refs)
            invoke_getWithRelationships_error_cb(1, a_batch_element_error)

        method.side_effect = call_callbacks

        manager.getWithRelationships(two_datas, a_ref, a_context, success_callback, error_callback)

        method.assert_called_once_with(
            two_datas,
            a_ref,
            a_context,
            a_host_session,
            success_callback,
            error_callback,
            resultTraitSet=None,
        )

        success_callback.assert_called_once_with(0, two_different_refs)
        error_callback.assert_called_once_with(1, a_batch_element_error)

        mock_manager_interface.mock.reset_mock()

        # Check optional resultTraitSet

        manager.getWithRelationships(
            two_datas,
            a_ref,
            a_context,
            success_callback,
            error_callback,
            resultTraitSet=an_entity_trait_set,
        )

        method.assert_called_once_with(
            two_datas,
            a_ref,
            a_context,
            a_host_session,
            success_callback,
            error_callback,
            resultTraitSet=an_entity_trait_set,
        )


class Test_Manager_BatchElementErrorPolicyTag:
    def test_unique(self):
        assert (
            Manager.BatchElementErrorPolicyTag.kVariant
            is not Manager.BatchElementErrorPolicyTag.kException
        )


class Test_Manager_resolve_with_callback_signature:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.resolve)
        assert method_introspector.is_implemented_once(Manager, "resolve")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        a_traitsdata,
        a_batch_element_error,
        invoke_resolve_success_cb,
        invoke_resolve_error_cb,
    ):
        success_callback = mock.Mock()
        error_callback = mock.Mock()

        method = mock_manager_interface.mock.resolve

        def call_callbacks(*_args):
            invoke_resolve_success_cb(123, a_traitsdata)
            invoke_resolve_error_cb(456, a_batch_element_error)

        method.side_effect = call_callbacks

        manager.resolve(
            some_refs, an_entity_trait_set, a_context, success_callback, error_callback
        )

        method.assert_called_once_with(
            some_refs, an_entity_trait_set, a_context, a_host_session, mock.ANY, mock.ANY
        )

        success_callback.assert_called_once_with(123, a_traitsdata)
        error_callback.assert_called_once_with(456, a_batch_element_error)


batch_element_error_codes = [
    BatchElementError.ErrorCode.kUnknown,
    BatchElementError.ErrorCode.kInvalidEntityReference,
    BatchElementError.ErrorCode.kMalformedEntityReference,
    BatchElementError.ErrorCode.kEntityAccessError,
    BatchElementError.ErrorCode.kEntityResolutionError,
]

batch_element_exceptions = [
    UnknownBatchElementException,
    InvalidEntityReferenceBatchElementException,
    MalformedEntityReferenceBatchElementException,
    EntityAccessErrorBatchElementException,
    EntityResolutionErrorBatchElementException,
]

batch_element_error_code_exception_pairs = list(
    zip(batch_element_error_codes, batch_element_exceptions)
)


class Test_Manager_resolve_with_singular_default_overload:
    def test_when_success_then_single_TraitsData_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        an_entity_trait_set,
        a_context,
        a_traitsdata,
        invoke_resolve_success_cb,
    ):
        method = mock_manager_interface.mock.resolve

        def call_callbacks(*_args):
            invoke_resolve_success_cb(0, a_traitsdata)

        method.side_effect = call_callbacks

        actual_traitsdata = manager.resolve(a_ref, an_entity_trait_set, a_context)

        method.assert_called_once_with(
            [a_ref], an_entity_trait_set, a_context, a_host_session, mock.ANY, mock.ANY
        )

        assert actual_traitsdata is a_traitsdata

    @pytest.mark.parametrize(
        "error_code,expected_exception", batch_element_error_code_exception_pairs
    )
    def test_when_BatchElementError_then_appropriate_exception_raised(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        an_entity_trait_set,
        a_context,
        invoke_resolve_error_cb,
        error_code,
        expected_exception,
    ):
        method = mock_manager_interface.mock.resolve

        expected_index = 213
        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_resolve_error_cb(expected_index, batch_element_error)
            pytest.fail("Exception should have short-circuited this")

        method.side_effect = call_callbacks

        with pytest.raises(expected_exception, match=batch_element_error.message) as exc:
            manager.resolve(a_ref, an_entity_trait_set, a_context)

        method.assert_called_once_with(
            [a_ref], an_entity_trait_set, a_context, a_host_session, mock.ANY, mock.ANY
        )

        assert exc.value.index == expected_index
        assert exc.value.error == batch_element_error


class Test_Manager_resolve_with_singular_throwing_overload:
    def test_when_resolve_success_then_single_TraitsData_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        an_entity_trait_set,
        a_context,
        a_traitsdata,
        invoke_resolve_success_cb,
    ):
        method = mock_manager_interface.mock.resolve

        def call_callbacks(*_args):
            invoke_resolve_success_cb(0, a_traitsdata)

        method.side_effect = call_callbacks

        actual_traitsdata = manager.resolve(
            a_ref,
            an_entity_trait_set,
            a_context,
            Manager.BatchElementErrorPolicyTag.kException,
        )

        method.assert_called_once_with(
            [a_ref], an_entity_trait_set, a_context, a_host_session, mock.ANY, mock.ANY
        )

        assert actual_traitsdata is a_traitsdata

    @pytest.mark.parametrize(
        "error_code,expected_exception", batch_element_error_code_exception_pairs
    )
    def test_when_BatchElementError_then_appropriate_exception_raised(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        an_entity_trait_set,
        a_context,
        error_code,
        expected_exception,
        invoke_resolve_error_cb,
    ):
        method = mock_manager_interface.mock.resolve

        expected_index = 213
        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_resolve_error_cb(expected_index, batch_element_error)
            pytest.fail("Exception should have short-circuited this")

        method.side_effect = call_callbacks

        with pytest.raises(expected_exception, match=batch_element_error.message) as exc:
            manager.resolve(
                a_ref,
                an_entity_trait_set,
                a_context,
                Manager.BatchElementErrorPolicyTag.kException,
            )

        method.assert_called_once_with(
            [a_ref], an_entity_trait_set, a_context, a_host_session, mock.ANY, mock.ANY
        )

        assert exc.value.index == expected_index
        assert exc.value.error == batch_element_error


class Test_Manager_resolve_with_singular_variant_overload:
    def test_when_resolve_success_then_single_TraitsData_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        an_entity_trait_set,
        a_context,
        a_traitsdata,
        invoke_resolve_success_cb,
    ):
        method = mock_manager_interface.mock.resolve

        def call_callbacks(*_args):
            invoke_resolve_success_cb(0, a_traitsdata)

        method.side_effect = call_callbacks

        actual_traitsdata = manager.resolve(
            a_ref,
            an_entity_trait_set,
            a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        method.assert_called_once_with(
            [a_ref], an_entity_trait_set, a_context, a_host_session, mock.ANY, mock.ANY
        )

        assert actual_traitsdata is a_traitsdata

    @pytest.mark.parametrize("error_code", batch_element_error_codes)
    def test_when_BatchElementError_then_BatchElementError_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        an_entity_trait_set,
        a_context,
        error_code,
        invoke_resolve_error_cb,
    ):
        method = mock_manager_interface.mock.resolve

        expected_index = 213
        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_resolve_error_cb(expected_index, batch_element_error)

        method.side_effect = call_callbacks

        actual = manager.resolve(
            a_ref,
            an_entity_trait_set,
            a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        method.assert_called_once_with(
            [a_ref], an_entity_trait_set, a_context, a_host_session, mock.ANY, mock.ANY
        )

        assert actual == batch_element_error


class Test_Manager_resolve_with_batch_default_overload:
    def test_when_success_then_multiple_TraitsDatas_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        some_populated_traitsdatas,
        invoke_resolve_success_cb,
    ):
        method = mock_manager_interface.mock.resolve

        def call_callbacks(*_args):
            invoke_resolve_success_cb(0, some_populated_traitsdatas[0])
            invoke_resolve_success_cb(1, some_populated_traitsdatas[1])

        method.side_effect = call_callbacks

        actual_traitsdatas = manager.resolve(some_refs, an_entity_trait_set, a_context)

        method.assert_called_once_with(
            some_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert len(actual_traitsdatas) == 2
        assert actual_traitsdatas[0] is some_populated_traitsdatas[0]
        assert actual_traitsdatas[1] is some_populated_traitsdatas[1]

    def test_when_success_out_of_order_then_TraitsDatas_returned_in_order(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        some_populated_traitsdatas,
        invoke_resolve_success_cb,
    ):
        method = mock_manager_interface.mock.resolve

        def call_callbacks(*_args):
            invoke_resolve_success_cb(1, some_populated_traitsdatas[1])
            invoke_resolve_success_cb(0, some_populated_traitsdatas[0])

        method.side_effect = call_callbacks

        actual_traitsdatas = manager.resolve(some_refs, an_entity_trait_set, a_context)

        method.assert_called_once_with(
            some_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert len(actual_traitsdatas) == 2
        assert actual_traitsdatas[0] is some_populated_traitsdatas[0]
        assert actual_traitsdatas[1] is some_populated_traitsdatas[1]

    @pytest.mark.parametrize(
        "error_code,expected_exception", batch_element_error_code_exception_pairs
    )
    def test_when_BatchElementError_then_appropriate_exception_raised(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        error_code,
        a_traitsdata,
        expected_exception,
        invoke_resolve_success_cb,
        invoke_resolve_error_cb,
    ):
        method = mock_manager_interface.mock.resolve
        expected_index = 123

        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_resolve_success_cb(0, a_traitsdata)
            invoke_resolve_error_cb(expected_index, batch_element_error)
            pytest.fail("Exception should have short-circuited this")

        method.side_effect = call_callbacks

        with pytest.raises(expected_exception, match=batch_element_error.message) as exc:
            manager.resolve(some_refs, an_entity_trait_set, a_context)

        method.assert_called_once_with(
            some_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert exc.value.index == expected_index
        assert exc.value.error == batch_element_error


class Test_Manager_resolve_with_batch_throwing_overload:
    def test_when_success_then_multiple_TraitsDatas_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        some_populated_traitsdatas,
        invoke_resolve_success_cb,
    ):
        method = mock_manager_interface.mock.resolve

        def call_callbacks(*_args):
            invoke_resolve_success_cb(0, some_populated_traitsdatas[0])
            invoke_resolve_success_cb(1, some_populated_traitsdatas[1])

        method.side_effect = call_callbacks

        actual_traitsdatas = manager.resolve(
            some_refs,
            an_entity_trait_set,
            a_context,
            Manager.BatchElementErrorPolicyTag.kException,
        )

        method.assert_called_once_with(
            some_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert len(actual_traitsdatas) == 2
        assert actual_traitsdatas[0] is some_populated_traitsdatas[0]
        assert actual_traitsdatas[1] is some_populated_traitsdatas[1]

    def test_when_success_out_of_order_then_TraitsDatas_returned_in_order(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        some_populated_traitsdatas,
        invoke_resolve_success_cb,
    ):
        method = mock_manager_interface.mock.resolve

        def call_callbacks(*_args):
            # Success
            invoke_resolve_success_cb(1, some_populated_traitsdatas[1])
            invoke_resolve_success_cb(0, some_populated_traitsdatas[0])

        method.side_effect = call_callbacks

        actual_traitsdatas = manager.resolve(
            some_refs,
            an_entity_trait_set,
            a_context,
            Manager.BatchElementErrorPolicyTag.kException,
        )

        method.assert_called_once_with(
            some_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert len(actual_traitsdatas) == 2
        assert actual_traitsdatas[0] is some_populated_traitsdatas[0]
        assert actual_traitsdatas[1] is some_populated_traitsdatas[1]

    @pytest.mark.parametrize(
        "error_code,expected_exception", batch_element_error_code_exception_pairs
    )
    def test_when_BatchElementError_then_appropriate_exception_raised(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        error_code,
        a_traitsdata,
        expected_exception,
        invoke_resolve_success_cb,
        invoke_resolve_error_cb,
    ):
        method = mock_manager_interface.mock.resolve
        expected_index = 123

        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_resolve_success_cb(0, a_traitsdata)
            invoke_resolve_error_cb(expected_index, batch_element_error)
            pytest.fail("Exception should have short-circuited this")

        method.side_effect = call_callbacks

        with pytest.raises(expected_exception, match=batch_element_error.message) as exc:
            manager.resolve(
                some_refs,
                an_entity_trait_set,
                a_context,
                Manager.BatchElementErrorPolicyTag.kException,
            )

        method.assert_called_once_with(
            some_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert exc.value.index == expected_index
        assert exc.value.error == batch_element_error


class Test_Manager_resolve_with_batch_variant_overload:
    @pytest.mark.parametrize("error_code", batch_element_error_codes)
    def test_when_mixed_output_then_returned_list_contains_output(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        a_traitsdata,
        error_code,
        invoke_resolve_success_cb,
        invoke_resolve_error_cb,
    ):
        method = mock_manager_interface.mock.resolve
        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_resolve_success_cb(0, a_traitsdata)
            invoke_resolve_error_cb(1, batch_element_error)

        method.side_effect = call_callbacks

        actual_traitsdata_and_error = manager.resolve(
            some_refs,
            an_entity_trait_set,
            a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        method.assert_called_once_with(
            some_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert len(actual_traitsdata_and_error) == 2
        assert actual_traitsdata_and_error[0] is a_traitsdata
        assert actual_traitsdata_and_error[1] == batch_element_error

    def test_when_mixed_output_out_of_order_then_output_returned_in_order(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        an_entity_trait_set,
        a_context,
        invoke_resolve_success_cb,
        invoke_resolve_error_cb,
    ):
        method = mock_manager_interface.mock.resolve

        entity_refs = [a_ref] * 4

        batch_element_error0 = BatchElementError(
            BatchElementError.ErrorCode.kEntityResolutionError, "0 some string ✨"
        )
        traitsdata1 = TraitsData({"trait1"})
        batch_element_error2 = BatchElementError(
            BatchElementError.ErrorCode.kEntityResolutionError, "0 some string ✨"
        )
        traitsdata3 = TraitsData({"trait3"})

        def call_callbacks(*_args):
            invoke_resolve_success_cb(1, traitsdata1)
            invoke_resolve_error_cb(0, batch_element_error0)
            invoke_resolve_success_cb(3, traitsdata3)
            invoke_resolve_error_cb(2, batch_element_error2)

        method.side_effect = call_callbacks

        actual_traitsdata_and_error = manager.resolve(
            entity_refs,
            an_entity_trait_set,
            a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        method.assert_called_once_with(
            entity_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert len(actual_traitsdata_and_error) == 4
        assert actual_traitsdata_and_error[0] == batch_element_error0
        assert actual_traitsdata_and_error[1] is traitsdata1
        assert actual_traitsdata_and_error[2] == batch_element_error2
        assert actual_traitsdata_and_error[3] is traitsdata3


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

        actual = manager.managementPolicy(some_entity_trait_sets, a_context)

        assert actual == expected
        method.assert_called_once_with(some_entity_trait_sets, a_context, a_host_session)


class Test_Manager_preflight_callback_signature:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.preflight)
        assert method_introspector.is_implemented_once(Manager, "preflight")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        a_batch_element_error,
        invoke_preflight_success_cb,
        invoke_preflight_error_cb,
    ):
        success_callback = mock.Mock()
        error_callback = mock.Mock()

        method = mock_manager_interface.mock.preflight

        def call_callbacks(*_args):
            input_refs = method.call_args[0][0]
            invoke_preflight_success_cb(123, input_refs[0])
            invoke_preflight_error_cb(456, a_batch_element_error)

        method.side_effect = call_callbacks

        manager.preflight(
            some_refs, an_entity_trait_set, a_context, success_callback, error_callback
        )

        method.assert_called_once_with(
            some_refs, an_entity_trait_set, a_context, a_host_session, mock.ANY, mock.ANY
        )

        success_callback.assert_called_once_with(123, some_refs[0])
        error_callback.assert_called_once_with(456, a_batch_element_error)


class Test_Manager_preflight_with_singular_default_overload:
    def test_when_success_then_single_EntityReference_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        an_entity_trait_set,
        a_context,
        a_different_ref,
        invoke_preflight_success_cb,
    ):
        method = mock_manager_interface.mock.preflight

        def call_callbacks(*_args):
            invoke_preflight_success_cb(0, a_different_ref)

        method.side_effect = call_callbacks

        actual_ref = manager.preflight(a_ref, an_entity_trait_set, a_context)

        method.assert_called_once_with(
            [a_ref], an_entity_trait_set, a_context, a_host_session, mock.ANY, mock.ANY
        )

        assert actual_ref == a_different_ref

    @pytest.mark.parametrize(
        "error_code,expected_exception", batch_element_error_code_exception_pairs
    )
    def test_when_BatchElementError_then_appropriate_exception_raised(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        an_entity_trait_set,
        a_context,
        error_code,
        expected_exception,
        invoke_preflight_error_cb,
    ):
        method = mock_manager_interface.mock.preflight

        expected_index = 213
        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_preflight_error_cb(expected_index, batch_element_error)
            pytest.fail("Exception should have short-circuited this")

        method.side_effect = call_callbacks

        with pytest.raises(expected_exception, match=batch_element_error.message) as exc:
            manager.preflight(a_ref, an_entity_trait_set, a_context)

        method.assert_called_once_with(
            [a_ref], an_entity_trait_set, a_context, a_host_session, mock.ANY, mock.ANY
        )

        assert exc.value.index == expected_index
        assert exc.value.error == batch_element_error


class Test_Manager_preflight_with_singular_throwing_overload:
    def test_when_preflight_success_then_single_EntityReference_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        an_entity_trait_set,
        a_context,
        a_different_ref,
        invoke_preflight_success_cb,
    ):
        method = mock_manager_interface.mock.preflight

        def call_callbacks(*_args):
            invoke_preflight_success_cb(0, a_different_ref)

        method.side_effect = call_callbacks

        actual_ref = manager.preflight(
            a_ref,
            an_entity_trait_set,
            a_context,
            Manager.BatchElementErrorPolicyTag.kException,
        )

        method.assert_called_once_with(
            [a_ref], an_entity_trait_set, a_context, a_host_session, mock.ANY, mock.ANY
        )

        assert actual_ref == a_different_ref

    @pytest.mark.parametrize(
        "error_code,expected_exception", batch_element_error_code_exception_pairs
    )
    def test_when_BatchElementError_then_appropriate_exception_raised(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        an_entity_trait_set,
        a_context,
        error_code,
        expected_exception,
        invoke_preflight_error_cb,
    ):
        method = mock_manager_interface.mock.preflight

        expected_index = 213
        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            # Success
            invoke_preflight_error_cb(expected_index, batch_element_error)
            pytest.fail("Exception should have short-circuited this")

        method.side_effect = call_callbacks

        with pytest.raises(expected_exception, match=batch_element_error.message) as exc:
            manager.preflight(
                a_ref,
                an_entity_trait_set,
                a_context,
                Manager.BatchElementErrorPolicyTag.kException,
            )

        method.assert_called_once_with(
            [a_ref], an_entity_trait_set, a_context, a_host_session, mock.ANY, mock.ANY
        )

        assert exc.value.index == expected_index
        assert exc.value.error == batch_element_error


class Test_Manager_preflight_with_singular_variant_overload:
    def test_when_preflight_success_then_single_EntityReference_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        an_entity_trait_set,
        a_context,
        a_different_ref,
        invoke_preflight_success_cb,
    ):
        method = mock_manager_interface.mock.preflight

        def call_callbacks(*_args):
            invoke_preflight_success_cb(0, a_different_ref)

        method.side_effect = call_callbacks

        actual_ref = manager.preflight(
            a_ref,
            an_entity_trait_set,
            a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        method.assert_called_once_with(
            [a_ref], an_entity_trait_set, a_context, a_host_session, mock.ANY, mock.ANY
        )

        assert actual_ref == a_different_ref

    @pytest.mark.parametrize("error_code", batch_element_error_codes)
    def test_when_BatchElementError_then_BatchElementError_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        an_entity_trait_set,
        a_context,
        error_code,
        invoke_preflight_error_cb,
    ):
        method = mock_manager_interface.mock.preflight

        expected_index = 213
        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_preflight_error_cb(expected_index, batch_element_error)

        method.side_effect = call_callbacks

        actual = manager.preflight(
            a_ref,
            an_entity_trait_set,
            a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        method.assert_called_once_with(
            [a_ref], an_entity_trait_set, a_context, a_host_session, mock.ANY, mock.ANY
        )

        assert actual == batch_element_error


class Test_Manager_preflight_with_batch_default_overload:
    def test_when_success_then_multiple_EntityReferences_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        some_different_refs,
        invoke_preflight_success_cb,
    ):
        method = mock_manager_interface.mock.preflight

        def call_callbacks(*_args):
            invoke_preflight_success_cb(0, some_different_refs[0])
            invoke_preflight_success_cb(1, some_different_refs[1])

        method.side_effect = call_callbacks

        actual_refs = manager.preflight(some_refs, an_entity_trait_set, a_context)

        method.assert_called_once_with(
            some_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert actual_refs == some_different_refs

    def test_when_success_out_of_order_then_EntityReferences_returned_in_order(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        some_different_refs,
        invoke_preflight_success_cb,
    ):
        method = mock_manager_interface.mock.preflight

        def call_callbacks(*_args):
            invoke_preflight_success_cb(1, some_different_refs[1])
            invoke_preflight_success_cb(0, some_different_refs[0])

        method.side_effect = call_callbacks

        actual_refs = manager.preflight(some_refs, an_entity_trait_set, a_context)

        method.assert_called_once_with(
            some_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert actual_refs == some_different_refs

    @pytest.mark.parametrize(
        "error_code,expected_exception", batch_element_error_code_exception_pairs
    )
    def test_when_BatchElementError_then_appropriate_exception_raised(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        error_code,
        a_different_ref,
        expected_exception,
        invoke_preflight_success_cb,
        invoke_preflight_error_cb,
    ):
        method = mock_manager_interface.mock.preflight
        expected_index = 123

        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_preflight_success_cb(0, a_different_ref)
            invoke_preflight_error_cb(expected_index, batch_element_error)
            pytest.fail("Exception should have short-circuited this")

        method.side_effect = call_callbacks

        with pytest.raises(expected_exception, match=batch_element_error.message) as exc:
            manager.preflight(some_refs, an_entity_trait_set, a_context)

        method.assert_called_once_with(
            some_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert exc.value.index == expected_index
        assert exc.value.error == batch_element_error


class Test_Manager_preflight_with_batch_throwing_overload:
    def test_when_success_then_multiple_EntityReferences_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        some_different_refs,
        invoke_preflight_success_cb,
    ):
        method = mock_manager_interface.mock.preflight

        def call_callbacks(*_args):
            invoke_preflight_success_cb(0, some_different_refs[0])
            invoke_preflight_success_cb(1, some_different_refs[1])

        method.side_effect = call_callbacks

        actual_refs = manager.preflight(
            some_refs,
            an_entity_trait_set,
            a_context,
            Manager.BatchElementErrorPolicyTag.kException,
        )

        method.assert_called_once_with(
            some_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert actual_refs == some_different_refs

    def test_when_success_out_of_order_then_EntityReferences_returned_in_order(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        some_different_refs,
        invoke_preflight_success_cb,
    ):
        method = mock_manager_interface.mock.preflight

        def call_callbacks(*_args):
            invoke_preflight_success_cb(1, some_different_refs[1])
            invoke_preflight_success_cb(0, some_different_refs[0])

        method.side_effect = call_callbacks

        actual_refs = manager.preflight(
            some_refs,
            an_entity_trait_set,
            a_context,
            Manager.BatchElementErrorPolicyTag.kException,
        )

        method.assert_called_once_with(
            some_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert actual_refs == some_different_refs

    @pytest.mark.parametrize(
        "error_code,expected_exception", batch_element_error_code_exception_pairs
    )
    def test_when_BatchElementError_then_appropriate_exception_raised(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        error_code,
        a_different_ref,
        expected_exception,
        invoke_preflight_success_cb,
        invoke_preflight_error_cb,
    ):
        method = mock_manager_interface.mock.preflight
        expected_index = 123

        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_preflight_success_cb(0, a_different_ref)
            invoke_preflight_error_cb(expected_index, batch_element_error)
            pytest.fail("Exception should have short-circuited this")

        method.side_effect = call_callbacks

        with pytest.raises(expected_exception, match=batch_element_error.message) as exc:
            manager.preflight(
                some_refs,
                an_entity_trait_set,
                a_context,
                Manager.BatchElementErrorPolicyTag.kException,
            )

        method.assert_called_once_with(
            some_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert exc.value.index == expected_index
        assert exc.value.error == batch_element_error


class Test_Manager_preflight_with_batch_variant_overload:
    @pytest.mark.parametrize("error_code", batch_element_error_codes)
    def test_when_mixed_output_then_returned_list_contains_output(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        an_entity_trait_set,
        a_context,
        a_different_ref,
        error_code,
        invoke_preflight_success_cb,
        invoke_preflight_error_cb,
    ):
        method = mock_manager_interface.mock.preflight
        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_preflight_success_cb(0, a_different_ref)
            invoke_preflight_error_cb(1, batch_element_error)

        method.side_effect = call_callbacks

        actual_ref_or_error = manager.preflight(
            some_refs,
            an_entity_trait_set,
            a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        method.assert_called_once_with(
            some_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert len(actual_ref_or_error) == 2
        assert actual_ref_or_error[0] == a_different_ref
        assert actual_ref_or_error[1] == batch_element_error

    def test_when_mixed_output_out_of_order_then_output_returned_in_order(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        an_entity_trait_set,
        a_context,
        invoke_preflight_success_cb,
        invoke_preflight_error_cb,
    ):
        method = mock_manager_interface.mock.preflight

        entity_refs = [a_ref] * 4

        batch_element_error0 = BatchElementError(
            BatchElementError.ErrorCode.kEntityResolutionError, "0 some string ✨"
        )
        entity_ref1 = EntityReference("ref1")
        batch_element_error2 = BatchElementError(
            BatchElementError.ErrorCode.kEntityResolutionError, "2 some string ✨"
        )
        entity_ref3 = EntityReference("ref3")

        def call_callbacks(*_args):
            invoke_preflight_success_cb(1, entity_ref1)
            invoke_preflight_error_cb(0, batch_element_error0)
            invoke_preflight_success_cb(3, entity_ref3)
            invoke_preflight_error_cb(2, batch_element_error2)

        method.side_effect = call_callbacks

        actual_ref_or_error = manager.preflight(
            entity_refs,
            an_entity_trait_set,
            a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        method.assert_called_once_with(
            entity_refs,
            an_entity_trait_set,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert len(actual_ref_or_error) == 4
        assert actual_ref_or_error[0] == batch_element_error0
        assert actual_ref_or_error[1] == entity_ref1
        assert actual_ref_or_error[2] == batch_element_error2
        assert actual_ref_or_error[3] == entity_ref3


class Test_Manager_register_callback_overload:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.register)
        assert method_introspector.is_implemented_once(Manager, "register")

    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        a_context,
        some_entity_traitsdatas,
        a_batch_element_error,
        invoke_register_success_cb,
        invoke_register_error_cb,
    ):
        success_callback = mock.Mock()
        error_callback = mock.Mock()

        method = mock_manager_interface.mock.register

        def call_callbacks(*_args):
            input_refs = method.call_args[0][0]
            invoke_register_success_cb(123, input_refs[0])
            invoke_register_error_cb(456, a_batch_element_error)

        method.side_effect = call_callbacks

        manager.register(
            some_refs, some_entity_traitsdatas, a_context, success_callback, error_callback
        )

        method.assert_called_once_with(
            some_refs, some_entity_traitsdatas, a_context, a_host_session, mock.ANY, mock.ANY
        )

        success_callback.assert_called_once_with(123, some_refs[0])
        error_callback.assert_called_once_with(456, a_batch_element_error)

    def test_when_called_with_mixed_array_lengths_then_IndexError_is_raised(
        self, manager, some_refs, a_traitsdata, a_context
    ):
        datas = [a_traitsdata for _ in some_refs]

        with pytest.raises(IndexError):
            manager.register(some_refs[1:], datas, a_context, mock.Mock(), mock.Mock())

        with pytest.raises(IndexError):
            manager.register(some_refs, datas[1:], a_context, mock.Mock(), mock.Mock())

    def test_when_called_with_varying_trait_sets_then_ValueError_is_raised(
        self, manager, some_refs, a_context
    ):
        datas = [TraitsData({f"trait{i}", "🦀"}) for i in range(len(some_refs))]

        with pytest.raises(ValueError):
            manager.register(some_refs, datas, a_context, mock.Mock(), mock.Mock())

    def test_when_called_with_None_data_then_TypeError_is_raised(
        self, manager, some_refs, a_context, a_traitsdata
    ):
        with pytest.raises(TypeError):
            manager.register(some_refs, [a_traitsdata, None], a_context, mock.Mock(), mock.Mock())


class Test_Manager_register_with_singular_default_overload:
    def test_when_success_then_single_EntityReference_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        a_context,
        a_different_ref,
        a_traitsdata,
        invoke_register_success_cb,
    ):
        method = mock_manager_interface.mock.register

        def call_callbacks(*_args):
            invoke_register_success_cb(0, a_different_ref)

        method.side_effect = call_callbacks

        actual_ref = manager.register(a_ref, a_traitsdata, a_context)

        method.assert_called_once_with(
            [a_ref],
            [a_traitsdata],
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert actual_ref == a_different_ref

    @pytest.mark.parametrize(
        "error_code,expected_exception", batch_element_error_code_exception_pairs
    )
    def test_when_BatchElementError_then_appropriate_exception_raised(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        a_context,
        error_code,
        expected_exception,
        a_traitsdata,
        invoke_register_error_cb,
    ):
        method = mock_manager_interface.mock.register

        expected_index = 213
        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_register_error_cb(expected_index, batch_element_error)
            pytest.fail("Exception should have short-circuited this")

        method.side_effect = call_callbacks

        with pytest.raises(expected_exception, match=batch_element_error.message) as exc:
            manager.register(a_ref, a_traitsdata, a_context)

        method.assert_called_once_with(
            [a_ref],
            [a_traitsdata],
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert exc.value.index == expected_index
        assert exc.value.error == batch_element_error


class Test_Manager_register_with_singular_throwing_overload:
    def test_when_register_success_then_single_EntityReference_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        a_context,
        a_different_ref,
        a_traitsdata,
        invoke_register_success_cb,
    ):
        method = mock_manager_interface.mock.register

        def call_callbacks(*_args):
            invoke_register_success_cb(0, a_different_ref)

        method.side_effect = call_callbacks

        actual_ref = manager.register(
            a_ref,
            a_traitsdata,
            a_context,
            Manager.BatchElementErrorPolicyTag.kException,
        )

        method.assert_called_once_with(
            [a_ref],
            [a_traitsdata],
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert actual_ref == a_different_ref

    @pytest.mark.parametrize(
        "error_code,expected_exception", batch_element_error_code_exception_pairs
    )
    def test_when_BatchElementError_then_appropriate_exception_raised(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        a_context,
        error_code,
        expected_exception,
        a_traitsdata,
        invoke_register_error_cb,
    ):
        method = mock_manager_interface.mock.register

        expected_index = 213
        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_register_error_cb(expected_index, batch_element_error)
            pytest.fail("Exception should have short-circuited this")

        method.side_effect = call_callbacks

        with pytest.raises(expected_exception, match=batch_element_error.message) as exc:
            manager.register(
                a_ref,
                a_traitsdata,
                a_context,
                Manager.BatchElementErrorPolicyTag.kException,
            )

        method.assert_called_once_with(
            [a_ref],
            [a_traitsdata],
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert exc.value.index == expected_index
        assert exc.value.error == batch_element_error


class Test_Manager_register_with_singular_variant_overload:
    def test_when_register_success_then_single_EntityReference_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        a_context,
        a_different_ref,
        a_traitsdata,
        invoke_register_success_cb,
    ):
        method = mock_manager_interface.mock.register

        def call_callbacks(*_args):
            invoke_register_success_cb(0, a_different_ref)

        method.side_effect = call_callbacks

        actual_ref = manager.register(
            a_ref,
            a_traitsdata,
            a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        method.assert_called_once_with(
            [a_ref],
            [a_traitsdata],
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert actual_ref == a_different_ref

    @pytest.mark.parametrize("error_code", batch_element_error_codes)
    def test_when_BatchElementError_then_BatchElementError_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        a_context,
        error_code,
        a_traitsdata,
        invoke_register_error_cb,
    ):
        method = mock_manager_interface.mock.register

        expected_index = 213
        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_register_error_cb(expected_index, batch_element_error)

        method.side_effect = call_callbacks

        actual = manager.register(
            a_ref,
            a_traitsdata,
            a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        method.assert_called_once_with(
            [a_ref],
            [a_traitsdata],
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert actual == batch_element_error


class Test_Manager_register_with_batch_default_overload:
    def test_when_success_then_multiple_EntityReferences_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        a_context,
        some_different_refs,
        some_entity_traitsdatas,
        invoke_register_success_cb,
    ):
        method = mock_manager_interface.mock.register

        def call_callbacks(*_args):
            invoke_register_success_cb(0, some_different_refs[0])
            invoke_register_success_cb(1, some_different_refs[1])

        method.side_effect = call_callbacks

        actual_refs = manager.register(some_refs, some_entity_traitsdatas, a_context)

        method.assert_called_once_with(
            some_refs,
            some_entity_traitsdatas,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert actual_refs == some_different_refs

    def test_when_success_out_of_order_then_EntityReferences_returned_in_order(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        a_context,
        some_different_refs,
        some_entity_traitsdatas,
        invoke_register_success_cb,
    ):
        method = mock_manager_interface.mock.register

        def call_callbacks(*_args):
            invoke_register_success_cb(1, some_different_refs[1])
            invoke_register_success_cb(0, some_different_refs[0])

        method.side_effect = call_callbacks

        actual_refs = manager.register(some_refs, some_entity_traitsdatas, a_context)

        method.assert_called_once_with(
            some_refs,
            some_entity_traitsdatas,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert actual_refs == some_different_refs

    @pytest.mark.parametrize(
        "error_code,expected_exception", batch_element_error_code_exception_pairs
    )
    def test_when_BatchElementError_then_appropriate_exception_raised(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        some_entity_traitsdatas,
        a_context,
        error_code,
        a_different_ref,
        expected_exception,
        invoke_register_success_cb,
        invoke_register_error_cb,
    ):
        method = mock_manager_interface.mock.register
        expected_index = 123

        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_register_success_cb(0, a_different_ref)
            invoke_register_error_cb(expected_index, batch_element_error)
            pytest.fail("Exception should have short-circuited this")

        method.side_effect = call_callbacks

        with pytest.raises(expected_exception, match=batch_element_error.message) as exc:
            manager.register(some_refs, some_entity_traitsdatas, a_context)

        method.assert_called_once_with(
            some_refs,
            some_entity_traitsdatas,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert exc.value.index == expected_index
        assert exc.value.error == batch_element_error


class Test_Manager_register_with_batch_throwing_overload:
    def test_when_success_then_multiple_EntityReferences_returned(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        some_entity_traitsdatas,
        a_context,
        some_different_refs,
        invoke_register_success_cb,
    ):
        method = mock_manager_interface.mock.register

        def call_callbacks(*_args):
            invoke_register_success_cb(0, some_different_refs[0])
            invoke_register_success_cb(1, some_different_refs[1])

        method.side_effect = call_callbacks

        actual_refs = manager.register(
            some_refs,
            some_entity_traitsdatas,
            a_context,
            Manager.BatchElementErrorPolicyTag.kException,
        )

        method.assert_called_once_with(
            some_refs,
            some_entity_traitsdatas,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert actual_refs == some_different_refs

    def test_when_success_out_of_order_then_EntityReferences_returned_in_order(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        some_entity_traitsdatas,
        a_context,
        some_different_refs,
        invoke_register_success_cb,
    ):
        method = mock_manager_interface.mock.register

        def call_callbacks(*_args):
            invoke_register_success_cb(1, some_different_refs[1])
            invoke_register_success_cb(0, some_different_refs[0])

        method.side_effect = call_callbacks

        actual_refs = manager.register(
            some_refs,
            some_entity_traitsdatas,
            a_context,
            Manager.BatchElementErrorPolicyTag.kException,
        )

        method.assert_called_once_with(
            some_refs,
            some_entity_traitsdatas,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert actual_refs == some_different_refs

    @pytest.mark.parametrize(
        "error_code,expected_exception", batch_element_error_code_exception_pairs
    )
    def test_when_BatchElementError_then_appropriate_exception_raised(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        some_entity_traitsdatas,
        a_context,
        error_code,
        a_different_ref,
        expected_exception,
        invoke_register_success_cb,
        invoke_register_error_cb,
    ):
        method = mock_manager_interface.mock.register
        expected_index = 123

        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_register_success_cb(0, a_different_ref)
            invoke_register_error_cb(expected_index, batch_element_error)

            pytest.fail("Exception should have short-circuited this")

        method.side_effect = call_callbacks

        with pytest.raises(expected_exception, match=batch_element_error.message) as exc:
            manager.register(
                some_refs,
                some_entity_traitsdatas,
                a_context,
                Manager.BatchElementErrorPolicyTag.kException,
            )

        method.assert_called_once_with(
            some_refs,
            some_entity_traitsdatas,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert exc.value.index == expected_index
        assert exc.value.error == batch_element_error


class Test_Manager_register_with_batch_variant_overload:
    @pytest.mark.parametrize("error_code", batch_element_error_codes)
    def test_when_mixed_output_then_returned_list_contains_output(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        some_refs,
        some_entity_traitsdatas,
        a_context,
        a_different_ref,
        error_code,
        invoke_register_success_cb,
        invoke_register_error_cb,
    ):
        method = mock_manager_interface.mock.register
        batch_element_error = BatchElementError(error_code, "some string ✨")

        def call_callbacks(*_args):
            invoke_register_success_cb(0, a_different_ref)
            invoke_register_error_cb(1, batch_element_error)

        method.side_effect = call_callbacks

        actual_ref_or_error = manager.register(
            some_refs,
            some_entity_traitsdatas,
            a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        method.assert_called_once_with(
            some_refs,
            some_entity_traitsdatas,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert len(actual_ref_or_error) == 2
        assert actual_ref_or_error[0] == a_different_ref
        assert actual_ref_or_error[1] == batch_element_error

    def test_when_mixed_output_out_of_order_then_output_returned_in_order(
        self,
        manager,
        mock_manager_interface,
        a_host_session,
        a_ref,
        a_traitsdata,
        a_context,
        invoke_register_success_cb,
        invoke_register_error_cb,
    ):
        method = mock_manager_interface.mock.register

        entity_refs = [a_ref] * 4
        entity_traitsdatas = [a_traitsdata] * 4

        batch_element_error0 = BatchElementError(
            BatchElementError.ErrorCode.kEntityResolutionError, "0 some string ✨"
        )
        entity_ref1 = EntityReference("ref1")
        batch_element_error2 = BatchElementError(
            BatchElementError.ErrorCode.kEntityResolutionError, "2 some string ✨"
        )
        entity_ref3 = EntityReference("ref3")

        def call_callbacks(*_args):
            invoke_register_success_cb(1, entity_ref1)
            invoke_register_error_cb(0, batch_element_error0)
            invoke_register_success_cb(3, entity_ref3)
            invoke_register_error_cb(2, batch_element_error2)

        method.side_effect = call_callbacks

        actual_ref_or_error = manager.register(
            entity_refs,
            entity_traitsdatas,
            a_context,
            Manager.BatchElementErrorPolicyTag.kVariant,
        )

        method.assert_called_once_with(
            entity_refs,
            entity_traitsdatas,
            a_context,
            a_host_session,
            mock.ANY,
            mock.ANY,
        )

        assert len(actual_ref_or_error) == 4
        assert actual_ref_or_error[0] == batch_element_error0
        assert actual_ref_or_error[1] == entity_ref1
        assert actual_ref_or_error[2] == batch_element_error2
        assert actual_ref_or_error[3] == entity_ref3


class Test_Manager_createContext:
    def test_method_defined_in_cpp(self, method_introspector):
        assert not method_introspector.is_defined_in_python(Manager.createContext)
        assert method_introspector.is_implemented_once(Manager, "createContext")

    def test_context_is_created_with_expected_properties(
        self, manager, mock_manager_interface, a_host_session
    ):
        state_a = managerApi.ManagerStateBase()
        mock_manager_interface.mock.createState.return_value = state_a

        context_a = manager.createContext()

        assert context_a.access == Context.Access.kUnknown
        assert context_a.retention == Context.Retention.kTransient
        assert context_a.managerState is state_a
        assert isinstance(context_a.locale, TraitsData)
        assert context_a.locale.traitSet() == set()
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
        context_a.access = Context.Access.kWrite
        context_a.retention = Context.Retention.kSession
        context_a.locale = TraitsData()
        mock_manager_interface.mock.reset_mock()

        state_b = managerApi.ManagerStateBase()
        mock_manager_interface.mock.createChildState.return_value = state_b

        context_b = manager.createChildContext(context_a)

        assert context_b is not context_a
        assert context_b.managerState is state_b
        assert context_b.access == context_a.access
        assert context_b.retention == context_a.retention
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
        context_a.access = Context.Access.kWrite
        context_a.retention = Context.Retention.kSession
        context_a.locale = original_locale

        context_b = manager.createChildContext(context_a)

        assert context_b.locale == context_a.locale
        original_locale.setTraitProperty("a", "v", 2)
        assert context_b.locale != context_a.locale

    def test_when_called_with_parent_with_no_managerState_then_createChildState_is_not_called(
        self, manager, mock_manager_interface
    ):
        context_a = Context()
        context_a.access = Context.Access.kWrite
        context_a.retention = Context.Retention.kSession
        context_a.locale = TraitsData()
        context_b = manager.createChildContext(context_a)

        assert context_b.access == context_a.access
        assert context_b.retention == context_a.retention
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
def an_empty_traitsdata():
    return TraitsData(set())


@pytest.fixture
def some_entity_traitsdatas():
    first = TraitsData({"a_trait"})
    second = TraitsData({"a_trait"})
    first.setTraitProperty("a_trait", "a_prop", 123)
    second.setTraitProperty("a_trait", "a_prop", 456)
    return [first, second]


@pytest.fixture
def some_populated_traitsdatas():
    return [TraitsData(set("trait1")), TraitsData(set("trait2"))]


@pytest.fixture
def a_traitsdata():
    return TraitsData(set())


@pytest.fixture
def a_batch_element_error():
    return BatchElementError(BatchElementError.ErrorCode.kUnknown, "some message")


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
def some_refs(manager):
    return [manager.createEntityReference("asset://c"), manager.createEntityReference("asset://d")]


@pytest.fixture
def some_different_refs(manager):
    return [manager.createEntityReference("asset://e"), manager.createEntityReference("asset://f")]


@pytest.fixture
def invoke_getWithRelationship_success_cb(mock_manager_interface):
    def invoke(idx, entityReferences):
        callback = mock_manager_interface.mock.getWithRelationship.call_args[0][4]
        callback(idx, entityReferences)

    return invoke


@pytest.fixture
def invoke_getWithRelationship_error_cb(mock_manager_interface):
    def invoke(idx, batch_element_error):
        callback = mock_manager_interface.mock.getWithRelationship.call_args[0][5]
        callback(idx, batch_element_error)

    return invoke


@pytest.fixture
def invoke_getWithRelationships_success_cb(mock_manager_interface):
    def invoke(idx, entityReferences):
        callback = mock_manager_interface.mock.getWithRelationships.call_args[0][4]
        callback(idx, entityReferences)

    return invoke


@pytest.fixture
def invoke_getWithRelationships_error_cb(mock_manager_interface):
    def invoke(idx, batch_element_error):
        callback = mock_manager_interface.mock.getWithRelationships.call_args[0][5]
        callback(idx, batch_element_error)

    return invoke


@pytest.fixture
def invoke_resolve_success_cb(mock_manager_interface):
    def invoke(idx, traits_data):
        callback = mock_manager_interface.mock.resolve.call_args[0][4]
        callback(idx, traits_data)

    return invoke


@pytest.fixture
def invoke_resolve_error_cb(mock_manager_interface):
    def invoke(idx, batch_element_error):
        callback = mock_manager_interface.mock.resolve.call_args[0][5]
        callback(idx, batch_element_error)

    return invoke


@pytest.fixture
def invoke_preflight_success_cb(mock_manager_interface):
    def invoke(idx, traits_data):
        callback = mock_manager_interface.mock.preflight.call_args[0][4]
        callback(idx, traits_data)

    return invoke


@pytest.fixture
def invoke_preflight_error_cb(mock_manager_interface):
    def invoke(idx, batch_element_error):
        callback = mock_manager_interface.mock.preflight.call_args[0][5]
        callback(idx, batch_element_error)

    return invoke


@pytest.fixture
def invoke_register_success_cb(mock_manager_interface):
    def invoke(idx, traits_data):
        callback = mock_manager_interface.mock.register.call_args[0][4]
        callback(idx, traits_data)

    return invoke


@pytest.fixture
def invoke_register_error_cb(mock_manager_interface):
    def invoke(idx, batch_element_error):
        callback = mock_manager_interface.mock.register.call_args[0][5]
        callback(idx, batch_element_error)

    return invoke
