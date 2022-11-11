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
Entry point for command-line execution of the manager plugin test
harness.
"""

# pylint: disable=invalid-name

import argparse
import inspect
import sys

from openassetio.test.manager import harness, apiComplianceSuite


cmdline = argparse.ArgumentParser(
    prog="openassetio.test.manager",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=inspect.cleandoc(
        """
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
                    "settings": { <manager_setting>: <value> },
                    "shared": { "<fixture_name>": <value> }
                    "<Test_ClassName>" : {
                        "shared": { "<fixture_name>": <value> }
                        "<test_method_name>" : {
                            "<fixture_name>" : <value>,
                            ...
                        },
                        ...
                    },
                    ...
                }

                Test classes, method, and fixture names are available in
                openassetio.test.manager.apiComplianceSuite.

                NOTE: Fixture names should only contain alpha-numeric characters
                and underscores.
                """
    ),
)

cmdline.add_argument(
    "-f", "--fixtures", metavar="FILE", required=True, help="Path to Python fixtures file"
)

# The following "argument" is just a dummy for the help text. If
# additional arguments are provided, `args.extraArgs` will be
# `True`, yet those arguments will still go in the
# "unrecognized" list (i.e. `extraArgs`).
cmdline.add_argument("extraArgs", action="store_true", help="Arguments to pass to the test runner")

#
# Main
#

args, extraArgs = cmdline.parse_known_args(sys.argv[1:])

fixtures = harness.fixturesFromPyFile(args.fixtures)
isSuccessful = harness.executeSuite(apiComplianceSuite, fixtures, extraArgs)

sys.exit(int(not isSuccessful))
