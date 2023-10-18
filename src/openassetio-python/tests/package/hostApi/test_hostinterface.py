#
#   Copyright 2013-2023 The Foundry Visionmongers Ltd
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
Tests that cover the openassetio.hostApi.HostInterface class.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
import pytest

from openassetio.hostApi import HostInterface


class Test_HostInterface_identifier:
    def test_is_pure_virtual(self, an_unimplemented_host_interface):
        with pytest.raises(RuntimeError, match="Tried to call pure virtual function"):
            an_unimplemented_host_interface.identifier()


class Test_HostInterface_displayName:
    def test_is_pure_virtual(self, an_unimplemented_host_interface):
        with pytest.raises(RuntimeError, match="Tried to call pure virtual function"):
            an_unimplemented_host_interface.displayName()


@pytest.fixture
def an_unimplemented_host_interface():
    return HostInterface()
