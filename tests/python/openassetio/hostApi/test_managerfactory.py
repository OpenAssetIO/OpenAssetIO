#
#   Copyright 2022 The Foundry Visionmongers Ltd
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
Tests that cover the openassetio.hostApi.ManagerFactory class.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
from unittest import mock

import pytest

from openassetio import _openassetio  # pylint: disable=no-name-in-module
from openassetio.hostApi import ManagerFactory, Manager, ManagerInterfaceFactoryInterface


CppManagerFactory = _openassetio.hostApi.ManagerFactory


class Test_ManagerFactory_ManagerDetail_equality:
    def test_when_other_is_equal_then_compares_equal(self):
        managerDetails = ManagerFactory.ManagerDetail(
            identifier="a", displayName="b", info={"c": "d"})
        otherManagerDetail = ManagerFactory.ManagerDetail(
            identifier="a", displayName="b", info={"c": "d"})

        assert managerDetails == otherManagerDetail

    @pytest.mark.parametrize(
        "otherManagerDetail", [
            ManagerFactory.ManagerDetail(
                identifier="z", displayName="b", info={"c": "d"}),
            ManagerFactory.ManagerDetail(
                identifier="a", displayName="z", info={"c": "d"}),
            ManagerFactory.ManagerDetail(
                identifier="a", displayName="b", info={"c": "z"})])
    def test_when_other_has_unequal_field_then_object_compares_unequal(self, otherManagerDetail):
        managerDetails = ManagerFactory.ManagerDetail(
            identifier="a", displayName="b", info={"c": "d"})

        assert managerDetails != otherManagerDetail


class Test_ManagerFactory_identifiers:
    def test_wraps_the_corresponding_method_of_the_held_interface(
            self, mock_manager_interface_factory, a_manager_factory):
        expected = ["first.identifier", "second.identifier"]
        mock_manager_interface_factory.mock.identifiers.return_value = expected

        actual = a_manager_factory.identifiers()

        assert actual == expected


class Test_ManagerFactory_availableManagers:
    def test_when_no_implemetations_then_reports_no_implemetation_detais(
            self, mock_manager_interface_factory, a_manager_factory):
        mock_manager_interface_factory.mock.identifiers.return_value = []
        mock_manager_interface_factory.mock.instantiate.side_effect = []

        expected = {}

        # action

        actual = a_manager_factory.availableManagers()

        # confirm

        assert actual == expected

    def test_when_has_implementations_then_reports_implementation_details(
            self, create_mock_manager_interface, mock_manager_interface_factory,
            a_manager_factory):
        # setup

        identifiers = ["first.identifier", "second.identifier"]
        mock_manager_interface_factory.mock.identifiers.return_value = identifiers

        first_manager_interface = create_mock_manager_interface()
        second_manager_interface = create_mock_manager_interface()
        first_manager_interface.mock.identifier.return_value = "first.identifier"
        second_manager_interface.mock.identifier.return_value = "second.identifier"
        first_manager_interface.mock.displayName.return_value = "First"
        second_manager_interface.mock.displayName.return_value = "Second"
        first_manager_interface.mock.info.return_value = {"first": "info"}
        second_manager_interface.mock.info.return_value = {"second": "info"}

        mock_manager_interface_factory.mock.instantiate.side_effect = [
            first_manager_interface, second_manager_interface
        ]

        expected = {
            "first.identifier": ManagerFactory.ManagerDetail(
                identifier="first.identifier", displayName="First", info={"first": "info"}),
            "second.identifier": ManagerFactory.ManagerDetail(
                identifier="second.identifier", displayName="Second", info={"second": "info"})
        }

        # action

        actual = a_manager_factory.availableManagers()

        # confirm

        assert actual == expected


# TODO(DF) C++ specific tests can be removed once ManagerFactory is
#  fully migrated to C++ (i.e. once Manager and possibly HostSession is
#  fully migrated to C++).
class Test_CppManagerFactory_createManager:

    def test_returns_a_cpp_manager(self, a_cpp_manager_factory):
        manager = a_cpp_manager_factory.createManager("a.manager")
        assert isinstance(manager, _openassetio.hostApi.Manager)

    def test_manager_is_properly_configured(
            self, assert_expected_manager, a_cpp_manager_factory, mock_manager_interface_factory):
        # setup

        expected_identifier = "a.manager"

        # action

        manager = a_cpp_manager_factory.createManager(expected_identifier)

        # confirm

        mock_manager_interface_factory.mock.instantiate.assert_called_once_with(
            expected_identifier)
        assert_expected_manager(manager)


class Test_CppManagerFactory_createManagerForInterface:

    def test_returns_a_cpp_manager(self, mock_manager_interface_factory, mock_host_interface,
            mock_logger):

        manager = CppManagerFactory.createManagerForInterface(
            "a.manager", mock_host_interface, mock_manager_interface_factory, mock_logger)

        assert isinstance(manager, _openassetio.hostApi.Manager)

    def test_manager_is_properly_configured(
            self, assert_expected_manager, mock_manager_interface_factory, mock_host_interface,
            mock_logger):
        # setup

        expected_identifier = "a.manager"

        # action

        manager = CppManagerFactory.createManagerForInterface(
            expected_identifier, mock_host_interface, mock_manager_interface_factory, mock_logger)

        # confirm

        mock_manager_interface_factory.mock.instantiate.assert_called_once_with(
            expected_identifier)
        assert_expected_manager(manager)


class Test_ManagerFactory:
    def test_inherits_from_cpp(self):
        # We assume if the Python implementation is a subclass of the
        # C++ implementation then the tests for methods `identifiers`
        # and `availableManagers` (which are not overridden) are valid
        # for both C++ and Python and so don't need to be duplicated.
        assert issubclass(ManagerFactory, _openassetio.hostApi.ManagerFactory)


class Test_ManagerFactory_createManager:

    def test_returns_a_manager(self, a_manager_factory):
        manager = a_manager_factory.createManager("a.manager")
        assert isinstance(manager, Manager)

    def test_manager_is_properly_configured(
            self, assert_expected_manager, a_manager_factory, mock_manager_interface_factory):
        # setup

        expected_identifier = "a.manager"

        # action

        manager = a_manager_factory.createManager(expected_identifier)

        # confirm

        assert isinstance(manager, Manager)
        mock_manager_interface_factory.mock.instantiate.assert_called_once_with(
            expected_identifier)
        assert_expected_manager(manager)


class Test_ManagerFactory_createManagerForInterface:

    def test_returns_a_manager(
            self, mock_manager_interface_factory, mock_host_interface, mock_logger):

        manager = ManagerFactory.createManagerForInterface(
            "a.manager", mock_host_interface, mock_manager_interface_factory, mock_logger)

        assert isinstance(manager, Manager)

    def test_manager_is_properly_configured(
            self, assert_expected_manager, mock_manager_interface_factory, mock_host_interface,
            mock_logger):
        # setup

        expected_identifier = "a.manager"

        # action

        manager = ManagerFactory.createManagerForInterface(
            expected_identifier, mock_host_interface, mock_manager_interface_factory, mock_logger)

        # confirm

        mock_manager_interface_factory.mock.instantiate.assert_called_once_with(
            expected_identifier)
        assert_expected_manager(manager)


@pytest.fixture
def assert_expected_manager(mock_host_interface, mock_manager_interface):
    # Assert the expected manager is constructed and is given the
    # expected host session in method calls (`settings()` abused
    # here for this purpose).
    def assert_for_manager(manager):
        expected_host_identifier = "a.host"
        expected_settings = {"some": "settings"}

        mock_host_interface.mock.identifier.return_value = expected_host_identifier

        def assert_expected_host(hostSession):
            assert hostSession.host().identifier() == expected_host_identifier
            return mock.DEFAULT

        mock_manager_interface.mock.settings.side_effect = assert_expected_host
        mock_manager_interface.mock.settings.return_value = expected_settings

        assert manager.settings() == expected_settings

    return assert_for_manager


@pytest.fixture
def a_manager_factory(mock_host_interface, mock_manager_interface_factory, mock_logger):
    return ManagerFactory(mock_host_interface, mock_manager_interface_factory, mock_logger)


@pytest.fixture
def a_cpp_manager_factory(mock_host_interface, mock_manager_interface_factory, mock_logger):
    return CppManagerFactory(mock_host_interface, mock_manager_interface_factory, mock_logger)


@pytest.fixture
def mock_manager_interface_factory(mock_logger, mock_manager_interface):
    factory = MockManagerInterfaceFactory(mock_logger)
    factory.mock.instantiate.return_value = mock_manager_interface
    return factory


class MockManagerInterfaceFactory(ManagerInterfaceFactoryInterface):
    """
    `ManagerInterfaceFactoryInterface` that forwards calls to an
    internal mock.
    @see mock_manager_interface_factory
    """
    def __init__(self, logger):
        ManagerInterfaceFactoryInterface.__init__(self, logger)
        self.mock = mock.create_autospec(
            ManagerInterfaceFactoryInterface, spec_set=True, instance=True)

    def identifiers(self):
        return self.mock.identifiers()

    def instantiate(self, identifier):
        return self.mock.instantiate(identifier)
