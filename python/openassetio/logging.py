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

import abc
import os
import sys


##
# @name Logger Interface
class LoggerInterface(object):
    __metaclass__ = abc.ABCMeta

    ##
    # @name Log Severity
    # @{

    kDebugAPI = 6
    kDebug = 5
    kInfo = 4
    kProgress = 3
    kWarning = 2
    kError = 1
    kCritical = 0

    ## A mapping of severity levels to readable labels
    kSeverityNames = ['critical', 'error', 'warning', 'progress', 'info', 'debug', 'debugAPI']

    ## @}

    @abc.abstractmethod
    def log(self, message, severity):
        """
        Logs a message to the user.

        This method must be implemented to present the supplied message
        to the user in an appropriate fashion.

        @param message str, The message string to be logged.

        @param severity int, One of the severity constants defined in
        @ref openassetio.logging
        """
        raise NotImplementedError

    def progress(self, decimalProgress, message=""):
        """
        Logs the progress of a task.

        This method should be overridden if you wish to customize the
        presentation of progress messages beyond the default
        implementation that simply logs them as any other message.

        @param decimalProgress float, Normalised progress between 0 and
        1, if set to a value less than 0 it should be considered
        cancelled, if greater than one, complete.

        @param message str, A message to display with the progress. If
        None is supplied, assume that there is no message and any
        previous message may remain. Set to an empty string if it is
        desired to always clear any previous message.
        """
        msg = "%3d%% %s" % (int(100 * decimalProgress), message if message is not None else "")
        self.log(msg, self.kProgress)


class SeverityFilter(LoggerInterface):
    """
    The SeverityFilter is a wrapper for a logger that drops messages
    below a requested severity. More severe messages are relayed.

    @envvar **OPENASSETIO_LOGGING_SEVERITY** *[int]* If set, the
    default displaySeverity for the filter is set to the value of the
    env var.
    """

    def __init__(self, upstreamLogger):

        self.__maxSeverity = self.kWarning

        if "OPENASSETIO_LOGGING_SEVERITY" in os.environ:
            try:
                self.__maxSeverity = int(os.environ["OPENASSETIO_LOGGING_SEVERITY"])
            except ValueError:
                pass

        self.__upstreamLogger = upstreamLogger

    def upstreamLogger(self):
        return self.__upstreamLogger

    ## @name Filter Severity
    # Messages logged with a severity greater or equal to this will be displayed.
    # Note: Confusingly, greater severities (ie. worse consequence) have a lower
    # numerical equivalent.
    # @todo Revisit severity <> int mappings etc...
    ## @{

    def setSeverity(self, severity):
        self.__maxSeverity = severity

    def getSeverity(self):
        return self.__maxSeverity

    ## @}

    # LoggerInterface methods

    def log(self, message, severity):

        if severity > self.__maxSeverity:
            return

        self.__upstreamLogger.log(message, severity)

    def progress(self, decimalProgress, message=""):

        if self.__maxSeverity < self.kProgress:
            return

        self.__upstreamLogger.progress(decimalProgress, message)


class ConsoleLogger(LoggerInterface):

    def __init__(self, colorOutput=True, forceDefaultStreams=False):
        """
        A simple filtered Logger that prints messages to stdout/stderr.

        @param colorOutput bool [True] Make a vague attempt to color
        the output using terminal escape codes.

        @param forceDefaultStreams bool [False] Some applications remap
        the std outputs. When set, logging will attempt to write to the
        'real' sys.stderr and sys.stdout instead of the remapped
        outputs. If these have been closed, it will fall back to the
        remapped outputs.
        """
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

    def log(self, message, severity):

        severityStr = "[%s]" % self.kSeverityNames[severity]
        msg = "%11s: %s\n" % (severityStr, message)
        outStream = self.__stderr if severity < self.kInfo else self.__stdout
        outStream.write(self.__colorMsg(msg, severity) if self.__colorOutput else msg)

    @staticmethod
    def __colorMsg(msg, severity):

        end = '\033[0m'
        color = '\033[0;3%dm'

        if severity == LoggerInterface.kDebug:
            return "%s%s%s" % (color % 2, msg, end)
        if severity == LoggerInterface.kDebugAPI:
            return "%s%s%s" % (color % 6, msg, end)
        if severity == LoggerInterface.kWarning:
            return "%s%s%s" % (color % 3, msg, end)
        if severity < LoggerInterface.kWarning:
            return "%s%s%s" % (color % 1, msg, end)

        return msg
