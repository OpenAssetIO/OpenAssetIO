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
Tests of C++ binding utilities, which require dummy C++ classes that
shouldn't be included in the main sources.
"""

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
import weakref
from unittest import mock

import pytest

from openassetio import _openassetio_test  # pylint: disable=no-name-in-module


class Test_PyRetainingSharedPtr_arg:
    def test_when_not_using_PyRetainingSharedPtr_in_constructor_then_python_implementation_is_lost(
        self,
    ):
        container = _openassetio_test.SimpleCppContainer(SimpleCppType())
        element = container.heldObject()

        with pytest.raises(RuntimeError) as err:
            element.value()

        assert str(err.value) == 'Tried to call pure virtual function "SimpleBaseCppType::value"'

    def test_when_not_using_PyRetainingSharedPtr_in_factory_then_python_implementation_is_lost(
        self,
    ):
        container = _openassetio_test.SimpleCppContainer.make(SimpleCppType())
        element = container.heldObject()

        with pytest.raises(RuntimeError) as err:
            element.value()

        assert str(err.value) == 'Tried to call pure virtual function "SimpleBaseCppType::value"'

    def test_when_not_using_PyRetainingSharedPtr_in_list_then_python_implementation_is_lost(self):
        container = _openassetio_test.SimpleCppListContainer([SimpleCppType(), SimpleCppType()])
        elements = container.heldObjects()

        with pytest.raises(RuntimeError) as err:
            elements[0].value()

        assert str(err.value) == 'Tried to call pure virtual function "SimpleBaseCppType::value"'

    def test_when_using_constructor_then_TypeError_reports_expected_type_in_error_message(self):
        with pytest.raises(TypeError) as err:
            _openassetio_test.PyRetainingSimpleCppContainer(123)

        assert "SimpleBaseCppType" in str(err.value)

    def test_when_using_factory_then_TypeError_reports_expected_type_in_error_message(self):
        with pytest.raises(TypeError) as err:
            _openassetio_test.PyRetainingSimpleCppContainer.makeFromPtrValue(123)

        assert "SimpleBaseCppType" in str(err.value)

    def test_when_using_constructor_then_python_implementation_is_retained(self):
        container = _openassetio_test.PyRetainingSimpleCppContainer(SimpleCppType())
        element = container.heldObject()

        assert element.value() == 2

    def test_when_using_factory_then_python_implementation_is_retained(self):
        container = _openassetio_test.PyRetainingSimpleCppContainer.makeFromPtrValue(
            SimpleCppType()
        )
        element = container.heldObject()

        assert element.value() == 2

    def test_when_using_factory_taking_const_ref_argument_then_python_implementation_is_retained(
        self,
    ):
        container = _openassetio_test.PyRetainingSimpleCppContainer.makeFromConstRefPtr(
            SimpleCppType()
        )
        element = container.heldObject()

        assert element.value() == 2

    def test_when_using_multi_arg_constructor_then_python_implementation_is_retained(self):
        container = _openassetio_test.PyRetainingMultiElementCppContainer(
            SimpleCppType(), OtherSimpleCppType(), SimpleCppType()
        )
        element1 = container.heldObject1()
        element2 = container.heldObject2()
        element3 = container.heldObject3()

        assert element1.value() == 2
        assert element2.otherValue() == 3
        assert element3.value() == 2

    def test_when_using_multi_arg_factory_then_python_implementation_is_retained(self):
        container = _openassetio_test.PyRetainingMultiElementCppContainer.make(
            # Note: the False has no effect, just used to check
            # signature matching.
            SimpleCppType(),
            False,
            OtherSimpleCppType(),
            SimpleCppType(),
        )

        element1 = container.heldObject1()
        element2 = container.heldObject2()
        element3 = container.heldObject3()

        assert element1.value() == 2
        assert element2.otherValue() == 3
        assert element3.value() == 2

    def test_when_using_list_container_then_python_implementation_is_retained(self):
        container = _openassetio_test.PyRetainingSimpleCppListContainer(
            [SimpleCppType(), SimpleCppType()]
        )
        elements = container.heldObjects()

        assert len(elements) == 2
        assert elements[0].value() == 2
        assert elements[1].value() == 2


class Test_PyRetainingSharedPtr_return:
    def test_when_not_using_PyRetainingSharedPtr_then_python_implementation_is_lost(self):
        factory = SimpleBaseCppFactory()
        element = factory.createNewObjectInDerivedInstance()

        with pytest.raises(RuntimeError) as err:
            element.value()

        assert str(err.value) == 'Tried to call pure virtual function "SimpleBaseCppType::value"'

    def test_when_using_PyRetainingSharedPtr_then_python_implementation_is_retained(self):
        factory = PyRetainingSimpleCppFactory()
        element = factory.createNewObjectInDerivedInstance()

        assert element.value() == 2


class Test_PyRetainingSharedPtr_cleanup:
    def test_when_container_goes_out_of_scope_then_python_and_cpp_objects_destroyed(self):
        """
        Create a C++ container with an element, let the container go out
        of scope and be destroyed, and check the element is destroyed in
        both C++ and Python.
        """
        # pylint: disable=attribute-defined-outside-init

        # For checking Python instance destruction.
        self.weak_ref = None
        # For checking C++ instance destruction
        self.death_watcher = mock.Mock()

        def create_container():
            # DeathwatchedCppType takes a callback that will be called
            # in its destructor.
            element = DeathwatchedSimpleCppType(self.death_watcher)
            self.weak_ref = weakref.ref(element)

            container = _openassetio_test.PyRetainingSimpleCppContainer(element)

            # Double-check
            assert element.value() == 3
            assert self.weak_ref().value() == 3
            self.death_watcher.assert_not_called()

            return container

        def create_then_forget_container():
            container = create_container()  # pylint: disable=unused-variable

            # Double-check
            assert self.weak_ref().value() == 3
            self.death_watcher.assert_not_called()

        create_then_forget_container()

        assert self.weak_ref() is None
        self.death_watcher.assert_called()

    def test_when_factory_feeds_container_and_container_destroyed_then_cpp_element_destroyed(self):
        """
        Have a C++ container use a C++ factory to create an element,
        let the container go out of scope and be destroyed, and check
        the element is destroyed in both C++ and Python.
        """
        # pylint: disable=attribute-defined-outside-init

        # For checking Python instance destruction.
        self.weak_ref = None
        # For checking C++ instance destruction
        self.death_watcher = mock.Mock()

        def create_container():
            # Create element with Python factory.
            # createNewObjectInDerivedInstance calls createObject on
            # the Python class via the C++ trampoline. Then:
            # * Pybind will initialise the PyObject with a shared_ptr.
            # * When the Python createObject method returns, pybind will
            #   "cast" the Python object to PyRetainingSharedPtr.
            # * The createObject trampoline will then return a
            #   shared_ptr constructed from the PyRetainingSharedPtr.
            # * createNewObjectInDerivedInstance thus receives a
            #   shared_ptr as it expects, and pybind converts this to
            #   the Python object `element` below.
            element = PyRetainingDeathwatchedFactory(
                self.death_watcher
            ).createNewObjectInDerivedInstance()
            self.weak_ref = weakref.ref(element)

            # Store element in container. `element` will be "cast" to a
            # new PyRetainingSharedPtr.
            container = _openassetio_test.PyRetainingSimpleCppContainer(element)

            # Double-check
            assert element.value() == 3
            assert self.weak_ref().value() == 3
            self.death_watcher.assert_not_called()

            return container

        def create_then_forget_container():
            container = create_container()  # pylint: disable=unused-variable

            # Double-check
            assert self.weak_ref().value() == 3
            self.death_watcher.assert_not_called()

        create_then_forget_container()

        assert self.weak_ref() is None
        self.death_watcher.assert_called()


class SimpleCppType(_openassetio_test.SimpleBaseCppType):
    def value(self):
        return 2


class OtherSimpleCppType(_openassetio_test.OtherSimpleBaseCppType):
    def otherValue(self):
        return 3


class SimpleBaseCppFactory(_openassetio_test.SimpleBaseCppFactory):
    def createNewObject(self):
        return SimpleCppType()


class PyRetainingSimpleCppFactory(_openassetio_test.PyRetainingSimpleBaseCppFactory):
    def createNewObject(self):
        return SimpleCppType()


class DeathwatchedSimpleCppType(_openassetio_test.DeathwatchedSimpleCppType):
    def value(self):
        return 3


class PyRetainingDeathwatchedFactory(_openassetio_test.PyRetainingSimpleBaseCppFactory):
    def __init__(self, callback):
        _openassetio_test.PyRetainingSimpleBaseCppFactory.__init__(self)
        self.__callback = callback

    def createNewObject(self):
        return DeathwatchedSimpleCppType(self.__callback)
