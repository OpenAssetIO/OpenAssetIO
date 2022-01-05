"""
Provides a test PluginSystemPlugin implementation.
"""

from openassetio.pluginSystem import PluginSystemPlugin

class PackagePlugin(PluginSystemPlugin):
    # pylint: disable=missing-class-docstring

    @classmethod
    def identifier(cls):
        return "org.openassetio.test.pluginSystem.resources.packagePlugin"
