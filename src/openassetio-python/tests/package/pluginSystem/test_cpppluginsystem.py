#
#   Copyright 2013-2025 The Foundry Visionmongers Ltd
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
import re

import pytest

from openassetio import errors
from openassetio.pluginSystem import CppPluginSystem


lib_ext = "so" if os.name == "posix" else "dll"


class Test_CppPluginSystem_scan:
    def test_when_path_contains_a_module_plugin_definition_then_it_is_loaded(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        a_cpp_plugin_path,
        plugin_a_identifier,
    ):
        a_plugin_system.scan(a_cpp_plugin_path, the_manager_plugin_module_hook)

        assert a_plugin_system.identifiers() == [
            plugin_a_identifier,
        ]

    def test_when_path_contains_multiple_entries_then_all_plugins_are_loaded(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        the_cpp_plugins_root_path,
        plugin_b_identifier,
        plugin_a_identifier,
    ):
        path_a = os.path.join(the_cpp_plugins_root_path, "pathA")
        path_b = os.path.join(the_cpp_plugins_root_path, "pathB")
        combined_path = os.pathsep.join([path_a, path_b])
        a_plugin_system.scan(combined_path, the_manager_plugin_module_hook)

        expected_identifiers = {plugin_b_identifier, plugin_a_identifier}
        assert set(a_plugin_system.identifiers()) == expected_identifiers

    def test_when_multiple_plugins_share_identifiers_then_leftmost_is_used(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        the_cpp_plugins_root_path,
        plugin_a_identifier,
        mock_logger,
    ):
        # The module plugin exists in pathA and pathC
        resources_path = pathlib.Path(the_cpp_plugins_root_path)
        path_a = resources_path / "pathA"
        path_c = resources_path / "pathC"
        path_a_lib = path_a / f"pathA.{lib_ext}"
        path_c_lib = path_c / f"pathC.{lib_ext}"

        a_plugin_system.scan(
            paths=os.pathsep.join((str(path_a), str(path_c))),
            moduleHookName=the_manager_plugin_module_hook,
        )
        path, _ = a_plugin_system.plugin(plugin_a_identifier)

        assert "pathA" in path.parts
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kDebug,
            f"CppPluginSystem: Skipping '{plugin_a_identifier}' defined in '{path_c_lib}'."
            f" Already registered by '{path_a_lib}'",
        )

        a_plugin_system.reset()

        a_plugin_system.scan(
            paths=os.pathsep.join((str(path_c), str(path_a))),
            moduleHookName=the_manager_plugin_module_hook,
        )
        path, _ = a_plugin_system.plugin(plugin_a_identifier)

        assert "pathC" in path.parts
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kDebug,
            f"CppPluginSystem: Skipping '{plugin_a_identifier}' defined in '{path_a_lib}'."
            f" Already registered by '{path_c_lib}'",
        )

    def test_when_multiple_plugin_loaders_load_duplicate_plugins_then_libraries_not_unloaded(
        self,
        the_manager_plugin_module_hook,
        plugin_a_identifier,
        the_cpp_plugins_root_path,
        mock_logger,
    ):
        # This is really a test that dlopen/dlclose is reference
        # counted.

        resources_path = pathlib.Path(the_cpp_plugins_root_path)
        path_a = resources_path / "pathA"
        path_c = resources_path / "pathC"
        path_a_lib = path_a / f"pathA.{lib_ext}"
        path_c_lib = path_c / f"pathC.{lib_ext}"

        first_plugin_system = CppPluginSystem(mock_logger)
        second_plugin_system = CppPluginSystem(mock_logger)
        first_plugin_system.scan(paths=str(path_a), moduleHookName=the_manager_plugin_module_hook)
        # Will hit "Already registered" and dlclose `pathA.so`, which is
        # needed by the first plugin system. But libs should be
        # refcounted, so nothing breaks.
        second_plugin_system.scan(
            paths=os.pathsep.join((str(path_c), str(path_a))),
            moduleHookName=the_manager_plugin_module_hook,
        )

        # Confidence check that we hit the expected code path.
        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kDebug,
            f"CppPluginSystem: Skipping '{plugin_a_identifier}' defined in '{path_a_lib}'."
            f" Already registered by '{path_c_lib}'",
        )

    def test_when_path_contains_symlinks_then_plugins_are_loaded(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        a_cpp_plugin_path_with_symlinks,
        plugin_b_identifier,
        plugin_a_identifier,
    ):
        a_plugin_system.scan(a_cpp_plugin_path_with_symlinks, the_manager_plugin_module_hook)

        expected_identifiers = {plugin_b_identifier, plugin_a_identifier}
        assert set(a_plugin_system.identifiers()) == expected_identifiers

    def test_when_search_path_is_a_symlink_then_plugins_are_loaded(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        a_symlink_to_a_cpp_plugin_path,
        plugin_a_identifier,
    ):
        a_plugin_system.scan(a_symlink_to_a_cpp_plugin_path, the_manager_plugin_module_hook)

        expected_identifiers = {plugin_a_identifier}
        assert set(a_plugin_system.identifiers()) == expected_identifiers

    def test_when_scan_called_multiple_times_then_plugins_combined(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        the_cpp_plugins_root_path,
        plugin_b_identifier,
        plugin_a_identifier,
    ):
        a_plugin_system.scan(
            paths=os.path.join(the_cpp_plugins_root_path, "pathA"),
            moduleHookName=the_manager_plugin_module_hook,
        )
        a_plugin_system.scan(
            paths=os.path.join(the_cpp_plugins_root_path, "pathB"),
            moduleHookName=the_manager_plugin_module_hook,
        )

        expected_identifiers = {plugin_b_identifier, plugin_a_identifier}
        assert set(a_plugin_system.identifiers()) == expected_identifiers

    def test_when_path_contains_duplicate_entries_then_plugin_remains_loaded(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        a_cpp_plugin_path,
        a_cpp_plugin_path_with_symlinks,
        plugin_a_identifier,
        mock_logger,
    ):
        # Essentially testing that dlclose is refcounted.

        combined_path = os.pathsep.join([a_cpp_plugin_path_with_symlinks, a_cpp_plugin_path])
        path_a_lib = os.path.join(a_cpp_plugin_path, f"pathA.{lib_ext}")
        symlink_path_a_lib = os.path.join(a_cpp_plugin_path_with_symlinks, f"pathA.{lib_ext}")

        a_plugin_system.scan(combined_path, the_manager_plugin_module_hook)

        mock_logger.mock.log.assert_any_call(
            mock_logger.Severity.kDebug,
            f"CppPluginSystem: Skipping '{plugin_a_identifier}' defined in '{path_a_lib}'."
            f" Already registered by '{symlink_path_a_lib}'",
        )
        # Confidence check: we can still use the plugin instance.
        assert a_plugin_system.plugin(plugin_a_identifier)[1].identifier() == plugin_a_identifier

    def test_when_path_is_not_a_directory_then_warning_is_logged(
        self, a_plugin_system, the_manager_plugin_module_hook, mock_logger
    ):
        a_plugin_system.scan("/some/invalid/path", the_manager_plugin_module_hook)

        mock_logger.mock.log.assert_called_with(
            mock_logger.Severity.kDebug,
            "CppPluginSystem: Skipping as not a directory '/some/invalid/path'",
        )

    def test_when_plugins_broken_then_skipped_with_expected_errors(
        self, broken_cpp_plugins_path, a_plugin_system, the_manager_plugin_module_hook, mock_logger
    ):
        a_plugin_system.scan(broken_cpp_plugins_path, the_manager_plugin_module_hook)

        assert not a_plugin_system.identifiers()

        kDebug = mock_logger.Severity.kDebug
        kWarning = mock_logger.Severity.kWarning

        non_lib_path = os.path.join(broken_cpp_plugins_path, "not-a-lib.txt")
        fake_lib_path = os.path.join(broken_cpp_plugins_path, f"fake-lib.{lib_ext}")
        directory_path = os.path.join(broken_cpp_plugins_path, f"a-directory.{lib_ext}")
        non_plugin_path = os.path.join(broken_cpp_plugins_path, f"nonplugin.{lib_ext}")
        identifier_throw_exception_path = os.path.join(
            broken_cpp_plugins_path, f"identifier-throw-exception.{lib_ext}"
        )
        identifier_throw_nonexception_path = os.path.join(
            broken_cpp_plugins_path, f"identifier-throw-nonexception.{lib_ext}"
        )
        factory_return_null_path = os.path.join(
            broken_cpp_plugins_path, f"factory-return-null.{lib_ext}"
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
            RegexMatch(
                re.escape(f"CppPluginSystem: Failed to open library '{fake_lib_path}':") + " .+"
            ),
        )
        mock_logger.mock.log.assert_any_call(
            kDebug,
            RegexMatch(
                re.escape(
                    "CppPluginSystem: No top-level 'openassetioPlugin' function in"
                    f" '{non_plugin_path}':"
                )
                + " .+"
            ),
        )

        mock_logger.mock.log.assert_any_call(
            kWarning,
            "CppPluginSystem: Caught exception calling 'identifier' of"
            f" '{identifier_throw_exception_path}':"
            " Thrown from identifier",
        )

        mock_logger.mock.log.assert_any_call(
            kWarning,
            "CppPluginSystem: Caught exception calling 'identifier' of"
            f" '{identifier_throw_nonexception_path}':"
            " <unknown non-exception value caught>",
        )

        mock_logger.mock.log.assert_any_call(
            kWarning, f"CppPluginSystem: Null plugin returned by '{factory_return_null_path}'"
        )


class Test_CppPluginSystem_reset:
    def test_when_reset_then_identifiers_empty(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        a_cpp_plugin_path,
        plugin_a_identifier,
    ):
        a_plugin_system.scan(a_cpp_plugin_path, the_manager_plugin_module_hook)
        # Confidence check.
        assert a_plugin_system.identifiers() == [plugin_a_identifier]

        a_plugin_system.reset()

        assert a_plugin_system.identifiers() == []

    def test_when_plugin_system_reset_then_plugin_still_accessible(
        self,
        a_plugin_system,
        the_manager_plugin_module_hook,
        a_cpp_plugin_path,
        plugin_a_identifier,
    ):
        # Essentially testing that we don't dlclose the last reference
        # to the dll on reset.

        a_plugin_system.scan(a_cpp_plugin_path, the_manager_plugin_module_hook)
        _path, plugin = a_plugin_system.plugin(plugin_a_identifier)

        a_plugin_system.reset()

        assert plugin.identifier() == plugin_a_identifier


class Test_CppPluginSystem_destruction:
    def test_when_plugin_system_destructs_then_plugin_still_accessible(
        self, a_cpp_plugin_path, the_manager_plugin_module_hook, plugin_a_identifier, mock_logger
    ):
        # Essentially testing that we don't dlclose the last reference
        # to the dll on destruction.

        def get_plugin():
            plugin_system = CppPluginSystem(mock_logger)
            plugin_system.scan(a_cpp_plugin_path, the_manager_plugin_module_hook)
            return plugin_system.plugin(plugin_a_identifier)

        _path, plugin = get_plugin()

        assert plugin.identifier() == plugin_a_identifier


class Test_CppPluginSystem_plugin:
    def test_when_plugin_not_found_then_raises_InputValidationException(self, a_plugin_system):
        with pytest.raises(
            errors.InputValidationException,
            match="CppPluginSystem: No plug-in registered with the identifier 'nonexistent'",
        ):
            a_plugin_system.plugin("nonexistent")


class RegexMatch:
    def __init__(self, pattern):
        self.__pattern = pattern

    def __eq__(self, text):
        return bool(re.search(self.__pattern, text))


@pytest.fixture
def a_plugin_system(mock_logger):
    return CppPluginSystem(mock_logger)


@pytest.fixture(scope="module", autouse=True)
def skip_if_no_test_plugins_available(the_cpp_plugins_root_path):
    """
    Skip tests in this module if there are no plugins to test against.

    Some test runs may genuinely not have access to the plugins, e.g.
    when building/testing Python wheels, since the test plugins are
    created by CMake when test targets are enabled. In this case, skip
    the tests in this module.

    If we know we are running via CTest (i.e.
    OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR is defined), then the test
    plugins should definitely exist. So in this case, ensure we do _not_
    disable these tests.
    """
    if (
        not os.path.isdir(the_cpp_plugins_root_path)
        and os.environ.get("OPENASSETIO_TEST_CPP_PLUGINS_SUBDIR") is None
    ):
        pytest.skip("Skipping C++ plugin system tests as no test plugins are available")
