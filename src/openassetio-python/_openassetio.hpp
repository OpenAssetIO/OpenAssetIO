// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
/**
 * Python binding bootstrap functions and typedefs.
 */
#pragma once

#include <memory>

#include <pybind11/pybind11.h>

#include <openassetio/typedefs.hpp>

#include "PyRetainingSharedPtr.hpp"

OPENASSETIO_FWD_DECLARE(LoggerInterface)
OPENASSETIO_FWD_DECLARE(ManagerStateBase)
OPENASSETIO_FWD_DECLARE(managerApi, ManagerInterface)
OPENASSETIO_FWD_DECLARE(hostApi, HostInterface)
OPENASSETIO_FWD_DECLARE(hostApi, ManagerInterfaceFactoryInterface)

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
using RetainCommonPyArgs =
    openassetio::RetainPyArgs<openassetio::LoggerInterfacePtr, openassetio::ManagerStateBasePtr,
                              openassetio::managerApi::ManagerInterfacePtr,
                              openassetio::hostApi::HostInterfacePtr,
                              openassetio::hostApi::ManagerInterfaceFactoryInterfacePtr>;

/// Concise pybind alias.
namespace py = pybind11;

/// Register the LoggerInterface class with Python.
void registerLoggerInterface(const py::module& mod);

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

/// Register the ManagerInterfaceFactoryInterface class with Python.
void registerManagerInterfaceFactoryInterface(const py::module& mod);

/// Register the Manager class with Python.
void registerManager(const py::module& mod);

/// Register the ManagerFactory class with Python.
void registerManagerFactory(const py::module& mod);

/// Register the TraitsData class with Python.
void registerTraitsData(const py::module& mod);

/// Register the ManagerStateBase class with Python.
void registerManagerStateBase(const py::module& mod);
