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

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

from openassetio.managerApi import HostSession


class Test_HostSession_inheritance:
    def test_class_is_final(self):
        with pytest.raises(TypeError):

            class _(HostSession):
                pass


class Test_HostSession_init:
    def test_when_host_is_None_then_raises_TypeError(self, mock_logger):
        with pytest.raises(TypeError) as err:
            HostSession(None, mock_logger)

        assert str(err.value).startswith("__init__(): incompatible constructor arguments")

    def test_when_invalid_host_then_raises_TypeError(self, mock_logger):
        with pytest.raises(TypeError) as err:
            HostSession(object(), mock_logger)

        assert str(err.value).startswith("__init__(): incompatible constructor arguments")

    def test_when_logger_is_None_then_raises_TypeError(self, a_host):
        with pytest.raises(TypeError) as err:
            HostSession(a_host, None)

        assert str(err.value).startswith("__init__(): incompatible constructor arguments")

    def test_when_invalid_logger_then_raises_TypeError(self, a_host):
        with pytest.raises(TypeError) as err:
            HostSession(a_host, object())

        assert str(err.value).startswith("__init__(): incompatible constructor arguments")


class Test_HostSession_host:
    def test_returns_expected_host_instance(self, a_host_session, a_host):
        actual_host = a_host_session.host()

        assert actual_host is a_host


class Test_HostSession_logger:
    def test_returns_expected_logger_instance(self, a_host_session, mock_logger):
        actual_logger = a_host_session.logger()

        assert actual_logger is mock_logger
