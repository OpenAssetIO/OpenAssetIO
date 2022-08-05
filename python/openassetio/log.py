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
@namespace openassetio.log
Provides the core classes that facilitate message and progress logging.
"""

import os

from . import _openassetio  # pylint: disable=no-name-in-module


LoggerInterface = _openassetio.log.LoggerInterface
ConsoleLogger = _openassetio.log.ConsoleLogger



class SeverityFilter(LoggerInterface):
    """
    The SeverityFilter is a wrapper for a logger that drops messages
    below a requested severity. More severe messages are relayed.

    @envvar **OPENASSETIO_LOGGING_SEVERITY** *[int]* If set, the
    default displaySeverity for the filter is set to the value of the
    env var.
    """

    def __init__(self, upstreamLogger):
        LoggerInterface.__init__(self)

        self.__minSeverity = self.kWarning

        if "OPENASSETIO_LOGGING_SEVERITY" in os.environ:
            try:
                self.__minSeverity = int(os.environ["OPENASSETIO_LOGGING_SEVERITY"])
            except ValueError:
                pass

        self.__upstreamLogger = upstreamLogger

    def upstreamLogger(self):
        """
        Returns the logger wrapped by the filter.

        @return LoggerInterface
        """
        return self.__upstreamLogger

    ## @name Filter Severity
    # Messages logged with a severity greater or equal to this will be displayed.
    ## @{

    def setSeverity(self, severity):
        """
        Sets the minimum severity of message that will be passed on to
        the @ref upstreamLogger.

        @param severity `int` One of the LoggerInterface severity
        constants.

        @see @ref LoggerInterface
        """
        self.__minSeverity = severity

    def getSeverity(self):
        """
        Returns the minimum seveirty of message that will be passed on
        to the @ref upstreamLogger by the filter.

        @return `int`

        @see @ref LoggerInterface
        """
        return self.__minSeverity

    ## @}

    # LoggerInterface methods

    def log(self, severity, message):
        """
        Log only if `severity` is greater than or equal to this logger's
        configured severity level.
        """
        if severity < self.__minSeverity:
            return

        self.__upstreamLogger.log(severity, message)
