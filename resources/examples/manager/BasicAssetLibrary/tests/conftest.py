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
Shared fixtures for BasicAssetLibrary pytest coverage.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import os
import pytest

from openassetio.test.manager import harness


@pytest.fixture(autouse=True)
def bal_plugin_env(bal_base_dir, monkeypatch):
    """
    Provides a modified environment with the BasicAssetLibrary
    plugin on the OpenAssetIO search path.
    """
    plugin_dir = os.path.join(bal_base_dir, "plugin")
    monkeypatch.setenv("OPENASSETIO_PLUGIN_PATH", plugin_dir)


@pytest.fixture
def harness_fixtures(bal_base_dir):
    """
    Provides the fixtues dict for the BasicAssetLibrary when used with
    the openassetio.test.manager.apiComplianceSuite.
    """
    fixtures_path = os.path.join(bal_base_dir, "tests", "fixtures.py")
    return harness.fixturesFromPyFile(fixtures_path)


@pytest.fixture
def bal_base_dir():
    """
    Provides the path to the base directory for the BasicAssetLibrary
    codebase.
    """
    return os.path.dirname(os.path.dirname(__file__))
