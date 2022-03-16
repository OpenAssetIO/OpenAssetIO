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

    def test_importing_Specification_succeeds(self):
        from openassetio import Specification

    def test_importing_SpecificationFactory_succeeds(self):
        from openassetio import SpecificationFactory

    def test_importing_specifications_succeeds(self):
        from openassetio import specifications


class Test_core_imports:

    def test_importing_audit_succeeds(self):
        from openassetio._core import audit

    def test_importing_debug_succeeds(self):
        from openassetio._core import debug

    def test_importing_objects_succeeds(self):
        from openassetio._core import objects


class Test_hostAPI_imports:

    def test_importing_HostInterface_succeeds(self):
        from openassetio.hostAPI import HostInterface

    def test_importing_Manager_succeeds(self):
        from openassetio.hostAPI import Manager

    def test_importing_ManagerFactoryInterface_succeeds(self):
        from openassetio.hostAPI import ManagerFactoryInterface

    def test_importing_Session_succeeds(self):
        from openassetio.hostAPI import Session

    def test_importing_terminology_succeeds(self):
        from openassetio.hostAPI import terminology

    def test_importing_transactions_succeeds(self):
        from openassetio.hostAPI import transactions


class Test_managerAPI_imports:

    def test_importing_Host_succeeds(self):
        from openassetio.managerAPI import Host

    def test_importing_HostSession_succeeds(self):
        from openassetio.managerAPI import HostSession

    def test_importing_ManagerInterface_succeeds(self):
        from openassetio.managerAPI import ManagerInterface


class Test_pluginSystem_imports:

    def test_importing_ManagerPlugin_succeeds(self):
        from openassetio.pluginSystem import ManagerPlugin

    def test_importing_PluginSystem_succeeds(self):
        from openassetio.pluginSystem import PluginSystem

    def test_importing_PluginSystemManagerFactory_succeeds(self):
        from openassetio.pluginSystem import PluginSystemManagerFactory

    def test_importing_PluginSystemPlugin_succeeds(self):
        from openassetio.pluginSystem import PluginSystemPlugin
