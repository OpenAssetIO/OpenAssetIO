#
#   Copyright 2023 The Foundry Visionmongers Ltd
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
Common test utils for our GIL handling behaviour
"""
# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=invalid-name,c-extension-no-member
# pylint: disable=missing-class-docstring,missing-function-docstring
import inspect

import pytest

# pylint: disable=no-name-in-module
from openassetio import _openassetio, EntityReference, Context
from openassetio.trait import TraitsData


@pytest.fixture
def find_unimplemented_test_cases():
    def finder(target_class, test_class):
        methods = (
            name
            for (name, obj) in inspect.getmembers(target_class)
            if not name.startswith("_") and inspect.isroutine(obj)
        )

        return [
            method
            for method in methods
            if not inspect.ismethod(getattr(test_class, f"test_{method}", None))
        ]

    return finder


@pytest.fixture
def a_threaded_mock_manager_interface(mock_manager_interface):
    return _openassetio._testutils.gil.wrapInThreadedManagerInterface(mock_manager_interface)


@pytest.fixture
def a_context():
    return Context()


@pytest.fixture
def a_traits_data():
    return TraitsData()


@pytest.fixture
def an_entity_reference():
    return EntityReference("")
