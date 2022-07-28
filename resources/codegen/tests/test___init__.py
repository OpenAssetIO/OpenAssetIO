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
Tests for the main openassetio_codegen.generate entry point.
"""

import logging
import os
from unittest import mock

import pytest

import openassetio_codegen


class Test_generate:
    def test_when_description_path_valid_then_generate_called_with_declaration(
        self,
        yaml_path_all,
        declaration_all,
        some_output_dir,
        some_creation_callback,
        mock_language_a,
        a_capturing_logger,
    ):
        openassetio_codegen.generate(
            description_path=yaml_path_all,
            output_directory=some_output_dir,
            languages=["a"],
            creation_callback=some_creation_callback,
            logger=a_capturing_logger,
        )

        call_args = mock_language_a.generate.call_args[0]
        assert call_args[0] == declaration_all

    def test_when_description_path_invalid_then_FileNotFoundError_raised(
        self,
        some_output_dir,
        some_creation_callback,
        a_capturing_logger,
    ):
        with pytest.raises(FileNotFoundError):
            openassetio_codegen.generate(
                description_path="invalid",
                output_directory=some_output_dir,
                languages=["a"],
                creation_callback=some_creation_callback,
                logger=a_capturing_logger,
            )

    def test_when_language_set_then_generate_called_with_supplied_generation_arguments(
        self,
        yaml_path_all,
        some_output_dir,
        some_creation_callback,
        mock_language_a,
        a_capturing_logger,
    ):
        openassetio_codegen.generate(
            description_path=yaml_path_all,
            output_directory=some_output_dir,
            languages=["a"],
            creation_callback=some_creation_callback,
            logger=a_capturing_logger,
        )

        call_args = mock_language_a.generate.call_args[0]
        assert call_args[2] == some_output_dir
        assert call_args[3] is some_creation_callback

    def test_when_multiple_languages_set_then_generate_called_for_all(
        self,
        yaml_path_all,
        some_output_dir,
        some_creation_callback,
        mock_language_a,
        mock_language_b,
        a_capturing_logger,
    ):
        openassetio_codegen.generate(
            description_path=yaml_path_all,
            output_directory=some_output_dir,
            languages=["a", "b"],
            creation_callback=some_creation_callback,
            logger=a_capturing_logger,
        )

        mock_language_a.generate.assert_called()
        mock_language_b.generate.assert_called()

    def test_when_language_not_set_then_generate_not_called(
        self,
        yaml_path_all,
        some_output_dir,
        some_creation_callback,
        mock_language_a,
        a_capturing_logger,
    ):
        openassetio_codegen.generate(
            description_path=yaml_path_all,
            output_directory=some_output_dir,
            languages=[],
            creation_callback=some_creation_callback,
            logger=a_capturing_logger,
        )

        mock_language_a.generate.assert_not_called()

    def test_when_logger_supplied_then_called_with_child_logger_with_language_suffix(
        self,
        yaml_path_all,
        some_output_dir,
        some_creation_callback,
        mock_language_a,
        a_capturing_logger,
    ):
        openassetio_codegen.generate(
            description_path=yaml_path_all,
            output_directory=some_output_dir,
            languages=["a"],
            creation_callback=some_creation_callback,
            logger=a_capturing_logger,
        )

        call_args = mock_language_a.generate.call_args[0]
        assert call_args[4].name == f"{a_capturing_logger.name}.a"

    def test_when_dry_run_set_true_then_generate_not_called(
        self,
        yaml_path_all,
        some_output_dir,
        some_creation_callback,
        mock_language_a,
        a_capturing_logger,
    ):
        openassetio_codegen.generate(
            description_path=yaml_path_all,
            output_directory=some_output_dir,
            languages=["a"],
            creation_callback=some_creation_callback,
            logger=a_capturing_logger,
            dry_run=True,
        )

        mock_language_a.generate.assert_not_called()

    def test_when_dry_run_set_false_then_generate_called(
        self,
        yaml_path_all,
        some_output_dir,
        some_creation_callback,
        mock_language_a,
        a_capturing_logger,
    ):
        openassetio_codegen.generate(
            description_path=yaml_path_all,
            output_directory=some_output_dir,
            languages=["a"],
            creation_callback=some_creation_callback,
            logger=a_capturing_logger,
            dry_run=False,
        )

        mock_language_a.generate.assert_called()

    def test_when_no_globals_then_generator_called_with_default_globals(
        self,
        yaml_path_all,
        some_output_dir,
        some_creation_callback,
        mock_language_a,
        a_capturing_logger,
    ):

        openassetio_codegen.generate(
            description_path=yaml_path_all,
            output_directory=some_output_dir,
            languages=["a"],
            creation_callback=some_creation_callback,
            logger=a_capturing_logger,
        )

        expected_globals = openassetio_codegen.generators.helpers.default_template_globals()
        expected_globals["language"] = "a"

        call_args = mock_language_a.generate.call_args[0]
        assert call_args[1] == expected_globals

    def test_when_globals_supplied_then_generator_called_with_updated_globals(
        self,
        yaml_path_all,
        some_output_dir,
        some_creation_callback,
        mock_language_a,
        a_capturing_logger,
    ):

        extra_globals = {"a": 1, "b": "🤠", "copyrightOwner": "Me"}

        openassetio_codegen.generate(
            description_path=yaml_path_all,
            output_directory=some_output_dir,
            languages=["a"],
            creation_callback=some_creation_callback,
            logger=a_capturing_logger,
            template_globals=extra_globals,
        )

        expected_globals = openassetio_codegen.generators.helpers.default_template_globals()
        expected_globals.update(extra_globals)
        expected_globals["language"] = "a"

        call_args = mock_language_a.generate.call_args[0]
        assert call_args[1] == expected_globals

    def test_when_globals_supplied_include_language_then_generator_global_not_overridden(
        self,
        yaml_path_all,
        some_output_dir,
        some_creation_callback,
        mock_language_a,
        a_capturing_logger,
    ):

        extra_globals = {"language": "b"}

        openassetio_codegen.generate(
            description_path=yaml_path_all,
            output_directory=some_output_dir,
            languages=["a"],
            creation_callback=some_creation_callback,
            logger=a_capturing_logger,
            template_globals=extra_globals,
        )

        expected_globals = openassetio_codegen.generators.helpers.default_template_globals()
        expected_globals["language"] = "a"

        call_args = mock_language_a.generate.call_args[0]
        assert call_args[1] == expected_globals

    def test_when_valid_then_structure_is_logged_as_info(
        self,
        yaml_path_all,
        some_output_dir,
        some_creation_callback,
        a_capturing_logger,
        structure_all_log_messages,
    ):
        openassetio_codegen.generate(
            description_path=yaml_path_all,
            output_directory=some_output_dir,
            languages=[],
            creation_callback=some_creation_callback,
            logger=a_capturing_logger
        )

        assert a_capturing_logger.handlers[0].messages == structure_all_log_messages

    def test_when_dry_run_set_true_then_structure_is_still_logged_as_info(
        self,
        yaml_path_all,
        some_output_dir,
        some_creation_callback,
        a_capturing_logger,
        structure_all_log_messages,
    ):
        openassetio_codegen.generate(
            description_path=yaml_path_all,
            output_directory=some_output_dir,
            languages=[],
            creation_callback=some_creation_callback,
            logger=a_capturing_logger,
            dry_run=True,
        )

        assert a_capturing_logger.handlers[0].messages == structure_all_log_messages


@pytest.fixture
def mock_language_a(monkeypatch):
    mock_generator = mock.Mock()
    mock_generator.generate = mock.Mock()
    monkeypatch.setattr(openassetio_codegen.generators, "a", mock_generator, raising=False)
    return mock_generator


@pytest.fixture
def mock_language_b(monkeypatch):
    mock_generator = mock.Mock()
    mock_generator.generate = mock.Mock()
    monkeypatch.setattr(openassetio_codegen.generators, "b", mock_generator, raising=False)
    return mock_generator


@pytest.fixture
def some_output_dir():
    return os.path.join("some", "path")


@pytest.fixture
def some_creation_callback():
    return lambda _: _


@pytest.fixture
def structure_all_log_messages():
    return [
        (logging.INFO, "Package: openassetio-codegen-test-all"),
        (logging.INFO, "Traits:"),
        (logging.INFO, "aNamespace:"),
        (logging.INFO, "  - AllProperties"),
        (logging.INFO, "  - NoProperties"),
        (logging.INFO, "  - NoPropertiesMultipleUsage"),
        (logging.INFO, "anotherNamespace:"),
        (logging.INFO, "  - NoProperties"),
        (logging.INFO, "Specifications:"),
        (logging.INFO, "test:"),
        (logging.INFO, "  - LocalAndExternalTrait"),
        (logging.INFO, "  - OneExternalTrait"),
        (logging.INFO, "  - TwoLocalTraits"),
    ]
