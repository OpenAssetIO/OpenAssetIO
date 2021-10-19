#
#   Copyright 2013-2021 [The Foundry Visionmongers Ltd]
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

from ..logging import LoggerInterface
from .. import exceptions


__all__ = ['PluginSystem']


class PluginSystem(object):
    """
    Loads Python Packages on a custom search path. If they manager a
    top-level 'plugin' attribute, that holds a class derived from
    PluginSystemPlugin, it will be registered with its identifier. Once
    a plug-in has registered an identifier, any subsequent registrations
    with that id will be skipped.
    """

    def __init__(self, logger):
        self.__map = {}
        self.__paths = {}
        self.__logger = logger

    def scan(self, paths):
        import os.path
        import imp
        import hashlib

        self.__logger.log(
            "PluginSystem: Looking for packages on: %s" % paths, self.__logger.kDebug)

        for path in paths.split(os.pathsep):

            if not os.path.isdir(path):
                self.__logger.log(
                    "PluginSystem: Omitting '%s' from plug-in search as"
                    " its not a directory" % path, self.__logger.kDebug)

            for bundle in os.listdir(path):

                bundlePath = os.path.join(path, bundle)
                if not os.path.isdir(bundlePath):
                    self.__logger.log(
                        "PluginSystem: Omitting '%s' as its not a package directory" % path,
                        self.__logger.kDebug)
                    continue

                # Make a unique namespace to ensure the plugin identifier is all that
                # really matters
                moduleName = hashlib.md5(bundlePath.encode("utf-8")).hexdigest()

                try:

                    module = imp.load_module(
                        moduleName, None, bundlePath, ("", "", imp.PKG_DIRECTORY))
                    if hasattr(module, 'plugin'):
                        self.register(module.plugin, bundlePath)

                except Exception as e:
                    msg = "PluginSystem: Caught exception loading plug-in from '%s':\n%s" % (
                        bundlePath, e)
                    self.__logger.log(msg, self.__logger.kError)

    def identifiers(self):
        return self.__map.keys()

    def getPlugin(self, identifier):

        if identifier not in self.__map:
            msg = "PluginSystem: No plug-in registered with the identifier '%s'" % identifier
            raise exceptions.PluginError(msg)

        return self.__map[identifier]

    def register(self, cls, path="<unknown>"):

        identifier = cls.getIdentifier()
        if identifier in self.__map:
            msg = "PluginSystem: Skipping class '%s' defined in '%s'. Already registered by '%s'" \
                  % (cls, path, self.__paths[identifier])
            self.__logger.log(msg, self.__logger.kDebug)
            return

        msg = "PluginSystem: Registered plug-in '%s' from '%s'" % (cls, path)
        self.__logger.log(msg, self.__logger.kDebug)

        self.__map[identifier] = cls
        self.__paths[identifier] = path
