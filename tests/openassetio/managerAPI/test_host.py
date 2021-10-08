#
#   Copyright 2013-2021 [The Foundry Visionmongers Ltd]
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

import pytest
from unittest import mock

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

    def test__getInterface(self, mock_host_interface):
        a_host = Host(mock_host_interface)
        assert a_host._getInterface() is mock_host_interface

    def test_getIdentifier(self, host, mock_host_interface):
        method = mock_host_interface.getIdentifier
        assert host.getIdentifier() == method.return_value
        method.assert_called_once_with()

    def test_getDisplayName(self, host, mock_host_interface):
        method = mock_host_interface.getDisplayName
        assert host.getDisplayName() == method.return_value
        method.assert_called_once_with()

    def test_getInfo(self, host, mock_host_interface):
        method = mock_host_interface.getInfo
        assert host.getInfo() == method.return_value
        method.assert_called_once_with()

    def test_getDocumentReference(self, host, mock_host_interface):
        method = mock_host_interface.getDocumentReference
        assert host.getDocumentReference() == method.return_value
        method.assert_called_once_with()

    def test_getKnownEntityReferences(self, host, mock_host_interface, an_entity_spec):
        method = mock_host_interface.getKnownEntityReferences
        assert host.getKnownEntityReferences(an_entity_spec) == method.return_value
        method.assert_called_once_with(specification=an_entity_spec)
