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
import unittest

from . import _implementation


__all__ = ['executeSuite', 'fixturesFromPyFile', 'FixtureAugmentedTestCase']


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
        "<Test_Case_name>": {
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

    The test harness takes care of extracting the appropriate function
    sub-dictionary and making it available through `self._fixtures`.
    """

    managerIdentifier = fixtures["identifier"]
    harness = _implementation.createHarness(managerIdentifier)
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

    @see `resources/examples/SampleAssetManager/test/fixures.py` for a
      reference fixtures file.
    """
    spec = importlib.util.spec_from_file_location("TestFixtures", path)
    if not spec:
        # Standard stack-trace is unhelpful as it just says:
        #    'NoneType' has no attribute 'loader'
        raise RuntimeError(f"Unable to parse '{path}'")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "fixtures"):
        raise RuntimeError(
            f"Missing top-level 'fixtures' variable in '{path}'")

    return module.fixtures


class FixtureAugmentedTestCase(unittest.TestCase):
    """
    Base test case class that all test classes must inherit from.

    Expects test harness fixtures and an OpenAssetIO session to be
    provided, hence requires that `unittest` is provided with the custom
    ValidatorTestLoader test case loader.

    Fixtures, session and manager interface are then provided to
    subclasses via protected members.
    """

    def __init__(self, fixtures, session, locale, *args, **kwargs):
        """
        Initializes an instance of this class.

        Makes available `_fixtures`, `_session` and `_manager` to
        subclasses.

        @param fixtures `Dict[Any, Any]` Dictionary of fixtures specific
        to the current test case.

        @param session hostAPI.Session.Session The OpenAssetIO
        @ref session to be used by test cases.

        @param locale specifications.LocaleSpecification The @ref locale
        to use by test cases.

        @param args `List[Any]` Additional args passed along to the
        base class.

        @param kwargs: `Dict[str, Any]` Additional keyword args passed
        along to the base class.
        """
        self._fixtures = fixtures  # type: dict
        self._session = session  # type: hostAPI.Session
        self._locale = locale  # type: specifications.LocaleSpecification
        self._manager = session.currentManager()  # type: managerAPI.Manager
        super(FixtureAugmentedTestCase, self).__init__(*args, **kwargs)

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
