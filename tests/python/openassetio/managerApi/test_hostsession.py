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
Tests that cover the openassetio.managerApi.HostSession class.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

from openassetio import log
from openassetio.managerApi import Host, HostSession


@pytest.fixture
def a_host(mock_host_interface):
    return Host(mock_host_interface)


@pytest.fixture
def host_session(a_host, mock_logger):
    return HostSession(a_host, mock_logger)


class Test_HostSession_init:
    def test_when_host_is_None_then_raises_TypeError(self, mock_logger):
        with pytest.raises(TypeError) as err:
            HostSession(None, mock_logger)

        assert str(err.value).startswith("__init__(): incompatible constructor arguments")

    def test_when_invalid_host_then_raises_TypeError(self, mock_logger):
        with pytest.raises(TypeError) as err:
            HostSession(object(), mock_logger)

        assert str(err.value).startswith("__init__(): incompatible constructor arguments")


class Test_HostSession_host:
    def test_returns_expected_host_instance(self, host_session, a_host):
        actual_host = host_session.host()

        assert actual_host is a_host


class TestHostSession_log:
    def test_forwards_to_logger(self, host_session, mock_logger):
        a_message = "A message"
        a_severity = log.LoggerInterface.kCritical

        host_session.log(a_message, a_severity)
        mock_logger.mock.log.assert_called_once_with(a_message, a_severity)
