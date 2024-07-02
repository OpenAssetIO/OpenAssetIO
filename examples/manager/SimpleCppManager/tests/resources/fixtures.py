#
#   Copyright 2013-2022 The Foundry Visionmongers Ltd
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
Manager test harness test case fixtures for openassetio.test.manager
API compliance test suite.
"""

# pylint: disable=all

kIdentifier = "org.openassetio.examples.manager.simplecppmanager"

fixtures = {
    "identifier": kIdentifier,
    "settings": {
        "prefix": "simplecpp://",
        "read_policy": "openassetio-mediacreation:managementPolicy.Managed",
        "read_traits": """
simplecpp://test/entity/1,openassetio-mediacreation:usage.Entity
simplecpp://test/entity/1,openassetio-mediacreation:content.LocatableContent,location,file:///tmp/test1.txt
simplecpp://test/entity/1,openassetio-mediacreation:identity.DisplayName,name,Test Entity 1
""",
    },
    "Test_info": {"test_matches_fixture": {"info": {}}},
    "Test_identifier": {"test_matches_fixture": {"identifier": kIdentifier}},
    "Test_displayName": {"test_matches_fixture": {"display_name": "Simple C++ Manager"}},
    "Test_isEntityReferenceString": {
        "shared": {
            "a_valid_reference": "simplecpp://😀",
            "an_invalid_reference": "implecpp://😀",
        }
    },
    "Test_entityTraits": {
        "test_when_querying_missing_reference_for_read_then_resolution_error_is_returned": {
            "a_reference_to_a_missing_entity": "simplecpp://😀",
            "expected_error_message": "Entity not found",
        },
        "test_when_read_only_entity_queried_for_write_then_access_error_is_returned": {
            "a_reference_to_a_readonly_entity": "simplecpp://test/entity/1",
            "expected_error_message": "Entity access is read-only",
        },
    },
    "Test_resolve": {
        "shared": {
            "a_reference_to_a_readable_entity": "simplecpp://test/entity/1",
            "a_set_of_valid_traits": {
                "openassetio-mediacreation:identity.DisplayName",
                "openassetio-mediacreation:content.LocatableContent",
            },
        },
        "test_when_resolving_read_only_reference_for_publish_then_access_error_is_returned": {
            "a_reference_to_a_readonly_entity": "simplecpp://test/entity/1",
            "the_error_string_for_a_reference_to_a_readonly_entity": "Entity access is read-only",
        },
        "test_when_resolving_missing_reference_then_resolution_error_is_returned": {
            "a_reference_to_a_missing_entity": "simplecpp://😀",
            "the_error_string_for_a_reference_to_a_missing_entity": "Entity not found",
        },
    },
}
