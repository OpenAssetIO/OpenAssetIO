#
#   Copyright 2023 The Foundry Visionmongers Ltd
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
Tests that cover the string token substitute utility.
"""
# pylint: disable=missing-function-docstring,missing-class-docstring,
# pylint: disable=invalid-name
import re

import pytest

from openassetio import utils, errors


class Test_substitute:
    def test_when_no_substitutions_then_returns_same_string(self):
        assert utils.substitute("hello", {}) == "hello"

    def test_when_substitutions_available_then_returns_substituted_string(self):
        assert utils.substitute("hello {name}", {"name": "world"}) == "hello world"

    def test_when_missing_substitution_variable_then_raises_InputValidationException(self):
        expected_error = re.escape(
            "substitute(): failed to process the input string 'hello {name}': argument not found"
        )

        with pytest.raises(errors.InputValidationException, match=expected_error):
            utils.substitute("hello {name}", {})

    def test_when_extra_substitution_variable_then_extra_is_ignored(self):
        assert (
            utils.substitute("hello {name}", {"name": "world", "extra": "ignored"})
            == "hello world"
        )

    def test_when_allowed_value_types_then_substitutes_correctly(self):
        assert utils.substitute("hello {name}", {"name": "world"}) == "hello world"
        assert utils.substitute("hello {name}", {"name": 123}) == "hello 123"
        assert utils.substitute("hello {name}", {"name": 1.23}) == "hello 1.23"
        assert utils.substitute("hello {name}", {"name": True}) == "hello true"
        assert utils.substitute("hello {name}", {"name": False}) == "hello false"

    def test_when_unknown_value_types_then_raises_TypeError(self):
        expected_error = re.escape(
            "substitute(): incompatible function arguments."
            " The following argument types are supported"
        )

        with pytest.raises(TypeError, match=expected_error):
            utils.substitute("hello {name}", {"name": object()})

        with pytest.raises(TypeError, match=expected_error):
            utils.substitute("hello {name}", {"name": {"value": "world"}})

    def test_when_integer_format_specifier_then_substitutes_correctly(self):
        # We only officially support integer padding. Many other formats
        # are technically possible.
        assert utils.substitute("hello {name:04d}", {"name": 1}) == "hello 0001"
        assert utils.substitute("hello {name:04d}", {"name": 123}) == "hello 0123"
        assert utils.substitute("hello {name:04d}", {"name": 12345}) == "hello 12345"
