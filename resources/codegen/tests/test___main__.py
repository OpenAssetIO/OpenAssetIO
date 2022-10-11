#
#   Copyright 2022 The Foundry Visionmongers Ltd
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
Test for the openassetio-codgen CLI tool
"""

import datetime
import logging
import os
import subprocess
import sys


class Test_CLI_exit_code:
    def test_when_successful_then_exit_code_is_zero(self, yaml_path_all, tmp_path):
        assert execute_cli("-o", tmp_path, yaml_path_all).returncode == 0

    def test_when_invalid_input_path_then_exit_code_is_one(self, yaml_path_all, tmp_path):
        assert execute_cli("-o", tmp_path, "invalid").returncode == 1

    def test_when_invalid_args_set_then_exit_code_is_two(self):
        assert execute_cli("--invalid-arg").returncode == 2


class Test_CLI_output:
    def test_when_verbose_off_then_stdout_is_empty(self, yaml_path_minimal, tmp_path):
        assert execute_cli("--python", "-o", tmp_path, yaml_path_minimal).stdout == ""

    def test_when_verbose_on_then_created_paths_written_to_stdout(
        self, yaml_path_minimal, creations_minimal_python, tmp_path
    ):
        expected = [os.path.join(tmp_path, path) for path in creations_minimal_python]
        actual = execute_cli(
            "--python", "-o", tmp_path, yaml_path_minimal, "-v"
        ).stdout.splitlines()

        assert actual == expected

    def test_when_verbose_and_logging_on_then_created_paths_written_to_stdout(
        self, yaml_path_minimal, creations_minimal_python, tmp_path
    ):
        expected = [os.path.join(tmp_path, path) for path in creations_minimal_python]
        actual = execute_cli(
            "--python", "-o", tmp_path, yaml_path_minimal, "-v", "-l", "DEBUG"
        ).stdout.splitlines()

        assert actual == expected

    def test_when_logging_not_set_then_INFO_messages_not_written_to_stderr(
        self, yaml_path_minimal, tmp_path
    ):
        assert execute_cli("--python", "-o", tmp_path, yaml_path_minimal).stderr.splitlines() == []

    def test_when_logging_set_to_INFO_then_INFO_messages_written_to_stderr(
        self, yaml_path_minimal, tmp_path
    ):
        assert (
            "INFO:"
            in execute_cli("--python", "-o", tmp_path, "-l", "INFO", yaml_path_minimal).stderr
        )


class Test_CLI_args_dry_run:
    def test_when_not_set_then_code_is_generated_to_expected_path(
        self, yaml_path_minimal, tmp_path
    ):
        execute_cli("--python", "-o", tmp_path, yaml_path_minimal)

        assert os.path.isdir(os.path.join(tmp_path, "python"))

    def test_when_d_set_then_code_is_not_generated(self, yaml_path_minimal, tmp_path):
        execute_cli("--python", "-d", "-o", tmp_path, yaml_path_minimal)

        assert not os.path.isdir(os.path.join(tmp_path, "python"))

    def test_when_dryrun_set_then_code_is_not_generated(self, yaml_path_minimal, tmp_path):
        execute_cli("--python", "--dry-run", "-o", tmp_path, yaml_path_minimal)

        assert not os.path.isdir(os.path.join(tmp_path, "python"))

    def test_when_set_then_exit_code_is_zero(self, yaml_path_minimal, tmp_path):
        assert execute_cli("--python", "-d", "-o", tmp_path, yaml_path_minimal).returncode == 0


class Test_CLI_args_output_dir:
    def test_when_not_set_then_exit_code_is_two(self, yaml_path_minimal):
        assert execute_cli("--python", yaml_path_minimal).returncode == 2

    def test_when_o_set_then_code_is_generated_to_expected_path(self, yaml_path_minimal, tmp_path):
        execute_cli("--python", "-o", tmp_path, yaml_path_minimal)

        assert os.path.isdir(os.path.join(tmp_path, "python"))

    def test_when_outputdir_set_then_code_is_generated_to_expected_path(
        self, yaml_path_minimal, tmp_path
    ):
        execute_cli("--python", "--output-dir", tmp_path, yaml_path_minimal)

        assert os.path.isdir(os.path.join(tmp_path, "python"))


class Test_CLI_args_copyright_owner:
    def test_when_not_set_then_no_copyright_added(self, tmp_path, yaml_path_minimal):
        execute_cli("--python", "-o", tmp_path, yaml_path_minimal)

        assert "SPDX-License-Identifier:" not in file_contents(
            tmp_path, "python", "p_p", "__init__.py"
        )

    def test_when_set_then_copyright_added_with_owner(self, tmp_path, yaml_path_minimal):
        execute_cli("--python", "--copyright-owner", "An Owner", "-o", tmp_path, yaml_path_minimal)
        contents = file_contents(tmp_path, "python", "p_p", "__init__.py")

        assert "SPDX-License-Identifier:" in contents
        assert "An Owner" in contents


class Test_CLI_args_copyright_date:
    def test_when_not_set_then_copyright_date_is_this_year(self, tmp_path, yaml_path_minimal):
        execute_cli("--python", "--copyright-owner", "An Owner", "-o", tmp_path, yaml_path_minimal)
        contents = file_contents(tmp_path, "python", "p_p", "__init__.py")

        assert f"Copyright {datetime.date.today().year} An Owner" in contents

    def test_when_set_then_copyright_date_is_as_specified(self, tmp_path, yaml_path_minimal):
        execute_cli(
            "--python",
            "--copyright-owner",
            "An Owner",
            "--copyright-date",
            "2010-2022",
            "-o",
            tmp_path,
            yaml_path_minimal,
        )
        contents = file_contents(tmp_path, "python", "p_p", "__init__.py")

        assert "Copyright 2010-2022 An Owner" in contents


class Test_CLI_args_spdxLicenseIdentifier:
    def test_when_not_set_then_apache_two_used(self, tmp_path, yaml_path_minimal):
        execute_cli("--python", "--copyright-owner", "An Owner", "-o", tmp_path, yaml_path_minimal)
        contents = file_contents(tmp_path, "python", "p_p", "__init__.py")

        assert "SPDX-License-Identifier: Apache-2.0" in contents

    def test_when_set_then_license_added_with_specified_identifier(
        self, tmp_path, yaml_path_minimal
    ):
        execute_cli(
            "--python",
            "--spdx-license-identifier",
            "Unlicense",
            "--copyright-owner",
            "An Owner",
            "-o",
            tmp_path,
            yaml_path_minimal,
        )
        contents = file_contents(tmp_path, "python", "p_p", "__init__.py")

        assert "SPDX-License-Identifier: Unlicense" in contents


class Test_CLI_args_help:
    def test_when_h_set_then_help_is_generated(self, tmp_path, yaml_path_minimal):
        assert "usage: openassetio-codegen" in execute_cli("-h").stdout

    def test_when_help_set_then_help_is_generated(self, tmp_path, yaml_path_minimal):
        assert "usage: openassetio-codegen" in execute_cli("--help").stdout


class Test_CLI_args_python:
    def test_when_python_set_then_python_is_generated(self, tmp_path, yaml_path_minimal):
        execute_cli("--python", "-o", tmp_path, yaml_path_minimal)

        assert os.path.isdir(os.path.join(tmp_path, "python"))

    def test_when_only_python_set_then_only_python_is_generated(self, tmp_path, yaml_path_minimal):
        execute_cli("--python", "-o", tmp_path, yaml_path_minimal)

        assert os.listdir(tmp_path) == [
            "python",
        ]


class Test_CLI_default_languages:
    def test_when_none_set_then_all_languages_are_generated(self, tmp_path, yaml_path_minimal):
        execute_cli("--python", "-o", tmp_path, yaml_path_minimal)

        assert os.listdir(tmp_path) == [
            "python",
        ]


#
# Helpers
#


def execute_cli(*args):
    all_args = [sys.executable, "-m", "openassetio_codegen"]
    all_args.extend(args)
    # We explicitly don't want an exception to be raised.
    # pylint: disable=subprocess-run-check
    return subprocess.run(all_args, capture_output=True, encoding="utf-8")


def file_contents(*args):
    path = os.path.join(*args)
    return "\n".join(open(path, encoding="utf-8").readlines())
