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
@namespace openassetio.test.specifications
Specifications for use within openassetio test harnesses.
"""

from openassetio.specifications import LocaleSpecification


class TestHarnessLocale(LocaleSpecification):
    """
    A locale for test cases run as part of one of the API supplied
    test harnesses.
    """
    _type = "test.harness"

    testSuite = LocaleSpecification.TypedProperty(str, doc="The name of the test suite being run")
    testCase = LocaleSpecification.TypedProperty(str, doc="The name of the test case being run")
