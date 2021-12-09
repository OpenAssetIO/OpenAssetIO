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

"""
The SampleAssetManager provides a working example of a primitive
asset management system, exposed through an OpenAssetIO ManagerPlugin.

It aims to demonstrate a canonical binding of a manager to the
OpenAssetIO API.

The actual inner workings and approach of the manager itself should
be taken with a pinch of salt though, and not used as a reference
for "how to build an asset management system". It is a minimal
implementation that serves the needs of the API for testing and
the purposes of exploring host workflows.

This package should be placed on $OAIO_PLUGIN_PATH. This does not
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


class SampleAssetManagerPlugin(ManagerPlugin):
    """
    The ManagerPlugin is responsible for constructing instances of the
    manager's implementation of the OpenAssetIO interfaces and
    returning them to the host.
    """

    @staticmethod
    def identifier():
        # The identifier here _must_ be the same as the one returned by
        # the interface implementation for it's `identifier` method.
        #
        # Note that it should always be light-weight to construct
        # instances of the ManagerInterface class. See the notes under
        # the "Initialization" section of:
        #   https://thefoundryvisionmongers.github.io/OpenAssetIO/classopenassetio_1_1manager_a_p_i_1_1_manager_interface_1_1_manager_interface.html#details (pylint: disable=line-too-long)
        from .SampleAssetManagerInterface import SampleAssetManagerInterface
        return SampleAssetManagerInterface.identifier()

    @classmethod
    def interface(cls):
        from .SampleAssetManagerInterface import SampleAssetManagerInterface
        return SampleAssetManagerInterface()


# Set the plugin class as the public entrypoint for the plugin system.
# A plugin is only considered if it exposes a `plugin` variable at this
# level, holding a class derived from ManagerPlugin.

# pylint: disable=invalid-name
plugin = SampleAssetManagerPlugin
