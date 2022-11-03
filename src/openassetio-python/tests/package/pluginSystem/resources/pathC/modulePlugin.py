"""
Provides a plugin that uses the same identifier as the ModulePlugin in
the `pathA` folder.
"""

from openassetio.pluginSystem import PythonPluginSystemManagerPlugin


class ModulePlugin(PythonPluginSystemManagerPlugin):
    """
    Provides an alternate implementation of the ModulePlugin
    to aid testing of path precedence.
    """

    @classmethod
    def identifier(cls):
        identifier = "org.openassetio.test.pluginSystem.resources.modulePlugin"
        return identifier

    @classmethod
    def interface(cls):
        # This is nonsense, but allows us to check where this was
        # loaded from in precedence checks.
        return {"file": __file__}


# pylint: disable=invalid-name
plugin = ModulePlugin
