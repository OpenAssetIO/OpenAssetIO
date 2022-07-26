# SPDX-License-Identifier: Apache-2.0
# Copyright 2013-2022 The Foundry Visionmongers Ltd

# C++ to Python bridge, exposing e.g. the Python plugin system to C++.
add_subdirectory(bridge)
# Python C extension module making C++ types usable in Python.
add_subdirectory(module)
