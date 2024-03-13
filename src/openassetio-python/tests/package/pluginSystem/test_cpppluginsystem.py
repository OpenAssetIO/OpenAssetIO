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
"""
These tests check the functionality of the CppPluginSystem class.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import os
import pathlib

import pytest

from openassetio import errors
from openassetio.pluginSystem import CppPluginSystem

# TODO(DF): GIL tests

class Test_CppPluginSystem_scan:
    def test_when_path_contains_a_module_plugin_definition_then_it_is_loaded(
        self, a_plugin_system, a_cpp_module_plugin_path, module_plugin_identifier
    ):
        a_plugin_system.scan(a_cpp_module_plugin_path)
        assert a_plugin_system.identifiers() == [
            module_plugin_identifier,
        ]

    def test_when_path_contains_multiple_entries_then_all_plugins_are_loaded(
        self,
        a_plugin_system,
        the_cpp_resources_directory_path,
        package_plugin_identifier,
        module_plugin_identifier,
    ):
        path_a = os.path.join(the_cpp_resources_directory_path, "pathA")
        path_b = os.path.join(the_cpp_resources_directory_path, "pathB")
        combined_path = os.pathsep.join([path_a, path_b])
        a_plugin_system.scan(combined_path)

        expected_identifiers = {package_plugin_identifier, module_plugin_identifier}
        assert set(a_plugin_system.identifiers()) == expected_identifiers

    def test_when_multiple_plugins_share_identifiers_then_leftmost_is_used(
        self,
        a_plugin_system,
        the_cpp_resources_directory_path,
        module_plugin_identifier,
        mock_logger,
    ):
        # The module plugin exists in pathA and pathC
        resources_path = pathlib.Path(the_cpp_resources_directory_path)
        path_a = resources_path / "pathA"
        path_c = resources_path / "pathC"

        a_plugin_system.scan(paths=os.pathsep.join((str(path_a), str(path_c))))
        path, _ = a_plugin_system.plugin(module_plugin_identifier)

        assert "pathA" in path.parts
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kDebug,
            f"CppPluginSystem: Skipping '{module_plugin_identifier}' defined in"
            f" '{path_c / 'libopenassetio-core-pluginSystem-test-pathC.so'}'."
            f" Already registered by"
            f" '{path_a / 'libopenassetio-core-pluginSystem-test-pathA.so'}'",
        )

        a_plugin_system.reset()

        a_plugin_system.scan(paths=os.pathsep.join((str(path_c), str(path_a))))
        path, _ = a_plugin_system.plugin(module_plugin_identifier)

        assert "pathC" in path.parts
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kDebug,
            f"CppPluginSystem: Skipping '{module_plugin_identifier}' defined in"
            f" '{path_a / 'libopenassetio-core-pluginSystem-test-pathA.so'}'."
            f" Already registered by"
            f" '{path_c / 'libopenassetio-core-pluginSystem-test-pathC.so'}'",
        )

    def test_when_path_contains_symlinks_then_plugins_are_loaded(
        self,
        a_plugin_system,
        a_cpp_plugin_path_with_symlinks,
        package_plugin_identifier,
        module_plugin_identifier,
    ):
        a_plugin_system.scan(a_cpp_plugin_path_with_symlinks)

        expected_identifiers = {package_plugin_identifier, module_plugin_identifier}
        assert set(a_plugin_system.identifiers()) == expected_identifiers

    def test_when_scan_called_multiple_times_then_plugins_combined(
        self,
        a_plugin_system,
        the_cpp_resources_directory_path,
        package_plugin_identifier,
        module_plugin_identifier,
    ):
        a_plugin_system.scan(paths=os.path.join(the_cpp_resources_directory_path, "pathA"))
        a_plugin_system.scan(paths=os.path.join(the_cpp_resources_directory_path, "pathB"))

        expected_identifiers = {package_plugin_identifier, module_plugin_identifier}
        assert set(a_plugin_system.identifiers()) == expected_identifiers

    def test_when_path_is_not_a_directory_then_warning_is_logged(
        self, a_plugin_system, mock_logger
    ):
        a_plugin_system.scan("/some/invalid/path")

        mock_logger.mock.log.assert_called_with(
            mock_logger.Severity.kDebug,
            "CppPluginSystem: Skipping as not a directory '/some/invalid/path'",
        )

    def test_when_plugins_broken_then_skipped_with_expected_errors(
        self, broken_cpp_plugins_path, mock_logger
    ):
        plugin_system = CppPluginSystem(mock_logger)
        plugin_system.scan(broken_cpp_plugins_path)

        # TODO(DF): How to check dlclose is called on failed plugin loads?
        # TODO(DF): Check `openassetioPlugin` symbol exists but is bad?

        assert not plugin_system.identifiers()

        kDebug = mock_logger.Severity.kDebug

        libext = "so" if os.name == "posix" else "dll"

        non_lib_path = os.path.join(broken_cpp_plugins_path, "not-a-lib.txt")
        fake_lib_path = os.path.join(broken_cpp_plugins_path, f"fake-lib.{libext}")
        directory_path = os.path.join(broken_cpp_plugins_path, f"a-directory.{libext}")
        non_plugin_path = os.path.join(broken_cpp_plugins_path, f"nonplugin.{libext}")
        static_throw_exception_path = os.path.join(
            broken_cpp_plugins_path, f"staticthrow-exception.{libext}"
        )
        static_throw_nonexception_path = os.path.join(
            broken_cpp_plugins_path, f"staticthrow-nonexception.{libext}"
        )
        entrypoint_throw_exception_path = os.path.join(
            broken_cpp_plugins_path, f"entrypointthrow-exception.{libext}"
        )
        entrypoint_throw_nonexception_path = os.path.join(
            broken_cpp_plugins_path, f"entrypointthrow-nonexception.{libext}"
        )

        mock_logger.mock.log.assert_any_call(
            kDebug,
            f"CppPluginSystem: Ignoring as it is not a library binary '{non_lib_path}'",
        )
        mock_logger.mock.log.assert_any_call(
            kDebug,
            f"CppPluginSystem: Ignoring as it is not a library binary '{directory_path}'",
        )
        mock_logger.mock.log.assert_any_call(
            kDebug,
            f"CppPluginSystem: Failed to open library '{fake_lib_path}':"
            f" {fake_lib_path}: file too short",
        )
        mock_logger.mock.log.assert_any_call(
            kDebug,
            "CppPluginSystem: No top-level 'openassetioPlugin' function in"
            f" '{non_plugin_path}': {non_plugin_path}: undefined symbol: openassetioPlugin",
        )
        # mock_logger.mock.log.assert_any_call(
        #     kDebug,
        #     "CppPluginSystem: Caught exception during static initialisation of"
        #     f" '{static_throw_exception_path}': Statically thrown",
        # )
        # mock_logger.mock.log.assert_any_call(
        #     kDebug,
        #     "CppPluginSystem: Caught exception during static initialisation of"
        #     f" '{static_throw_nonexception_path}':"
        #     " <unknown non-exception value caught>",
        # )
        mock_logger.mock.log.assert_any_call(
            kDebug,
            "CppPluginSystem: Caught exception calling 'openassetioPlugin' of"
            f" '{entrypoint_throw_exception_path}': Thrown from entrypoint",
        )
        mock_logger.mock.log.assert_any_call(
            kDebug,
            "CppPluginSystem: Caught exception calling 'openassetioPlugin' of"
            f" '{entrypoint_throw_nonexception_path}':"
            " <unknown non-exception value caught>",
        )


class Test_CppPluginSystem_plugin:
    def test_when_plugin_not_found_then_raises_InputValidationException(self, a_plugin_system):
        with pytest.raises(
            errors.InputValidationException,
            match="CppPluginSystem: No plug-in registered with the identifier 'nonexistent'",
        ):
            a_plugin_system.plugin("nonexistent")


@pytest.fixture
def a_plugin_system(mock_logger):
    return CppPluginSystem(mock_logger)
