// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd
#include <tuple>

#include <Python.h>
#include <pybind11/embed.h>

#include <openassetio/export.h>

#include <catch2/catch.hpp>
#include <catch2/trompeloeil.hpp>

#include <openassetio/python/converter.hpp>

#include <openassetio/Context.hpp>
#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/Manager.hpp>
#include <openassetio/hostApi/ManagerFactory.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/ConsoleLogger.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/log/SeverityFilter.hpp>
#include <openassetio/managerApi/Host.hpp>
#include <openassetio/managerApi/HostSession.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>
#include <openassetio/trait/TraitsData.hpp>
#include <openassetio/ui/hostApi/UIDelegateImplementationFactoryInterface.hpp>
#include <openassetio/ui/managerApi/UIDelegateInterface.hpp>

/*
 * The below tests exercise the to/from python converter functions.
 * These functions are intended to work with raw CPython, and we want
 * to test them in that manner. However, we occasionally use pybind
 * to create python objects purely for convenience.
 */
namespace py = pybind11;

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace {
constexpr const char* kTestTraitId = "TestTrait";

// You need an indirect macro argument to have expansion happen.
#define STRINGIFY2(s) #s
#define STRINGIFY(s) STRINGIFY2(s)

}  // namespace

SCENARIO("Mutations in one language are reflected in the other") {
  // Cause the openassetio-python lib to be loaded so pybind can cast.
  py::module_::import("openassetio");

  GIVEN("A C++ object casted to a Python object") {
    const trait::TraitsDataPtr traitsData = trait::TraitsData::make();
    PyObject* pyTraitsData = python::converter::castToPyObject(traitsData);
    REQUIRE(pyTraitsData != nullptr);

    WHEN("data is set via the C++ object") {
      traitsData->addTrait(kTestTraitId);

      THEN("Python object reflects that data set") {
        // NOLINTNEXTLINE(cppcoreguidelines-pro-type-vararg)
        PyObject* resultBool = PyObject_CallMethod(pyTraitsData, "hasTrait", "s", kTestTraitId);

        // Use CHECK rather than REQUIRE in order to ensure the Decrefs
        // below actually execute.
        CHECK(PyBool_Check(resultBool));
        CHECK(PyObject_IsTrue(resultBool));
        Py_DECREF(resultBool);
      }
    }

    WHEN("data is set via the Python object") {
      // NOLINTNEXTLINE(cppcoreguidelines-pro-type-vararg)
      PyObject_CallMethod(pyTraitsData, "addTrait", "s", kTestTraitId);

      THEN("C++ object reflects the data set") { CHECK(traitsData->hasTrait(kTestTraitId)); }
    }
    Py_DECREF(pyTraitsData);
  }

  GIVEN("A Python object casted to a C++ object") {
    // Use pybind to conveniently create a CPython object with a ref count of 1.
    const py::object pyClass = py::module_::import("openassetio.trait").attr("TraitsData");
    py::object pyInstance = pyClass();
    PyObject* pyTraitsData = pyInstance.release().ptr();
    const trait::TraitsDataPtr traitsData =
        openassetio::python::converter::castFromPyObject<trait::TraitsData>(pyTraitsData);

    WHEN("data is set via the C++ object") {
      traitsData->addTrait(kTestTraitId);

      THEN("Python object reflects that data set") {
        // NOLINTNEXTLINE(cppcoreguidelines-pro-type-vararg)
        PyObject* resultBool = PyObject_CallMethod(pyTraitsData, "hasTrait", "s", kTestTraitId);

        // Use CHECK rather than REQUIRE in order to ensure the Decrefs
        // below actually execute.
        CHECK(PyBool_Check(resultBool));
        CHECK(PyObject_IsTrue(resultBool));
        Py_DECREF(resultBool);
      }
    }

    WHEN("data is set via the Python object") {
      // NOLINTNEXTLINE(cppcoreguidelines-pro-type-vararg)
      PyObject_CallMethod(pyTraitsData, "addTrait", "s", kTestTraitId);
      THEN("C++ object reflects the data set") { CHECK(traitsData->hasTrait(kTestTraitId)); }
    }
    Py_DECREF(pyTraitsData);
  }
}

SCENARIO("Casting to PyObject extends object lifetime") {
  GIVEN("A Python object casted from a C++ object") {
    trait::TraitsDataPtr traitsData = trait::TraitsData::make();
    traitsData->addTrait(kTestTraitId);
    PyObject* pyTraitsData = python::converter::castToPyObject(traitsData);

    WHEN("C++ reference is destroyed") {
      CHECK(Py_REFCNT(pyTraitsData) == 1);  // Initial condition.
      traitsData.reset();

      THEN("object remains alive and can be operated on via the Python interpreter") {
        CHECK(Py_REFCNT(pyTraitsData) == 1);
        // NOLINTNEXTLINE(cppcoreguidelines-pro-type-vararg)
        PyObject* resultBool = PyObject_CallMethod(pyTraitsData, "hasTrait", "s", kTestTraitId);

        // Use CHECK rather than REQUIRE in order to ensure the Decrefs
        // below actually execute.
        CHECK(PyBool_Check(resultBool));
        CHECK(PyObject_IsTrue(resultBool));
        Py_DECREF(resultBool);
      }
    }
    Py_DECREF(pyTraitsData);
  }
}

SCENARIO("Casting to a C++ object binds object lifetime") {
  GIVEN("A python object") {
    py::module_::import("openassetio");

    // Use pybind to conveniently create a CPython object with a ref count of 1.
    const py::object pyClass = py::module_::import("openassetio.trait").attr("TraitsData");
    py::object pyInstance = pyClass();
    PyObject* pyTraitsData = pyInstance.release().ptr();
    CHECK(Py_REFCNT(pyTraitsData) == 1);

    WHEN("Python object is converted to a C++ object") {
      trait::TraitsDataPtr traitsData =
          openassetio::python::converter::castFromPyObject<trait::TraitsData>(pyTraitsData);

      THEN("Python reference is obtained") { CHECK(Py_REFCNT(pyTraitsData) == 2); }

      AND_WHEN("C++ reference is destroyed") {
        traitsData.reset();

        THEN("Python reference is released") { CHECK(Py_REFCNT(pyTraitsData) == 1); }
      }
    }

    Py_DECREF(pyTraitsData);
  }
}

SCENARIO("Attempting to cast from an incorrect Python type") {
  using hostApi::Manager;
  using hostApi::ManagerPtr;
  namespace converter = python::converter;

  GIVEN("an invalid for casting Python object") {
    // Use pybind to conveniently create a CPython object with a ref count of 1.
    const py::object pyClass = py::module_::import("decimal").attr("Decimal");
    py::object pyInstance = pyClass(1.0);
    // PyDecimal is not a type pybind has been registered to convert.
    PyObject* pyDecimal = pyInstance.release().ptr();

    /*
     * Pybind error messages vary between release and debug mode:
     * "Unable to cast Python instance of type <class 'decimal.Decimal'> to C++
     * type 'openassetio::v1::hostApi::Manager'"
     * vs.
     * "Unable to cast Python instance to C++ type (compile in debug
     * mode for details)"
     */
    WHEN("object is converted to a C++ object") {
      REQUIRE_THROWS_WITH(converter::castFromPyObject<Manager>(pyDecimal),
                          Catch::Matchers::StartsWith("Unable to cast Python instance"));
    }

    Py_DECREF(pyDecimal);
  }

  WHEN("None is converted to a C++ object") {
    const ManagerPtr manager = converter::castFromPyObject<Manager>(Py_None);

    THEN("C++ object pointer is null") { CHECK(manager.get() == nullptr); }
  }
}

// NB: This test is excluded by default and is executed by explicitly
// specifying the [no_openassetio_module] tag to the Catch2 runner
// executable.
// This is because we _must not_ have `_openassetio.so` loaded for these
// tests.
SCENARIO("Error attempting to convert API objects without openassetio module loaded",
         "[.][no_openassetio_module]") {
  GIVEN("A Python environment without openassetio loaded") {
    REQUIRE_FALSE(py::module_::import("sys").attr("modules").contains("openassetio"));

    AND_GIVEN("an OpenAssetIO C++ API object") {
      const trait::TraitsDataPtr traitsData = trait::TraitsData::make();

      WHEN("the C++ object is casted to a Python object") {
        THEN("cast throws expected exception") {
          REQUIRE_THROWS_WITH(openassetio::python::converter::castToPyObject(traitsData),
                              std::string("Unregistered type : openassetio::" STRINGIFY(
                                  OPENASSETIO_CORE_ABI_VERSION) "::trait::TraitsData"));
        }
      }

      AND_GIVEN("A CPython error state is already set") {
        // If the process terminates with a CPython error, pybind will
        // emit an exception on destruction, causing a terminate call.
        // As we explicitly set an error in this test, use a scope to
        // make sure we clean up after ourselves.
        const py::error_scope errorCleanup;

        const std::string errorString = "Test Error";
        // Set the CPython exception.
        PyErr_SetString(PyExc_RuntimeError, errorString.c_str());

        WHEN("the C++ object is casted to a Python object") {
          THEN("cast throws expected exception") {
            REQUIRE_THROWS_WITH(openassetio::python::converter::castToPyObject(traitsData),
                                std::string("Unregistered type : openassetio::" STRINGIFY(
                                    OPENASSETIO_CORE_ABI_VERSION) "::trait::TraitsData"));

            AND_THEN("CPython error state is maintained") {
              // castToPyObject, despite messing with the PyErr state
              // itself, should have correctly reset the exception back.
              CHECK(PyErr_ExceptionMatches(PyExc_RuntimeError));
              const py::error_scope errors;
              CHECK(std::string(py::str(errors.value)) == errorString);
            }
          }
        }
      }
    }
  }
}

namespace {

// clang-format off
using CastableClasses = std::tuple<
    Context,
    trait::TraitsData,
    hostApi::HostInterface,
    hostApi::Manager,
    hostApi::ManagerFactory,
    hostApi::ManagerImplementationFactoryInterface,
    log::ConsoleLogger,
    log::LoggerInterface,
    log::SeverityFilter,
    managerApi::Host,
    managerApi::HostSession,
    managerApi::ManagerInterface,
    ui::hostApi::UIDelegateImplementationFactoryInterface,
    ui::managerApi::UIDelegateInterface
>;
// clang-format on
}  // namespace

// NOLINTNEXTLINE(cppcoreguidelines-avoid-c-arrays,cppcoreguidelines-avoid-non-const-global-variables)
TEMPLATE_LIST_TEST_CASE("Appropriate classes have castFromPyObject functions", "",
                        CastableClasses) {
  // These tests check that the nullptr exception works, but also
  // serve to verify that the functions exist for all expected types.
  PyObject* empty = nullptr;
  REQUIRE_THROWS_WITH(openassetio::python::converter::castFromPyObject<TestType>(empty),
                      std::string("Attempting to cast a nullptr PyObject in "
                                  "openassetio::python::converter::castFromPyObject"));
}

// NOLINTNEXTLINE(cppcoreguidelines-avoid-c-arrays,cppcoreguidelines-avoid-non-const-global-variables)
TEMPLATE_LIST_TEST_CASE("Appropriate classes have castToPyObject functions", "", CastableClasses) {
  // These tests check that nullptrs are converted to None, but also
  // serve to verify that the functions exist for all expected types.
  const typename TestType::Ptr empty = nullptr;
  CHECK(openassetio::python::converter::castToPyObject(empty) == Py_None);
}
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
