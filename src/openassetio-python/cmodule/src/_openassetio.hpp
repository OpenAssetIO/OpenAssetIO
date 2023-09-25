// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2023 The Foundry Visionmongers Ltd
/**
 * Python binding bootstrap functions and typedefs.
 */
#pragma once

#include <memory>

#include <pybind11/pybind11.h>

#include <openassetio/typedefs.hpp>

#include "PyRetainingSharedPtr.hpp"

OPENASSETIO_FWD_DECLARE(ManagerStateBase)
OPENASSETIO_FWD_DECLARE(managerApi, ManagerInterface)
OPENASSETIO_FWD_DECLARE(managerApi, EntityReferencePagerInterface)
OPENASSETIO_FWD_DECLARE(log, LoggerInterface)
OPENASSETIO_FWD_DECLARE(hostApi, HostInterface)
OPENASSETIO_FWD_DECLARE(hostApi, ManagerImplementationFactoryInterface)

/**
 * Similar to PYBIND11_OVERRIDE, but allows different arguments to be
 * given to the Python implementation and the C++ fallback (base
 * class) implementation.
 *
 * For example, this is useful to decorate std::function callbacks
 * with `PyRetainingSharedPtr`s, so that Python objects are kept alive
 * as they pass through C++ callbacks.
 *
 * The CppArgs parameter must be a parentheses-enclosed,
 * comma-separated, list of arguments. These are given to the C++ base
 * class implementation, if no Python override is found.
 *
 * All remaining arguments following the CppArgs (not
 * parentheses-enclosed) are passed to the Python override
 * implementation, if one exists.
 */
#define OPENASSETIO_PYBIND11_OVERRIDE_ARGS(Ret, Class, Fn, CppArgs, ... /* PyArgs */) \
  PYBIND11_OVERRIDE_IMPL(PYBIND11_TYPE(Ret), PYBIND11_TYPE(Class), #Fn, __VA_ARGS__); \
  return Class::Fn CppArgs

/**
 * Declare a `RetainPyArgs` alias with common template arguments.
 *
 * The template arguments are those types that we expect to be derived
 * from in Python, and where the associated Python instance(s) must not
 * be destroyed, at least until there are no more references in C++.
 *
 * This alias can then be used as a convenience in `.def(...)` calls
 * without having to re-specify the list of types to match against
 * the arguments of the decorated function.
 *
 * @see PyRetainingSharedPtr
 * @see RetainPyArgs
 */
using RetainCommonPyArgs = openassetio::RetainPyArgs<
    openassetio::log::LoggerInterfacePtr, openassetio::ManagerStateBasePtr,
    openassetio::managerApi::ManagerInterfacePtr, openassetio::hostApi::HostInterfacePtr,
    openassetio::hostApi::ManagerImplementationFactoryInterfacePtr,
    openassetio::managerApi::EntityReferencePagerInterfacePtr>;

/// Concise pybind alias.
namespace py = pybind11;

/// Register constants for use as dict keys.
void registerAccess(const py::module& mod);

/// Register constants for use as dict keys.
void registerConstants(const py::module& mod);

/// Register the LoggerInterface class with Python.
void registerLoggerInterface(const py::module& mod);

/// Register the ConsoleLogger class with Python.
void registerConsoleLogger(const py::module& mod);

/// Register the SeverityFilter class with Python.
void registerSeverityFilter(const py::module& mod);

/// Register the Context class with Python.
void registerContext(const py::module& mod);

/// Register the HostInterface class with Python.
void registerHostInterface(const py::module& mod);

/// Register the Host class with Python.
void registerHost(const py::module& mod);

/// Register the HostSession class with Python.
void registerHostSession(const py::module& mod);

/// Register the ManagerInterface class with Python.
void registerManagerInterface(const py::module& mod);

/// Register the ManagerImplementationFactoryInterface class with Python.
void registerManagerImplementationFactoryInterface(const py::module& mod);

/// Register the Manager class with Python.
void registerManager(const py::module& mod);

/// Register the ManagerFactory class with Python.
void registerManagerFactory(const py::module& mod);

/// Register the TraitsData class with Python.
void registerTraitsData(const py::module& mod);

/// Register the ManagerStateBase class with Python.
void registerManagerStateBase(const py::module& mod);

/// Register the EntityReference type with Python.
void registerEntityReference(const py::module& mod);

/// Register the BatchElementError type with Python.
void registerBatchElementError(const py::module& mod);

// Register exceptions, including BatchElementExceptions.
void registerExceptions(const py::module& mod);

/// Register the EntityReferencePager class with Python.
void registerEntityReferencePager(const py::module& mod);

/// Register the EntityReferencePagerInterface class with Python.
void registerEntityReferencePagerInterface(const py::module& mod);
