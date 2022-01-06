"""
Provides a plugin that uses the same identifier as the ModulePlugin in
the `pathA` folder.
"""

from openassetio.pluginSystem import PluginSystemPlugin

class ModulePlugin(PluginSystemPlugin):
    """
    Provides an alternate implementation of the ModulePlugin
    to aid testing of path precedence.
    """

    @classmethod
    def identifier(cls):
        identifier = "org.openassetio.test.pluginSystem.resources.modulePlugin"
        return identifier

# pylint: disable=invalid-name
plugin = ModulePlugin
