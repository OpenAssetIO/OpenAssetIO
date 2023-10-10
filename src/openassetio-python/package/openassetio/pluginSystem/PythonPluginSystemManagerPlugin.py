#
#   Copyright 2013-2021 The Foundry Visionmongers Ltd
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""
@namespace openassetio.pluginSystem.PythonPluginSystemManagerPlugin
A single-class module, providing the PythonPluginSystemManagerPlugin
class.
"""

from .PythonPluginSystemPlugin import PythonPluginSystemPlugin
from ..errors import NotImplementedException


# As this is an abstract interface, these are expected
# pylint: disable=unused-argument

__all__ = ["PythonPluginSystemManagerPlugin"]


class PythonPluginSystemManagerPlugin(PythonPluginSystemPlugin):
    """
    This class represents the various derived classes that make up the
    binding to a @ref asset_management_system.

    It used by the dynamic plug-in discovery mechanism (@ref
    openassetio.pluginSystem.PythonPluginSystem) to instantiate the main
    classes in an implementation.

    The class will never be instantiated itself, so all functionality is
    via class methods.

    In order to register a new asset management system, simply place a
    python package on the appropriate search path, that has a top-level
    attribute called 'plugin', that holds a class derived from this.
    """

    @staticmethod
    def identifier():
        """
        Returns an identifier to uniquely identify the plug-in.
        Generally, this should be the identifier used by the manager.
        The identifier should use only alpha-numeric characters and '.',
        '_' or '-'. For example:

            "org.openassetio.test.manager"

        @return str

        @see @fqref{managerApi.ManagerInterface} "ManagerInterface"
        """
        raise NotImplementedException("identifier not implemented")

    @classmethod
    def interface(cls):
        """
        Constructs an instance of the
        @fqref{managerApi.ManagerInterface} "ManagerInterface".

        This is an instance of some class derived from ManagerInterface
        to be bound to the Host-facing @fqref{hostApi.Manager} "Manager".

        Generally this is only directly called by the @ref
        openassetio.pluginSystem.PythonPluginSystemManagerImplementationFactory.

        @return ManagerInterface instance
        """
        raise NotImplementedException("interface not implemented")
