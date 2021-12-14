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
Tests that cover the openassetio.hostAPI.Specification class.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

from openassetio import Specification


class PrefixASpec(Specification):
    _prefix = "prefixA"
    _type = "spec"
    # Properties
    aString = Specification.TypedProperty(str)
    anInt = Specification.TypedProperty(int)


class Test_Specification_construction:

    def test_when_constructed_then_has_expected_schema_components(self):
        a_spec = PrefixASpec()

        assert a_spec.schema() == "prefixA:spec"
        assert a_spec.prefix() == "prefixA"
        assert a_spec.type() == "spec"

