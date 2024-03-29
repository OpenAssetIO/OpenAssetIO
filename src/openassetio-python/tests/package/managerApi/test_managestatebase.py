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
Tests that cover the openassetio.managerApi.ManagerStateBase class.
"""

# pylint: disable=invalid-name
# pylint: disable=missing-class-docstring,missing-function-docstring


from openassetio.managerApi import ManagerStateBase


class Test_ManagerStateBase:
    def test_can_create_derived_class_with_custom_properties(self):
        class TestState(ManagerStateBase):
            def __init__(self, value):
                super().__init__()
                self.__value = value

            def value(self):
                return self.__value

        a_state = TestState(42)
        assert a_state.value() == 42
