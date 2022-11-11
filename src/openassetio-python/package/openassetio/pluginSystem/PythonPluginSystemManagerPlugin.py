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

    @warning This class, may be used in a batch, or UI session, so
    consequently, it is imperative that no ui libraries (QtCore, QtGui
    etc...) are imported unless @ref uiDelegate() is called, and
    ideally, even then, this should be deferred until something is
    requested from the @needsref
    openassetio-ui.implementation.ManagerUIDelegate.
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

        @see @ref openassetio.managerApi.ManagerInterface
        "ManagerInterface"
        """
        raise NotImplementedError

    @classmethod
    def interface(cls):
        """
        Constructs an instance of the @ref
        openassetio.managerApi.ManagerInterface.

        This is an instance of some class derived from ManagerInterface
        to be bound to the Host-facing @ref openassetio.hostApi.Manager.

        Generally this is only directly called by the @ref
        openassetio.pluginSystem.PythonPluginSystemManagerImplementationFactory.
        It may be called multiple times in a session, but there as the
        ManagerInterface API itself is specified as being stateless
        (aside from any internal caching/etc...) then there is no
        pre-requisite to always return a new instance.

        @return ManagerInterface instance
        """
        raise NotImplementedError

    @classmethod
    def uiDelegate(cls, interfaceInstance):
        """
        Constructs an instance of the @needsref
        openassetio-ui.implementation.ManagerUIDelegate

        This is an instance of some class derived from ManagerUIDelegate
        that is used by the @needsref UISessionManager to provide
        widgets to a host that may bind into panels in the application,
        or to allow the application to delegate asset browsing/picking
        etc...

        @param interfaceInstance An instance of the plugins interface as
        returned by @ref interface(), this is to allow UI to be
        configured in relation to a specific instantiation, which may
        perhaps target a different endpoint due to its settings, etc...

        @note It is safe to import any UI toolkits, etc... *within in
        this call*, but generally you may want to deffer this to methods
        in the delegate.

        @return An instance of some class derived from @needsref
        ManagerUIDelegate.
        """
        return None
