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
Tests for the traitgen generator helpers
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import datetime

import pytest

from openassetio_traitgen import datamodel
from openassetio_traitgen.generators import helpers


class Test_to_upper_camel_alnum:
    def test_when_legal_then_is_unchanged(self):
        expected = "AlreadyUpperCamelCase"
        assert helpers.to_upper_camel_alnum(expected) == expected

    def test_when_illegal_then_output_only_contains_alnum(self):
        input = "#This! is a  ## complex-string  WithSome ExistingCamel and_snake 4 u!!"
        expected = "ThisIsAComplexStringWithSomeExistingCamelAndSnake4U"
        assert helpers.to_upper_camel_alnum(input) == expected


class Test_to_lower_camel_alnum:
    def test_when_legal_then_is_unchanged(self):
        expected = "alreadyLowerCamelCase"
        assert helpers.to_lower_camel_alnum(expected) == expected

    def test_when_illegal_then_output_only_contains_alnum(self):
        input = "!!This! is a  ## complex-string  WithSome ExistingCamel and_snake 4 u!!"
        expected = "thisIsAComplexStringWithSomeExistingCamelAndSnake4U"
        assert helpers.to_lower_camel_alnum(input) == expected


class Test_default_template_globals:
    def test_copyrightDate_is_this_year(self):
        expected = datetime.date.today().year
        actual = helpers.default_template_globals()["copyrightDate"]
        assert actual == expected

    def test_copyrightOwner_is_empty(self):
        actual = helpers.default_template_globals()["copyrightOwner"]
        assert actual == ""

    def test_spdxLicenseIdentifier_is_this_apache_two(self):
        actual = helpers.default_template_globals()["spdxLicenseIdentifier"]
        assert actual == "Apache-2.0"


class Test_packaged_dependencies:
    def test_when_traits_then_list_is_empty(self, some_trait_declarations):
        assert helpers.package_dependencies(some_trait_declarations) == []

    def test_when_specifications_then_list_is_sorted_unique_packages(
        self, some_specification_declarations
    ):
        assert helpers.package_dependencies(some_specification_declarations) == [
            "packageA",
            "packageB",
            "packageC",
        ]


#
# Fixtures
#


@pytest.fixture
def some_trait_declarations():
    return [
        datamodel.TraitDeclaration(
            id="package:namespace.Name1",
            name="Name1",
            description="A trait",
            properties=[],
            usage=[],
        ),
        datamodel.TraitDeclaration(
            id="package:namespace.Name2",
            name="Name2",
            description="Another trait",
            properties=[],
            usage=[],
        ),
    ]


@pytest.fixture
def some_specification_declarations():
    return [
        datamodel.SpecificationDeclaration(
            id="Specification1",
            description="A specification",
            usage=[],
            trait_set=[
                datamodel.TraitReference(
                    package="packageB",
                    namespace="namespace",
                    name="cat",
                    unique_name_parts=("cat",),
                    id="packageB:namespace.cat",
                ),
                datamodel.TraitReference(
                    package="packageA",
                    namespace="namespace",
                    name="hat",
                    unique_name_parts=("hat",),
                    id="packageA:namespace.hat",
                ),
            ],
        ),
        datamodel.SpecificationDeclaration(
            id="Specification2",
            description="Another specification",
            usage=[],
            trait_set=[
                datamodel.TraitReference(
                    package="packageB",
                    namespace="namespace",
                    name="cat",
                    unique_name_parts=("cat",),
                    id="packageB:namespace.cat",
                ),
                datamodel.TraitReference(
                    package="packageC",
                    namespace="namespace",
                    name="mouse",
                    unique_name_parts=("mouse",),
                    id="packageC:namespace.mouse",
                ),
            ],
        ),
    ]
