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
These test ensure that all modules are importable. This can help catch
dependencies between packages due to the hoisting required to hide
duplicate namespaces to match the future C++ implementation appearance.
"""

import pytest

# pylint: disable=no-self-use
# pylint: disable=invalid-name
# pylint: disable=unused-import,import-outside-toplevel
# pylint: disable=missing-class-docstring,missing-function-docstring


@pytest.fixture(autouse=True)
def always_unload_openassetio_modules(unload_openassetio_modules): # pylint: disable=unused-argument
    """
    Removes openassetio modules from the sys.modules cache that
    otherwise mask cyclic dependencies.
    """


class Test_package_imports:

    def test_importing_openassetui_succeeds(self):
        import openassetio

    def test_importing_constants_succeeds(self):
        from openassetio import constants

    def test_importing_Context_succeeds(self):
        from openassetio import Context

    def test_importing_exceptions_succeeds(self):
        from openassetio import exceptions

    def test_importing_log_succeeds(self):
        from openassetio import log

    def test_importing_SpecificationBase_succeeds(self):
        from openassetio import SpecificationBase

    def test_importing_Trait_succeeds(self):
        from openassetio import Trait


class Test_core_imports:

    def test_importing_audit_succeeds(self):
        from openassetio._core import audit

    def test_importing_debug_succeeds(self):
        from openassetio._core import debug

    def test_importing_objects_succeeds(self):
        from openassetio._core import objects


class Test_hostApi_imports:

    def test_importing_HostInterface_succeeds(self):
        from openassetio.hostApi import HostInterface

    def test_importing_ManagerFactory(self):
        from openassetio.hostApi import ManagerFactory

    def test_importing_Manager_succeeds(self):
        from openassetio.hostApi import Manager

    def test_importing_ManagerInterfaceFactoryInterface_succeeds(self):
        from openassetio.hostApi import ManagerInterfaceFactoryInterface

    def test_importing_Session_succeeds(self):
        from openassetio.hostApi import Session

    def test_importing_terminology_succeeds(self):
        from openassetio.hostApi import terminology


class Test_managerApi_imports:

    def test_importing_Host_succeeds(self):
        from openassetio.managerApi import Host

    def test_importing_HostSession_succeeds(self):
        from openassetio.managerApi import HostSession

    def test_importing_ManagerInterface_succeeds(self):
        from openassetio.managerApi import ManagerInterface


class Test_pluginSystem_imports:

    def test_importing_ManagerPlugin_succeeds(self):
        from openassetio.pluginSystem import ManagerPlugin

    def test_importing_PluginSystem_succeeds(self):
        from openassetio.pluginSystem import PluginSystem

    def test_importing_PluginSystemManagerInterfaceFactory_succeeds(self):
        from openassetio.pluginSystem import PluginSystemManagerInterfaceFactory

    def test_importing_PluginSystemPlugin_succeeds(self):
        from openassetio.pluginSystem import PluginSystemPlugin
