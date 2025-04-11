#
#   Copyright 2025 The Foundry Visionmongers Ltd
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
Tests for the available values of the UI-specific access mode enum.
"""
# pylint: disable=missing-class-docstring,invalid-name,missing-function-docstring

from openassetio.ui.access import UIAccess


class Test_UIAccess:
    def test_has_expected_constants(self, root_enum, assert_expected_enum_values):
        assert_expected_enum_values(
            UIAccess, root_enum.kRead, root_enum.kWrite, root_enum.kCreateRelated
        )
