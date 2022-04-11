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
Tests that cover the openassetio.managerAPI.HostSession class.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

from unittest import mock

import pytest

from openassetio import log
from openassetio.managerAPI import Host, HostSession


@pytest.fixture
def mock_host():
    return mock.create_autospec(spec=Host)


@pytest.fixture
def mock_logger():
    return mock.create_autospec(spec=log.LoggerInterface)


@pytest.fixture
def host_session(mock_host, mock_logger):
    return HostSession(mock_host, mock_logger)


class TestHostSession():

    def test_construction(self, host_session, mock_host):
        assert host_session.host() is mock_host

    def test_log(self, host_session, mock_logger):
        mock_logger.reset_mock()

        a_message = "A message"
        a_severity = log.LoggerInterface.kCritical

        host_session.log(a_message, a_severity)
        mock_logger.log.assert_called_once_with(a_message, a_severity)

    def test_progress(self, host_session, mock_logger):
        a_progress = 0.1

        host_session.progress(a_progress)
        mock_logger.progress.assert_called_once_with(a_progress, None)

        for message in ("A message", "", None):
            mock_logger.reset_mock()
            host_session.progress(a_progress, message=message)
            mock_logger.progress.assert_called_once_with(a_progress, message=message)
