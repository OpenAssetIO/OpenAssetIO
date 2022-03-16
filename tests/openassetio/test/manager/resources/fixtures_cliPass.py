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
that when run against the StubManager, result in a pass.
"""

# pylint: disable=all

kIdentifier = "org.openassetio.test.manager.stubManager"

fixtures = {
    "identifier": kIdentifier,
    "Test_identifier": {
        "test_matches_fixture": {
            "identifier": kIdentifier
        }
    },
    "Test_displayName": {
        "test_matches_fixture": {
            "display_name": "Stub Manager"
        }
    },
    "Test_info": {
        "test_matches_fixture": {
            "info" : {}
        }
    }
}
