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
@namespace openassetio_traitgen.generators
Language generators for the openassetio-traitgen tool.

Each language generator is responsible for producing language-idiomatic
code from the supplied PackageDeclaration, based on the OpenAssetIO
style guide.

It should be noted that though the front-end input validation (through
schema.json) constrains the character set of the declaration, this should
never be assumed. It may be relaxed at a future point, and there is no
guarantee that all fields will be legal identifiers in any given target
language.

As such, every generator should conform and validate all input data from
the declaration, assuming any free-form fields to be UTF-8 strings.

The `helpers` module provides utilities to convert names to common
restricted character set scenarios, based on the project style guide.

Each generator should expose itself as an attribute in this module whose
name matches the string passed to the `languages` argument of
`openassetio_traitgen.generate`.

Each generator has a single entry point as shown below:

    def generate(
        package_declaration: datamodel.PackageDeclaration,
        globals_: dict,
        output_directory: str,
        creation_callback,
        logger: logging.Logger,
    ):
        ...

  - package_declaration: The package declaration to generate
  - globals_: Template globals, see: helpers.default_template_globals
  - output_directory: The root directory to generate code under. Each
      generator should create appropriate sub-directories under this
      root as required by the language.
  - creation_callback: A callback that must be called with the path to
      every file and directory created during generation (even if it
      already exists).
  - logger: A logger to use for any user-facing messaging or
      diagnostic reporting.
"""
from . import helpers
from . import python

# All known language generators
ALL = ("python",)
