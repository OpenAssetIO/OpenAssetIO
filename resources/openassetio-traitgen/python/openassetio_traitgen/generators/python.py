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
A traitgen generator that outputs a python package based on the
openassetio_traitgen PackageDefinition model.
"""

import keyword
import logging
import os
import re

from typing import List, NamedTuple

import jinja2

from . import helpers
from ..datamodel import PackageDeclaration, PropertyType

__all__ = ["generate"]


#
## Code Generation
#


# pylint: disable=too-many-locals
def generate(
    package_declaration: PackageDeclaration,
    globals_: dict,
    output_directory: str,
    creation_callback,
    logger: logging.Logger,
):
    """
    Generates a python package for the supplied definition under outputDirPath.
    """

    env = _create_jinja_env(globals_, logger)

    def render_template(name: str, path: str, variables: dict):
        """
        A convenience to render a named template into its corresponding
        file and call the creationCallback.
        """
        # NB: Jinja assumes '/' on all plaftorms:
        #  https://github.com/pallets/jinja/blob/7fb13bf94443f067c74204a1aee368fdf0591764/src/jinja2/loaders.py#L29
        template = env.get_template(f"python/{name}.py.in")
        with open(path, "w", encoding="utf-8") as file:
            file.write(template.render(variables))
        creation_callback(path)

    def create_dir_with_path_components(*args) -> str:
        """
        A convenience to create a directory from the supplied path
        components, calling the creationCallback and returning its path
        as a string.
        """
        path = os.path.join(*args)
        os.makedirs(path, exist_ok=True)
        creation_callback(path)
        return path

    # Top level package directory, under a "python" subdirectory
    package_name = env.filters["to_py_module_name"](package_declaration.id)
    package_dir_path = create_dir_with_path_components(output_directory, "python", package_name)

    # Collect which sub-packages we should import at the top level, so
    # they're available without a 'from x import y' statement.
    package_init_imports = []

    # Sub-packages for traits and specifications
    for kind in ("traits", "specifications"):

        namespaces = getattr(package_declaration, kind, None)
        if namespaces:

            package_init_imports.append(kind)

            # Create the directory for the sub-package
            subpackage_dir_path = create_dir_with_path_components(package_dir_path, kind)

            # Collect the resulting module names for each namespace
            # So we can pre-import them in the sub-package init.
            subpackage_init_imports = []

            # Generate a single-file module for each namespace
            for namespace in namespaces:
                safe_namespace = env.filters["to_py_module_name"](namespace.id)
                subpackage_init_imports.append(safe_namespace)
                render_template(
                    kind,
                    os.path.join(subpackage_dir_path, f"{safe_namespace}.py"),
                    {
                        "package": package_declaration,
                        "namespace": namespace,
                        "imports": helpers.package_dependencies(namespace.members),
                    },
                )

            # Generate the sub-package __init__.py that pre-imports all
            # of the sub-modules.
            subpackage_init_imports.sort()
            docstring = f"{kind.capitalize()} defined in the '{package_declaration.id}' package."
            render_template(
                "__init__",
                os.path.join(subpackage_dir_path, "__init__.py"),
                {"docstring": docstring, "relImports": subpackage_init_imports},
            )

    # Package __init__.py
    render_template(
        "__init__",
        os.path.join(package_dir_path, "__init__.py"),
        {"docstring": package_declaration.description, "relImports": package_init_imports},
    )


#
## Jinja setup
#


def _create_jinja_env(env_globals, logger):
    """
    Creates a custom Jinja2 environment with:
     - A package a loader that automatically finds templates within a
       'templates' directory in the openassetio_traitgen python package.
     - Updated globals.
     - Custom filters.
    """
    env = jinja2.Environment(loader=jinja2.PackageLoader("openassetio_traitgen"))
    env.globals.update(env_globals)
    _install_custom_filters(env, logger)
    return env


# Custom filters


def _install_custom_filters(environment, logger):
    """
    Installs custom filters in to the Jinja template environment that allow
    data from the model to be conformed to python-specific standards.

    The toPy* methods will log a warning if the string is changed from
    the input during this process. An error will be raised if this
    resulted in an empty string.
    """

    def validate_identifier(string: str, original: str):
        """
        Validates some string is a legal python variable name.
        """
        if not string.isidentifier():
            raise ValueError(f"{string}' (from '{original}' is not a valid python identifier.")
        if keyword.iskeyword(string):
            raise ValueError(f"{string}' (from '{original}' is a reserved python keyword.")

    def to_py_module_name(string: str):
        """
        Conforms the supplied string a legal module name.
        """
        # Don't warn for - to _ as it is expected that setuptools
        # creates a safe name from the package name anyway.
        # eg: openassetio-traitgen -> openassetio_traitgen
        no_hypens = string.replace("-", "_")
        module_name = re.sub(r"[^a-zA-Z0-9_]", "_", no_hypens)
        if module_name != no_hypens:
            logger.warning(f"Conforming '{string}' to '{module_name}' for module name")
        return module_name

    def to_py_class_name(string: str):
        """
        Conforms the supplied string a legal python class name.
        """
        class_name = helpers.to_upper_camel_alnum(string)
        if class_name != string:
            logger.warning(f"Conforming '{string}' to '{class_name}' for class name")
        validate_identifier(class_name, string)
        return class_name

    def to_py_trait_accessor_name(name_parts: List[str]):
        """
        Conforms the supplied trait name to a legal function name
        beginning with a lowercase letter.
        """
        capitalized_parts = [helpers.to_upper_camel_alnum(part) for part in name_parts]
        unique_name = "".join(capitalized_parts)
        accessor_name = helpers.to_lower_camel_alnum(unique_name)
        # We expect the first letter to change to lowercase
        if accessor_name != f"{unique_name[0].lower()}{unique_name[1:]}":
            logger.warning(
                f"Conforming '{unique_name}' to '{accessor_name}' for trait getter name"
            )
        validate_identifier(accessor_name, unique_name)
        return accessor_name

    def to_py_var_accessor_name(string: str):
        """
        Conforms the supplied string a legal function name, but
        beginning with an uppercase letter so it can be prefixed with
        get or set.
        """
        accessor_name = helpers.to_upper_camel_alnum(string)
        if accessor_name != f"{string[0].upper()}{string[1:]}":
            logger.warning(
                f"Conforming '{string}' to '{accessor_name}' for property accessor name"
            )
        validate_identifier(accessor_name, string)
        return accessor_name

    def to_py_var_name(string: str):
        """
        Conforms the supplied string to a valid python var name,
        starting with a lowercase letter.
        """
        var_name = helpers.to_lower_camel_alnum(string)
        if var_name != string:
            logger.warning(f"Conforming '{string}' to '{var_name}' for variable name")
        validate_identifier(var_name, string)
        return var_name

    type_map = {
        PropertyType.STRING: "str",
        PropertyType.INTEGER: "int",
        PropertyType.FLOAT: "float",
        PropertyType.BOOL: "bool",
        PropertyType.DICT: "dict",  # This must be InfoDictionary, but this isn't bound
    }

    def to_py_type(declaration_type):
        """
        Returns the python value type for a property declaration (PropertyType).
        """
        return type_map[declaration_type]

    environment.filters["to_upper_camel_alnum"] = helpers.to_upper_camel_alnum
    environment.filters["to_py_module_name"] = to_py_module_name
    environment.filters["to_py_class_name"] = to_py_class_name
    environment.filters["to_py_trait_accessor_name"] = to_py_trait_accessor_name
    environment.filters["to_py_var_accessor_name"] = to_py_var_accessor_name
    environment.filters["to_py_var_name"] = to_py_var_name
    environment.filters["to_py_type"] = to_py_type
