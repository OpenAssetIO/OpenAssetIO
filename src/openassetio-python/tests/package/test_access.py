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
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

from openassetio.access import (
    EntityTraitsAccess,
    PolicyAccess,
    RelationsAccess,
    ResolveAccess,
    PublishingAccess,
    DefaultEntityAccess,
    kAccessNames,
)


class Test_root_enum:
    def test_expected_constants_are_unique_and_exhaustive(
        self, root_enum, assert_expected_enum_values
    ):
        assert_expected_enum_values(
            root_enum,
            root_enum.kRead,
            root_enum.kWrite,
            root_enum.kCreateRelated,
            root_enum.kRequired,
            root_enum.kManagerDriven,
        )


class Test_kAccessNames:
    def test_access_names_indices_match_constants(self, root_enum):
        assert kAccessNames[int(root_enum.kRead)] == "read"
        assert kAccessNames[int(root_enum.kWrite)] == "write"
        assert kAccessNames[int(root_enum.kCreateRelated)] == "createRelated"
        assert kAccessNames[int(root_enum.kRequired)] == "required"
        assert kAccessNames[int(root_enum.kManagerDriven)] == "managerDriven"


class Test_PolicyAccess:
    def test_has_expected_constants(self, root_enum, assert_expected_enum_values):
        assert_expected_enum_values(
            PolicyAccess,
            root_enum.kRead,
            root_enum.kWrite,
            root_enum.kCreateRelated,
            root_enum.kRequired,
            root_enum.kManagerDriven,
        )


class Test_RelationsAccess:
    def test_has_expected_constants(self, root_enum, assert_expected_enum_values):
        assert_expected_enum_values(
            RelationsAccess,
            root_enum.kRead,
            root_enum.kWrite,
            root_enum.kCreateRelated,
        )


class Test_ResolveAccess:
    def test_has_expected_constants(self, root_enum, assert_expected_enum_values):
        assert_expected_enum_values(ResolveAccess, root_enum.kRead, root_enum.kManagerDriven)


class Test_EntityTraitsAccess:
    def test_has_expected_constants(self, root_enum, assert_expected_enum_values):
        assert_expected_enum_values(EntityTraitsAccess, root_enum.kRead, root_enum.kWrite)


class Test_PublishingAccess:
    def test_has_expected_constants(self, root_enum, assert_expected_enum_values):
        assert_expected_enum_values(PublishingAccess, root_enum.kWrite, root_enum.kCreateRelated)


class Test_DefaultEntityAccess:
    def test_has_expected_constants(self, root_enum, assert_expected_enum_values):
        assert_expected_enum_values(
            DefaultEntityAccess,
            root_enum.kRead,
            root_enum.kWrite,
            root_enum.kCreateRelated,
        )
