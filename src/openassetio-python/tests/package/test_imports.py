#
#   Copyright 2013-2023 The Foundry Visionmongers Ltd
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

Cases should be added for any of the following:
 - Discreet Python modules.
 - C++ implementations hoisted in an __init__.py file.
"""

import pytest


# pylint: disable=invalid-name
# pylint: disable=unused-import,import-outside-toplevel
# pylint: disable=missing-class-docstring,missing-function-docstring


@pytest.fixture(autouse=True)
def always_unload_openassetio_modules(
    unload_openassetio_modules,  # pylint: disable=unused-argument
):
    """
    Removes openassetio modules from the sys.modules cache that
    otherwise mask cyclic dependencies.
    """


class Test_package_imports:
    def test_importing_openassetio_succeeds(self):
        import openassetio

    def test_importing_constants_succeeds(self):
        from openassetio import constants

    def test_importing_Context_succeeds(self):
        from openassetio import Context

    def test_importing_EntityReference_succeeds(self):
        from openassetio import EntityReference

    def test_importing_log_succeeds(self):
        from openassetio import log

    def test_importing_utils_succeeds(self):
        from openassetio import utils


class Test_hostApi_imports:
    def test_importing_HostInterface_succeeds(self):
        from openassetio.hostApi import HostInterface

    def test_importing_ManagerFactory(self):
        from openassetio.hostApi import ManagerFactory

    def test_importing_Manager_succeeds(self):
        from openassetio.hostApi import Manager

    def test_importing_ManagerImplementationFactoryInterface_succeeds(self):
        from openassetio.hostApi import ManagerImplementationFactoryInterface

    def test_importing_terminology_succeeds(self):
        from openassetio.hostApi import terminology


class Test_managerApi_imports:
    def test_importing_Host_succeeds(self):
        from openassetio.managerApi import Host

    def test_importing_HostSession_succeeds(self):
        from openassetio.managerApi import HostSession

    def test_importing_ManagerInterface_succeeds(self):
        from openassetio.managerApi import ManagerInterface

    def test_importing_ManagerStateBase_succeeds(self):
        from openassetio.managerApi import ManagerStateBase


class Test_pluginSystem_imports:
    def test_importing_PythonPluginSystemManagerPlugin_succeeds(self):
        from openassetio.pluginSystem import PythonPluginSystemManagerPlugin

    def test_importing_PythonPluginSystem_succeeds(self):
        from openassetio.pluginSystem import PythonPluginSystem

    def test_importing_PythonPluginSystemManagerImplementationFactory_succeeds(self):
        from openassetio.pluginSystem import (
            PythonPluginSystemManagerImplementationFactory,
        )

    def test_importing_PythonPluginSystemPlugin_succeeds(self):
        from openassetio.pluginSystem import PythonPluginSystemPlugin


class Test_errors_imports:
    def test_importing_OpenAssetIOException_succeeds(self):
        from openassetio.errors import OpenAssetIOException

    def test_importing_ConfigurationException_succeeds(self):
        from openassetio.errors import ConfigurationException

    def test_importing_InputValidationException_succeeds(self):
        from openassetio.errors import InputValidationException

    def test_importing_NotImplementedException_succeeds(self):
        from openassetio.errors import NotImplementedException

    def test_importing_UnhandledException_succeeds(self):
        from openassetio.errors import UnhandledException


class Test_trait_imports:
    def test_importing_TraitsData_succeeds(self):
        from openassetio.trait import TraitsData


class Test_test_imports:
    def test_importing_manager_succeeds(self):
        from openassetio.test import manager


class Test_test_manager_imports:
    def test_importing_apiComplianceSuite_succeeds(self):
        from openassetio.test.manager import apiComplianceSuite

    def test_importing_harness_succeeds(self):
        from openassetio.test.manager import harness


class Test_ui_hostApi_imports:
    def test_importing_UIDelegateImplementationFactoryInterface_succeeds(self):
        from openassetio.ui.hostApi import UIDelegateImplementationFactoryInterface


class Test_ui_managerApi_imports:
    def test_importing_UIDelegateInterface_succeeds(self):
        from openassetio.ui.managerApi import UIDelegateInterface
