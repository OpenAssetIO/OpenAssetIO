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

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import os
import subprocess

import pytest

class Test_CLI_exit_code:

    def test_when_passing_then_exit_code_is_zero(self, test_resources_dir):
        fixtures = os.path.join(test_resources_dir, "fixtures_pass.py")
        assert execute_cli(fixtures).returncode == 0

    def test_when_failing_then_exit_code_is_one(self, test_resources_dir):
        fixtures = os.path.join(test_resources_dir, "fixtures_fail.py")
        result = execute_cli(fixtures)
        # Ensure the failure is for the right reason, as other random
        # errors could have an exit code of 1
        assert (
            "FAIL: test_matches_fixture "
            "(openassetio.test.managerValidator.validatorSuite.Test_identifier)"
            in str(result.stderr))
        assert result.returncode == 1

    def test_when_fixtures_file_is_missing_then_exit_code_is_one(self):
        assert execute_cli("/i/do/not/exist.py").returncode == 1


@pytest.fixture(autouse=True)
def test_openassetio_env(test_resources_dir, monkeypatch):
    """
    A fixture that configures the process environment such
    that the OpenAssetIO library can load the associated
    test resource plugins, and debug logging is enabled.
    """
    plugin_path = os.path.join(test_resources_dir, "plugins")
    monkeypatch.setenv("OPENASSETIO_PLUGIN_PATH", plugin_path)
    monkeypatch.setenv("OPENASSETIO_LOGGING_SEVERITY", "6")


@pytest.fixture
def test_resources_dir():
    """
    The path to the resources directory for this test suite.
    """
    test_dir = os.path.dirname(__file__)
    return os.path.join(test_dir, "resources")


def execute_cli(fixtures_path):
    """
    Invokes the managerValidator CLI via a subprocess.

    @param fixturesPath `str` The path to the test fixtues .py file.
    @param extra_args `List[str]` Additional args to pass to the CLI.

    @return `subprocess.CompletedProcess` The results of the invocation.
    """
    all_args = ["python", "-m", "openassetio.test.managerValidator"]
    all_args.extend(["-f", fixtures_path])
    # We explicitly don't want an exception to be raised.
    # pylint: disable=subprocess-run-check
    return subprocess.run(all_args, capture_output=True)
