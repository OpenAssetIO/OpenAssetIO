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
Fixtures for executeSuiteTests.py
"""

fixtures = {
    "identifier": "org.openassetio.test.manager.stubManager",
    "settings": { "test_setting": "a_value" },
    "shared": {
        "a_global_value": 1,
        "a_class_overridden_global_value": 3,
        "a_function_overridden_global_value": 6
    },
    "Test_executeSuite_fixtures": {
        "shared": {
            "a_class_value": 2,
            "a_class_overridden_global_value": 4
        },
        "test_fixtures_include_those_for_the_test": {
            "a_unique_value": 5
        },
        "test_when_function_fixture_is_set_then_overrides_global": {
            "a_function_overridden_global_value": 7
        },
        "test_fixtures_contain_no_additional_keys": {
            "another_unique_value": 42
        }
    },
    "Test_executeSuite_with_case_fixtures": {
        "non_existant_test": {}
    }
}
