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
Tests for deprecated functionality.

All cases must have a link to the relevant GitHub issue in their
docstrings.
"""

# pylint: disable=missing-function-docstring,import-outside-toplevel


def test_renamed_kField_constants():
    """
    https://github.com/OpenAssetIO/OpenAssetIO/issues/998
    """
    from openassetio import constants

    assert constants.kField_SmallIcon == constants.kInfoKey_SmallIcon
    assert constants.kField_Icon == constants.kInfoKey_Icon
    assert (
        constants.kField_EntityReferencesMatchPrefix
        == constants.kInfoKey_EntityReferencesMatchPrefix
    )


def test_top_level_TraitsData_import():
    """
    https://github.com/OpenAssetIO/OpenAssetIO/issues/1127
    """
    from openassetio import trait, TraitsData

    assert TraitsData is trait.TraitsData
