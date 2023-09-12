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
@namespace openassetio.pluginSystem.PythonPluginSystemPlugin
A single-class module, providing the PythonPluginSystemPlugin class.
"""

from ..errors import NotImplementedException


class PythonPluginSystemPlugin(object):
    """
    The base class that defines a plugin of the plugin system.

    Only modules and packages that expose an instance of this class
    will be loaded by the plugin system when scanning any given
    path.
    """

    @classmethod
    def identifier(cls):
        """
        This method is required by all plugins, in order to uniquely
        identify this plugin. If there are duplicate plugins with the
        same identifier, the first one encountered will be used, and all
        others will be ignored.
        """
        raise NotImplementedException("identifier not implemented")
