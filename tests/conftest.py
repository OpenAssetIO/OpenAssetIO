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
    Removes openassetio modules from the sys.modules cache that
    otherwise mask cyclic dependencies or bleed state from a
    previous test case.
    """
    to_delete = [
        name for name in sys.modules if name.startswith("openassetio")]
    for name in to_delete:
        del sys.modules[name]
