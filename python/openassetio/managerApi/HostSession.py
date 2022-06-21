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
@namespace openassetio.managerApi.HostSession
A single-class module, providing the HostSession class.
"""

from openassetio import _openassetio  # pylint: disable=no-name-in-module

from ..log import LoggerInterface


class HostSession(_openassetio.managerApi.HostSession):
    """
    The HostSession is a manager-facing class that represents a discreet
    API session started by a @ref host in order to communicate with a
    manager.

    Any generalised API interactions a Manager may wish to make with a
    Host should be performed through the HostSession instance supplied
    with any ManagerInterface entrypoint. These objects should not be
    directly constructed, cached or otherwise persisted by a Manager.

    The HostSession provides access to:
      - A concrete instance of the @fqref{hostApi.HostInterface}
        "HostInterface", implemented by the tool or
        application that initiated the API session.
      - A logging callback. All user-facing messaging should be directed
        through this entrypoint. This ensures it will be appropriately
        presented to the user.

    @see @ref log
    @see @fqref{hostApi.HostInterface} "HostInterface"
    """
    kDebugAPI = LoggerInterface.kDebugAPI
    kDebug = LoggerInterface.kDebug
    kInfo = LoggerInterface.kInfo
    kProgress = LoggerInterface.kProgress
    kWarning = LoggerInterface.kWarning
    kError = LoggerInterface.kError
    kCritical = LoggerInterface.kCritical

    def __init__(self, host, logger):
        """
        The HostSession should not be directly constructed. They will be
        automatically managed by the API middleware.

        @private
        """
        super().__init__(host)

        self.__logger = logger

    def log(self, message, severity):
        """
        Logs a message to the user.

        All user-facing messaging should be routed though this method.
        It will be mapped to the correct host sub-systems to ensure that
        it is presented correctly.

        @see @ref openassetio.log "log"
        """
        self.__logger.log(message, severity)

    def progress(self, decimalProgress, message=None):
        """
        Logs the supplied progress. Hosts may implement specific
        handling for progress messages, mapping them to custom UI
        element. If not, it will be logged as-per other messages, with a
        kProgress severity.

        @param decimalProgress float, Normalised progress between 0 and
        1, if set to a value less than 0 it will be considered
        cancelled, if greater than one, complete.

        @param message str, A string message to display with the
        progress. If None is supplied, it is assumed that there is no
        message and the previous message may remain. Set to an empty
        string if it is desired to always clear the previous message.
        """
        self.__logger.progress(decimalProgress, message=message)
