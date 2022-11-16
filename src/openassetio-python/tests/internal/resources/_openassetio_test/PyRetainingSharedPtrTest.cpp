// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd
/**
 * Bindings used for testing PyRetainingSharedPtr behaviour.
 */
#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <PyRetainingSharedPtr.hpp>

namespace py = pybind11;

/**
 * Base class to be inherited in Python.
 */
struct SimpleBaseCppType {
  virtual ~SimpleBaseCppType() = default;
  virtual int value() = 0;
};

/**
 * Pybind trampoline for the SimpleBaseCppType class.
 */
struct PySimpleBaseCppType : SimpleBaseCppType {
  using SimpleBaseCppType::SimpleBaseCppType;
  int value() override { PYBIND11_OVERRIDE_PURE(int, SimpleBaseCppType, value, /* no args */); }
};

/**
 * Container class holding a shared_ptr to a SimpleBaseCppType, to be
 * bound to Python.
 */
struct SimpleCppContainer {
  explicit SimpleCppContainer(std::shared_ptr<SimpleBaseCppType> heldObject)
      : heldObject_{std::move(heldObject)} {}

  static SimpleCppContainer make(std::shared_ptr<SimpleBaseCppType> heldObject) {
    return SimpleCppContainer(std::move(heldObject));
  }

  [[nodiscard]] std::shared_ptr<SimpleBaseCppType> heldObject() const { return heldObject_; }

 private:
  std::shared_ptr<SimpleBaseCppType> heldObject_;
};

/**
 * Container class holding a list of shared_ptrs to SimpleBaseCppType,
 * to be bound to Python.
 */
struct SimpleCppListContainer {
  explicit SimpleCppListContainer(std::vector<std::shared_ptr<SimpleBaseCppType>> heldObjects)
      : heldObjects_{std::move(heldObjects)} {}

  [[nodiscard]] std::vector<std::shared_ptr<SimpleBaseCppType>> heldObjects() const {
    return heldObjects_;
  }

 private:
  std::vector<std::shared_ptr<SimpleBaseCppType>> heldObjects_;
};

/**
 * Duplicate of SimpleCppContainer to be bound to Python with
 * PyRetainingSharedPtr decorators.
 */
struct RetainingSimpleCppContainer : SimpleCppContainer {
  static RetainingSimpleCppContainer makeFromPtrValue(
      std::shared_ptr<SimpleBaseCppType> heldObject) {
    return RetainingSimpleCppContainer(std::move(heldObject));
  }

  static RetainingSimpleCppContainer makeFromConstRefPtr(
      const std::shared_ptr<SimpleBaseCppType>& heldObject) {
    return RetainingSimpleCppContainer(heldObject);
  }

  using SimpleCppContainer::SimpleCppContainer;
};

/**
 * Base class to be inherited in Python.
 */
struct OtherSimpleBaseCppType {
  virtual ~OtherSimpleBaseCppType() = default;
  virtual int otherValue() = 0;
};

/**
 * Pybind trampoline for the OtherSimpleBaseCppType class.
 */
struct PyOtherSimpleBaseCppType : OtherSimpleBaseCppType {
  using OtherSimpleBaseCppType::OtherSimpleBaseCppType;
  int otherValue() override {
    PYBIND11_OVERRIDE_PURE(int, OtherSimpleBaseCppType, value, /* no args */);
  }
};

/**
 * Container class holding multiple shared_ptrs, to be bound to Python.
 */
struct RetainingMultiElementCppContainer {
  explicit RetainingMultiElementCppContainer(std::shared_ptr<SimpleBaseCppType> heldObject1,
                                             std::shared_ptr<OtherSimpleBaseCppType> heldObject2,
                                             std::shared_ptr<SimpleBaseCppType> heldObject3)
      : heldObject1_{std::move(heldObject1)},
        heldObject2_{std::move(heldObject2)},
        heldObject3_{std::move(heldObject3)} {}
  ~RetainingMultiElementCppContainer() = default;

  static RetainingMultiElementCppContainer make(
      std::shared_ptr<SimpleBaseCppType> heldObject1, [[maybe_unused]] bool ignored,
      std::shared_ptr<OtherSimpleBaseCppType> heldObject2,
      std::shared_ptr<SimpleBaseCppType> heldObject3) {
    return RetainingMultiElementCppContainer(std::move(heldObject1), std::move(heldObject2),
                                             std::move(heldObject3));
  }

  [[nodiscard]] std::shared_ptr<SimpleBaseCppType> heldObject1() const { return heldObject1_; }
  [[nodiscard]] std::shared_ptr<OtherSimpleBaseCppType> heldObject2() const {
    return heldObject2_;
  }
  [[nodiscard]] std::shared_ptr<SimpleBaseCppType> heldObject3() const { return heldObject3_; }

 private:
  std::shared_ptr<SimpleBaseCppType> heldObject1_;
  std::shared_ptr<OtherSimpleBaseCppType> heldObject2_;
  std::shared_ptr<SimpleBaseCppType> heldObject3_;
};

/**
 * Duplicate of SimpleCppListContainer to be bound to Python with
 * PyRetainingSharedPtr decorators.
 */
struct RetainingSimpleCppListContainer : SimpleCppListContainer {
  using SimpleCppListContainer::SimpleCppListContainer;
};

/**
 * Base class for a factory that creates SimpleBaseCppType objects, with
 * the creation implemented in a Python subclass, but called through
 * C++.
 */
struct SimpleBaseCppFactory {
  virtual ~SimpleBaseCppFactory() = default;
  virtual std::shared_ptr<SimpleBaseCppType> createNewObject() = 0;

  std::shared_ptr<SimpleBaseCppType> createNewObjectInDerivedInstance() {
    return createNewObject();
  }
};

/**
 * Pybind trampoline for SimpleBaseCppFactory.
 */
struct PySimpleBaseCppFactory : SimpleBaseCppFactory {
  using SimpleBaseCppFactory::SimpleBaseCppFactory;
  std::shared_ptr<SimpleBaseCppType> createNewObject() override {
    PYBIND11_OVERRIDE_PURE(
        std::shared_ptr<SimpleBaseCppType>, SimpleBaseCppFactory, createNewObject,
        /* no args */);
  }
};

/**
 * Duplicate of SimpleBaseCppFactory to be bound to Python with
 * PyRetainingSharedPtr return type..
 */
struct RetainingSimpleBaseCppFactory : SimpleBaseCppFactory {
  using SimpleBaseCppFactory::SimpleBaseCppFactory;
};

/**
 * Pybind trampoline for RetainingSimpleBaseCppFactory.
 *
 * The smart pointer type given as the return type for the
 * PYBIND11_OVERRIDE_PURE macro is overridden to be a
 * PyRetainingSharedPtr.
 */
struct PyRetainingSimpleBaseCppFactory : RetainingSimpleBaseCppFactory {
  using RetainingSimpleBaseCppFactory::RetainingSimpleBaseCppFactory;
  std::shared_ptr<SimpleBaseCppType> createNewObject() override {
    PYBIND11_OVERRIDE_PURE(openassetio::PyRetainingSharedPtr<SimpleBaseCppType>,
                           RetainingSimpleBaseCppFactory, createNewObject,
                           /* no args */);
  }
};

/**
 * A SimpleBaseCppType that calls a given Python callback in its
 * destructor.
 */
struct DeathwatchedSimpleCppType : SimpleBaseCppType {
  DeathwatchedSimpleCppType() = default;

  explicit DeathwatchedSimpleCppType(pybind11::function watcher) : watcher_{std::move(watcher)} {}
  ~DeathwatchedSimpleCppType() override { watcher_(); }  // NOLINT(bugprone-exception-escape)

  py::function watcher_;
};

/**
 * Pybind trampoline for the DeathwatchedSimpleCppType class.
 */
struct PyDeathwatchedSimpleCppType : DeathwatchedSimpleCppType {
  using DeathwatchedSimpleCppType::DeathwatchedSimpleCppType;
  int value() override {
    PYBIND11_OVERRIDE_PURE(int, DeathwatchedSimpleCppType, value, /* no args */);
  }
};

void registerPyRetainingSharedPtrTestTypes(const py::module_& mod) {
  py::class_<SimpleBaseCppType, std::shared_ptr<SimpleBaseCppType>, PySimpleBaseCppType>(
      mod, "SimpleBaseCppType")
      .def(py::init())
      .def("value", &SimpleBaseCppType::value);

  py::class_<SimpleCppContainer>(mod, "SimpleCppContainer")
      .def(py::init<std::shared_ptr<SimpleBaseCppType>>())
      .def_static("make", &SimpleCppContainer::make)
      .def("heldObject", &SimpleCppContainer::heldObject);

  py::class_<SimpleCppListContainer>(mod, "SimpleCppListContainer")
      .def(py::init<std::vector<std::shared_ptr<SimpleBaseCppType>>>())
      .def("heldObjects", &SimpleCppListContainer::heldObjects);

  py::class_<SimpleBaseCppFactory, PySimpleBaseCppFactory>(mod, "SimpleBaseCppFactory")
      .def(py::init())
      .def("createNewObjectInDerivedInstance",
           &SimpleBaseCppFactory::createNewObjectInDerivedInstance);

  py::class_<RetainingSimpleCppContainer>(mod, "PyRetainingSimpleCppContainer")
      .def(py::init<openassetio::PyRetainingSharedPtr<SimpleBaseCppType>>())
      .def_static("makeFromPtrValue",
                  openassetio::RetainPyArgs<std::shared_ptr<SimpleBaseCppType>>::forFn<
                      &RetainingSimpleCppContainer::makeFromPtrValue>())
      .def_static("makeFromConstRefPtr",
                  openassetio::RetainPyArgs<std::shared_ptr<SimpleBaseCppType>>::forFn<
                      &RetainingSimpleCppContainer::makeFromConstRefPtr>())
      .def("heldObject", &RetainingSimpleCppContainer::heldObject);

  py::class_<OtherSimpleBaseCppType, std::shared_ptr<OtherSimpleBaseCppType>,
             PyOtherSimpleBaseCppType>(mod, "OtherSimpleBaseCppType")
      .def(py::init())
      .def("otherValue", &OtherSimpleBaseCppType::otherValue);

  py::class_<RetainingMultiElementCppContainer>(mod, "PyRetainingMultiElementCppContainer")
      .def(py::init<openassetio::PyRetainingSharedPtr<SimpleBaseCppType>,
                    openassetio::PyRetainingSharedPtr<OtherSimpleBaseCppType>,
                    openassetio::PyRetainingSharedPtr<SimpleBaseCppType>>())
      .def_static("make", openassetio::RetainPyArgs<std::shared_ptr<SimpleBaseCppType>,
                                                    std::shared_ptr<OtherSimpleBaseCppType>>::
                              forFn<&RetainingMultiElementCppContainer::make>())
      .def("heldObject1", &RetainingMultiElementCppContainer::heldObject1)
      .def("heldObject2", &RetainingMultiElementCppContainer::heldObject2)
      .def("heldObject3", &RetainingMultiElementCppContainer::heldObject3);

  py::class_<RetainingSimpleCppListContainer>(mod, "PyRetainingSimpleCppListContainer")
      .def(py::init([](std::vector<openassetio::PyRetainingSharedPtr<SimpleBaseCppType>> list) {
        return RetainingSimpleCppListContainer{{list.begin(), list.end()}};
      }))
      .def("heldObjects", &RetainingSimpleCppListContainer::heldObjects);

  py::class_<RetainingSimpleBaseCppFactory, PyRetainingSimpleBaseCppFactory>(
      mod, "PyRetainingSimpleBaseCppFactory")
      .def(py::init())
      .def("createNewObjectInDerivedInstance",
           &RetainingSimpleBaseCppFactory::createNewObjectInDerivedInstance);

  py::class_<DeathwatchedSimpleCppType, SimpleBaseCppType,
             std::shared_ptr<DeathwatchedSimpleCppType>, PyDeathwatchedSimpleCppType>(
      mod, "DeathwatchedSimpleCppType")
      .def(py::init<py::function>())
      .def("value", &SimpleBaseCppType::value);
}
