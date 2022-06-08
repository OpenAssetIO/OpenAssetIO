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

/**
 * Holder type for pybind-registered classes whose instances can exist
 * simultaneously in C++ and Python.
 *
 * Ensuring all such types are constructed and held as a ref-counted
 * smart pointer saves many object lifetime headaches.
 */
template <class T>
using Holder = openassetio::SharedPtr<T>;

/// Register the HostInterface class with Python.
void registerHostInterface(const py::module& mod);

/// Register the Host class with Python.
void registerHost(const py::module& mod);

/// Register the ManagerInterface class with Python.
void registerManagerInterface(const py::module& mod);

/// Register the Manager class with Python.
void registerManager(const py::module& mod);

/// Register the TraitsData class with Python.
void registerTraitsData(const py::module& mod);
