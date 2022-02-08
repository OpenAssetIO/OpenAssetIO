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
Manager test harness test case fixtures for standard apiComplianceSuite,
that when run against the StubManager, result in a fail.
"""

# pylint: disable=all

fixtures = {
    "identifier": "org.openassetio.test.manager.stubManager",
    "Test_identifier": {
        "test_matches_fixture": {
            # Fail here by expecting a different identifier
            "identifier": "not.the.right.identifier"
        }
    },
    "Test_displayName": {
        "test_matches_fixture": {
            "displayName": "Stub Manager"
        }
    },
    "Test_info": {
        "test_matches_fixture": {
            "info" : {}
        }
    },
    "Test_managementPolicy": {
        "test_calling_with_read_context_and_entity_reference": { "valid_entity_reference": "" },
        "test_calling_with_write_context_and_entity_reference": { "valid_entity_reference": "" },
        "test_calling_with_read_multiple_context_and_entity_reference": { "valid_entity_reference": ""},
        "test_calling_with_write_multiple_context_and_entity_reference": { "valid_entity_reference": "" }
    }
}

