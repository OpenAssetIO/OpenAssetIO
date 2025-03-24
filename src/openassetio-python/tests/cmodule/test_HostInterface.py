#
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
# pylint: disable=missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name,protected-access
"""
Tests for the Python bindings of the HostInterface class.
"""
from openassetio import constants
from openassetio import _openassetio  # pylint: disable=no-name-in-module


class Test_HostInterface_info:
    def test_when_implemented_in_cpp_then_info_does_not_have_isPython(self):
        host_interface = _openassetio._testutils.createCppHostInterface()

        info = host_interface.info()

        assert constants.kInfoKey_IsPython not in info
