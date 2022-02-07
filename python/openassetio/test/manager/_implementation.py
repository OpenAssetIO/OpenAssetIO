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
@namespace openassetio.test.manager._implementation
Private implementation classes for the manager test framework.
@private
"""
import unittest

from openassetio import hostAPI, pluginSystem, logging

from .specifications import ManagerTestHarnessLocale


__all__ = ['createHarness']


def createHarness(managerIdentifier):
    """
    Create the test harness used begin test case execution.
    @private
    """
    hostInterface = _ValidatorHarnessHostInterface()
    logger = logging.SeverityFilter(logging.ConsoleLogger())
    managerFactory = pluginSystem.PluginSystemManagerFactory(logger)

    session = hostAPI.Session(hostInterface, logger, managerFactory)
    session.useManager(managerIdentifier)

    loader = _ValidatorTestLoader(session)
    return _ValidatorHarness(unittest.main, loader)


class _ValidatorHarness:
    """
    The manager test harness.

    It acts as an anti-corruption layer around a unittest-compatible
    test runner, injecting a custom testcase loader.

    @private
    """
    # pylint: disable=too-few-public-methods

    _kValidatorHarnessProgramName = "openassetio.test.manager"

    def __init__(self, runner, loader):
        """
        Initializes an instance of this class.

        @param runner `unittest.main` A unittest-compatible test runner.

        @param loader ValidatorTestLoader A unittest-compatible test
        case loader that injects test fixtures into test case instances.
        """
        self.__runner = runner
        self.__loader = loader

    def executeTests(self, extraArgs, module, fixtures):
        """
        Run the tests harness test cases in the provided `module`,
        passing any `extraArgs` to the test runner.

        @param extraArgs `List[str]` Arguments to pass to the unittest
        runner.

        @param module `types.ModuleType` Python module containing the
        test cases to execute.

        @param fixtures `dict` A dictionary containing fixtures for the
        the tests. See harness.executeSuite for structure.

        @return `bool` `True` if all tests succeeded, `False` otherwise.
        """
        # Ensure the loader has the correct fixtures
        self.__loader.setFixtures(fixtures)
        # Prepend the "program name" to simulate full argv for unittest.
        argv = [self._kValidatorHarnessProgramName]
        if extraArgs:
            argv.extend(extraArgs)
        runnerInstance = self.__runner(
            testLoader=self.__loader, argv=argv, module=module, exit=False)
        return runnerInstance.result.wasSuccessful()


class _ValidatorTestLoader(unittest.loader.TestLoader):
    """
    Custom test case loader that injects test harness fixtures into
    test cases for use in querying and assertions.

    @private
    """
    def __init__(self, session):
        """
        Initializes an instance of this class.

        @param session hostAPI.Session.Session Test harness OpenAssetIO
        @ref session
        """
        self.__session = session
        self.__fixtures = {}
        super(_ValidatorTestLoader, self).__init__()

    def loadTestsFromTestCase(self, testCaseClass):
        """
        Override of base class to additionally inject fixtures and
        OpenAssetIO @ref session into test cases.

        Injects the child dict of the `fixtures` dict that corresponds
        to the test case class and method. If no such dict is available
        then the injected fixtures for the test case will be `None`.

        @param testCaseClass FixtureAugmentedTestCase Test case class
        that supports injection of fixtures.

        @return `unittest.suite.TestSuite` The unittest suite to
        execute.
        """
        testCaseNames = self.getTestCaseNames(testCaseClass)
        cases = []
        for testCaseName in testCaseNames:

            locale = ManagerTestHarnessLocale()
            locale.testCase = f"{testCaseClass.__name__}.{testCaseName}"

            cases.append(testCaseClass(
                self.__fixtures.get(testCaseClass.__name__, {}).get(testCaseName),
                self.__session, locale, testCaseName
            ))

        return self.suiteClass(cases)

    def setFixtures(self, fixtures):
        """
        Sets the fixtures that will be used for test cases loaded by the class.

        @param fixtures `Dict[Any, Any]` Dictionary of test case fixtures.

        """
        self.__fixtures = fixtures


class _ValidatorHarnessHostInterface(hostAPI.HostInterface):
    """
    Minimal required OpenAssetIO hostAPI.HostInterface.HostInterface
    implementation.

    @private
    """
    def identifier(self):
        return "org.openassetio.test.manager.harness"

    def displayName(self):
        return "OpenAssetIO Manager Test Harness"
