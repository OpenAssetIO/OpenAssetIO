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
Integration tests for CLI operation of the manager test harness.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import os
import subprocess
import sys

import pytest


class Test_CLI_exit_code:
    def test_when_passing_then_exit_code_is_zero(self, a_passing_fixtures_file):
        proc = execute_cli(a_passing_fixtures_file)
        try:
            assert proc.returncode == 0
        except AssertionError:
            print("STDOUT:\n%s\n\nSTDERR:\n%s" % (proc.stdout.decode(), proc.stderr.decode()))
            raise

    def test_when_failing_then_exit_code_is_one(self, a_failing_fixtures_file):
        result = execute_cli(a_failing_fixtures_file)
        # Ensure the failure is for the right reason, as other random
        # errors could have an exit code of 1
        assert (
            "FAIL: test_matches_fixture "
            "(openassetio.test.manager.apiComplianceSuite.Test_identifier" in str(result.stderr)
        )
        assert result.returncode == 1

    def test_when_fixtures_file_is_missing_then_exit_code_is_one(self):
        assert execute_cli("/i/do/not/exist.py").returncode == 1


class Test_CLI_output:
    def test_api_logging_goes_to_standard_out(self, a_passing_fixtures_file, monkeypatch):
        monkeypatch.setenv("OPENASSETIO_LOGGING_SEVERITY", "0")
        assert "debug: PythonPluginSystem" in str(execute_cli(a_passing_fixtures_file).stderr)

    def test_unittest_output_written_to_stderr(self, a_passing_fixtures_file):
        assert "Ran" in str(execute_cli(a_passing_fixtures_file).stderr)

    def test_when_failing_then_errors_written_to_stderr(self, a_failing_fixtures_file):
        assert "FAILED" in str(execute_cli(a_failing_fixtures_file).stderr)


class Test_CLI_arguments:
    def test_when_called_without_fixtures_arg_then_exits_with_usage_and_exit_code_is_two(self):
        result = execute_cli(None)
        assert result.returncode == 2
        assert "usage:" in str(result.stderr)

    def test_when_called_with_additional_args_then_they_are_passed_to_unittest(
        self, a_passing_fixtures_file
    ):
        # We use the "-v" flag that includes the test name in the
        # output to stderr
        result = execute_cli(a_passing_fixtures_file, "-v")
        # Check the tests passed first to avoid false positives from
        # a fail of our target check.
        assert result.returncode == 0
        assert "test_is_correct_type" in str(result.stderr)


@pytest.fixture
def a_passing_fixtures_file(resources_dir):
    return os.path.join(resources_dir, "fixtures_cliPass.py")


@pytest.fixture
def a_failing_fixtures_file(resources_dir):
    return os.path.join(resources_dir, "fixtures_cliFail.py")


def execute_cli(fixtures_path, *extra_args):
    """
    Invokes the manager CLI via a subprocess.

    @param fixturesPath `str` The path to the test fixtues .py file.
    @param extra_args `List[str]` Additional args to pass to the CLI.

    @return `subprocess.CompletedProcess` The results of the invocation.
    """
    # We may well be running inside a venv interpreter, but without
    # the venv being active in the current environment. The effect
    # of this is that the python on $PATH may not be the one that is
    # correctly configured with the appropriate dependencies, so we
    # attempt to use the same executable as the tests.

    # Str wrapping prevents issues with Path objects in Windows
    # Python 3.7
    all_args = [sys.executable, "-m", "openassetio.test.manager"]
    if fixtures_path:
        all_args.extend(["-f", str(fixtures_path)])
    if extra_args:
        str_extra_args = [str(a) for a in extra_args]
        all_args.extend(str_extra_args)
    # We explicitly don't want an exception to be raised.
    # pylint: disable=subprocess-run-check
    return subprocess.run(all_args, capture_output=True)
