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
Testing pybind11's GIL handling behaviour
"""

# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name,c-extension-no-member
# pylint: disable=missing-class-docstring,missing-function-docstring
import threading

# pylint: disable=no-name-in-module
from openassetio import _openassetio_test


class Test_gil:
    # pylint: disable=attribute-defined-outside-init
    def test_when_calling_as_callable_object_in_another_thread_then_doesnt_error(self):
        self.state_to_update = False
        main_thread_id = threading.current_thread().ident

        def update_state():
            assert threading.current_thread().ident != main_thread_id
            self.state_to_update = True

        _openassetio_test.runCallableInThread(update_state)

        assert self.state_to_update is True

    def test_when_calling_as_py_function_in_another_thread_then_doesnt_error(self):
        self.state_to_update = False
        main_thread_id = threading.current_thread().ident

        def update_state():
            assert threading.current_thread().ident != main_thread_id
            self.state_to_update = True

        _openassetio_test.runPyFunctionInThread(update_state)

        assert self.state_to_update is True

    def test_when_calling_as_std_function_in_another_thread_then_doesnt_error(self):
        self.state_to_update = False
        main_thread_id = threading.current_thread().ident

        def update_state():
            assert threading.current_thread().ident != main_thread_id
            self.state_to_update = True

        _openassetio_test.runStdFunctionInThread(update_state)

        assert self.state_to_update is True

    def test_when_calling_bound_member_in_another_thread_then_doesnt_error(self):
        class MyFlag(_openassetio_test.Flag):
            def __init__(self):
                self.value = None
                _openassetio_test.Flag.__init__(self)

            def set(self, value):
                assert threading.current_thread().ident != main_thread_id
                self.value = value

            def get(self):
                return self.value

        flag = MyFlag()
        main_thread_id = threading.current_thread().ident

        returned_flag_value = _openassetio_test.flagInThread(flag)

        assert flag.value is True
        assert returned_flag_value is flag.value
