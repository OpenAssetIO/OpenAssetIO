"""
Provides a test PythonPluginSystemPlugin implemented within a single file
module.
"""

from openassetio.pluginSystem import PythonPluginSystemPlugin


class ModulePlugin(PythonPluginSystemPlugin):
    # pylint: disable=missing-class-docstring

    @classmethod
    def identifier(cls):
        return "org.openassetio.test.pluginSystem.resources.modulePlugin"


# pylint: disable=invalid-name
plugin = ModulePlugin
