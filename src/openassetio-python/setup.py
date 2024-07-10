#
#   Copyright 2013-2022 The Foundry Visionmongers Ltd
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
import os
import pathlib
import subprocess
import shlex
import sys
from typing import List

from setuptools import (
    setup,
    Extension,
    find_packages,
)

import setuptools.command.build_ext


class build_ext(setuptools.command.build_ext.build_ext):
    """
    Custom setuptools command class to puppet CMake.
    """

    def build_extension(self, _ext: Extension):
        """
        Hook called by setuptools to build the given Extension.

        @param _ext: Extension to build (we only have one, so ignored).
        """
        if self.editable_mode:
            raise NotImplementedError("OpenAssetIO does not support editable installs")

        cmake_project_path = pathlib.Path("../..")

        if not os.path.isfile(cmake_project_path / "CMakeLists.txt"):
            # Unfortunately there doesn't seem to be a way to detect the
            # version of pip that launched this process. So assume if
            # CMakeLists.txt is missing then its probably because the
            # wrong version of pip was used.
            raise FileNotFoundError(
                "CMakeLists.txt not found. Installing OpenAssetIO from source requires an in-tree"
                "build. If using pip, ensure pip>=21.3."
            )

        self.__cmake(
            [
                "-S",
                str(cmake_project_path),
                "-B",
                self.build_temp,
                "-G",
                "Ninja",
                # Place output artifacts where setuptools expects.
                "--install-prefix",
                os.path.abspath(self.build_lib),
                "--preset",
                "setuptools",
                # Ensure expected Python environment is discovered by
                # CMake's `find_package` during the build.
                f"-DPython_EXECUTABLE={sys.executable}",
            ]
        )

        self.__cmake(["--build", self.build_temp, "--target", "openassetio-python-module"])

        self.__cmake(
            [
                "--install",
                self.build_temp,
                "--component",
                "openassetio-python-module",
            ]
        )

    def __cmake(self, args: List[str]):
        """
        Execute `cmake` as a subprocess with given arguments.

        @param args: Command-line arguments to pass to `cmake`.
        """
        args = ["cmake"] + args
        self.announce(" ".join(map(shlex.quote, args)), level=2)
        subprocess.check_call(args, env=os.environ.copy())


setup(
    packages=find_packages(where="package"),
    package_dir={"": "package"},
    package_data={"": ["py.typed", "_openassetio/*.pyi"]},
    ext_modules=[Extension("openassetio._openassetio", sources=[])],
    cmdclass={"build_ext": build_ext},
    # See pyproject.toml for other metadata fields.
)
