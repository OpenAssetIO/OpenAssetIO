#
#   Copyright 2022 The Foundry Visionmongers Ltd
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
Tests for the Python code generator.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=too-few-public-methods
# pylint: disable=missing-class-docstring,missing-function-docstring

import inspect
import logging
import os
import sys

import pytest

from typing import Any, NamedTuple

from openassetio import SpecificationBase, Trait, TraitsData
from openassetio_codegen import datamodel, generate
from openassetio_codegen.generators import python as python_generator

#
# Tests: Packages and Structure
#
# These cases cover the structure of the generated packages, ensuring
# they contain the expected sub-modules, classes and their methods.
# Functional testing is covered later.
#


class Test_python_package_all:
    def test_package_is_grouped_under_python_subdirectory(self, generated_path):
        assert os.path.isdir(os.path.join(generated_path, "python"))

    def test_package_is_importable(self, extended_python_path):
        # pylint: disable=unused-import,import-error,unused-argument,import-outside-toplevel
        import openassetio_codegen_test_all

        del sys.modules["openassetio_codegen_test_all"]

    def test_package_docstring(self, module_all):
        assert (
            module_all.__doc__
            == """
Test classes to validate the integrity of the openassetio-codegen tool.
"""
        )


class Test_python_package_all_traits:
    def test_contains_declaration_namespaces(self, module_all):
        assert inspect.ismodule(module_all.traits.aNamespace)
        assert inspect.ismodule(module_all.traits.anotherNamespace)

    def test_aNamespace_docstring_contains_declaration_description(self, module_all):
        assert (
            module_all.traits.aNamespace.__doc__
            == """
Trait definitions in the 'aNamespace' namespace.

A Namespace
"""
        )

    def test_anotherNamespace_docstring_contains_declaration_description(self, module_all):
        assert (
            module_all.traits.anotherNamespace.__doc__
            == """
Trait definitions in the 'anotherNamespace' namespace.

Another Namespace
"""
        )

    def test_aNamespace_module_traits_are_suffixed_with_Trait(self, module_all):
        assert inspect.isclass(module_all.traits.aNamespace.NoPropertiesTrait)
        assert inspect.isclass(module_all.traits.aNamespace.NoPropertiesMultipleUsageTrait)
        assert inspect.isclass(module_all.traits.aNamespace.AllPropertiesTrait)

    def test_anotherNamespace_module_traits_are_suffixed_with_Trait(self, module_all):
        assert inspect.isclass(module_all.traits.anotherNamespace.NoPropertiesTrait)


class Test_python_package_all_traits_aNamespace_NoPropertiesTrait:
    def test_docstring_contains_description(self, module_all):
        assert (
            module_all.traits.aNamespace.NoPropertiesTrait.__doc__
            == """
    Another trait, this time with no properties.
    """
        )

    def test_kId_is_declaration_id(self, module_all):
        assert (
            module_all.traits.aNamespace.NoPropertiesTrait.kId
            == "openassetio-codegen-test-all:aNamespace.NoProperties"
        )


class Test_python_package_all_traits_aNamespace_NoPropertiesMultipleUsageTrait:
    def test_has_expected_docstring(self, module_all):
        assert (
            module_all.traits.aNamespace.NoPropertiesMultipleUsageTrait.__doc__
            == """
    Another trait, this time with multiple usage.
    Usage: entity, relationship
    """
        )

    def test_kId_is_declaration_id(self, module_all):
        assert (
            module_all.traits.aNamespace.NoPropertiesMultipleUsageTrait.kId
            == "openassetio-codegen-test-all:aNamespace.NoPropertiesMultipleUsage"
        )


class Test_python_package_all_traits_aNamespace_AllPropertiesTrait:
    def test_has_expected_docstring(self, module_all):
        assert (
            module_all.traits.aNamespace.AllPropertiesTrait.__doc__
            == """
    A trait with properties of all types.
    """
        )

    def test_kId_is_declaration_id(self, module_all):
        assert (
            module_all.traits.aNamespace.AllPropertiesTrait.kId
            == "openassetio-codegen-test-all:aNamespace.AllProperties"
        )

    @pytest.mark.parametrize("property_type", ["string", "int", "float", "bool", "dict"])
    def test_has_prefixed_property_getters_with_expected_docstring(
        self, module_all, property_type
    ):
        property_name = f"{property_type}Property"
        function_name = f"get{property_type.capitalize()}Property"
        function = getattr(module_all.traits.aNamespace.AllPropertiesTrait, function_name)

        assert inspect.isfunction(function)
        assert (
            function.__doc__
            == f"""
        Gets the value of the {property_name} property or the supplied default.

        A {property_type}-typed property.
        """
        )

    @pytest.mark.parametrize("property_type", ["string", "int", "float", "bool", "dict"])
    def test_has_prefixed_property_setters_with_expected_docstring(
        self, module_all, property_type
    ):
        property_name = f"{property_type}Property"
        function_name = f"set{property_type.capitalize()}Property"
        function = getattr(module_all.traits.aNamespace.AllPropertiesTrait, function_name)

        assert inspect.isfunction(function)
        assert (
            function.__doc__
            == f"""
        Sets the {property_name} property.

        A {property_type}-typed property.
        """
        )


class Test_python_package_all_specifications:
    def test_contains_declaration_namespaces(self, module_all):
        assert inspect.ismodule(module_all.specifications.test)

    def test_test_docstring_contains_declaration_description(self, module_all):
        assert (
            module_all.specifications.test.__doc__
            == """
Specification definitions in the 'test' namespace.

Test specifications.
"""
        )

    def test_test_module_specifications_are_suffixed_with_Specification(self, module_all):
        assert inspect.isclass(module_all.specifications.test.TwoLocalTraitsSpecification)
        assert inspect.isclass(module_all.specifications.test.OneExternalTraitSpecification)
        assert inspect.isclass(module_all.specifications.test.LocalAndExternalTraitSpecification)


class Test_python_package_all_specifications_test_TwoLocalTraitsSpecification:
    def test_docstring_contains_description(self, module_all):
        assert (
            module_all.specifications.test.TwoLocalTraitsSpecification.__doc__
            == """
    A specification with two traits.
    """
        )

    def test_trait_set_composes_target_trait_kIds(self, module_all):
        expected = {
            module_all.traits.aNamespace.NoPropertiesTrait.kId,
            module_all.traits.anotherNamespace.NoPropertiesTrait.kId,
        }
        assert module_all.specifications.test.TwoLocalTraitsSpecification.kTraitSet == expected

    def test_has_trait_getters_with_expected_docstring(self, module_all):

        trait_one = module_all.traits.aNamespace.NoPropertiesTrait
        trait_two = module_all.traits.anotherNamespace.NoPropertiesTrait

        assert inspect.isfunction(
            module_all.specifications.test.TwoLocalTraitsSpecification.aNamespaceNoPropertiesTrait
        )
        assert (
            module_all.specifications.test.TwoLocalTraitsSpecification.aNamespaceNoPropertiesTrait.__doc__
            == f"""
        Returns the view for the '{trait_one.kId}' trait wrapped around
        the data held in this instance.
        """
        )

        assert inspect.isfunction(
            module_all.specifications.test.TwoLocalTraitsSpecification.anotherNamespaceNoPropertiesTrait
        )
        assert (
            module_all.specifications.test.TwoLocalTraitsSpecification.anotherNamespaceNoPropertiesTrait.__doc__
            == f"""
        Returns the view for the '{trait_two.kId}' trait wrapped around
        the data held in this instance.
        """
        )


class Test_python_package_all_specifications_test_OneExternalTraitSpecification:
    def test_docstring_contains_description(self, module_all):
        assert (
            module_all.specifications.test.OneExternalTraitSpecification.__doc__
            == """
    A specification referencing traits in another package.
    """
        )

    def test_trait_set_composes_target_trait_kIds(self, module_all, module_traits_only):
        expected = {
            module_traits_only.traits.test.AnotherTrait.kId,
        }
        assert module_all.specifications.test.OneExternalTraitSpecification.kTraitSet == expected

    def test_has_trait_getters_with_expected_docstring(self, module_all, module_traits_only):
        trait = module_traits_only.traits.test.AnotherTrait

        assert inspect.isfunction(
            module_all.specifications.test.OneExternalTraitSpecification.anotherTrait
        )
        assert (
            module_all.specifications.test.OneExternalTraitSpecification.anotherTrait.__doc__
            == f"""
        Returns the view for the '{trait.kId}' trait wrapped around
        the data held in this instance.
        """
        )


class Test_python_package_all_specifications_test_LocalAndExternalTraitSpecification:
    def test_docstring_contains_description(self, module_all):
        assert (
            module_all.specifications.test.LocalAndExternalTraitSpecification.__doc__
            == """
    A specification referencing traits in this and another package.
    Usage: entity, managementPolicy
    """
        )

    def test_trait_set_composes_target_trait_kIds(self, module_all, module_traits_only):
        expected = {
            module_all.traits.aNamespace.NoPropertiesTrait.kId,
            module_traits_only.traits.aNamespace.NoPropertiesTrait.kId,
        }
        assert (
            module_all.specifications.test.LocalAndExternalTraitSpecification.kTraitSet == expected
        )

    def test_has_trait_getters_with_expected_docstring(self, module_all, module_traits_only):

        trait_one = module_all.traits.aNamespace.NoPropertiesTrait
        trait_two = module_traits_only.traits.aNamespace.NoPropertiesTrait

        assert inspect.isfunction(
            module_all.specifications.test.LocalAndExternalTraitSpecification.openassetioCodegenTestAllANamespaceNoPropertiesTrait
        )
        assert (
            module_all.specifications.test.LocalAndExternalTraitSpecification.openassetioCodegenTestAllANamespaceNoPropertiesTrait.__doc__
            == f"""
        Returns the view for the '{trait_one.kId}' trait wrapped around
        the data held in this instance.
        """
        )

        assert inspect.isfunction(
            module_all.specifications.test.LocalAndExternalTraitSpecification.openassetioCodegenTestTraitsOnlyANamespaceNoPropertiesTrait
        )
        assert (
            module_all.specifications.test.LocalAndExternalTraitSpecification.openassetioCodegenTestTraitsOnlyANamespaceNoPropertiesTrait.__doc__
            == f"""
        Returns the view for the '{trait_two.kId}' trait wrapped around
        the data held in this instance.
        """
        )


class Test_python_package_traits_only:
    def test_package_is_importable(self, extended_python_path):
        # pylint: disable=unused-import,import-error,unused-argument,import-outside-toplevel
        import openassetio_codegen_test_traits_only

        del sys.modules["openassetio_codegen_test_traits_only"]

    def test_no_specifications_module(self, module_traits_only):
        with pytest.raises(AttributeError):
            module_traits_only.specifications

    def test_traits_are_suffixed_with_Trait(self, module_traits_only):
        assert inspect.isclass(module_traits_only.traits.test.AnotherTrait)
        assert inspect.isclass(module_traits_only.traits.aNamespace.NoPropertiesTrait)


class Test_python_package_specifications_only:
    def test_package_is_importable(self, extended_python_path):
        # pylint: disable=unused-import,import-error,unused-argument,import-outside-toplevel
        import openassetio_codegen_test_specifications_only

        del sys.modules["openassetio_codegen_test_specifications_only"]

    def test_no_traits_module(self, module_specifications_only):
        with pytest.raises(AttributeError):
            module_traits_only.traits

    def test_specifications_are_suffixed_with_Specification(self, module_specifications_only):
        assert inspect.isclass(module_specifications_only.specifications.test.SomeSpecification)


#
# Tests: Functionality
#
# These cases cover the functionality of the auto-generated methods.
# They specifically target only one Trait and Specification that exhaust
# possible options rather than re-testing all generated permutations.
#


class Test_AllPropertiesTrait:
    def test_subclass_of_openassetio_Trait(self, all_properties_trait):
        assert issubclass(all_properties_trait, Trait)

    def test_traitId_is_composed_of_package_aNamespace_and_name(self, all_properties_trait):
        assert all_properties_trait.kId == "openassetio-codegen-test-all:aNamespace.AllProperties"


class PropertyTestValues(NamedTuple):
    name: str
    valid_value: Any
    invalid_value: Any


kAllPropertiesTrait_property_test_values = (
    PropertyTestValues("boolProperty", True, 123),
    PropertyTestValues("intProperty", 42, "🐁"),
    PropertyTestValues("floatProperty", 12.3, False),
    PropertyTestValues("stringProperty", "⛅ outside today", 12),
    # Re-instate once InfoDictionary is supported in TraitsData
    # See: https://github.com/OpenAssetIO/OpenAssetIO/issues/527
    # PropertyTestValues("dictProperty", {"a": 1, "b": "2", "c": False}, "Mouse"),
)


@pytest.mark.parametrize("property", kAllPropertiesTrait_property_test_values)
class Test_AllPropertiesTrait_getter:
    def test_when_property_is_set_then_returns_expected_value(
        self, all_properties_trait, an_all_properties_traitsData, property
    ):
        an_all_properties_traitsData.setTraitProperty(
            all_properties_trait.kId, property.name, property.valid_value
        )
        a_trait = all_properties_trait(an_all_properties_traitsData)
        getter = getattr(a_trait, f"get{property.name[0].upper()}{property.name[1:]}")

        assert getter() == property.valid_value

    def test_when_property_not_set_then_returns_None(
        self, all_properties_trait, an_all_properties_traitsData, property
    ):
        a_trait = all_properties_trait(an_all_properties_traitsData)
        getter = getattr(a_trait, f"get{property.name[0].upper()}{property.name[1:]}")

        assert getter() is None

    def test_when_property_not_set_and_default_given_then_returns_default(
        self, all_properties_trait, an_all_properties_traitsData, property
    ):
        a_trait = all_properties_trait(an_all_properties_traitsData)
        getter = getattr(a_trait, f"get{property.name[0].upper()}{property.name[1:]}")

        assert getter(defaultValue=property.valid_value) == property.valid_value

    def test_when_property_has_wrong_type_then_raises_TypeError(
        self, all_properties_trait, an_all_properties_traitsData, property
    ):
        an_all_properties_traitsData.setTraitProperty(
            all_properties_trait.kId, property.name, property.invalid_value
        )
        a_trait = all_properties_trait(an_all_properties_traitsData)
        getter = getattr(a_trait, f"get{property.name[0].upper()}{property.name[1:]}")

        with pytest.raises(TypeError) as err:
            assert getter()

        assert (
            str(err.value)
            == f"Invalid stored value type: '{type(property.invalid_value).__name__}' should be '{type(property.valid_value).__name__}'."
        )

    def test_when_property_has_wrong_type_and_default_given_then_returns_default(
        self, all_properties_trait, an_all_properties_traitsData, property
    ):
        an_all_properties_traitsData.setTraitProperty(
            all_properties_trait.kId, property.name, property.invalid_value
        )
        a_trait = all_properties_trait(an_all_properties_traitsData)
        getter = getattr(a_trait, f"get{property.name[0].upper()}{property.name[1:]}")

        assert getter(defaultValue=property.valid_value) == property.valid_value


@pytest.mark.parametrize("property", kAllPropertiesTrait_property_test_values)
class Test_AllPropertiesTrait_set:
    def test_when_set_then_trait_data_contains_value(
        self, all_properties_trait, an_all_properties_traitsData, property
    ):
        a_trait = all_properties_trait(an_all_properties_traitsData)
        setter = getattr(a_trait, f"set{property.name[0].upper()}{property.name[1:]}")

        setter(property.valid_value)

        actual = an_all_properties_traitsData.getTraitProperty(
            all_properties_trait.kId, property.name
        )
        assert actual == property.valid_value

    def test_when_traitsData_does_not_have_trait_then_set_also_imbues(
        self, all_properties_trait, an_empty_traitsData, property
    ):
        a_trait = all_properties_trait(an_empty_traitsData)
        setter = getattr(a_trait, f"set{property.name[0].upper()}{property.name[1:]}")

        setter(property.valid_value)

        actual = an_empty_traitsData.getTraitProperty(all_properties_trait.kId, property.name)
        assert actual == property.valid_value

    def test_when_type_is_wrong_then_TypeError_is_raised(
        self, all_properties_trait, an_all_properties_traitsData, property
    ):
        a_trait = all_properties_trait(an_all_properties_traitsData)
        setter = getattr(a_trait, f"set{property.name[0].upper()}{property.name[1:]}")

        with pytest.raises(TypeError) as err:
            setter(property.invalid_value)

        assert (
            str(err.value) == f"{property.name} must be a '{type(property.valid_value).__name__}'."
        )


class Test_LocalAndExternalTraitSpecification:
    def test_subclass_of_openassetio_SpecificationBase(
        self, local_and_external_trait_specification
    ):
        assert issubclass(local_and_external_trait_specification, SpecificationBase)

    def test_external_trait_accessor_is_of_expected_type(
        self, local_and_external_trait_specification, module_traits_only
    ):
        a_specification = local_and_external_trait_specification(TraitsData())
        assert isinstance(
            a_specification.openassetioCodegenTestTraitsOnlyANamespaceNoPropertiesTrait(),
            module_traits_only.traits.aNamespace.NoPropertiesTrait,
        )

    def test_external_trait_instance_wraps_specifications_traits_data(
        self, local_and_external_trait_specification
    ):
        a_traits_data = TraitsData()
        a_specification = local_and_external_trait_specification(a_traits_data)
        a_trait = a_specification.openassetioCodegenTestTraitsOnlyANamespaceNoPropertiesTrait()
        assert a_trait._data is a_traits_data  # pylint: disable=protected-access

    def test_package_local_trait_accessor_is_of_expected_type(
        self, local_and_external_trait_specification, module_all
    ):
        a_specification = local_and_external_trait_specification(TraitsData())
        assert isinstance(
            a_specification.openassetioCodegenTestAllANamespaceNoPropertiesTrait(),
            module_all.traits.aNamespace.NoPropertiesTrait,
        )

    def test_local_trait_instance_wraps_specifications_traits_data(
        self, local_and_external_trait_specification
    ):
        a_traits_data = TraitsData()
        a_specification = local_and_external_trait_specification(a_traits_data)
        a_trait = a_specification.openassetioCodegenTestAllANamespaceNoPropertiesTrait()
        assert a_trait._data is a_traits_data  # pylint: disable=protected-access


class Test_generate:
    def test_when_files_created_then_creation_callback_is_called(
        self, declaration_exotic_values, creations_exotic_values, tmp_path_factory
    ):
        output_dir = tmp_path_factory.mktemp("test_python_generate_callback")
        expected = [os.path.join(output_dir, p) for p in creations_exotic_values]

        actual = []

        def creation_callback(path):
            actual.append(path)

        python_generator.generate(
            declaration_exotic_values,
            {},
            output_dir,
            creation_callback,
            logging.Logger("Test_generate"),
        )

        assert actual == expected

    def test_when_names_invalid_then_warnings_are_logged(
        self,
        declaration_exotic_values,
        warnings_exotic_values,
        a_capturing_logger,
        tmp_path_factory,
    ):
        output_dir = tmp_path_factory.mktemp("test_python_generate_warnings")
        python_generator.generate(
            declaration_exotic_values, {}, output_dir, lambda _: _, a_capturing_logger
        )

        assert a_capturing_logger.handlers[0].messages == warnings_exotic_values


#
# Fixtures
#


@pytest.fixture(scope="module")
def generated_path(
    yaml_path_all, yaml_path_traits_only, yaml_path_specifications_only, tmp_path_factory
):
    output_dir = tmp_path_factory.mktemp("generated_path")

    def creation_callback(_):
        pass

    # As there are dependencies between the different packages, we need
    # to generate them all together to avoid import errors.
    for description in (yaml_path_all, yaml_path_traits_only, yaml_path_specifications_only):
        generate(
            description_path=description,
            output_directory=output_dir,
            languages=[
                "python",
            ],
            creation_callback=creation_callback,
            logger=logging.Logger(name="Capturing logger"),
        )

    return output_dir


@pytest.fixture
def extended_python_path(generated_path, monkeypatch):
    """
    Temporarily extends sys.path to include the generated code directory.
    """
    packages_path = os.path.join(generated_path, "python")
    monkeypatch.syspath_prepend(packages_path)


@pytest.fixture
def module_all(extended_python_path):
    """
    Retrieves the python module corresponding to the 'all' description.
    """
    # pylint: disable=import-error,unused-argument,import-outside-toplevel
    import openassetio_codegen_test_all

    del sys.modules["openassetio_codegen_test_all"]

    return openassetio_codegen_test_all


@pytest.fixture
def module_traits_only(extended_python_path):
    """
    Retrieves the python module corresponding to the 'traits-only' description.
    """
    # pylint: disable=import-error,unused-argument,import-outside-toplevel
    import openassetio_codegen_test_traits_only

    del sys.modules["openassetio_codegen_test_traits_only"]

    return openassetio_codegen_test_traits_only


@pytest.fixture
def module_specifications_only(extended_python_path):
    """
    Retrieves the python module corresponding to the 'specifications-only' description.
    """
    # pylint: disable=import-error,unused-argument,import-outside-toplevel
    import openassetio_codegen_test_specifications_only

    del sys.modules["openassetio_codegen_test_specifications_only"]

    return openassetio_codegen_test_specifications_only


@pytest.fixture
def all_properties_trait(module_all):
    return module_all.traits.aNamespace.AllPropertiesTrait


@pytest.fixture
def an_empty_traitsData():
    return TraitsData(set())


@pytest.fixture
def an_all_properties_traitsData(module_all):
    return TraitsData({module_all.traits.aNamespace.AllPropertiesTrait.kId})


@pytest.fixture
def local_and_external_trait_specification(module_all):
    return module_all.specifications.test.LocalAndExternalTraitSpecification


@pytest.fixture
def creations_exotic_values():
    return [
        os.path.join("python", "p_p"),
        os.path.join("python", "p_p", "traits"),
        os.path.join("python", "p_p", "traits", "t_n.py"),
        os.path.join("python", "p_p", "traits", "__init__.py"),
        os.path.join("python", "p_p", "specifications"),
        os.path.join("python", "p_p", "specifications", "s_n.py"),
        os.path.join("python", "p_p", "specifications", "__init__.py"),
        os.path.join("python", "p_p", "__init__.py"),
    ]


@pytest.fixture
def warnings_exotic_values():
    return [
        (logging.WARNING, "Conforming 'p📦p' to 'p_p' for module name"),
        (logging.WARNING, "Conforming 't!n' to 't_n' for module name"),
        (logging.WARNING, "Conforming 't&' to 'T' for class name"),
        (logging.WARNING, "Conforming 'p$' to 'P' for property accessor name"),
        (logging.WARNING, "Conforming 'p$' to 'p' for variable name"),
        (logging.WARNING, "Conforming 's!n' to 's_n' for module name"),
        (logging.WARNING, "Conforming 's^' to 'S' for class name"),
        (logging.WARNING, "Conforming 't!n' to 't_n' for module name"),
        (logging.WARNING, "Conforming 't&' to 'T' for class name"),
        (logging.WARNING, "Conforming 't!n' to 't_n' for module name"),
        (logging.WARNING, "Conforming 't&' to 'T' for class name"),
    ]
