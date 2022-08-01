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
import sys

from . import _openassetio  # pylint: disable=no-name-in-module


LoggerInterface = _openassetio.LoggerInterface


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


class ConsoleLogger(LoggerInterface):
    """
    A simple logger that prints messages to stdout/stderr.
    """

    def __init__(self, colorOutput=True, forceDefaultStreams=False):
        """
        @param colorOutput bool [True] Make a vague attempt to color
        the output using terminal escape codes.

        @param forceDefaultStreams bool [False] Some applications remap
        the std outputs. When set, logging will attempt to write to the
        'real' sys.stderr and sys.stdout instead of the remapped
        outputs. If these have been closed, it will fall back to the
        remapped outputs.
        """
        LoggerInterface.__init__(self)
        self.__colorOutput = colorOutput

        self.__stdout = sys.stdout
        self.__stderr = sys.stderr

        if forceDefaultStreams:
            # In some occasions, the real std outs may have been closed (for example in
            # osx somewhere, when an app is launched in the GUI and uses something like
            # py2app. So, we try to fall back on the facaded outs instead.
            if not sys.__stdout__.closed:
                self.__stdout = sys.__stdout__
            if not sys.__stderr__.closed:
                self.__stderr = sys.__stderr__

    def log(self, severity, message):
        """
        Log to stderr for severity greater than `kInfo`, stdout
        otherwise.
        """
        severityStr = "[%s]" % self.kSeverityNames[severity]
        msg = "%11s: %s\n" % (severityStr, message)
        outStream = self.__stderr if severity > self.kInfo else self.__stdout
        outStream.write(self.__colorMsg(msg, severity) if self.__colorOutput else msg)

    @staticmethod
    def __colorMsg(msg, severity):

        end = '\033[0m'
        color = '\033[0;3%dm'

        if severity == LoggerInterface.kDebug:
            return "%s%s%s" % (color % 2, msg, end)
        if severity == LoggerInterface.kDebugApi:
            return "%s%s%s" % (color % 6, msg, end)
        if severity == LoggerInterface.kWarning:
            return "%s%s%s" % (color % 3, msg, end)
        if severity > LoggerInterface.kWarning:
            return "%s%s%s" % (color % 1, msg, end)

        return msg
