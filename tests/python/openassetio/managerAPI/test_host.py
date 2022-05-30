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
Tests that cover the openassetio.managerAPI.host class.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

from openassetio import Context
from openassetio.managerAPI import Host


@pytest.fixture
def host(mock_host_interface):
    return Host(mock_host_interface)


@pytest.fixture()
def a_context():
    return Context()


class TestHost():

    # __str__ and __repr__ aren't tested as they're debug tricks that need
    # assessing when this is ported to cpp

    def test__interface(self, mock_host_interface):
        # pylint: disable=protected-access
        a_host = Host(mock_host_interface)
        assert a_host._interface() is mock_host_interface

    def test_identifier(self, host, mock_host_interface):
        expected = "some identifier"
        mock_host_interface.mock.identifier.return_value = expected

        actual = host.identifier()

        assert actual == expected
        mock_host_interface.mock.identifier.assert_called_once_with()

    def test_displayName(self, host, mock_host_interface):
        expected = "some display name"
        mock_host_interface.mock.displayName.return_value = expected

        actual = host.displayName()

        assert actual == expected
        mock_host_interface.mock.displayName.assert_called_once_with()

    def test_info(self, host, mock_host_interface):
        expected = {"some": "info"}
        mock_host_interface.mock.info.return_value = expected

        actual = host.info()

        assert actual == expected
        mock_host_interface.mock.info.assert_called_once_with()
