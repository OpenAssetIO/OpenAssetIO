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
"""@namespace openassetio._core.debug
Assorted decorators to help with API development. For the sake of
optimisation, and help(fn) still making sense, then they may be disabled
by default.

@envvar **OPENASSETIO_DEBUG** *int* [1] when non-zero, debug decorators
will be enabled, allowing API calls to be monitored and timed using the
kDebug and kDebugApi logging severity displays

In order to use these decorators the target class must derive from
Debuggable, and have its `_debugLogFn` set to an callable that matches
the @fqref{log.LoggerInterface.log} "LoggerInterface.log" signature. This
callback will be used to output debug information. If no callback is
set, no debug output will be produced.

@todo The current logging implementation doesn't have any global
'display severity' concept (for good reasons), this has precluded any of
the optimisations we used to make earlying-out when we're at kInfo or
less. Once we port this implementation to cpp, then we may wish to
adjust how we enable/disable this functionality to avoid any unwanted
overhead per-call.
"""

# For private decorator implementation methods
# pylint: disable=invalid-name

import functools
import os
import time

from ..log import LoggerInterface


__all__ = ["debugCall", "debugApiCall", "Debuggable"]

enableDebugDecorators = os.environ.get("OPENASSETIO_DEBUG", "1") != "0"


class Debuggable:
    """
    A base class for any objects that you with to make use of the debug
    decorators with.
    """

    ## If enabled, decorated calls on the object will be logged
    _debugCalls = True
    ## Set to a callable that matches @ref openassetio.log.LoggerInterface.log
    _debugLogFn = None


def debugCall(function):
    """
    Use as a decorator to trace usage of the decorated function though
    the kDebug logging severity. This should only be used on bound
    methods.
    """

    # Early out if we're not enabled
    if not enableDebugDecorators:
        return function

    # Because some of our decorators get chained, let see if we have the
    # original function, otherwise we just log the decorator, which is
    # useful to neither man nor beast (only our decorators bother to set this).
    debugFn = function
    if hasattr(function, "func_wrapped"):
        debugFn = function.func_wrapped

    @functools.wraps(function)
    def _debugCall(*args, **kwargs):
        return __debugCall(function, debugFn, LoggerInterface.Severity.kDebug, *args, **kwargs)

    return _debugCall


def debugApiCall(function):
    """
    Use as a decorator to trace usage of the decorated API functions
    through the kDebugApi logging severity. This should only be used on
    bound methods.
    """
    # See notes in debugCall

    # Early out if we're not enabled
    if not enableDebugDecorators:
        return function

    debugFn = function
    if hasattr(function, "func_wrapped"):
        debugFn = function.func_wrapped

    @functools.wraps(function)
    def _debugApiCall(*args, **kwargs):
        return __debugCall(function, debugFn, LoggerInterface.Severity.kDebugApi, *args, **kwargs)

    return _debugApiCall


def __debugCall(function, traceFn, severity, self, *args, **kwargs):
    if not isinstance(self, Debuggable):
        raise RuntimeError(
            "Debug tracing methods can only be used on instances of a"
            " class derived from Debuggable"
        )

    # pylint: disable=protected-access

    # function and traceFn are provided so that when the function is wrapped,
    # traceFn is printed to the log, but function (usually the wrapper) is
    # still executed.

    # Debugging can be disabled on-the-fly if the object has a _debugCalls
    # attribute who's value casts to False
    enabled = self._debugCalls and self._debugLogFn is not None
    if not enabled:
        return function(self, *args, **kwargs)

    allArgs = [repr(a) for a in args]
    allArgs.extend(["%s=%r" % (k, v) for k, v in kwargs.items()])

    msg = "-> %x %r.%s( %s )" % (id(self), self, traceFn.__name__, ", ".join(allArgs))
    self._debugLogFn(msg, severity)

    result = "<exception>"
    timer = _Timer()
    try:
        with timer:
            result = function(self, *args, **kwargs)
    finally:
        msg = "<- %x %r.%s [%s] %r" % (id(self), self, traceFn.__name__, timer, result)
        self._debugLogFn(msg, severity)

    return result


class _Timer(object):
    """
    A simple timer object that can be used, for, er, timing things from
    a wall-clock point of view.
    """

    def __init__(self):
        object.__init__(self)
        self.start = 0
        self.end = None

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()

    def interval(self):
        """
        Returns the interval of time the timer ran for. If the timer
        is still running, then it will report the interval to the
        time the method was called.

        @return `float` The time interval as per `time.time()`
        """
        end = self.end if self.end is not None else time.time()
        return end - self.start

    def __str__(self):
        return "%.05fs" % self.interval()
