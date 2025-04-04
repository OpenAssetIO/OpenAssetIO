// SPDX-License-Identifier: Apache-2.0
// Copyright 2023-2025 The Foundry Visionmongers Ltd
#include <functional>
#include <future>
#include <memory>
#include <utility>

#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <trompeloeil.hpp>

#include <openassetio/hostApi/HostInterface.hpp>
#include <openassetio/hostApi/ManagerImplementationFactoryInterface.hpp>
#include <openassetio/log/LoggerInterface.hpp>
#include <openassetio/managerApi/EntityReferencePagerInterface.hpp>
#include <openassetio/managerApi/ManagerInterface.hpp>

/*
 * Hack trompeloeil to make use of its internals, but provide our own
 * mock implementation body, in order to mock threaded calls.
 *
 * The body starts a thread, and forwards requests to a (Python)
 * wrapped instance in that thread, then waits on the thread and
 * returns the result (see usage of std::async).
 */

#undef TROMPELOEIL_IMPLEMENT_MOCK_
/**
 * Swap `trompeloeil_interface_name` for `Base`, which must be defined
 * on the class as an alias to the base class.
 */
#define TROMPELOEIL_IMPLEMENT_MOCK_(num, name, ...)                                             \
  TROMPELOEIL_MAKE_MOCK_(name, , num,                                                           \
                         decltype(::trompeloeil::nonconst_member_signature(&Base::name))::type, \
                         TROMPELOEIL_SEPARATE(__VA_ARGS__), )

#undef TROMPELOEIL_IMPLEMENT_CONST_MOCK_
/**
 * Swap `trompeloeil_interface_name` for `Base`, which must be defined
 * on the class as an alias to the base class.
 */
#define TROMPELOEIL_IMPLEMENT_CONST_MOCK_(num, name, ...)                                    \
  TROMPELOEIL_MAKE_MOCK_(name, const, num,                                                   \
                         decltype(::trompeloeil::const_member_signature(&Base::name))::type, \
                         TROMPELOEIL_SEPARATE(__VA_ARGS__), )

/**
 * Override body of mock to add our std::async call.
 */
#undef TROMPELOEIL_MAKE_MOCK_
#define TROMPELOEIL_MAKE_MOCK_(name, constness, num, sig, spec, ...)                           \
  ::trompeloeil::return_of_t<TROMPELOEIL_REMOVE_PAREN(sig)> name(                              \
      TROMPELOEIL_PARAM_LIST(num, sig)) constness spec {                                       \
    if (PyGILState_Check()) {                                                                  \
      throw std::runtime_error{"GIL was not released"};                                        \
    }                                                                                          \
    return std::async(std::launch::async, &Base::name, wrapped_.get() TROMPELOEIL_PARAMS(num)) \
        .get();                                                                                \
  }

namespace py = pybind11;

namespace {

/// Used to test calling bound members in another thread.
struct Flag {
  virtual ~Flag() = default;
  virtual void set(bool) = 0;
  virtual bool get() = 0;
};

/// Used to test calling bound members in another thread.
struct PyFlag : Flag {
  void set(bool value) override { PYBIND11_OVERRIDE_PURE(void, Flag, set, value); }
  bool get() override { PYBIND11_OVERRIDE_PURE(bool, Flag, get, /* no args */); }
};

namespace managerApi = openassetio::managerApi;

/*
 * Note: the IMPLEMENT_* macros, below, expand to the TROMPELOEIL_*
 * macros, above.
 */

struct ThreadedManagerInterface : managerApi::ManagerInterface {
  using Base = ManagerInterface;
  static Ptr make(Ptr wrapped) {
    return std::make_shared<ThreadedManagerInterface>(std::move(wrapped));
  }
  explicit ThreadedManagerInterface(Ptr wrapped) : wrapped_{std::move(wrapped)} {}
  Ptr wrapped_;

  IMPLEMENT_CONST_MOCK0(identifier);
  IMPLEMENT_CONST_MOCK0(displayName);
  IMPLEMENT_MOCK1(hasCapability);
  IMPLEMENT_MOCK0(info);
  IMPLEMENT_MOCK2(updateTerminology);
  IMPLEMENT_MOCK1(settings);
  IMPLEMENT_MOCK2(initialize);
  IMPLEMENT_MOCK1(flushCaches);
  IMPLEMENT_MOCK4(managementPolicy);
  IMPLEMENT_MOCK1(createState);
  IMPLEMENT_MOCK2(createChildState);
  IMPLEMENT_MOCK2(persistenceTokenForState);
  IMPLEMENT_MOCK2(stateFromPersistenceToken);
  IMPLEMENT_MOCK2(isEntityReferenceString);
  IMPLEMENT_MOCK5(entityExists);
  IMPLEMENT_MOCK6(entityTraits);
  IMPLEMENT_MOCK7(resolve);
  IMPLEMENT_MOCK6(defaultEntityReference);
  IMPLEMENT_MOCK9(getWithRelationship);
  IMPLEMENT_MOCK9(getWithRelationships);
  IMPLEMENT_MOCK7(preflight);
  IMPLEMENT_MOCK7(register_);
};

struct ThreadedEntityReferencePagerInterface : managerApi::EntityReferencePagerInterface {
  using Base = EntityReferencePagerInterface;
  static Ptr make(Ptr wrapped) {
    return std::make_shared<ThreadedEntityReferencePagerInterface>(std::move(wrapped));
  }
  explicit ThreadedEntityReferencePagerInterface(Ptr wrapped) : wrapped_{std::move(wrapped)} {}
  Ptr wrapped_;

  IMPLEMENT_MOCK1(hasNext);
  IMPLEMENT_MOCK1(get);
  IMPLEMENT_MOCK1(next);
  IMPLEMENT_MOCK1(close);
};

namespace hostApi = openassetio::hostApi;

struct ThreadedHostInterface : hostApi::HostInterface {
  using Base = HostInterface;
  static Ptr make(Ptr wrapped) {
    return std::make_shared<ThreadedHostInterface>(std::move(wrapped));
  }
  explicit ThreadedHostInterface(Ptr wrapped) : wrapped_{std::move(wrapped)} {}
  Ptr wrapped_;

  IMPLEMENT_CONST_MOCK0(identifier);
  IMPLEMENT_CONST_MOCK0(displayName);
  IMPLEMENT_MOCK0(info);
};

namespace log = openassetio::log;

struct ThreadedLoggerInterface : log::LoggerInterface {
  using Base = LoggerInterface;
  static Ptr make(Ptr wrapped) {
    return std::make_shared<ThreadedLoggerInterface>(std::move(wrapped));
  }
  explicit ThreadedLoggerInterface(Ptr wrapped) : wrapped_{std::move(wrapped)} {}
  Ptr wrapped_;

  IMPLEMENT_MOCK2(log);
};

struct ThreadedManagerImplFactory : hostApi::ManagerImplementationFactoryInterface {
  using Base = ManagerImplementationFactoryInterface;
  static Ptr make(log::LoggerInterfacePtr logger, Ptr wrapped) {
    return std::make_shared<ThreadedManagerImplFactory>(std::move(logger), std::move(wrapped));
  }
  explicit ThreadedManagerImplFactory(log::LoggerInterfacePtr logger, Ptr wrapped)
      : ManagerImplementationFactoryInterface(std::move(logger)), wrapped_{std::move(wrapped)} {}
  Ptr wrapped_;

  IMPLEMENT_MOCK0(identifiers);
  IMPLEMENT_MOCK1(instantiate);
};

}  // namespace

extern void registerRunInThread(py::module_& mod) {
  mod.def(
      "runCallableInThread",
      [](const py::object& func) {
        std::async(std::launch::async, [&func]() {
          // Callable py::objects need explicit GIL re-acquire.
          [[maybe_unused]] const py::gil_scoped_acquire gil{};
          func();
        }).get();
      },
      py::arg("func"), py::call_guard<py::gil_scoped_release>());

  mod.def(
      "runPyFunctionInThread",
      [](const py::function& func) {
        std::async(std::launch::async, [&func]() {
          // py::function needs explicit GIL re-acquire, unlike
          // std::function.
          [[maybe_unused]] const py::gil_scoped_acquire gil{};
          func();
        }).get();
      },
      py::arg("func"), py::call_guard<py::gil_scoped_release>());

  mod.def(
      "runStdFunctionInThread",
      [](const std::function<void()>& func) { std::async(std::launch::async, func).get(); },
      py::arg("func"), py::call_guard<py::gil_scoped_release>());

  py::class_<Flag, PyFlag>{mod, "Flag"}
      .def(py::init())
      .def("get", &Flag::get)
      .def("set", &Flag::set);

  mod.def(
      "flagInThread",
      [](Flag& flag) {
        std::async(std::launch::async, [&flag]() { flag.set(true); }).get();

        return flag.get();
      },
      py::arg("func"), py::call_guard<py::gil_scoped_release>());

  auto gil = mod.def_submodule("gil");

  gil.def("wrapInThreadedManagerInterface", &ThreadedManagerInterface::make);
  gil.def("wrapInThreadedEntityReferencePagerInterface",
          &ThreadedEntityReferencePagerInterface::make);
  gil.def("wrapInThreadedHostInterface", &ThreadedHostInterface::make);
  gil.def("wrapInThreadedLoggerInterface", &ThreadedLoggerInterface::make);
  gil.def("wrapInThreadedManagerImplFactory", &ThreadedManagerImplFactory::make);
}
