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
from unittest import mock

import pytest

from openassetio import hostAPI, logging
from openassetio.test.managerValidator import validatorHarness


@pytest.fixture
def mock_host_interface():
    return mock.create_autospec(
        validatorHarness.ValidatorHarnessHostInterface, instance=True, spec_set=True)


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
