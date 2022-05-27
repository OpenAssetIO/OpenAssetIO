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
Shared fixtures for codegen tests
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring

import logging
import os
import yaml

import pytest

from openassetio_codegen import datamodel


@pytest.fixture(scope="package")
def resources_dir():
    """
    The path to the resources directory for this test suite
    """
    test_dir = os.path.dirname(__file__)
    return os.path.join(test_dir, "resources")


@pytest.fixture(scope="package")
def yaml_path_all(resources_dir):
    return os.path.join(resources_dir, "openassetio-codegen-test-all.yaml")


@pytest.fixture(scope="package")
def yaml_path_traits_only(resources_dir):
    return os.path.join(resources_dir, "openassetio-codegen-test-traits-only.yaml")


@pytest.fixture(scope="package")
def yaml_path_specifications_only(resources_dir):
    return os.path.join(resources_dir, "openassetio-codegen-test-specifications-only.yaml")


@pytest.fixture(scope="package")
def yaml_path_invalid(resources_dir):
    return os.path.join(resources_dir, "invalid.yaml")


@pytest.fixture(scope="package")
def yaml_path_invalid_values(resources_dir):
    return os.path.join(resources_dir, "invalid_values.yaml")


@pytest.fixture(scope="package")
def yaml_path_minimal(resources_dir):
    return os.path.join(resources_dir, "minimal.yaml")


@pytest.fixture(scope="package")
def description_all(yaml_path_all):
    with open(yaml_path_all, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="package")
def description_traits_only(yaml_path_traits_only):
    with open(yaml_path_traits_only, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="package")
def description_specifications_only(yaml_path_specifications_only):
    with open(yaml_path_specifications_only, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="package")
def description_invalid(yaml_path_invalid):
    with open(yaml_path_invalid, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="package")
def description_invalid_values(yaml_path_invalid_values):
    with open(yaml_path_invalid_values, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="package")
def description_minimal(yaml_path_minimal):
    with open(yaml_path_minimal, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="package")
def description_exotic_values():
    return {
        "package": "p📦p",
        "description": "p",
        "traits": {
            "t!n": {
                "description": "n",
                "members": {
                    "t&": {
                        "description": "t",
                        "properties": {
                            "p$": {
                                "type": "boolean",
                                "description": "p"
                            }
                        }
                    }
                }
            }

        },
        "specifications": {
            "s!n": {
                "description": "",
                "members": {
                    "s^": {
                        "description": "",
                        "traitSet": [
                            {
                                "package": "p📦p",
                                "namespace": "t!n",
                                "name": "t&"
                            }
                        ]
                    }
                }
            }
        }
    }


@pytest.fixture
def declaration_all():
    # By design the parser sorts all namespace, trait, specification lists, and
    # traitSets by id/name to ensure stable generation from dict/map centric
    # descriptions.
    return datamodel.PackageDeclaration(
        id="openassetio-codegen-test-all",
        description="Test classes to validate the integrity of the openassetio-codegen tool.",
        traits=[
            datamodel.NamespaceDeclaration(
                id="aNamespace",
                description="A Namespace",
                members=[
                    datamodel.TraitDeclaration(
                        id="openassetio-codegen-test-all:aNamespace.AllProperties",
                        name="AllProperties",
                        description="A trait with properties of all types.",
                        usage=[],
                        properties=[
                            datamodel.PropertyDeclaration(
                                id="boolProperty",
                                type=datamodel.PropertyType.BOOL,
                                description="A bool-typed property.",
                            ),
                            datamodel.PropertyDeclaration(
                                id="dictProperty",
                                type=datamodel.PropertyType.DICT,
                                description="A dict-typed property.",
                            ),
                            datamodel.PropertyDeclaration(
                                id="floatProperty",
                                type=datamodel.PropertyType.FLOAT,
                                description="A float-typed property.",
                            ),
                            datamodel.PropertyDeclaration(
                                id="intProperty",
                                type=datamodel.PropertyType.INTEGER,
                                description="A int-typed property.",
                            ),
                            datamodel.PropertyDeclaration(
                                id="stringProperty",
                                type=datamodel.PropertyType.STRING,
                                description="A string-typed property.",
                            ),
                        ],
                    ),
                    datamodel.TraitDeclaration(
                        id="openassetio-codegen-test-all:aNamespace.NoProperties",
                        name="NoProperties",
                        description="Another trait, this time with no properties.",
                        properties=[],
                        usage=[],
                    ),
                    datamodel.TraitDeclaration(
                        id="openassetio-codegen-test-all:aNamespace.NoPropertiesMultipleUsage",
                        name="NoPropertiesMultipleUsage",
                        description="Another trait, this time with multiple usage.",
                        properties=[],
                        usage=["entity", "relationship"],
                    ),
                ],
            ),
            datamodel.NamespaceDeclaration(
                id="anotherNamespace",
                description="Another Namespace",
                members=[
                    datamodel.TraitDeclaration(
                        id="openassetio-codegen-test-all:anotherNamespace.NoProperties",
                        name="NoProperties",
                        description="Another NoProperties trait in a different namespace",
                        properties=[],
                        usage=[],
                    ),
                ],
            ),
        ],
        specifications=[
            datamodel.NamespaceDeclaration(
                id="test",
                description="Test specifications.",
                members=[
                    datamodel.SpecificationDeclaration(
                        id="LocalAndExternalTrait",
                        description=(
                            "A specification referencing traits in this and another package."
                        ),
                        usage=['entity', 'managementPolicy'],
                        trait_set=[
                            datamodel.TraitReference(
                                id="openassetio-codegen-test-all:aNamespace.NoProperties",
                                package="openassetio-codegen-test-all",
                                namespace="aNamespace",
                                name="NoProperties",
                                unique_name_parts=(
                                    "openassetio-codegen-test-all",
                                    "aNamespace",
                                    "NoProperties",
                                ),
                            ),
                            datamodel.TraitReference(
                                id="openassetio-codegen-test-traits-only:aNamespace.NoProperties",
                                package="openassetio-codegen-test-traits-only",
                                namespace="aNamespace",
                                name="NoProperties",
                                unique_name_parts=(
                                    "openassetio-codegen-test-traits-only",
                                    "aNamespace",
                                    "NoProperties",
                                ),
                            ),
                        ],
                    ),
                    datamodel.SpecificationDeclaration(
                        id="OneExternalTrait",
                        description="A specification referencing traits in another package.",
                        usage=[],
                        trait_set=[
                            datamodel.TraitReference(
                                id="openassetio-codegen-test-traits-only:test.Another",
                                package="openassetio-codegen-test-traits-only",
                                namespace="test",
                                name="Another",
                                unique_name_parts=("Another",),
                            ),
                        ],
                    ),
                    datamodel.SpecificationDeclaration(
                        id="TwoLocalTraits",
                        description="A specification with two traits.",
                        usage=[],
                        trait_set=[
                            datamodel.TraitReference(
                                id="openassetio-codegen-test-all:aNamespace.NoProperties",
                                package="openassetio-codegen-test-all",
                                namespace="aNamespace",
                                name="NoProperties",
                                unique_name_parts=("aNamespace", "NoProperties"),
                            ),
                            datamodel.TraitReference(
                                id="openassetio-codegen-test-all:anotherNamespace.NoProperties",
                                package="openassetio-codegen-test-all",
                                namespace="anotherNamespace",
                                name="NoProperties",
                                unique_name_parts=("anotherNamespace", "NoProperties"),
                            ),
                        ],
                    ),
                ],
            )
        ],
    )


@pytest.fixture
def declaration_traits_only():
    return datamodel.PackageDeclaration(
        id="openassetio-codegen-test-traits-only",
        description=(
            "Test classes to validate the integrity of the openassetio-codegen tool when only "
            "traits are defined."
        ),
        traits=[
            datamodel.NamespaceDeclaration(
                id="aNamespace",
                description="A namespace that overlaps with the all package",
                members=[
                    datamodel.TraitDeclaration(
                        id="openassetio-codegen-test-traits-only:aNamespace.NoProperties",
                        name="NoProperties",
                        description="Yet Another No Properties Trait",
                        properties=[],
                        usage=["managementPolicy"],
                    ),
                ],
            ),
            datamodel.NamespaceDeclaration(
                id="test",
                description="A namespace for testing.",
                members=[
                    datamodel.TraitDeclaration(
                        id="openassetio-codegen-test-traits-only:test.Another",
                        name="Another",
                        description="Yet Another Trait",
                        properties=[],
                        usage=["managementPolicy"],
                    ),
                ],
            ),
        ],
        specifications=[],
    )


@pytest.fixture
def declaration_specifications_only():
    return datamodel.PackageDeclaration(
        id="openassetio-codegen-test-specifications-only",
        description=(
            "Test classes to validate the integrity of the openassetio-codegen tool when only "
            "specifications are defined."
        ),
        traits=[],
        specifications=[
            datamodel.NamespaceDeclaration(
                id="test",
                description="More test specifications.",
                members=[
                    datamodel.SpecificationDeclaration(
                        id="Some",
                        description="Some specification",
                        usage=[],
                        trait_set=[
                            datamodel.TraitReference(
                                id="openassetio-codegen-test-all:aNamespace.AllProperties",
                                package="openassetio-codegen-test-all",
                                namespace="aNamespace",
                                name="AllProperties",
                                unique_name_parts=("AllProperties",),
                            ),
                            datamodel.TraitReference(
                                id="openassetio-codegen-test-traits-only:test.Another",
                                package="openassetio-codegen-test-traits-only",
                                namespace="test",
                                name="Another",
                                unique_name_parts=("Another",),
                            ),
                        ],
                    ),
                ],
            )
        ],
    )


@pytest.fixture
def declaration_exotic_values():
    """
    A declaration that contains exotic values that should be used to
    ensure generators properly handle a variety of incoming values.

    The up-front description validation presently doesn't allow these
    to be loaded from YAML, but we may relax this constraint in the
    future (eg: as part of l18n), and so its critical that generators
    of ASCII constrained languages sanitize and conform inputs (with
    warnings).
    """
    return datamodel.PackageDeclaration(
        id="p📦p",
        description="p",
        traits=[
            datamodel.NamespaceDeclaration(
                id="t!n",
                description="n",
                members=[
                    datamodel.TraitDeclaration(
                        id="p📦p:t!n.t&",
                        name="t&",
                        description="t",
                        usage=[],
                        properties=[
                            datamodel.PropertyDeclaration(
                                id="p$", description="p", type=datamodel.PropertyType.BOOL
                            )
                        ],
                    ),
                ],
            ),
        ],
        specifications=[
            datamodel.NamespaceDeclaration(
                id="s!n",
                description="",
                members=[
                    datamodel.SpecificationDeclaration(
                        id="s^",
                        description="",
                        usage=[],
                        trait_set=[
                            datamodel.TraitReference(
                                id="p📦p:t!n.t&",
                                package="p📦p",
                                namespace="t!n",
                                name="t&",
                                unique_name_parts=("t&",),
                            )
                        ],
                    )
                ],
            )
        ],
    )


# Note: This is here as the CLI tests use python generation to check
# functionality/console output.
@pytest.fixture
def creations_minimal_python():
    """
    The expected list of creations (relative to the output dir)
    from python generation of minimal.yaml.
    """
    return [
        os.path.join("python", "p_p"),
        os.path.join("python", "p_p", "traits"),
        os.path.join("python", "p_p", "traits", "tn.py"),
        os.path.join("python", "p_p", "traits", "__init__.py"),
        os.path.join("python", "p_p", "specifications"),
        os.path.join("python", "p_p", "specifications", "sn.py"),
        os.path.join("python", "p_p", "specifications", "__init__.py"),
        os.path.join("python", "p_p", "__init__.py"),
    ]


@pytest.fixture
def a_capturing_logger():
    logger = logging.Logger("test_openassetio_codegen")

    class CapturingHandler(logging.Handler):
        def __init__(self):
            super().__init__()
            self.messages = []

        def handle(self, record: logging.LogRecord) -> bool:
            self.messages.append((record.levelno, record.getMessage()))
            return True

    handler = CapturingHandler()
    logger.addHandler(handler)
    return logger
