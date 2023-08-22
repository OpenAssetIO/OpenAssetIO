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
@namespace openassetio._core.audit
This module provides utility code that allows method and object usage
to be audited.
"""

import copy
import functools
import inspect
import os


# Support the existing names for module-level vars
# pylint: disable=invalid-name


__all__ = [
    "auditor",
    "auditCall",
    "auditApiCall",
    "auditCalls",
    "captureArgs",
    "reprArgs",
    "Auditor",
]

##
# @namespace openassetio._core.audit
# This module permits auditing of the use of the various API calls during a
# series of operations.
# @envvar **OPENASSETIO_AUDIT** *int* [0] If non-zero API calls will be
# audited by default
# @envvar **OPENASSETIO_AUDIT_ARGS** *int* [0] If non-zero args will be
# captured during audit, if auditing is disabled, this has no effect.

## Will hold the singleton Auditor object
__auditor = None

## When set to True, decorated calls will be audited. When False, minimal
## additional code is run, to minimize performance impact. This should always
## be False by default.
auditCalls = os.environ.get("OPENASSETIO_AUDIT", "0") != "0"

## If True, the args for each invocation of a function will be recorded, to
## aide debugging
captureArgs = os.environ.get("OPENASSETIO_AUDIT_ARGS", "0") != "0"

## Some hosts have issues with us holding onto objects. Setting this to True
## will ensure that we repr the objects whilst they are still alive.
reprArgs = False


def auditor():
    """
    Returns a singleton Auditor, created on demand.
    """
    # pylint: disable=global-statement
    global __auditor
    if not __auditor:
        __auditor = Auditor()
    return __auditor


## @name Decorators
## @{


def auditCall(function):
    """
    A decorator to log a method, as long as auditCalls is True, with no
    other special logic.
    """

    @functools.wraps(function)
    def _auditCall(self, *args, **kwargs):
        if auditCalls:
            sharedAuditor = auditor()

            arg = __prepareArgs(args, kwargs)
            sharedAuditor.addMethod(function, arg=arg)

        return function(self, *args, **kwargs)

    # Store the original function on the method for other decorators
    _auditCall.func_wrapped = function

    return _auditCall if auditCalls else function


def auditApiCall(group=None, static=False):
    """
    A decorator to log a method as long as auditCalls is True, parsing
    the methods args and kwargs with an understanding of the various
    objects used in the openassetio. This of this as being analogous to
    'stateful packet inspection'.

    If auditCalls is False, functions will not be wrapped so docstrings
    are not obfuscated and the call stack isn't bloated. Because
    wrapping happens when the Class is parsed, for auditing to ever be
    enabled, it has to be set by the environment variable so that it's
    true before other classes are loaded from their modules. Otherwise,
    its too late to turn it on once the import has completed.

    @param group str, an optional group name to log the call under @ref
    Auditor.addMethod

    @param static bool, set to True if the decorated function is a
    static method.
    """

    def _wrapAuditApiCall(function):
        # We deliberately don't wrap the function if its disabled as it
        # a) obfuscates docstrings
        # b) adds unnecessarily to the call stack
        if not auditCalls:
            return function

        @functools.wraps(function)
        def _auditApiCall(*args, **kwargs):
            if auditCalls:
                sharedAuditor = auditor()

                instance = None
                if not static and args:
                    instance = args[0]

                arg = __prepareArgs(args if static else args[1:], kwargs)
                sharedAuditor.addMethod(function, obj=instance, group=group, arg=arg)

                for arg in args:
                    __auditObj(sharedAuditor, arg)
                for arg in kwargs.values():
                    __auditObj(sharedAuditor, arg)

            return function(*args, **kwargs)

        # Store the original function on the method for other decorators
        _auditApiCall.func_wrapped = function

        return _auditApiCall

    return _wrapAuditApiCall


## @}


def __auditObj(aud, obj):
    """
    Performs additional auditing of the supplied argument, including
    inspection of lists/dicts, and the various properties of a Context.

    @param aud Auditor, The Auditor to receive data
    """

    # Here to prevent cyclic dependencies
    # pylint: disable=import-outside-toplevel
    from .. import Context

    # Look inside sequence types / dicts
    if isinstance(obj, (list, tuple)):
        for element in obj:
            __auditObj(aud, element)
        return

    if isinstance(obj, dict):
        for value in obj.values():
            __auditObj(aud, value)
        return

    if isinstance(obj, Context):
        # If its a Context, add the context, and its options
        aud.addClass(obj)
        aud.addObj("Context.%s" % obj.access, group="Context Access")
        if obj.locale:
            aud.addClass(obj.locale, group="Locales")


def __prepareArgs(args, kwargs):
    arg = None

    if captureArgs and (args or kwargs):
        arg = (args, kwargs)
        if reprArgs:
            arg = repr(arg)

    return arg


class Auditor(object):
    """
    This class provides a quick-and-dirty accounting mechanism for
    Class, method and object usage. The idea is to look at the extents
    of usage, rather than any kind of realtime reporting.

    Raw coverage data is accessible, or can be sprinted to a string.
    """

    kKey_Count = "__count__"
    kKey_Args = "__args__"

    def __init__(self):
        super(Auditor, self).__init__()

        self.__enabled = True
        self.reset()

    def getEnabled(self):
        """
        @returns `bool` The enabled state of the Auditor.
        """
        return self.__enabled

    def setEnabled(self, enabled):
        """
        Sets the state of the auditor.

        When disabled, all audit calls will be lightweight no-ops.

        @param enabled `bool` The new enabled state.
        """
        self.__enabled = enabled

    def reset(self):
        """
        Clears any recorded usage.
        """
        self.__coverage = {}
        self.__groups = {}

    def addClass(self, obj, group=None):
        """
        Adds usage of the supplied Class.

        @param obj instance or class, The Class to record will
        ultimately be determined by inspection of __class__ or type() on
        this object or its base.

        @param group str [None], If supplied, the Class's usage will
        also be counted in the supplied group.

        @return dict, The coverage data dict for the Class
        """
        if not self.__enabled:
            return {}

        cls = self.__classFromObj(obj)

        # Classes are simply stored as top-level keys in the __coverage dict
        clsDict = self.__getObjDict(self.__coverage, cls)
        clsDict[self.kKey_Count] += 1

        # If we have a group, we store Classes as top-level keys there too
        if group:
            groupDict = self.__groups.setdefault(group, {})
            groupClsDict = self.__getObjDict(groupDict, cls)
            groupClsDict[self.kKey_Count] += 1

        # We return the dictionary for the Class to make chained usage easier later
        # on - so we don't have to go hunting for it twice
        return clsDict

    def addMethod(self, instanceMethod, obj=None, group=None, arg=None):
        """
        Adds usage of a method.

        @param instanceMethod object, The function or bound method that
        you will to count.

        @param obj object [None], If supplied the parent Class for the
        method will be determined from this object, rather than from
        introspection of the instanceMethod arg.

        @param group str, If supplied, a count will also be registered
        for the method under this group (note: for groups, the parent
        Class usage isn't recorded).

        @param arg dict [{}] Can contain the args passed to the method
        at the time of invocation, these will be stored as an array
        under the kKey_Args key in the functions coverage dict.

        @return dict, The coverage data dict for the method
        """

        if not self.__enabled:
            return {}

        # Count a usage of the methods Class, which will conveniently give us back
        # the right dictionary for any child methods, etc....
        cls = self.__classFromObj(obj if obj else instanceMethod)
        clsDict = self.addClass(cls)

        # Unpack the function object if its a bound method
        func = instanceMethod
        if hasattr(instanceMethod, "im_func"):
            func = instanceMethod.im_func

        # Now count the function as a key under it's parent Class's dict
        methodDict = self.__getObjDict(clsDict, func)
        methodDict[self.kKey_Count] += 1

        # If we have been supplied args, then append them to the kKey_Args key in
        # the method's dict.
        if arg:
            argsList = methodDict.setdefault(self.kKey_Args, [])
            try:
                argsList.append(copy.deepcopy(arg))
            except BaseException:  # pylint: disable=broad-except
                pass

        # If we have a group, count the method there too. We don't keep args here,
        # only in the main __coverage dict.
        if group:
            groupDict = self.__groups.setdefault(group, {})
            groupObjDict = self.__getObjDict(groupDict, func)
            groupObjDict[self.kKey_Count] += 1

        # Return this in case its useful
        return methodDict

    def addObj(self, obj, group=None):
        """
        Simply count the usage of 'something'. Doesn't really matter
        what, as long as its hashable so can be used as a key in a dict.

        @param obj hashable, The object to count a use of.

        @param group str [None], If supplied, a count will also be
        recorded under the named group.

        @return dict, The coverage dict for the object.
        """

        if not self.__enabled:
            return {}

        objDict = self.__getObjDict(self.__coverage, obj)
        objDict[self.kKey_Count] += 1

        if group:
            groupDict = self.__groups.setdefault(group, {})
            groupObjDict = self.__getObjDict(groupDict, obj)
            groupObjDict[self.kKey_Count] += 1

        return objDict

    def coverage(self):
        """
        @return dict, The main coverage data dict with all data since
        the last reset. It is a hierarchical dictionary where at any
        level two keys represent the coverage data: kKey_Count (int) and
        kKey_Args (list). Other keys in the dict represent child counts.
        For example top-level keys are Classes or arbitrary objects.
        Other keys under a Class dict are the methods of that Class.
        """
        return self.__coverage

    def groups(self):
        """
        @return dict, As per coverage, except the Grouping dict is
        returned. If no grouped counts have been made, this will be
        empty. Otherwise, the top-level keys will be group names, and
        values will be a dictionary of coverage dicts for arbitrary
        objects.
        """
        return self.__groups

    def sprintCoverage(self, groupsOnly=False):
        """
        @return str, A multi-line formatted string containing recorded
        coverage.
        """
        # pylint: disable=too-many-nested-blocks

        outputStr = ""

        if not groupsOnly and self.__coverage:
            outputStr += "Coverage:\n\n"
            for key in sorted(self.__coverage.keys()):
                # key will be a Class or arbitrary object
                itemDict = self.__coverage[key]
                objName = key.__name__ if hasattr(key, "__name__") else key
                outputStr += "  %s (%d)\n" % (objName, itemDict.get(self.kKey_Count, 0))
                for method, data in itemDict.items():
                    # method will be a method or function (or the count key for the class)
                    # data will be the data for that method
                    if method == self.kKey_Count:
                        continue
                    objName = method.__name__ if hasattr(method, "__name__") else method
                    outputStr += "    %s (%s)\n" % (objName, data.get(self.kKey_Count, 0))
                    # Print the args list for each invocation if we have the data
                    args = data.get(self.kKey_Args, [])
                    if args:
                        for arg in args:
                            # Some hosts will raise here based on binding issues, etc...
                            try:
                                outputStr += "        %r\n" % (arg,)
                            except BaseException:  # pylint: disable=broad-except
                                pass
                        outputStr += "\n"

        if self.__groups:
            outputStr += "\n"
            outputStr += "Groups:\n\n"
            for coverageGroup in sorted(self.__groups.keys()):
                # Groups are just arbitrary string keys
                outputStr += "  %s:\n" % coverageGroup
                gDict = self.__groups[coverageGroup]
                for key in sorted(gDict.keys()):
                    # key could be a class, or anything really
                    objName = key.__name__ if hasattr(key, "__name__") else key
                    outputStr += "    %s (%d)\n" % (objName, gDict[key].get(self.kKey_Count, 0))
                outputStr += "\n"

        return outputStr

    def __getObjDict(self, parentDict, obj):
        # Presently, we simply create a child dict for the obj if there isn't one,
        # and ensure it has the count key, and its initialized to 0
        return parentDict.setdefault(obj, {self.kKey_Count: 0})

    @staticmethod
    def __classFromObj(obj):
        # If its an instance method then get self, which will be an instance, or a
        # class in the case of @classmethods
        if hasattr(obj, "im_self"):
            obj = obj.im_self

        # If its a class, were good
        if inspect.isclass(obj):
            return obj

        # Else, see if we can get the class
        if hasattr(obj, "__class__"):
            return obj.__class__

        # Fall back on Type
        return type(obj)
