"""
Provides a test PythonPluginSystemPlugin implemented within a single file
module.
"""

from openassetio.pluginSystem import PythonPluginSystemManagerPlugin


class ModulePlugin(PythonPluginSystemManagerPlugin):
    # pylint: disable=missing-class-docstring

    @classmethod
    def identifier(cls):
        return "org.openassetio.test.pluginSystem.resources.modulePlugin"

    @classmethod
    def interface(cls):
        # This is nonsense, but allows us to check where this was
        # loaded from in precedence checks.
        return {"file": __file__}


# pylint: disable=invalid-name
plugin = ModulePlugin
