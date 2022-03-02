// SPDX-License-Identifier: Apache-2.0
// Copyright 2013-2022 The Foundry Visionmongers Ltd
/**
 * Python binding bootstrap functions and typedefs.
 */
#pragma once

#include <memory>

#include <pybind11/pybind11.h>

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
using Holder = std::shared_ptr<T>;

/// Register the ManagerInterface class with Python.
void registerManagerInterface(const py::module& mod);

/// Register the base specification class with Python.
void registerSpecification(const py::module& mod);

/// Register the BlobTrait class with Python.
void registerBlobTrait(const py::module& mod);
