"""
Provides a test PythonPluginSystemPlugin using the deprecated `plugin`
hook
"""

from openassetio.pluginSystem import PythonPluginSystemPlugin


class DeprecatedPlugin(PythonPluginSystemPlugin):
    # pylint: disable=missing-class-docstring

    @classmethod
    def identifier(cls):
        return "org.openassetio.test.pluginSystem.resources.deprecated"


# The `plugin` hook is deprecated in favour of `openassetioPlugin`
# pylint: disable=invalid-name
plugin = DeprecatedPlugin
