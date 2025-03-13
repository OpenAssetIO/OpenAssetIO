"""
Provides a test PythonPluginSystemPlugin implementation.
"""

from openassetio.pluginSystem import PythonPluginSystemPlugin


class PackagePlugin(PythonPluginSystemPlugin):
    # pylint: disable=missing-class-docstring

    @classmethod
    def identifier(cls):
        return "org.openassetio.test.pluginSystem.resources.pluginB"
