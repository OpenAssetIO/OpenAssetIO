#   Copyright 2025 The Foundry Visionmongers Ltd
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
These tests check the functionality of the hybrid
HybridPluginSystemUIDelegateImplementationFactory implementation.
"""
from unittest import mock

import pytest
from openassetio import errors

# pylint: disable=unused-argument,too-many-lines,too-many-locals
# pylint: disable=invalid-name,redefined-outer-name,
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=too-many-public-methods


from openassetio.ui.hostApi import UIDelegateImplementationFactoryInterface
from openassetio.ui.managerApi import UIDelegateInterface
from openassetio.ui.pluginSystem import HybridPluginSystemUIDelegateImplementationFactory


class Test_HybridPluginSystemUIDelegateImplementationFactory_init:
    def test_when_None_child_factory_then_raises_error(self, mock_logger, factory_a):
        with pytest.raises(
            errors.InputValidationException,
            match="HybridPluginSystem: UI delegate implementation factory cannot be None",
        ):
            HybridPluginSystemUIDelegateImplementationFactory([factory_a, None], mock_logger)

    def test_when_empty_child_factories_then_raises_error(self, mock_logger):
        with pytest.raises(
            errors.InputValidationException,
            match=(
                "HybridPluginSystem: At least one child UI delegate implementation factory must be"
                " provided"
            ),
        ):
            HybridPluginSystemUIDelegateImplementationFactory([], mock_logger)


class Test_HybridPluginSystemUIDelegateImplementationFactory_identifiers:

    def test_identifiers_from_all_children_deduplicated(self, mock_logger, factory_a, factory_b):
        factory_a.mock.identifiers.return_value = ["a", "c", "b"]
        factory_b.mock.identifiers.return_value = ["b", "c", "d"]

        factory = HybridPluginSystemUIDelegateImplementationFactory(
            [factory_b, factory_a], mock_logger
        )
        assert factory.identifiers() == ["a", "b", "c", "d"]


class Test_HybridPluginSystemUIDelegateImplementationFactory_instantiate:
    def test_when_no_match_from_multiple_child_factories_then_error_raised(
        self, factory_a, factory_b, mock_logger
    ):
        factory_a.mock.identifiers.return_value = ["bar"]
        factory_b.mock.identifiers.return_value = ["baz"]

        factory = HybridPluginSystemUIDelegateImplementationFactory(
            [factory_a, factory_b], mock_logger
        )

        with pytest.raises(
            errors.InputValidationException,
            match="HybridPluginSystem: No plug-in registered with the identifier 'foo'",
        ):
            factory.instantiate("foo")

    def test_when_single_factory_matches_then_uses_that_factorys_interface(
        self, mock_logger, factory_a, factory_b, the_plugin_identifier
    ):
        factory_a.mock.identifiers.return_value = ["a", the_plugin_identifier]
        factory_b.mock.identifiers.return_value = ["b"]

        factory = HybridPluginSystemUIDelegateImplementationFactory(
            [factory_a, factory_b], mock_logger
        )

        actual_ui_delegate_interface = factory.instantiate(the_plugin_identifier)

        factory_a.mock.instantiate.assert_called_once_with(the_plugin_identifier)
        assert not factory_b.mock.instantiate.called
        assert actual_ui_delegate_interface is factory_a.mock.instantiate.return_value

    def test_when_multiple_factories_provided_and_one_matches_then_uses_that_factorys_interface(
        self,
        mock_logger,
        factory_a,
        factory_b,
        the_plugin_identifier,
    ):
        factory_a.mock.identifiers.return_value = ["a"]
        factory_b.mock.identifiers.return_value = ["b", the_plugin_identifier]

        factory = HybridPluginSystemUIDelegateImplementationFactory(
            [factory_a, factory_b], mock_logger
        )

        actual_ui_delegate_interface = factory.instantiate(the_plugin_identifier)

        assert not factory_a.mock.instantiate.called
        factory_b.mock.instantiate.assert_called_once_with(the_plugin_identifier)

        assert actual_ui_delegate_interface is factory_b.mock.instantiate.return_value

    def test_when_multiple_factories_match_then_first_interface_used(
        self, mock_logger, factory_a, factory_b, the_plugin_identifier
    ):
        factory = HybridPluginSystemUIDelegateImplementationFactory(
            [factory_a, factory_b], mock_logger
        )

        actual_ui_delegate_interface = factory.instantiate(the_plugin_identifier)

        factory_a.mock.instantiate.assert_called_once_with(the_plugin_identifier)
        factory_b.mock.instantiate.assert_not_called()
        assert actual_ui_delegate_interface is factory_a.mock.instantiate.return_value

    def test_when_child_factories_go_out_of_scope_then_hybrid_retains_valid_reference(
        self, mock_logger, create_mock_ui_delegate_interface, the_plugin_identifier
    ):
        # I.e. test that PyRetainingSharedPtr is used in C++ to refer to
        # the child factories, so the Python facade is kept alive
        # despite going out of scope.

        def make_factory():
            factory_a = MockUIDelegateImplementationFactory(mock_logger)
            factory_a.mock.identifiers.return_value = [the_plugin_identifier]
            factory_a.mock.instantiate.return_value = create_mock_ui_delegate_interface()

            factory_b = MockUIDelegateImplementationFactory(mock_logger)
            factory_b.mock.identifiers.return_value = [the_plugin_identifier]
            factory_b.mock.instantiate.return_value = create_mock_ui_delegate_interface()

            return HybridPluginSystemUIDelegateImplementationFactory(
                [factory_a, factory_b], mock_logger
            )

        factory = make_factory()

        # Hoping to avoid pybind11 exception "RuntimeError: Tried to
        # call pure virtual function"
        ui_delegate_interface = factory.instantiate(the_plugin_identifier)

        assert isinstance(ui_delegate_interface, UIDelegateInterface)


def hybrid_ui_delegate_interface(hybrid_factory, the_plugin_identifier):
    return hybrid_factory.instantiate(the_plugin_identifier)


@pytest.fixture
def hybrid_factory(factory_a, factory_b, mock_logger):
    return HybridPluginSystemUIDelegateImplementationFactory([factory_a, factory_b], mock_logger)


@pytest.fixture
def factory_a(ui_delegate_interface_a, mock_logger, the_plugin_identifier):
    factory = MockUIDelegateImplementationFactory(mock_logger)
    factory.mock.identifiers.return_value = [the_plugin_identifier]
    factory.mock.instantiate.return_value = ui_delegate_interface_a
    return factory


@pytest.fixture
def factory_b(ui_delegate_interface_b, mock_logger, the_plugin_identifier):
    factory = MockUIDelegateImplementationFactory(mock_logger)
    factory.mock.identifiers.return_value = [the_plugin_identifier]
    factory.mock.instantiate.return_value = ui_delegate_interface_b
    return factory


@pytest.fixture
def ui_delegate_interface_a(create_mock_ui_delegate_interface):
    return create_mock_ui_delegate_interface()


@pytest.fixture
def ui_delegate_interface_b(create_mock_ui_delegate_interface):
    return create_mock_ui_delegate_interface()


@pytest.fixture
def the_plugin_identifier():
    return "org.openassetio.test.plugin"


class MockUIDelegateImplementationFactory(UIDelegateImplementationFactoryInterface):
    """
    `UIDelegateImplementationFactoryInterface` that forwards calls to an
    internal mock.
    """

    def __init__(self, logger):
        UIDelegateImplementationFactoryInterface.__init__(self, logger)
        self.mock = mock.create_autospec(
            UIDelegateImplementationFactoryInterface, spec_set=True, instance=True
        )

    def identifiers(self):
        return self.mock.identifiers()

    def instantiate(self, identifier):
        return self.mock.instantiate(identifier)
