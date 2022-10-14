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
import subprocess
import shlex

from setuptools import (
    setup,
    Extension,
    find_packages,
)

import setuptools.command.build_ext


class build_ext(setuptools.command.build_ext.build_ext):
    def build_extension(self, _ext: Extension):
        self._cmake(
            [
                "-S",
                ".",
                "-B",
                self.build_temp,
                "-G",
                "Ninja",
                # Place output artifacts where setuptools expects.
                "--install-prefix",
                os.path.abspath(self.build_lib),
                "--preset",
                "pip",
            ]
        )

        self._cmake(["--build", self.build_temp, "--target", "openassetio-python-module"])

        self._cmake(
            [
                "--install",
                self.build_temp,
                "--component",
                "openassetio-python-module",
            ]
        )

    def _cmake(self, args: list[str]):
        args = ["cmake"] + args
        self.announce(" ".join(map(shlex.quote, args)), level=2)
        subprocess.check_call(args, env=os.environ.copy(), stderr=subprocess.STDOUT)

    def get_outputs(self):
        return dict(self._get_output_mapping()).keys()

    def get_output_mapping(self):
        return {}


setup(
    name="openassetio",
    version="1.0.0-alpha.4",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    python_requires=">=3.9",
    ext_modules=[Extension("openassetio._openassetio", sources=[])],
    cmdclass={"build_ext": build_ext},
)
