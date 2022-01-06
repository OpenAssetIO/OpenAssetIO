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
Utilities for executing the manager test harness from the command line.
"""
import argparse
import collections
import importlib.util
import inspect
import unittest

from . import validatorHarness


__all__ = ["execute", "Parser", "ParsedArgs", "PyFixtureLoader"]


def execute(argv, testModule, parser=None, harnessFactory=None):
    """
    Command-line execution of the manager test harness.

    @param argv `List[str]` Command-line arguments as per `sys.argv`,
    including the executable name.  See @ref Parser for details of usage
    and supported arguments.

    @param testModule `types.ModuleType` Python module containing the
    test harness test case suite.

    @param parser Parser Utility to parse the command-line arguments
    and load fixtures. If `None` then the default parser will be used.

    @param harnessFactory validatorHarness.ValidatorHarnessFactory
    Factory for constructing dependencies required for execution of
    the test cases. If `None` then the default factory will be used.

    @return `bool` `True` if tests executed with no failures, `False`
    otherwise.
    """
    if parser is None:
        parser = Parser(PyFixtureLoader())
    if harnessFactory is None:
        harnessFactory = validatorHarness.ValidatorHarnessFactory()

    parsedArgs = parser.parse(argv)
    logger = harnessFactory.createLogger()
    hostInterface = harnessFactory.createHostInterface()
    managerFactory = harnessFactory.createManagerFactory(logger)
    session = harnessFactory.createSessionWithManager(
        parsedArgs.fixtures["identifier"], hostInterface, logger, managerFactory)
    unittestLoader = harnessFactory.createLoader(parsedArgs.fixtures, session)
    harness = harnessFactory.createHarness(unittest.main, unittestLoader)
    return harness.executeTests(parsedArgs.extraArgs, testModule)


ParsedArgs = collections.namedtuple("ParsedArgs", ("fixtures", "extraArgs"))


class Parser:
    """
    Parser for command-line arguments.

    Wraps `argparse` to parse command-line invocation flags and load the
    provided fixtures file.
    """
    # TODO(DF): @pylint-disable Should we update pylint rules to allow
    #  classes with a single public method?
    # pylint: disable=too-few-public-methods

    def __init__(self, fixtureLoader):
        """
        Initialises an instance of this class.

        @param fixtureLoader PyFixtureLoader Utility for loading
        the test case fixture dict.
        """
        self.__fixtureLoader = fixtureLoader

    def parse(self, argv):
        """
        Process the given command-line arguments and load fixtures.

        Uses `argparse` to present a nice command-line interface,
        including help text.

        @param argv Arguments passed on the command-line, as in
        `sys.argv`.

        @return ParsedArgs A `namedtuple` wrapping the result of parsing
        the command-line arguments.
        """
        cmdline = argparse.ArgumentParser(
            prog="managerValidator", formatter_class=argparse.RawDescriptionHelpFormatter,
            description=inspect.cleandoc("""
                The OpenAssetIO Manager test harness - A tool to validate a given 
                manager correctly implements the API interface.

                When executed with a manager-supplied fixtures file, the harness will
                load the specified manager plugin from OPENASSETIO_PLUGIN_PATH and 
                run a series of tests that validate:

                - Input handling
                - Return types and values

                Because OpenAssetIO places no constraints on the nature of an entity
                reference, it is necessary for any given manager to provide the test
                suite with valid input data that can be used to test entity related
                methods. In addition, as the result of many methods is also specific to
                the manager, in many cases, the test suite requires expected output to
                be specified too.

                This data is provided via a fixtures file. This is a python script that
                defines a top-level 'fixtures' variable containing this data. This
                variable should be a dict with the following structure:

                fixtures = {
                    "identifier" : "<identifier of target plugin>",
                    "<Test_ClassName>" : {
                        "<test_case_name>" : {
                            "<fixture_name>" : <value>,
                            ...
                        },
                        ...
                    },
                    ...
                }

                Test classes, case names, and fixture names are available in
                openassetio.test.managerValidator.validatorSuite.
                 """))
        cmdline.add_argument(
            "-f", "--fixtures", metavar="FILE", required=True, help="Path to Python fixtures file")
        # The following "argument" is just a dummy for the help text. If
        # additional arguments are provided, `args.extraArgs` will be
        # `True`, yet those arguments will still go in the
        # "unrecognized" list (i.e. `extraArgs`).
        cmdline.add_argument(
            "extraArgs", action="store_true", help="Arguments to pass to the test runner")

        args, extraArgs = cmdline.parse_known_args(argv[1:])

        return ParsedArgs(
            fixtures=self.__fixtureLoader.load(args.fixtures),
            extraArgs=extraArgs)


class PyFixtureLoader:
    """
    Utility that loads a Python module and extracts the `fixtures`
    top-level variable within.
    """
    # TODO(DF): @pylint-disable
    # pylint: disable=too-few-public-methods

    @staticmethod
    def load(filePath):
        """
        Execute the given Python file and extract its `fixtures`
        top-level variable.

        See `resources/examples/SampleAssetManager/test/fixtures.py` for
        a reference fixtures file.

        @param filePath `str` Python file to load.

        @return `dict` Dictionary of test case fixtures.
        """
        spec = importlib.util.spec_from_file_location("TestFixtures", filePath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.fixtures
