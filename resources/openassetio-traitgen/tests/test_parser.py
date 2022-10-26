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
Tests for the traitgen description parser.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import os

import pytest
import jsonschema

from openassetio_traitgen import datamodel, parser


class Test_Parser_loadYAML:
    def test_when_loading_valid_yaml_then_returned_dict_contains_expected_data(
        self, resources_dir
    ):
        yaml_path = os.path.join(resources_dir, "parser_load_test.yaml")
        expected = {"topLevelProperty": 1, "nested": {"property": "A property"}}

        assert parser.load_yaml(yaml_path) == expected

    def test_when_loading_missing_file_then_FileNotFoundError_raised(self):
        with pytest.raises(FileNotFoundError):
            parser.load_yaml("not_a_file")


class Test_Parser_validateDescription:
    def test_when_valid_then_noop(self, description_all):
        parser.validate_package_description(description_all)

    def test_when_invalid_keys_then_raises_ValidationError_raised(self, description_invalid):
        with pytest.raises(jsonschema.ValidationError):
            parser.validate_package_description(description_invalid)

    def test_when_invalid_values_then_raises_ValidationError_raised(
        self, description_invalid_values
    ):
        with pytest.raises(jsonschema.ValidationError):
            parser.validate_package_description(description_invalid_values)


class Test_Parser_buildPackageDeclaration:
    def test_when_contains_traits_and_specifications_then_expected_declaration_returned(
        self, description_all, declaration_all
    ):
        actual = parser.build_package_declaration(description_all)
        assert actual == declaration_all

    def test_when_traits_only_then_expected_declaration_returned(
        self, description_traits_only, declaration_traits_only
    ):
        actual = parser.build_package_declaration(description_traits_only)
        assert actual == declaration_traits_only

    def test_when_specifications_only_then_expected_declaration_returned(
        self, description_specifications_only, declaration_specifications_only
    ):
        actual = parser.build_package_declaration(description_specifications_only)
        assert actual == declaration_specifications_only

    def test_when_exotic_then_full_character_set_preserved(
        self, description_exotic_values, declaration_exotic_values
    ):
        actual = parser.build_package_declaration(description_exotic_values)
        assert actual == declaration_exotic_values
