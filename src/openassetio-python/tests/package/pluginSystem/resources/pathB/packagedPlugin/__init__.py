"""
Provides a test PythonPluginSystemPlugin implemented within a package.
"""

# pylint gets upset, but this is fine due to
# the way the plugin system loads plugins.
# pylint: disable=import-error
from .PackagePlugin import PackageManagerPlugin


# pylint: disable=invalid-name
openassetioPlugin = PackageManagerPlugin
