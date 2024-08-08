#
#   Copyright 2013-2023 The Foundry Visionmongers Ltd
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
Test CMake installed package
"""
# pylint: disable=missing-function-docstring,invalid-name
import os
from importlib import metadata

import pytest


@pytest.mark.skipif(
    os.environ.get("OPENASSETIO_CMAKE_PACKAGE_VERSION") is None, reason="CMake package only"
)
def test_cmake_dist_info():
    dist = metadata.distribution("openassetio")

    # Check METADATA file exists with required keys.
    assert set(dist.metadata.keys()) == {"Name", "Metadata-Version", "Version"}
    assert dist.metadata["Name"] == "openassetio"
    assert dist.metadata["Version"].startswith(os.environ["OPENASSETIO_CMAKE_PACKAGE_VERSION"])

    # The lack of a RECORD means that `pip` is unable to accidentally
    # uninstall the package
    assert dist.read_text("RECORD") is None

    # The INSTALLER is used by `pip` to provide a hint when reporting
    # that it is unable to install a package due to no RECORD.
    installer = dist.read_text("INSTALLER")
    assert installer is not None
    assert installer.strip() == "cmake"

    # The above uses files in the dist-info directory, whereas pip uses
    # the directory name itself. So check that they match.
    dist_info_path = os.path.join(
        dist.locate_file(""), f"{dist.metadata['Name']}-{dist.metadata['Version']}.dist-info"
    )
    assert os.path.isdir(dist_info_path)
    dist_from_dir = metadata.Distribution.at(dist_info_path)
    assert dict(dist.metadata) == dict(dist_from_dir.metadata)
