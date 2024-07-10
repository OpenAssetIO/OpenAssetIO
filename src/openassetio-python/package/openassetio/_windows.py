#
#   Copyright 2024 The Foundry Visionmongers Ltd
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""
Utility module to handle Windows dll loading idiosyncrasies.

The _openassetio Python C extension module has a dependency on the core
OpenAssetIO library. We cannot, in general, predict where this library
will be installed. On Linux/macOS, the rpath mechanism can be used by
installers. In Python 3.8+ on Windows, the best we can do is add to the
search paths here, allowing the user (or wrapper application) to control
the additional search path with an environment variable.
"""
import os
import warnings
import importlib
import pathlib


def addDllDirectoryFromEnvVar():
    """
    Add a DLL search path from the OPENASSETIO_DLL_PATH environment
    variable, if provided, and check if the openassetio Python C
    extension module can be imported.

    A relative path will be interpreted as relative to the openassetio
    package directory.

    Use the warnings module to provide helpful output if the import
    fails and/or the search path is invalid. Using the warnings module
    means that users can filter them if desired for a particular
    installation.

    An ImportWarning might seem more appropriate than the default
    (UserWarning), but Python will not print ImportWarnings unless the
    user explicitly enables them.
    """

    searchPath = os.environ.get("OPENASSETIO_DLL_PATH")
    if searchPath is not None:
        searchPath = pathlib.Path(searchPath)
        # Join path to directory of package if it is relative, else use
        # verbatim.
        if searchPath.is_absolute():
            fullSearchPath = searchPath
        else:
            fullSearchPath = (pathlib.Path(__file__).parent / searchPath).resolve(strict=False)

        # Warn if openassetio.dll is not found in the configured search
        # path.
        if not (fullSearchPath / "openassetio.dll").is_file():
            warning = f"OPENASSETIO_DLL_PATH given as '{searchPath}'"
            if not searchPath.is_absolute():
                warning += f" and resolved to '{fullSearchPath}'"
            warning += " does not contain openassetio.dll."
            warnings.warn(warning)

        # Add DLL search path.
        os.add_dll_directory(str(fullSearchPath))

    # Try to import the extension module and print a useful error if it
    # fails.
    try:
        importlib.import_module("openassetio._openassetio")
    except ImportError:
        warnings.warn(
            "Failed to load _openassetio extension module. Try"
            " setting the OPENASSETIO_DLL_PATH environment"
            " variable to the directory containing openassetio.dll"
        )
