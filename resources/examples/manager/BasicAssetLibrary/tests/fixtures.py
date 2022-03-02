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
Manager test harness fixtures for the apiComplianceSuite
"""

import json
import os


from openassetio.constants import kField_EntityReferencesMatchPrefix

#
# Test library
#

test_library_path = os.path.join(os.path.dirname(__file__), "resources", "library_apiComplianceSuite.json")
test_libray = {}

with open(test_library_path, "r", encoding="utf-8") as file:
    test_library = json.load(file)

#
# Constants
#

identifier = "org.openassetio.examples.manager.bal"

valid_ref = "bal:///references/can/contain/🐠"
non_ref = "not a Ŕeference"

an_existing_entity_name = next(iter(test_library["entities"].keys()))


fixtures = {
    "identifier": identifier,
    "settings": {
        "library_path": test_library_path
    },
    "shared": {
        "a_valid_reference": valid_ref,
        "a_malformed_reference": non_ref,
    },
    "Test_identifier": {
        "test_matches_fixture": {
            "identifier": identifier
        }
    },
    "Test_displayName": {
        "test_matches_fixture": {
            "display_name": "Basic Asset Library 📖"
        }
    },
    "Test_info": {
        "test_matches_fixture": {
            "info" : {
                kField_EntityReferencesMatchPrefix: "bal:///"
            }
        }
    },
    "Test_setSettings": {
        "shared": {
            "some_settings_with_valid_keys": {"library_path": "/dev/null"},
            "some_settings_with_invalid_keys": {"cat": True}
        }
    },
    "Test_getSettings": {
        "test_when_set_then_get_returns_updated_settings": {
            "some_new_settings_with_all_keys": {"library_path": "/dev/null"}
        },
        "test_when_set_with_subset_then_other_settings_unchanged": {
            "some_new_settings_with_a_subset_of_keys": {}
        }
    },
    "Test_entityExists": {
        "shared": {
            "a_reference_to_an_existing_entity": f"bal:///{an_existing_entity_name}",
            "a_reference_to_a_nonexisting_entity": valid_ref
        }
    },
    "Test_resolveEntityReference": {
        "test_matches_fixture_for_read": {
            "a_reference_to_a_readable_entity":
                    f"bal:///{an_existing_entity_name}",
            "the_primary_string_for_a_reference_to_a_readable_entity":
                    test_library["entities"][an_existing_entity_name]["versions"][-1]["primary_string"]
        },
        "test_when_resolving_read_only_reference_for_write_then_resolution_error_is_returned": {
            "a_reference_to_a_readonly_entity": f"bal:///{an_existing_entity_name}",
            "the_error_string_for_a_reference_to_a_readonly_entity": "BAL entities are read-only"
        }
    }
}
