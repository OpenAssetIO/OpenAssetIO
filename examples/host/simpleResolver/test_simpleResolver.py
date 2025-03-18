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
Test cases for the simpleResolver CLI.
"""

import json
import subprocess
import pathlib
import pytest
import sys

from openassetio.errors import BatchElementError
from openassetio.hostApi import ManagerFactory


# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring


class Test_simpleResolver_errors:
    def test_when_no_config_then_error_written_to_stderr_and_return_code_non_zero(
        self, monkeypatch
    ):
        monkeypatch.delenv("OPENASSETIO_DEFAULT_CONFIG", raising=False)
        result = execute_cli()
        expected_message = [
            "ERROR: No default manager configured, "
            f"check ${ManagerFactory.kDefaultManagerConfigEnvVarName}"
        ]
        assert result.stderr.splitlines() == expected_message
        assert result.returncode == 1

    def test_when_bad_config_then_error_written_to_stderr_and_return_code_non_zero(
        self, monkeypatch
    ):
        monkeypatch.setenv("OPENASSETIO_DEFAULT_CONFIG", "/some/bad/path")
        result = execute_cli()
        expected_message = [
            "ERROR: Could not load default config from '/some/bad/path', file does not exist."
        ]
        assert result.stderr.splitlines() == expected_message
        assert result.returncode == 1

    def test_when_env_set_and_no_args_then_usage_printed_and_return_code_is_one(
        self, test_config_env  # pylint: disable=unused-argument
    ):
        result = execute_cli()
        expected_message = (
            "usage: simpleResolver.py [-h] traitset entityref\n"
            "simpleResolver.py: error: the following arguments are required: traitset, entityref"
        )

        assert expected_message in result.stderr
        assert result.returncode == 2

    def test_when_entity_ref_and_trait_set_valid_then_expected_data_output_and_return_code_zero(
        self, test_config_env  # pylint: disable=unused-argument
    ):
        result = execute_cli("animal,named", "bal:///cat")
        data = json.loads(result.stdout)
        expected_data = {
            "animal": {"species": "🐈", "age": 12},
            "named": {"name": "Martin"},
        }
        assert data == expected_data
        assert result.returncode == 0

    def test_when_entity_ref_valid_and_trait_set_invalid_then_data_empty_and_return_code_zero(
        self, test_config_env  # pylint: disable=unused-argument
    ):
        result = execute_cli("someMissingTrait", "bal:///cat")
        data = json.loads(result.stdout)
        assert data == {}
        assert result.returncode == 0

    def test_when_entity_ref_invalid_then_error_and_return_code_wrapped(
        self, test_config_env  # pylint: disable=unused-argument
    ):
        result = execute_cli("named", "bal:///doesNotExist")
        # Don't test the specific message as it couples to BAL specifics
        assert "ERROR:" in result.stderr
        assert result.returncode == int(BatchElementError.ErrorCode.kEntityResolutionError)


def execute_cli(*args):
    """
    Executes simplerResolver with the supplied args, as per subprocess.run.
    """
    this_file = pathlib.Path(__file__)
    cli_path = this_file.parent / "simpleResolver.py"
    all_args = [sys.executable, str(cli_path)]
    all_args.extend(args)
    # We explicitly don't want an exception to be raised.
    # pylint: disable=subprocess-run-check
    return subprocess.run(all_args, capture_output=True, encoding="utf-8")


@pytest.fixture
def test_config_env(monkeypatch, tmpdir):
    """
    A fixture that configures the process environment such that the
    OpenAssetIO default config points to the example toml file.
    """
    this_file = pathlib.Path(__file__)
    config_file = this_file.parent / "bal_animals_openassetio_config.toml"
    monkeypatch.setenv("OPENASSETIO_DEFAULT_CONFIG", str(config_file))
    # Deliberately not same directory as the library JSON file, so
    # relies on ${config_dir} interpolation.
    monkeypatch.chdir(tmpdir)
