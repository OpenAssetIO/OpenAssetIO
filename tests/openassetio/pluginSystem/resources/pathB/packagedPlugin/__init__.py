"""
Provides a test PluginSystemPlugin implemented within a package.
"""

# pylint gets upset, but this is fine due to
# the way the plugin system loads plugins.
# pylint: disable=import-error
from .PackagePlugin import PackagePlugin

# pylint: disable=invalid-name
plugin = PackagePlugin
