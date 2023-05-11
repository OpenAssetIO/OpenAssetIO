// SPDX-License-Identifier: Apache-2.0
// Copyright 2022 The Foundry Visionmongers Ltd

// Check if needed

#include <pybind11/embed.h>

#include <openassetio/export.h>

#include <catch2/catch.hpp>
#include <catch2/trompeloeil.hpp>

#include <openassetio/python/converter/converters.hpp>

#include <openassetio/Context.hpp>
#include <openassetio/TraitsData.hpp>
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
#include <openassetio/managerApi/ManagerStateBase.hpp>
#include <openassetio/python/hostApi.hpp>

namespace py = pybind11;

namespace openassetio {
inline namespace OPENASSETIO_CORE_ABI_VERSION {
namespace {

struct MockManagerInterface : trompeloeil::mock_interface<managerApi::ManagerInterface> {
  IMPLEMENT_CONST_MOCK0(identifier);
  IMPLEMENT_CONST_MOCK0(displayName);
  IMPLEMENT_MOCK2(initialize);
  IMPLEMENT_CONST_MOCK3(managementPolicy);
  IMPLEMENT_CONST_MOCK2(isEntityReferenceString);
  IMPLEMENT_MOCK6(resolve);
  IMPLEMENT_MOCK6(preflight);
  IMPLEMENT_MOCK6(register_);  // NOLINT(readability-identifier-naming)
};

struct MockLogger : trompeloeil::mock_interface<openassetio::log::LoggerInterface> {
  IMPLEMENT_MOCK2(log);
};

struct MockHostInterface : trompeloeil::mock_interface<hostApi::HostInterface> {
  IMPLEMENT_CONST_MOCK0(identifier);
  IMPLEMENT_CONST_MOCK0(displayName);
  IMPLEMENT_CONST_MOCK0(info);
};

struct MockLoggerInterface : trompeloeil::mock_interface<log::LoggerInterface> {
  IMPLEMENT_MOCK2(log);
};

/**
 * Fixture providing a Manager instance injected with mock dependencies.
 */
struct ManagerFixture {
  const std::shared_ptr<managerApi::ManagerInterface> managerInterface =
      std::make_shared<openassetio::MockManagerInterface>();

  // For convenience, to avoid casting all the time in tests.
  MockManagerInterface& mockManagerInterface =
      static_cast<openassetio::MockManagerInterface&>(*managerInterface);

  // Create a HostSession with our mock HostInterface
  const managerApi::HostSessionPtr hostSession = managerApi::HostSession::make(
      managerApi::Host::make(std::make_shared<openassetio::MockHostInterface>()),
      std::make_shared<openassetio::MockLoggerInterface>());

  // Create the Manager under test.
  const hostApi::ManagerPtr manager = hostApi::Manager::make(managerInterface, hostSession);

  // For convenience, since almost every method takes a Context.
  const openassetio::ContextPtr context{openassetio::Context::make()};
};

}  // namespace

SCENARIO("Converting C++ API Objects to Python API Objects") {
  GIVEN("A c++ manager object") {
    const openassetio::ManagerFixture fixture;
    WHEN("The manager  is casted to a python object") {
      PyObject* pyManagerFromCast =
          openassetio::python::converter::castToPyObject(fixture.manager);
      THEN("The python has a singular ref-count") { CHECK(Py_REFCNT(pyManagerFromCast) == 1); }
      AND_THEN("The python object can be operated on via the python interpreter") {
        REQUIRE_CALL(fixture.mockManagerInterface, identifier()).LR_RETURN("Identifier");
        PyObject* identifier = PyObject_CallMethod(pyManagerFromCast, "identifier", nullptr);
        PyObject* str = PyUnicode_AsEncodedString(identifier, "utf-8", "~E~");
        const char* bytes = PyBytes_AS_STRING(str);
        CHECK_THAT(bytes, Catch::Equals("Identifier"));
      }
    }
  }
  GIVEN("A python object casted from a c++ object") {
    WHEN("The c++ object has fallen out of scope") {
      PyObject* pyManagerFromCast = nullptr;
      openassetio::MockManagerInterface* mockManager = nullptr;
      {
        const openassetio::ManagerFixture fixture;
        pyManagerFromCast = openassetio::python::converter::castToPyObject(fixture.manager);
        mockManager = &fixture.mockManagerInterface;
        CHECK(Py_REFCNT(pyManagerFromCast) == 1);
      }
      THEN("The python object remains alive and can be operated upon") {
        CHECK(Py_REFCNT(pyManagerFromCast) == 1);
        REQUIRE_CALL(*mockManager, identifier()).LR_RETURN("Identifier");
        PyObject* identifier = PyObject_CallMethod(pyManagerFromCast, "identifier", nullptr);
        PyObject* str = PyUnicode_AsEncodedString(identifier, "utf-8", "~E~");
        const char* bytes = PyBytes_AS_STRING(str);
        CHECK_THAT(bytes, Catch::Equals("Identifier"));
      }
    }
  }
}

SCENARIO("Converting Python API Objects to C++ API Objects") {
  GIVEN("A python manager object") {
    const openassetio::ManagerFixture fixture;

    // Create a python manager and release it, to simulate an unmanaged
    // PyObject being provided to us.
    const py::object pyClass = py::module_::import("openassetio.hostApi.Manager").attr("Manager");
    py::object pyInstance = pyClass(fixture.managerInterface, fixture.hostSession);
    PyObject* pyManager = pyInstance.release().ptr();
    CHECK(Py_REFCNT(pyManager) == 1);

    WHEN("The manager is converted to a C++ object") {
      openassetio::hostApi::ManagerPtr manager =
          openassetio::python::converter::castFromPyObject<openassetio::hostApi::Manager>(
              pyManager);

      THEN("The manager can be operated upon using the c++ runtime.") {
        REQUIRE_CALL(fixture.mockManagerInterface, identifier()).LR_RETURN("Identifier");
        CHECK(manager->identifier() == "Identifier");
      }
      AND_THEN("The python manager reference count has been increased") {
        CHECK(Py_REFCNT(pyManager) == 2);
      }
    }
    AND_WHEN("The manager falls out of scope") {
      THEN("The python manager reference count is reduced") { CHECK(Py_REFCNT(pyManager) == 1); }
    }
  }
  GIVEN("an invalid for casting python object") {
    // Create a python manager and release it, to simulate an unmanaged
    // PyObject being provided to us.
    py::object pyClass = py::module_::import("decimal").attr("Decimal");
    py::object pyInstance = pyClass(1.0);
    PyObject* pyDecimal = pyInstance.release().ptr();

    WHEN("The object is converted to a C++ object") {
      REQUIRE_THROWS_WITH(
          openassetio::python::converter::castFromPyObject<openassetio::hostApi::Manager>(
              pyDecimal),
          std::string("Could not cast pyObject to type ") +
              typeid(openassetio::hostApi::Manager).name());
    }
  }
}

namespace {

#define CLASS_AND_PTRS(Class) std::tuple<Class, Class##Ptr, Class##ConstPtr>

namespace hostApi = openassetio::hostApi;
namespace log = openassetio::log;
namespace managerApi = openassetio::managerApi;

// clang-format off

using ClassesWithPtrAlias = std::tuple<
    CLASS_AND_PTRS(openassetio::Context),
    CLASS_AND_PTRS(openassetio::TraitsData),
    CLASS_AND_PTRS(hostApi::HostInterface),
    CLASS_AND_PTRS(hostApi::Manager),
    CLASS_AND_PTRS(hostApi::ManagerFactory),
    CLASS_AND_PTRS(hostApi::ManagerImplementationFactoryInterface),
    CLASS_AND_PTRS(log::ConsoleLogger),
    CLASS_AND_PTRS(log::LoggerInterface),
    CLASS_AND_PTRS(log::SeverityFilter),
    CLASS_AND_PTRS(managerApi::Host),
    CLASS_AND_PTRS(managerApi::HostSession),
    CLASS_AND_PTRS(managerApi::ManagerInterface),
    CLASS_AND_PTRS(managerApi::ManagerStateBase)
>;
}  // namespace

// clang-format on
TEMPLATE_LIST_TEST_CASE("Appropriate classes have castFromPyObject functions", "",
                        ClassesWithPtrAlias) {
  using Class = std::tuple_element_t<0, TestType>;

  // These tests do check that the nullptr exception works, but also
  // serve to verify that the functions exist for all expected types.
  PyObject* empty = nullptr;
  REQUIRE_THROWS_WITH(openassetio::python::converter::castFromPyObject<Class>(empty),
                      std::string("pyObject cannot be null"));
}

TEMPLATE_LIST_TEST_CASE("Appropriate classes have castToPyObject functions", "",
                        ClassesWithPtrAlias) {
  using ClassPtr = std::tuple_element_t<1, TestType>;

  // These tests do check that the nullptr exception works, but also
  // serve to verify that the functions exist for all expected types.
  ClassPtr empty = nullptr;
  REQUIRE_THROWS_WITH(openassetio::python::converter::castToPyObject(empty),
                      std::string("objectPtr cannot be null"));
}

/*
using ClassesWithPtrAlias = std::tuple<
    // CLASS_AND_PTRS(openassetio::Context),
    CLASS_AND_PTRS(hostApi::Manager)
>;
// clang-format on


template <typename T>
using kHasToPyObjectT =
    decltype(openassetio::python::converter::castToPyObject(std::declval<T>()));

template <typename T, typename = std::void_t<>>
struct HasCastToPyObject : std::false_type {};

template <typename T>
struct HasCastToPyObject<T, std::void_t<kHasToPyObjectT<T>>> : std::true_type {};

template <typename T>
inline constexpr bool kHasCastToPyObjectV = HasCastToPyObject<T>::value;

struct HasCastToPyObject {
 private:
  template <class T, class Dummy = decltype(openassetio::python::converter::castToPyObject<T>(
                         std::declval<T&>()))>

  static constexpr bool exists(int thing) {
    return true;
  }

  template <class T>
  static constexpr bool exists(char thing) {
    return false;
  }

 public:
  template <class T>
  static constexpr bool check() {
    constexpr int kNoMatter = 42;
    return exists<T>(kNoMatter);
  }
};

}  // namespace

TEMPLATE_LIST_TEST_CASE("Appropriate classes have shared_ptr aliases", "", ClassesWithPtrAlias) {
  // using Class = std::tuple_element_t<0, TestType>;
  // using ClassPtr = std::tuple_element_t<1, TestType>;
  // using ClassConstPtr = std::tuple_element_t<2, TestType>;

  static_assert(HasCastToPyObject::check<openassetio::hostApi::ManagerPtr>());
  static_assert(HasCastToPyObject::check<std::string>());

  constexpr int kNumber = 5;
  auto* val = openassetio::python::converter::castToPyObject(kNumber);
  REQUIRE(val != nullptr);
  // static_assert(kHasCastToPyObject<std::shared_ptr<openassetio::hostApi::Manager>>());

  WHEN("thing") {
    //  STATIC_REQUIRE(kHasCastToPyObject<std::shared_ptr<openassetio::hostApi::Manager>>());
  }
}
*/
}  // namespace OPENASSETIO_CORE_ABI_VERSION
}  // namespace openassetio
