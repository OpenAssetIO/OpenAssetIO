#
#   Copyright 2024-2025 The Foundry Visionmongers Ltd
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
Smoke test for .pyi stub files
"""
# pylint: disable=missing-function-docstring,invalid-name
# pylint: disable=redefined-outer-name
import ast
import os
import pathlib

import pytest

import openassetio


expected_pyi_files = (
    "__init__.pyi",
    "access.pyi",
    "constants.pyi",
    "errors.pyi",
    "hostApi.pyi",
    "log.pyi",
    "managerApi.pyi",
    "pluginSystem.pyi",
    "trait.pyi",
    "utils.pyi",
    "ui/__init__.pyi",
    "ui/hostApi.pyi",
    "ui/managerApi.pyi",
    "ui/pluginSystem.pyi",
)


def test_expected_pyi_files_generated(pyi_dir: pathlib.Path):
    actual_pyi_files = set(
        p.relative_to(pyi_dir).as_posix()
        for p in pyi_dir.glob("**/*.pyi")
        if p.parent.name != "_testutils"
    )
    assert actual_pyi_files == set(expected_pyi_files)


@pytest.mark.parametrize("pyi_filename", expected_pyi_files)
def test_pyi_files_have_valid_python_ast(pyi_dir: pathlib.Path, pyi_filename):
    # Cannot import the module, since in pybind11-stubgen v2.5.1 the
    # ordering of statements causes errors. E.g. exception classes
    # inheriting from OpenAssetIOException come before the definition of
    # OpenAssetIOException in the .pyi file. So just check the AST is
    # valid. See
    # https://github.com/sizmailov/pybind11-stubgen/issues/231
    with open(pyi_dir / pyi_filename, encoding="utf-8") as pyi_file:
        ast.parse(pyi_file.read())


def test_py_typed_exists():
    assert pathlib.Path(openassetio.__file__).with_name("py.typed").is_file()


@pytest.fixture(scope="module", autouse=True)
def skip_if_stubs_disabled(pyi_dir):
    """
    Disable stub file tests if stubgen is not explicitly enabled and
    stubs directory does not exist.
    """
    if os.environ.get("OPENASSETIO_TEST_ENABLE_PYTHON_STUBGEN") != "1" and not pyi_dir.is_dir():
        pytest.skip("Skipping .pyi stub tests as stubs directory not found")


@pytest.fixture(scope="session")
def pyi_dir():
    return pathlib.Path(openassetio.__file__).with_name("_openassetio")
