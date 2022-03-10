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

from unittest import mock

import pytest

from openassetio import Context
from openassetio.specifications import EntitySpecification
from openassetio.hostAPI import HostInterface
from openassetio.managerAPI import Host


@pytest.fixture
def mock_host_interface():
    return mock.create_autospec(spec=HostInterface)


@pytest.fixture
def host(mock_host_interface):
    return Host(mock_host_interface)


@pytest.fixture()
def an_entity_spec():
    return EntitySpecification()


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
        method = mock_host_interface.identifier
        assert host.identifier() == method.return_value
        method.assert_called_once_with()

    def test_displayName(self, host, mock_host_interface):
        method = mock_host_interface.displayName
        assert host.displayName() == method.return_value
        method.assert_called_once_with()

    def test_info(self, host, mock_host_interface):
        method = mock_host_interface.info
        assert host.info() == method.return_value
        method.assert_called_once_with()
