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
Tests that cover the openassetio.access namespace.
"""
import collections

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
import pytest

from openassetio.access import (
    PolicyAccess,
    RelationsAccess,
    ResolveAccess,
    PublishingAccess,
    DefaultEntityAccess,
    kAccessNames,
)


class Test_root_enum:
    def test_expected_constants_are_unique_and_exhaustive(self, root_enum):
        assert_expected_enum_values(
            root_enum,
            root_enum.kRead,
            root_enum.kWrite,
            root_enum.kCreateRelated,
        )

        # The following is just a confidence check of pybind11 and our
        # test fixtures.

        all_enum_values = extract_comparable_values_from_enum_values(
            root_enum.kRead, root_enum.kWrite, root_enum.kCreateRelated
        )
        assert len(all_enum_values) == 3
        assert len(set(member.name for member in all_enum_values)) == 3
        assert len(set(member.value for member in all_enum_values)) == 3

        all_enum_values_from_class = extract_comparable_values_from_enum_class(root_enum)
        assert len(all_enum_values_from_class) == 3
        assert len(set(member.name for member in all_enum_values_from_class)) == 3
        assert len(set(member.value for member in all_enum_values_from_class)) == 3


class Test_kAccessNames:
    def test_access_names_indices_match_constants(self, root_enum):
        assert kAccessNames[int(root_enum.kRead)] == "read"
        assert kAccessNames[int(root_enum.kWrite)] == "write"
        assert kAccessNames[int(root_enum.kCreateRelated)] == "createRelated"


class Test_PolicyAccess:
    def test_has_expected_constants(self, root_enum):
        assert_expected_enum_values(
            PolicyAccess,
            root_enum.kRead,
            root_enum.kWrite,
            root_enum.kCreateRelated,
        )


class Test_RelationsAccess:
    def test_has_expected_constants(self, root_enum):
        assert_expected_enum_values(
            RelationsAccess,
            root_enum.kRead,
            root_enum.kWrite,
            root_enum.kCreateRelated,
        )


class Test_ResolveAccess:
    def test_has_expected_constants(self, root_enum):
        assert_expected_enum_values(ResolveAccess, root_enum.kRead, root_enum.kWrite)


class Test_PublishingAccess:
    def test_has_expected_constants(self, root_enum):
        assert_expected_enum_values(PublishingAccess, root_enum.kWrite, root_enum.kCreateRelated)


class Test_DefaultEntityAccess:
    def test_has_expected_constants(self, root_enum):
        assert_expected_enum_values(
            DefaultEntityAccess,
            root_enum.kRead,
            root_enum.kWrite,
            root_enum.kCreateRelated,
        )


@pytest.fixture
def root_enum():
    """
    An enum class that contains all possible values that we support.

    Uses PolicyAccess as a representative enum with all values.
    """
    return PolicyAccess


def assert_expected_enum_values(enum_under_test, *expected_values):
    expected = extract_comparable_values_from_enum_values(*expected_values)
    actual = extract_comparable_values_from_enum_class(enum_under_test)
    assert actual == expected


def extract_comparable_values_from_enum_class(enum_class):
    return extract_comparable_values_from_enum_values(*enum_class.__members__.values())


def extract_comparable_values_from_enum_values(*enum_values):
    return set(ComparableEnumValue(member.name, member.value) for member in enum_values)


# Required since enum values under different enum classes compare
# non-equal, even if their string name and integer values are identical.
ComparableEnumValue = collections.namedtuple("ComparableEnumValue", ("name", "value"))
