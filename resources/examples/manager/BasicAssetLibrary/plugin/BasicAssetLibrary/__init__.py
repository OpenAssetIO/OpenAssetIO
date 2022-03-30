#
#   Copyright 2013-2022 [The Foundry Visionmongers Ltd]
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
The BasicAssetLibrary provides a basic "librarian" asset management
system.

It serves to provide a minimum level of functionality to allow simple
demonstrations and end-to-end tests to be realized with a little
supporting infrastructure as possible.

The BasicAssetLibrary lives in the simpler category of asset
management systems - one that is not capable of providing information
about a future entity. In that, it can not determine the primary string
(e.g. path) for an entity that does not exist yet. It will simply
remember entities it is told about, and provide that information through
the OpenAssetIO API methods.

It is designed to be easy to bootstrap into a known state though a
simple JSON configuration file that provides the entirety of some
asset library.

This manager has no specific understanding about any kind of entity,
and consequently has no inherent hierarchy or structural understanding
of parent/child relationships. Entities are simply registered by name
in a flat global namespace.

This package should be placed on $OPENASSETIO_PLUGIN_PATH. This does not
need to be on `$PYTHONPATH` directly, the plugin system takes care
of extending Python's runtime paths accordingly.
"""

# pylint: disable=import-outside-toplevel
#
# It is important to minimise imports here. This module will be loaded
# when the plugin system scans for plugins. Postpone importing any
# of the actual implementation until it is needed by the
# ManagerPlugin's implementation.
from openassetio.pluginSystem import ManagerPlugin


class BasicAssetLibraryPlugin(ManagerPlugin):
    """
    The ManagerPlugin is responsible for constructing instances of the
    manager's implementation of the OpenAssetIO interfaces and
    returning them to the host.
    """

    @staticmethod
    def identifier():
        return "org.openassetio.examples.manager.bal"

    @classmethod
    def interface(cls):
        from .BasicAssetLibraryInterface import BasicAssetLibraryInterface

        return BasicAssetLibraryInterface()


# Set the plugin class as the public entrypoint for the plugin system.
# A plugin is only considered if it exposes a `plugin` variable at this
# level, holding a class derived from ManagerPlugin.

# pylint: disable=invalid-name
plugin = BasicAssetLibraryPlugin
