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
Common pytest fixtures available to all tests in this package.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-function-docstring

import os
from unittest import mock

import pytest

from openassetio import hostAPI, logging
from openassetio.specifications import LocaleSpecification


@pytest.fixture
def resources_dir():
    """
    The path to the resources directory for this test suite.
    """
    test_dir = os.path.dirname(__file__)
    return os.path.join(test_dir, "resources")


@pytest.fixture(autouse=True)
def openassetio_env_with_test_resources(resources_dir, monkeypatch):
    """
    A fixture that configures the process environment such
    that the OpenAssetIO library can load the associated
    test resource plugins, and debug logging is enabled.
    """
    plugin_path = os.path.join(resources_dir, "plugins")
    monkeypatch.setenv("OPENASSETIO_PLUGIN_PATH", plugin_path)


@pytest.fixture
def mock_manager_factory():
    return mock.create_autospec(hostAPI.ManagerFactoryInterface, instance=True, spec_set=True)


@pytest.fixture
def mock_session(mock_manager):
    sess = mock.create_autospec(hostAPI.Session, instance=True, spec_set=True)
    sess.currentManager.return_value = mock_manager
    return sess


@pytest.fixture
def mock_manager():
    return mock.create_autospec(hostAPI.Manager, instance=True, spec_set=True)


@pytest.fixture
def mock_logger():
    return mock.create_autospec(logging.LoggerInterface, instance=True, spec_set=False)


@pytest.fixture
def a_fixture_dict():
    return {
        "identifier": "org.some.manager"
    }


@pytest.fixture
def a_locale():
    return LocaleSpecification()
