// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
/**
 * Python binding bootstrap functions and typedefs.
 */
#pragma once

#include <memory>

#include <pybind11/pybind11.h>

#include <openassetio/typedefs.hpp>

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

/// Register the TraitsData class with Python.
void registerTraitsData(const py::module& mod);

/// Register the ManagerStateBase class with Python.
void registerManagerStateBase(const py::module& mod);
