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
Shared fixtures/code for pytest cases.
"""

import sys

import pytest

# pylint: disable=invalid-name


@pytest.fixture
def unload_openassetio_modules():
    """
    Temporarily removes openassetio modules from the sys.modules cache
    that otherwise mask cyclic dependencies or bleed state from a
    previous test case.

    We restore them afterwards to avoid issues where module-level
    imports in preceding tests end up with references to the deleted
    module. This causes `isinstance` and others to fail as the compared
    classes are at different addresses.
    """
    to_delete = {
        name: module for name, module in sys.modules.items() if name.startswith("openassetio")
    }
    # Remove the target modules from the cache
    for name in to_delete.keys():
        del sys.modules[name]
    # Yield to allow the target test to run
    yield
    # Restore the previously imported modules
    for name, module in to_delete.items():
        sys.modules[name] = module
