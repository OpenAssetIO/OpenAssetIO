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

# pylint: disable=no-self-use
# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

from unittest import mock

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
def mock_logger():
    return mock.create_autospec(spec=lg.LoggerInterface)


@pytest.fixture
def severity_filter(mock_logger):
    return lg.SeverityFilter(mock_logger)


all_severities = (
    lg.LoggerInterface.kDebugApi,
    lg.LoggerInterface.kDebug,
    lg.LoggerInterface.kInfo,
    lg.LoggerInterface.kProgress,
    lg.LoggerInterface.kWarning,
    lg.LoggerInterface.kError,
    lg.LoggerInterface.kCritical
)

severity_control_envvar = "OPENASSETIO_LOGGING_SEVERITY"


class Test_LoggerInterface:
    def test_severity_names(self):
        assert lg.LoggerInterface.kSeverityNames[lg.LoggerInterface.kCritical] == "critical"
        assert lg.LoggerInterface.kSeverityNames[lg.LoggerInterface.kError] == "error"
        assert lg.LoggerInterface.kSeverityNames[lg.LoggerInterface.kWarning] == "warning"
        assert lg.LoggerInterface.kSeverityNames[lg.LoggerInterface.kProgress] == "progress"
        assert lg.LoggerInterface.kSeverityNames[lg.LoggerInterface.kInfo] == "info"
        assert lg.LoggerInterface.kSeverityNames[lg.LoggerInterface.kDebug] == "debug"
        assert lg.LoggerInterface.kSeverityNames[lg.LoggerInterface.kDebugApi] == "debugApi"


class Test_SeverityFilter_init:

    def test_when_severity_envvar_not_set_then_initial_severity_is_warning(
            self, mock_logger, monkeypatch):

        monkeypatch.delenv(severity_control_envvar, raising=False)
        f = lg.SeverityFilter(mock_logger)
        assert f.getSeverity() == lg.LoggerInterface.kWarning

    def test_when_severity_envvar_set_then_initial_severity_matches_envvar_value(
            self, mock_logger, monkeypatch):

        for value, expected in (
                ("", lg.LoggerInterface.kWarning),
                ("not a valid value", lg.LoggerInterface.kWarning),
        ):
            monkeypatch.setenv(severity_control_envvar, value)
            f = lg.SeverityFilter(mock_logger)
            assert f.getSeverity() == expected

        for value, expected in (
                (lg.LoggerInterface.kDebugApi, lg.LoggerInterface.kDebugApi),
                (lg.LoggerInterface.kDebug, lg.LoggerInterface.kDebug),
                (lg.LoggerInterface.kInfo, lg.LoggerInterface.kInfo),
                (lg.LoggerInterface.kProgress, lg.LoggerInterface.kProgress),
                (lg.LoggerInterface.kWarning, lg.LoggerInterface.kWarning),
                (lg.LoggerInterface.kError, lg.LoggerInterface.kError),
                (lg.LoggerInterface.kCritical, lg.LoggerInterface.kCritical)
        ):
            monkeypatch.setenv(severity_control_envvar, str(int(value)))
            f = lg.SeverityFilter(mock_logger)
            assert f.getSeverity() == expected


class Test_SeverityFilter_setSeverity_getSeverity:

    def test_when_severity_is_set_then_get_returns_the_new_value(self, severity_filter):
        for severity in all_severities:
            severity_filter.setSeverity(severity)
            assert severity_filter.getSeverity() == severity


class Test_SeverityFilter_log:

    def test_only_messages_of_equal_or_greater_severity_are_relayed(
            self, severity_filter):

        mock_logger = severity_filter.upstreamLogger()

        msg = "A message"

        for filter_severity in all_severities:

            severity_filter.setSeverity(filter_severity)

            for message_severity in all_severities:
                mock_logger.reset_mock()
                severity_filter.log(msg, message_severity)
                if message_severity <= filter_severity:
                    mock_logger.log.assert_called_once_with(
                        msg, message_severity)
                else:
                    mock_logger.log.assert_not_called()
