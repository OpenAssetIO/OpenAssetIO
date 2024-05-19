"""
Provides a test PythonPluginSystemPlugin using the deprecated `plugin`
hook
"""

from openassetio.pluginSystem import PythonPluginSystemManagerPlugin


class DeprecatedPlugin(PythonPluginSystemManagerPlugin):
    # pylint: disable=missing-class-docstring

    @classmethod
    def identifier(cls):
        return "org.openassetio.test.pluginSystem.resources.deprecated"


# The `plugin` hook is deprecated in favour of `openassetioPlugin`
# pylint: disable=invalid-name
plugin = DeprecatedPlugin
