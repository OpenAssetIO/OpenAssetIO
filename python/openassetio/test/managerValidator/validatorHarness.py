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
Boilerplate classes for initialisation and execution of test cases.
"""
import unittest

from openassetio import hostAPI, pluginSystem, logging, managerAPI


__all__ = [
    "ValidatorHarnessFactory", "ValidatorHarness", "ValidatorTestLoader",
    "ValidatorHarnessHostInterface", "FixtureAugmentedTestCase"]


class ValidatorHarnessFactory:
    """
    Factory encapsulating the construction of dependencies required to
    run the manager validator test harness.
    """

    @staticmethod
    def createHarness(runner, loader):
        """
        Create the test harness used begin test case execution.

        @param runner `unittest.main` A unittest-compatible test runner.

        @param loader ValidatorTestLoader A unittest-compatible test
        case loader that injects test fixtures into test case instances.

        @return ValidatorHarness Test harness.
        """
        return ValidatorHarness(runner, loader)

    @staticmethod
    def createLoader(fixtures, session):
        """
        Create the test case loader that injects fixtures into test case
        instances as they are discovered and instantiated.

        @param fixtures `Dict[Any, Any]` Dictionary of test case
        fixtures.

        @param session hostAPI.Session.Session The OAIO session to
        inject into test cases.

        @return ValidatorTestLoader Test case loader.
        """
        return ValidatorTestLoader(fixtures, session)

    @staticmethod
    def createHostInterface():
        """
        Create the hostAPI.HostInterface.HostInterface to be used by the
        test harness @ref session.

        @return ValidatorHarnessHostInterface The
        hostAPI.HostInterface.HostInterface implementation used by the
        test harness.
        """
        return ValidatorHarnessHostInterface()

    @staticmethod
    def createSessionWithManager(identifier, hostInterface, logger, managerFactory):
        """
        Create a hostAPI.Session.Session instance and load the given
        manager plugin into it via the given `identifier`.

        @param identifier `str` Identifier of the manager plugin to
        load.

        @param hostInterface hostAPI.HostInterface.HostInterface The
        `HostInterface` implementation used by the test harness session.

        @param logger logging.LoggerInterface Logger to be used by the
        test harness session.

        @param managerFactory
        hostAPI.ManagerFactoryInterface.ManagerFactoryInterface
        Manager factory to be used by the test harness session.

        @return hostAPI.Session.Session Test harness session.
        """
        session = hostAPI.Session(hostInterface, logger, managerFactory)
        session.useManager(identifier)
        return session

    @staticmethod
    def createManagerFactory(logger):
        """
        Create the @ref manager factory to be used by the test harness
        session.

        @param logger logging.LoggerInterface Logger to be used by the
        manager factory.
        """
        return pluginSystem.PluginSystemManagerFactory(logger)

    @staticmethod
    def createLogger():
        """
        Create the logger to be used by the test harness OAIO @ref
        session.

        @return logging.SeverityFilter A logging.ConsoleLogger wrapped
        in a `SeverityFilter`.
        """
        return logging.SeverityFilter(logging.ConsoleLogger())


class ValidatorHarness:
    """
    Facade wrapping the unittest runner.

    Injects a custom testcase loader and acts as an anti-corruption
    layer around a unittest-compatible test runner.
    """
    # pylint: disable=too-few-public-methods

    _kValidatorHarnessProgramName = "managerValidator"

    def __init__(self, runner, loader):
        """
        Initializes an instance of this class.

        @param runner `unittest.main` A unittest-compatible test runner.

        @param loader ValidatorTestLoader A unittest-compatible test
        case loader that injects test fixtures into test case instances.
        """
        self.__runner = runner
        self.__loader = loader

    def executeTests(self, extraArgs, module):
        """
        Run the tests harness test cases in the provided `module`,
        passing any `extraArgs` to the test runner.

        @param extraArgs `List[str]` Arguments to pass to the unittest
        runner.

        @param module `types.ModuleType` Python module containing the
        test cases to execute.

        @return `bool` `True` if all tests succeeded, `False` otherwise.
        """
        # Prepend the "program name" to simulate full argv for unittest.
        argv = [self._kValidatorHarnessProgramName] + extraArgs
        runnerInstance = self.__runner(
            testLoader=self.__loader, argv=argv, module=module, exit=False)
        return runnerInstance.result.wasSuccessful()


class ValidatorTestLoader(unittest.loader.TestLoader):
    """
    Custom test case loader that injects test harness fixtures into
    test cases for use in querying and assertions.
    """
    def __init__(self, fixtures, session):
        """
        Initializes an instance of this class.

        @param fixtures `Dict[Any, Any]` Dictionary of test case
        fixtures.

        @param session hostAPI.Session.Session Test harness OAIO @ref
        session
        """
        self.__fixtures = fixtures
        self.__session = session
        super(ValidatorTestLoader, self).__init__()

    def loadTestsFromTestCase(self, testCaseClass):
        """
        Override of base class to additionally inject fixtures and OAIO
        @ref session into test cases.

        Injects the child dict of the `fixtures` dict that corresponds
        to the test case class and method. If no such dict is available
        then the injected fixtures for the test case will be `None`.

        @param testCaseClass FixtureAugmentedTestCase Test case class
        that supports injection of fixtures.

        @return `unittest.suite.TestSuite` The unittest suite to
        execute.
        """
        testCaseNames = self.getTestCaseNames(testCaseClass)
        loadedSuite = self.suiteClass(
            testCaseClass(
                self.__fixtures.get(testCaseClass.__name__, {}).get(testCaseName),
                self.__session, testCaseName
            )
            for testCaseName in testCaseNames)
        return loadedSuite


class ValidatorHarnessHostInterface(hostAPI.HostInterface):
    """
    Minimal required OAIO hostAPI.HostInterface.HostInterface
    implementation.
    """
    def identifier(self):
        return "org.openassetio.test.managerValidator"

    def displayName(self):
        return "OAIO Manager Validator"


class FixtureAugmentedTestCase(unittest.TestCase):
    """
    Base test case class that all test classes must inherit from.

    Expects test harness fixtures and an OAIO session to be provided,
    hence requires that `unittest` is provided with the custom
    ValidatorTestLoader test case loader.

    Fixtures, session and manager interface are then provided to
    subclasses via protected members.
    """
    def __init__(self, fixtures, session, *args, **kwargs):
        """
        Initializes an instance of this class.

        Makes available `_fixtures`, `_session` and `_manager` to
        subclasses.

        @param fixtures `Dict[Any, Any]` Dictionary of fixtures specific
        to the current test case.

        @param session hostAPI.Session.Session The OAIO @ref session
        to be used by test cases.

        @param args `List[Any]` Additional args passed along to the
        base class.

        @param kwargs: `Dict[str, Any]` Additional keyword args passed
        along to the base class.
        """
        self._fixtures = fixtures  # type: dict
        self._session = session  # type: hostAPI.Session
        self._manager = session.currentManager()  # type: managerAPI.ManagerInterface
        super(FixtureAugmentedTestCase, self).__init__(*args, **kwargs)

    def assertIsStringKeyPrimitiveValueDict(self, dictionary):
        """
        Assert that given `dictionary` is `str`-keyed with all primitive
        values.

        @param dictionary `Dict[Any, Any]` Dictionary to check.

        @exception `AssertionError` On failure.
        """
        self.assertIsInstance(dictionary, dict)

        for key, value in dictionary.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, (str, int, float, bool))
