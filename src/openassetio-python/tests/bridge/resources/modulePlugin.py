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
# Use the same plugin to test both manager and UI delegate plugin
# discovery, abusing Python weak typing. For these tests we only care
# that discovery is working, we don't need to instantiate.
openassetioPlugin = ModulePlugin
openassetioUIPlugin = ModulePlugin
