#
#   Copyright 2022 The Foundry Visionmongers Ltd
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
Entry point for command-line execution of the specification/trait
code generation tool.

The CLI is a thin wrapper around the `generate` entrypoint in the main
`openassetio_traitgen` module. See `openassetio-traitgen --help` for
more details on its use.
"""

# pylint: disable=invalid-name

import argparse
import inspect
import sys
import logging

from . import generate
from . import generators

#
# Defaults
#

# Default log level for message logging
DEFAULT_LOG_LEVEL = logging.getLevelName(logging.WARNING)


#
## Helpers
#


def _create_argparser():
    """
    Returns an argparse parser configured with the openassetio-traitgen
    flags and options.
    """

    cmdline = argparse.ArgumentParser(
        prog="openassetio-traitgen",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=inspect.cleandoc(
            """
            The openassetio-traitgen utility generates code that provides
            strongly-typed views on an openassetio traits data instance. The
            tool is capable of generating code in a number of languages from the
            supplied file, containing the simplified declaration of one or more
            traits or specifications using the OpenAssetIO traits and
            specification declaration schema.

            By default, code is generated for all supported unless one or more
            language flags are specified.
            """
        ),
    )

    cmdline.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Load and verify the supplied declarations without generating any code",
    )

    cmdline.add_argument("input", help="YAML file detailing traits and specifications to generate")

    cmdline.add_argument(
        "-o",
        "--output-dir",
        required=True,
        help="Generate code under the supplied directory, the utility will attempt to create this"
        " directory if it does not exist",
    )

    cmdline.add_argument(
        "--copyright-owner",
        type=str,
        help="The owner of the generated code, if set, a copyright and SPDX License Identifier will be added.",
    )

    cmdline.add_argument(
        "--copyright-date",
        type=str,
        help="The copyright date (range) of the generated code (defaults to the current year).",
    )

    cmdline.add_argument(
        "--spdx-license-identifier",
        type=str,
        help="The SPDX license identifier the generated code is released under (https://spdx.org/licenses).",
    )

    cmdline.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Prints the path to each file and directory generated to stdout.",
    )

    cmdline.add_argument(
        "-l",
        "--log-level",
        type=str,
        choices=("ERROR", "WARNING", "INFO", "DEBUG"),
        default=DEFAULT_LOG_LEVEL,
        help="Sets the logging level for diagnostic messages printed to stderr.",
    )

    cmdline.add_argument(
        "--python",
        dest="languages",
        action="append_const",
        const="python",
        help="Generate Python classes",
    )

    return cmdline


def _createStderrLogger():
    """
    Returns a logger that sends messages to stderr prefixed with
    module/severity.
    """
    formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(formatter)
    logger = logging.getLogger("openassetio-traitgen")
    logger.addHandler(handler)
    return logger


#
## Main
#


def main():
    """
    Runs code generation based on the arguments passed on the command
    line.
    """
    cmdline = _create_argparser()
    args = cmdline.parse_args()

    # Log messages are sent to std::err, std::out is reserved for newly
    # created files/folders, so they can be piped to other commands.
    logger = _createStderrLogger()
    logger.setLevel(args.log_level)

    templateGlobals = {}
    if args.copyright_owner:
        templateGlobals["copyrightOwner"] = args.copyright_owner
    if args.copyright_date:
        templateGlobals["copyrightDate"] = args.copyright_date
    if args.spdx_license_identifier:
        templateGlobals["spdxLicenseIdentifier"] = args.spdx_license_identifier

    # If -v is set, we output all files/folders created to std::out
    # to aid managing traitgen files in subsequent build steps.
    def creation_callback(path):
        if args.verbose:
            sys.stdout.write(f"{path}\n")

    generate(
        args.input,
        args.output_dir,
        args.languages or generators.ALL,
        creation_callback,
        logger,
        args.dry_run,
        templateGlobals,
    )


if __name__ == "__main__":
    main()
