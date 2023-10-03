#
#   Copyright 2013-2022 The Foundry Visionmongers Ltd
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
@namespace openassetio.test.manager.harness
A `unittest` based test harness that allows @ref manager plugin
developers to check that their implementation meets the requirements of
the API.

The harness can be invoked programatically or via tha CLI. The module
exposes the main test entry point and fixture loading methods. This
permits additional test suites to be written and run by the developer,
to test manager-specific functionality if desired.
"""

import importlib
import os
import sys
import unittest

from . import _implementation
from ...errors import ConfigurationException, InputValidationException


__all__ = ["executeSuite", "fixturesFromPyFile", "moduleFromFile", "FixtureAugmentedTestCase"]


def executeSuite(testSuiteModule, fixtures, unittestExtraArgs=None):
    """
    Executes the supplied test suite with the given fixtures, optionally
    passing extra arguments to the underlying unittest framework.

    @param testSuiteModule `module` A module of test cases deriving from
    `FixtureAugmentedTestCase`.

    @param fixtures `dict` The fixtures corresponding to the supplied
    testSuiteModule.

    @param unittestExtraArgs `List[str]` Additional args to pass to the
    `unittest` framework, see `unittest.main` `argv` for more details.

    @return `bool` True if the suite passed, False if there was one or
    more failures.

    The format of the fixtures dictionary is as follows:

    @code{.py}
    fixtures = {
        "identifier": <target manager plugin identifier>,
        "settings": { <manager_setting>: <value> },
        "shared": { "<fixture_name>": <value> },
        "<Test_Case_name>": {
            "shared": { "<fixture_name>": <value> },
            "<Test_function_name>": {
                "<fixture_name>": <value>,
                ...
            },
            ...
        },
        ...
    }
    @endcode

    Where:
     - `Test_Case_name`: The name of a test `class` declaration within
       the supplied suite that derives from @ref
       FixtureAugmentedTestCase.
     - `Test_function_name`: The the name of a test function defined
       within the named class.
     - `fixture_name`: The name of a fixture queried by the test
       function. This may be an input value, or an expected result.
     - `shared`: Fixtures values that will be inherited to inner
       classes or functions.

    The test harness takes care of extracting the appropriate function
    sub-dictionary and making it available through `self._fixtures`.

    NOTE: Fixture names need to be valid python variable names, and
    should only contain alpha-numeric characters and underscores.
    """

    managerIdentifier = fixtures["identifier"]
    settings = fixtures.get("settings")
    harness = _implementation.createHarness(managerIdentifier, settings)
    return harness.executeTests(unittestExtraArgs, testSuiteModule, fixtures)


def fixturesFromPyFile(path):
    """
    Loads a fixtures dict from the specified python file.

    The supplied path should point to a python file defining a top-level
    `fixtures` variable holding a `dict`, populated with the required
    fixtures for the target test suite.

    @param path `str` The path to the file to load fixtures from.

    @return `dict` The fixtures dict defined by the supplied file.

    @see executeSuite for details on the structure of the fixtures
    dictionary.

    @see The <a href="https://github.com/OpenAssetIO/Template-OpenAssetIO-Manager-Python"
    target="_blank">manager template</a> for a reference fixtures file.
    """
    module = moduleFromFile(path)
    if not hasattr(module, "fixtures"):
        raise ConfigurationException(f"Missing top-level 'fixtures' variable in '{path}'")

    return module.fixtures


def moduleFromFile(path):
    """
    Loads a python module from the specified file, without it needing
    to be on PYTHONPATH.

    The file name is used as the module name. This can be useful to load
    test suites from files that are not otherwise on PYTHONPATH.

    @param path `str` The path to the file to load the module from.

    @return The loaded module.
    """
    moduleName = os.path.basename(path)
    spec = importlib.util.spec_from_file_location(moduleName, path)
    if not spec:
        # Standard stack-trace is unhelpful as it just says:
        #    'NoneType' has no attribute 'loader'
        raise InputValidationException(f"Unable to parse '{path}'")

    module = importlib.util.module_from_spec(spec)
    # Without this, for package imports we get:
    #   'No module named '<moduleName>'
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FixtureAugmentedTestCase(unittest.TestCase):
    """
    Base test case class that all test classes must inherit from.

    Expects test harness fixtures and an OpenAssetIO @ref manager to be
    provided, hence requires that `unittest` is provided with the custom
    ValidatorTestLoader test case loader.

    Fixtures, manager and a suitable locale are then provided to
    subclasses via protected members.

    @warning The supplied locale should always be used for interactions
    with the manager under test, the @ref createTestContext convenience
    method will create a new context pre-configured with this locale.

    For performance reasons, by default, all test cases will share a
    single instance of the manager under test. This reduces setup costs,
    but precludes any testing of initialization behaviour.

    If the class variable `shareManager` is set to False for any given
    suite, the harness will instead create a new, uninitializesd manager
    for each case.
    """

    shareManager = True

    def __init__(self, fixtures, manager, locale, *args, **kwargs):
        """
        Initializes an instance of this class.

        Makes available `_fixtures` and `_manager` to
        subclasses.

        @param fixtures `Dict[Any, Any]` Dictionary of fixtures specific
        to the current test case.

        @param manager hostApi.Manager.Manager The OpenAssetIO
        @ref manager to be used by test cases.

        @param locale @fqref{trait.TraitsData} "TraitsData" The @ref
        locale to use by test cases.

        @param args `List[Any]` Additional args passed along to the
        base class.

        @param kwargs: `Dict[str, Any]` Additional keyword args passed
        along to the base class.
        """
        self._fixtures = fixtures  # type: dict
        self._manager = manager  # type: hostApi.Manager
        self._locale = locale  # type: openassetio.Specification

        super(FixtureAugmentedTestCase, self).__init__(*args, **kwargs)

        # Flush caches after every test, even if there was an error
        # during setUp.
        self.addCleanup(self._manager.flushCaches)

    def createTestContext(self):
        """
        A convenience method to create a context with the
        test locale, as provided by the test harness mechanism.
        """
        context = self._manager.createContext()
        context.locale = self._locale
        return context

    def assertIsStringKeyPrimitiveValueDict(self, dictionary):
        """
        Assert that given `dictionary` is `str`-keyed with all primitive
        values.

        @param dictionary `Dict[Any, Any]` Dictionary to check.

        @exception AssertionError On failure.
        """
        self.assertIsInstance(dictionary, dict)

        for key, value in dictionary.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, (str, int, float, bool))

    def assertValuesOfType(self, valueList, valueType, allowNone=False):
        """
        Asset that all values in the supplied list are of the desired
        type, or optionally None. An empty list will not fail the check.

        @param valueList `List[Any]` The list of values to check.
        @param valueType `Type` The expected value type, as compatible
          with `isinstance`.
        @param allowNone `bool` When True, one or more elements of the
          list may also be `None`.

        @exception AssertionError if any of the supplied values are not
          of the excpected type.
        """
        for value in valueList:
            if value is None and allowNone:
                continue
            self.assertIsInstance(value, valueType)

    def requireEntityReferencesFixture(self, fixtureName, skipTestIfMissing=False):
        """
        A convenience companion to requireFixture, to construct an
        entity reference object around each raw string in a list
        fixture.
        """
        return [
            self._manager.createEntityReference(r)
            for r in self.requireFixture(
                fixtureName,
                skipTestIfMissing,
            )
        ]

    def requireEntityReferenceFixture(self, fixtureName, skipTestIfMissing=False):
        """
        A convenience companion to requireFixture, to construct an
        entity reference object around a raw string fixture.
        """
        return self._manager.createEntityReference(
            self.requireFixture(
                fixtureName,
                skipTestIfMissing,
            )
        )

    def requireFixtures(self, fixtureNames, skipTestIfMissing=False):
        """
        Ensures that the supplied fixtures names are available for a
        test and returns their values.

        If any of the named fixtures are missing, the test will be
        failed or skipped accordingly and test execution aborted. A
        suitable message is generated by the function to inform
        observers of the test run as to which fixtures are missing.

        @param fixtureNames `List[str]` The required keys in
        self._fixtures.

        @param skipTestIfMissing `bool` When True, the test will
        be skipped instead of failing if one or more of the specificed
        fixtures are missing.

        @return `List[Any]` The values corresponding to each requested
        fixtures
        """
        # Pre-check all names to give a more informative message.
        missing = [name for name in fixtureNames if name not in self._fixtures]
        if missing:
            message = f"Required fixtures not found: {', '.join(missing)}"
            action = self.skipTest if skipTestIfMissing else self.fail
            action(message)
            # We should never get here as action should raise an
            # exception either way to abort/fail the test
            assert False
        else:
            return [self._fixtures[name] for name in fixtureNames]

    def collectRequiredFixtures(self, fixtureNames, skipTestIfMissing=False):
        """
        Performs the same checks as requireFixtures, but stores the
        fixture values on self under variables of the same name.

        This method is best suited to use in setUp where you wish
        to skip/fail a whole bunch of tests when fixtures are missing.
        """
        values = self.requireFixtures(fixtureNames, skipTestIfMissing)
        for name, value in zip(fixtureNames, values):
            setattr(self, name, value)

    def requireFixture(self, fixtureName, skipTestIfMissing=False):
        """
        A convenience companion to requireFixtures, when only a single
        fixture is needed.
        """
        return self.requireFixtures(
            [
                fixtureName,
            ],
            skipTestIfMissing,
        )[0]

    def collectRequiredFixture(self, fixtureName, skipTestIfMissing=False):
        """
        A convenience companion to collectRequiredFixtures, when only a
        single fixture is needed.
        """
        self.collectRequiredFixtures(
            [
                fixtureName,
            ],
            skipTestIfMissing,
        )
