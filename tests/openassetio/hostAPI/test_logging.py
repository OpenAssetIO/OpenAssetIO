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

import pytest
from unittest import mock

import openassetio.logging as lg


# The logging mechanism is very much in flux right now, as we move away from
# singleton/global loggers and to a per-session mechanism. Consequently we are
# investing in minimal testing here until this has stabilised. Both the design
# and implementation may well change significantly.
#
# The tests focus upon any API critical semantics of logging, vs the robustness
# of any of the placeholder implementation, or implementation borrowed from
# the old API.

def test_LoggerInterface_progress():
    logger = lg.LoggerInterface()
    logger.log = mock.create_autospec(logger.log)

    msg = "I am a message"
    expected_log_msg = f" 10% {msg}"
    logger.progress(0.1, msg)
    logger.log.assert_called_once_with(expected_log_msg, lg.LoggerInterface.kProgress)


@pytest.fixture
def mock_logger():
    return mock.create_autospec(spec=lg.LoggerInterface)


@pytest.fixture
def severity_filter(mock_logger):
    return lg.SeverityFilter(mock_logger)


class TestSeverityFilter():
    all_severities = (
        lg.LoggerInterface.kDebugAPI,
        lg.LoggerInterface.kDebug,
        lg.LoggerInterface.kInfo,
        lg.LoggerInterface.kProgress,
        lg.LoggerInterface.kWarning,
        lg.LoggerInterface.kError,
        lg.LoggerInterface.kCritical
    )

    def test_constructor(self, mock_logger, monkeypatch):

        var = "OPENASSETIO_LOGGING_SEVERITY"

        # Unset

        monkeypatch.delenv(var, raising=False)
        f = lg.SeverityFilter(mock_logger)
        assert f.getSeverity() == lg.LoggerInterface.kWarning

        # Set

        for value, expected in (
                ("", lg.LoggerInterface.kWarning),
                ("not a valid value", lg.LoggerInterface.kWarning),
                (lg.LoggerInterface.kDebugAPI, lg.LoggerInterface.kDebugAPI),
                (lg.LoggerInterface.kDebug, lg.LoggerInterface.kDebug),
                (lg.LoggerInterface.kInfo, lg.LoggerInterface.kInfo),
                (lg.LoggerInterface.kProgress, lg.LoggerInterface.kProgress),
                (lg.LoggerInterface.kWarning, lg.LoggerInterface.kWarning),
                (lg.LoggerInterface.kError, lg.LoggerInterface.kError),
                (lg.LoggerInterface.kCritical, lg.LoggerInterface.kCritical)
        ):
            monkeypatch.setenv(var, str(value))
            f = lg.SeverityFilter(mock_logger)
            assert f.getSeverity() == expected

    def test_severity_accessors(self, severity_filter):
        for severity in self.all_severities:
            severity_filter.setSeverity(severity)
            assert severity_filter.getSeverity() == severity

    def test_filtering(self, severity_filter):

        mock_logger = severity_filter.upstreamLogger()

        msg = "A message"

        for filter_severity in self.all_severities:

            severity_filter.setSeverity(filter_severity)

            for message_severity in self.all_severities:
                mock_logger.reset_mock()
                severity_filter.log(msg, message_severity)
                if message_severity <= filter_severity:
                    mock_logger.log.assert_called_once_with(msg, message_severity)
                else:
                    mock_logger.log.assert_not_called()
