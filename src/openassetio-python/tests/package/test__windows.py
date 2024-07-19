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
Tests that cover the openassetio._windows module, for augmenting dll
search paths.
"""
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
import os
import pathlib
import re
import importlib
from unittest import mock

import pytest

import openassetio
from openassetio import _windows


if os.name != "nt":
    pytest.skip("Windows specific tests", allow_module_level=True)


class Test_addDllDirectoryFromEnvVar:
    def test_when_openassetio_extension_successfully_imports_then_no_warning(self, recwarn):
        _windows.addDllDirectoryFromEnvVar()

        assert len(recwarn) == 0

    def test_when_openassetio_extension_fails_to_import_then_warns(self, monkeypatch):
        mock_import = mock.Mock(spec=importlib.import_module)
        mock_import.side_effect = ImportError

        monkeypatch.setattr(importlib, "import_module", mock_import)

        expected_warning = re.escape(
            "Failed to load _openassetio extension module. Try setting"
            " the OPENASSETIO_DLL_PATH environment variable to the"
            " directory containing openassetio.dll"
        )

        with pytest.warns(UserWarning, match=expected_warning):
            _windows.addDllDirectoryFromEnvVar()

        mock_import.assert_called_once_with("openassetio._openassetio")

    def test_when_no_env_var_then_does_not_add_dll_directory(
        self, monkeypatch, mock_add_dll_directory
    ):
        monkeypatch.delenv("OPENASSETIO_DLL_PATH", raising=False)

        _windows.addDllDirectoryFromEnvVar()

        mock_add_dll_directory.assert_not_called()

    def test_when_env_var_is_absolute_path_then_adds_dll_directory_verbatim(
        self, monkeypatch, mock_add_dll_directory, path_with_openassetio_dll
    ):
        monkeypatch.setenv("OPENASSETIO_DLL_PATH", str(path_with_openassetio_dll))

        _windows.addDllDirectoryFromEnvVar()

        mock_add_dll_directory.assert_called_once_with(str(path_with_openassetio_dll))

    def test_when_env_var_is_relative_path_then_adds_absolute_dll_directory(
        self, monkeypatch, mock_add_dll_directory
    ):
        relative_path = pathlib.Path("..", "something")
        expected_path = (pathlib.Path(openassetio.__file__).parent / relative_path).resolve(
            strict=False
        )

        monkeypatch.setenv("OPENASSETIO_DLL_PATH", str(relative_path))

        with pytest.warns(UserWarning):
            _windows.addDllDirectoryFromEnvVar()

        mock_add_dll_directory.assert_called_once_with(str(expected_path))

    def test_when_dll_path_contains_openassetio_dll_then_does_not_warn(
        self, monkeypatch, path_with_openassetio_dll, recwarn
    ):
        monkeypatch.setenv("OPENASSETIO_DLL_PATH", str(path_with_openassetio_dll))

        _windows.addDllDirectoryFromEnvVar()

        assert len(recwarn) == 0

    def test_when_absolute_dll_path_does_not_contain_openassetio_dll_then_warns_about_path(
        self, monkeypatch, path_without_openassetio_dll
    ):
        monkeypatch.setenv("OPENASSETIO_DLL_PATH", str(path_without_openassetio_dll))

        expected_warning = re.escape(
            f"OPENASSETIO_DLL_PATH given as '{path_without_openassetio_dll}' does"
            " not contain openassetio.dll."
        )

        with pytest.warns(UserWarning, match=expected_warning):
            _windows.addDllDirectoryFromEnvVar()

    def test_when_relative_dll_path_does_not_contain_openassetio_dll_then_warns_about_path(
        self, monkeypatch, path_without_openassetio_dll
    ):
        rel_path = os.path.relpath(
            path_without_openassetio_dll, os.path.dirname(openassetio.__file__)
        )
        monkeypatch.setenv("OPENASSETIO_DLL_PATH", rel_path)
        expected_warning = re.escape(
            f"OPENASSETIO_DLL_PATH given as '{rel_path}' and resolved to"
            f" '{path_without_openassetio_dll.resolve(strict=False)}' does not contain"
            f" openassetio.dll."
        )

        with pytest.warns(UserWarning, match=expected_warning):
            _windows.addDllDirectoryFromEnvVar()


@pytest.fixture()
def mock_add_dll_directory(monkeypatch):
    """
    Patches the _windows.addDllDirectoryFromEnvVar function with a mock
    and returns the mock.
    """
    mocked = mock.Mock()
    monkeypatch.setattr(os, "add_dll_directory", mocked)
    return mocked


@pytest.fixture()
def path_with_openassetio_dll(tmp_path):
    """
    Provides a temporary path containing an openassetio.dll file.
    """
    dll_path = tmp_path / "openassetio.dll"
    dll_path.touch()
    return tmp_path


@pytest.fixture
def path_without_openassetio_dll():
    """
    Provides an arbitrary path that does not contain an openassetio.dll
    file.
    """
    # Note: this must be a real path, or os.add_dll_directory will
    # raise. It must also be a path on the same drive as the
    # `openassetio` module, or computing a relative path from it will
    # raise.
    return pathlib.Path(openassetio.__file__).parent / "pluginSystem"
