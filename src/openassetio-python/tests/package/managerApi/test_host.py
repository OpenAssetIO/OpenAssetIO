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
Tests that cover the openassetio.managerApi.host class.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

from openassetio import Context
from openassetio.managerApi import Host


@pytest.fixture
def host(mock_host_interface):
    return Host(mock_host_interface)


@pytest.fixture()
def a_context():
    return Context()


# TODO(TC):  __str__ and __repr__ aren't tested as they're debug tricks that need
#   assessing when this is ported to cpp


class Test_Host_init:
    def test_when_inheriting_then_raises_TypeError(self):
        with pytest.raises(TypeError) as err:

            class _Derived(Host):
                pass

        assert str(err.value) == (
            "type 'openassetio._openassetio.managerApi.Host' is not an acceptable base type"
        )

    def test_when_invalid_interface_then_raises_TypeError(self):
        with pytest.raises(TypeError) as err:
            Host(object())

        assert str(err.value).startswith("__init__(): incompatible constructor arguments")


class Test_Host_identifier:
    def test_wraps_the_corresponding_method_of_the_held_interface(self, host, mock_host_interface):
        expected = "some identifier"
        mock_host_interface.mock.identifier.return_value = expected

        actual = host.identifier()

        assert actual == expected
        mock_host_interface.mock.identifier.assert_called_once_with()

    def test_when_interface_provides_wrong_type_then_raises_RuntimeError(
        self, host, mock_host_interface
    ):
        mock_host_interface.mock.identifier.return_value = 123

        with pytest.raises(RuntimeError) as err:
            host.identifier()

        assert str(err.value).startswith("Unable to cast Python instance")


class Test_Host_displayName:
    def test_wraps_the_corresponding_method_of_the_held_interface(self, host, mock_host_interface):
        expected = "some display name"
        mock_host_interface.mock.displayName.return_value = expected

        actual = host.displayName()

        assert actual == expected
        mock_host_interface.mock.displayName.assert_called_once_with()

    def test_when_interface_provides_wrong_type_then_raises_RuntimeError(
        self, host, mock_host_interface
    ):
        mock_host_interface.mock.displayName.return_value = 123

        with pytest.raises(RuntimeError) as err:
            host.displayName()

        assert str(err.value).startswith("Unable to cast Python instance")


class Test_Host_info:
    def test_wraps_the_corresponding_method_of_the_held_interface(self, host, mock_host_interface):
        expected = {"some": "info"}
        mock_host_interface.mock.info.return_value = expected

        actual = host.info()

        assert actual == expected
        mock_host_interface.mock.info.assert_called_once_with()

    def test_when_interface_provides_wrong_type_then_raises_RuntimeError(
        self, host, mock_host_interface
    ):
        mock_host_interface.mock.info.return_value = {123: 123}

        with pytest.raises(RuntimeError) as err:
            host.info()

        assert str(err.value).startswith("Unable to cast Python instance")
