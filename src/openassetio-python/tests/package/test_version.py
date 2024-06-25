#
# Copyright 2024 The Foundry Visionmongers Ltd

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Tests that cover the version introspection methods
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=too-few-public-methods
# pylint: disable=missing-class-docstring,missing-function-docstring

import re

import pytest

import openassetio

# Update this value each release
openassetio_version_string = "v1.0.0-beta.2.2"


@pytest.fixture(scope="module")
def extracted_version_nums():
    # Extract version numbers so we can test them
    pattern = r"v(\d+)\.(\d+)\.(\d+)-beta\.(\d+)\.(\d+)"
    match = re.search(pattern, openassetio_version_string)
    major_version = match.group(1)
    minor_version = match.group(2)
    patch_version = match.group(3)
    beta_major_version = match.group(4)
    beta_minor_version = match.group(5)
    return (
        int(major_version),
        int(minor_version),
        int(patch_version),
        int(beta_major_version),
        int(beta_minor_version),
    )


class Test_Version:
    def test_version_string(self):
        assert openassetio.versionString() == openassetio_version_string

    def test_major_version(self, extracted_version_nums):
        assert openassetio.majorVersion() == extracted_version_nums[0]

    def test_minor_version(self, extracted_version_nums):
        assert openassetio.minorVersion() == extracted_version_nums[1]

    def test_patch_version(self, extracted_version_nums):
        assert openassetio.patchVersion() == extracted_version_nums[2]

    def test_major_beta_version(self, extracted_version_nums):
        assert openassetio.betaMajorVersion() == extracted_version_nums[3]

    def test_minor_beta_version(self, extracted_version_nums):
        assert openassetio.betaMinorVersion() == extracted_version_nums[4]
