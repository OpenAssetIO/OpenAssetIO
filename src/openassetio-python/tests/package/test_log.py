#
#   Copyright 2013-2021 The Foundry Visionmongers Ltd
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
Tests that cover the openassetio.log module.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

import openassetio.log as lg


# The logging mechanism is very much in flux right now, as we move away from
# singleton/global loggers and to a per-session mechanism. Consequently we are
# investing in minimal testing here until this has stabilised. Both the design
# and implementation may well change significantly.
#
# The tests focus upon any API critical semantics of logging, vs the robustness
# of any of the placeholder implementation, or implementation borrowed from
# the old API.


@pytest.fixture
def severity_filter(mock_logger):
    return lg.SeverityFilter(mock_logger)


# Ordered by increasing severity value
all_severities = (
    lg.LoggerInterface.Severity.kDebugApi,
    lg.LoggerInterface.Severity.kDebug,
    lg.LoggerInterface.Severity.kInfo,
    lg.LoggerInterface.Severity.kProgress,
    lg.LoggerInterface.Severity.kWarning,
    lg.LoggerInterface.Severity.kError,
    lg.LoggerInterface.Severity.kCritical,
)

severity_control_envvar = "OPENASSETIO_LOGGING_SEVERITY"


class Test_ConsoleLogger_inheritance:
    def test_class_is_final(self):
        with pytest.raises(TypeError):

            class _(lg.ConsoleLogger):
                pass


class Test_ConsoleLogger:
    def test_when_logging_then_messages_are_written_to_stderr(self, capfd):
        # Clear the capture so we don't get swamped by any output from
        # previous tests.
        _ = capfd.readouterr()

        logger = lg.ConsoleLogger(shouldColorOutput=False)
        for severity in all_severities:
            logger.log(severity, "A message")
        output = capfd.readouterr()

        assert output.out == ""
        assert (
            output.err
            == "\n".join(
                [
                    f"{lg.LoggerInterface.kSeverityNames[int(s)] : >11}: A message"
                    for s in all_severities
                ]
            )
            + "\n"
        )

    def test_when_shouldColorOutput_not_set_then_messages_are_colored(self, capfd):
        _ = capfd.readouterr()
        logger = lg.ConsoleLogger(shouldColorOutput=True)
        logger.log(lg.LoggerInterface.Severity.kCritical, "A message")
        output = capfd.readouterr()

        assert "\033[0m" in output.err

    def test_when_shouldColorOutput_set_true_then_messages_are_colored(self, capfd):
        _ = capfd.readouterr()
        logger = lg.ConsoleLogger(shouldColorOutput=True)
        logger.log(lg.LoggerInterface.Severity.kCritical, "A message")
        output = capfd.readouterr()

        assert "\033[0m" in output.err

    def test_when_shouldColorOutput_set_false_then_messages_are_not_colored(self, capfd):
        _ = capfd.readouterr()
        logger = lg.ConsoleLogger(shouldColorOutput=False)
        logger.log(lg.LoggerInterface.Severity.kCritical, "A message")
        output = capfd.readouterr()

        assert "\033[0m" not in output.err


class Test_LoggerInterface:
    def test_severity_names(self):
        assert (
            lg.LoggerInterface.kSeverityNames[int(lg.LoggerInterface.Severity.kCritical)]
            == "critical"
        )
        assert (
            lg.LoggerInterface.kSeverityNames[int(lg.LoggerInterface.Severity.kError)] == "error"
        )
        assert (
            lg.LoggerInterface.kSeverityNames[int(lg.LoggerInterface.Severity.kWarning)]
            == "warning"
        )
        assert (
            lg.LoggerInterface.kSeverityNames[int(lg.LoggerInterface.Severity.kProgress)]
            == "progress"
        )
        assert lg.LoggerInterface.kSeverityNames[int(lg.LoggerInterface.Severity.kInfo)] == "info"
        assert (
            lg.LoggerInterface.kSeverityNames[int(lg.LoggerInterface.Severity.kDebug)] == "debug"
        )
        assert (
            lg.LoggerInterface.kSeverityNames[int(lg.LoggerInterface.Severity.kDebugApi)]
            == "debugApi"
        )

    def test_severity_index(self):
        for index, severity in enumerate(all_severities):
            assert severity.value == index

    def test_debugApi_calls_log_with_expected_severity_and_message(self, mock_logger):
        message = "a debugApi message"
        mock_logger.debugApi(message)
        mock_logger.mock.log.assert_called_once_with(
            lg.LoggerInterface.Severity.kDebugApi, message
        )

    def test_debug_calls_log_with_expected_severity_and_message(self, mock_logger):
        message = "a debug message"
        mock_logger.debug(message)
        mock_logger.mock.log.assert_called_once_with(lg.LoggerInterface.Severity.kDebug, message)

    def test_info_calls_log_with_expected_severity_and_message(self, mock_logger):
        message = "an info message"
        mock_logger.info(message)
        mock_logger.mock.log.assert_called_once_with(lg.LoggerInterface.Severity.kInfo, message)

    def test_progress_calls_log_with_expected_severity_and_message(self, mock_logger):
        message = "a progress message"
        mock_logger.progress(message)
        mock_logger.mock.log.assert_called_once_with(
            lg.LoggerInterface.Severity.kProgress, message
        )

    def test_warning_calls_log_with_expected_severity_and_message(self, mock_logger):
        message = "a warning message"
        mock_logger.warning(message)
        mock_logger.mock.log.assert_called_once_with(lg.LoggerInterface.Severity.kWarning, message)

    def test_error_calls_log_with_expected_severity_and_message(self, mock_logger):
        message = "an error message"
        mock_logger.error(message)
        mock_logger.mock.log.assert_called_once_with(lg.LoggerInterface.Severity.kError, message)

    def test_critical_calls_log_with_expected_severity_and_message(self, mock_logger):
        message = "a critical message"
        mock_logger.critical(message)
        mock_logger.mock.log.assert_called_once_with(
            lg.LoggerInterface.Severity.kCritical, message
        )


class Test_SeverityFilter_inheritance:
    def test_class_is_final(self):
        with pytest.raises(TypeError):

            class _(lg.SeverityFilter):
                pass


class Test_SeverityFilter_init:
    def test_when_logger_is_None_then_raises_TypeError(self):
        with pytest.raises(TypeError) as err:
            lg.SeverityFilter(None)

        assert str(err.value).startswith("__init__(): incompatible constructor arguments")

    def test_when_invalid_logger_then_raises_TypeError(self):
        with pytest.raises(TypeError) as err:
            lg.SeverityFilter(object())

        assert str(err.value).startswith("__init__(): incompatible constructor arguments")

    def test_when_severity_envvar_not_set_then_initial_severity_is_warning(
        self, mock_logger, monkeypatch
    ):
        monkeypatch.delenv(severity_control_envvar, raising=False)
        f = lg.SeverityFilter(mock_logger)
        assert f.getSeverity() == lg.LoggerInterface.Severity.kWarning

    def test_when_severity_envvar_set_then_initial_severity_matches_envvar_value(
        self, mock_logger, monkeypatch
    ):
        for value, expected in (
            ("", lg.LoggerInterface.Severity.kWarning),
            ("not a valid value", lg.LoggerInterface.Severity.kWarning),
        ):
            monkeypatch.setenv(severity_control_envvar, value)
            f = lg.SeverityFilter(mock_logger)
            assert f.getSeverity() == expected

        for expected in (
            lg.LoggerInterface.Severity.kDebugApi,
            lg.LoggerInterface.Severity.kDebug,
            lg.LoggerInterface.Severity.kInfo,
            lg.LoggerInterface.Severity.kProgress,
            lg.LoggerInterface.Severity.kWarning,
            lg.LoggerInterface.Severity.kError,
            lg.LoggerInterface.Severity.kCritical,
        ):
            monkeypatch.setenv(severity_control_envvar, str(int(expected)))
            f = lg.SeverityFilter(mock_logger)
            assert f.getSeverity() == expected

    def test_when_invalid_envvar_string_set_then_error_is_logged(self, mock_logger, monkeypatch):
        monkeypatch.setenv(severity_control_envvar, "invalid")
        _ = lg.SeverityFilter(mock_logger)
        mock_logger.mock.log.assert_called_with(
            lg.LoggerInterface.Severity.kError,
            "SeverityFilter: Invalid OPENASSETIO_LOGGING_SEVERITY value 'invalid' - ignoring.",
        )

    def test_when_invalid_envvar_severity_set_then_error_is_logged(self, mock_logger, monkeypatch):
        monkeypatch.setenv(severity_control_envvar, "12")
        _ = lg.SeverityFilter(mock_logger)
        mock_logger.mock.log.assert_called_with(
            lg.LoggerInterface.Severity.kError,
            "SeverityFilter: Invalid OPENASSETIO_LOGGING_SEVERITY value '12' - ignoring.",
        )


class Test_SeverityFilter_setSeverity_getSeverity:
    def test_when_severity_is_set_then_get_returns_the_new_value(self, severity_filter):
        for severity in all_severities:
            severity_filter.setSeverity(severity)
            assert severity_filter.getSeverity() == severity


class Test_SeverityFilter_log:
    def test_only_messages_of_equal_or_greater_severity_are_relayed(self, severity_filter):

        mock_logger = severity_filter.upstreamLogger()

        msg = "A message"

        for filter_severity in all_severities:

            severity_filter.setSeverity(filter_severity)

            for message_severity in all_severities:
                mock_logger.mock.reset_mock()
                severity_filter.log(message_severity, msg)
                if message_severity >= filter_severity:
                    mock_logger.mock.log.assert_called_once_with(message_severity, msg)
                else:
                    mock_logger.mock.log.assert_not_called()


class Test_SeverityFilter_upstreamLogger:
    def test_returns_the_constructor_supplied_logger(self, mock_logger):
        a_filter = lg.SeverityFilter(mock_logger)
        assert a_filter.upstreamLogger() is mock_logger
