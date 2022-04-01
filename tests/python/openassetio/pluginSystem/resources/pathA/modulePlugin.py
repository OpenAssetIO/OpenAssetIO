"""
Provides a test PluginSystemPlugin implemented within a single file
module.
"""

from openassetio.pluginSystem import PluginSystemPlugin

class ModulePlugin(PluginSystemPlugin):
    # pylint: disable=missing-class-docstring

    @classmethod
    def identifier(cls):
        return "org.openassetio.test.pluginSystem.resources.modulePlugin"

# pylint: disable=invalid-name
plugin = ModulePlugin
