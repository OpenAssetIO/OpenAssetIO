"""
Provides a test PythonPluginSystemPlugin implementation.
"""

from openassetio.pluginSystem import PythonPluginSystemManagerPlugin


class PackagePlugin(PythonPluginSystemManagerPlugin):
    # pylint: disable=missing-class-docstring

    @classmethod
    def identifier(cls):
        return "org.openassetio.test.pluginSystem.resources.packagePlugin"

    @classmethod
    def interface(cls):
        # This is nonsense, but allows us to check where this was
        # loaded from in precedence checks.
        return {"file": __file__}
