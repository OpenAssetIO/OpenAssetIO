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
Code to load and validate trait/specification definitions from
YAML declarations.
"""

import json
import operator
import os
import yaml

import jsonschema

from typing import List, Dict

from . import datamodel

__all__ = ("load_yaml", "validate_package_description", "build_package_declaration")


def load_yaml(path: str) -> dict:
    """
    Loads specification and trait definitions from a YAML file.
    """
    with open(path, "r", encoding="utf-8") as file:
        # It would be nice to take advantage of the auto-instantiation
        # of classes via the load(), but we can't really require
        # the addition of the `!!python/object` tag - as that would be
        # somewhat fragile.
        model = yaml.safe_load(file)
    return model


def validate_package_description(description: dict):
    """
    Validates the supplied package description meets the openassetio-codegen schema.
    """
    jsonschema.validate(description, schema=_load_schema())


def build_package_declaration(description: dict) -> datamodel.PackageDeclaration:
    """
    Populates a package declaration from the supplied package
    description.

    @param description A dict conforming to the openassetio-codegen
    schema. This should first be validated using the @ref
    validate_description method.
    """
    package_id = description["package"]
    return datamodel.PackageDeclaration(
        id=package_id,
        description=description.get("description", "").strip(),
        traits=_unpack_traits(description.get("traits", {}), package_id),
        specifications=_unpack_specifications(description.get("specifications", {}), package_id),
    )


#
# Private implementation
#


def _unpack_specifications(model: dict, package_id: str) -> List[datamodel.NamespaceDeclaration]:
    """
    Returns a list of NamespaceDeclarations containing
    SpecificationDeclarations from the supplied model.

    @param model A dict as per the "specifications" key in the JSON
    schema definition.
    """
    namespaces = []
    for namespace, data in model.items():
        specifications = [
            datamodel.SpecificationDeclaration(
                id=name,
                description=definition.get("description", "").strip(),
                trait_set=_unpack_trait_set(definition["traitSet"], package_id),
                usage=definition.get("usage", []),
            )
            for name, definition in data["members"].items()
        ]
        specifications.sort(key=_byId)

        namespaces.append(
            datamodel.NamespaceDeclaration(
                id=namespace, description=data["description"].strip(), members=specifications
            )
        )

    namespaces.sort(key=_byId)
    return namespaces


def _unpack_trait_set(trait_set: List[dict], package_id: str) -> List[datamodel.TraitReference]:
    """
    Returns a list of TraitReferences for the supplied trait set
    description.
    """
    # We need to provide a unique 'reference name' for each trait set
    # (e.g. to use in accessor method names). Ideally, this would be it's
    # name. However, you may have two traits with the same name in
    # different namespaces or packages. We don't want to have to always
    # use the full package/namespace/name path for trait accessor
    # methods, so we endeavour to find the shortest uniquely identifying
    # set of reference components.

    # Build a list of possible unique short names for all the trait
    # references of the trait set, we can then check for any given
    # reference, if any shorter set of components has been seen more
    # than once.
    # (This would be easier if you could mutate NamedTuples after
    # creation, but well, they're tuples aren't they...)
    all_permutations = []
    for trait in trait_set:
        all_permutations.extend(((trait["name"],), (trait["namespace"], trait["name"])))

    references = set()
    for trait in trait_set:

        package = trait.get("package", package_id)
        namespace = trait["namespace"]
        name = trait["name"]

        identifier = _build_trait_id(package, namespace, name)

        # Check to see which of the possible combinations of reference
        # parts is unique for this trait.
        unique_name_parts = (name,)
        alternatives = [
            (namespace, name),
            (package, namespace, name),
        ]
        while alternatives and all_permutations.count(unique_name_parts) > 1:
            unique_name_parts = alternatives.pop(0)

        references.add(
            datamodel.TraitReference(
                id=identifier,
                name=name,
                namespace=namespace,
                package=package,
                unique_name_parts=unique_name_parts,
            )
        )

    references = list(references)
    references.sort(key=_byId)
    return references


def _build_trait_id(package: str, namespace: str, name: str) -> str:
    return f"{package}:{namespace}.{name}"


def _unpack_traits(
    model: Dict[str, dict], package_id: str
) -> List[datamodel.NamespaceDeclaration]:
    """
    Returns a list of NamespaceDeclarations containing
    TraitDeclarations from the supplied model.

    @param model A dict as per the "specifications" key in the JSON
    schema definition.
    """
    namespaces = []
    for namespace, data in model.items():
        traits = [
            datamodel.TraitDeclaration(
                id=_build_trait_id(package_id, namespace, name),
                name=name,
                description=definition.get("description", "").strip(),
                properties=_unpack_properties(definition.get("properties", {})),
                usage=definition.get("usage", []),
            )
            for name, definition in data["members"].items()
        ]
        traits.sort(key=_byName)

        namespaces.append(
            datamodel.NamespaceDeclaration(
                id=namespace, description=data["description"].strip(), members=traits
            )
        )

    namespaces.sort(key=_byId)
    return namespaces


def _unpack_properties(model: Dict[str, dict]) -> List[datamodel.PropertyDeclaration]:
    """
    Returns a list of PropertyDefinitions sorted by id.

    @param model A dict as per the "properties" key under a trait
    definition in the JSON schema definition.
    """
    properties = [
        datamodel.PropertyDeclaration(
            id=id_,
            type=datamodel.PropertyType(data["type"]),
            description=data.get("description", "").strip(),
        )
        for id_, data in model.items()
    ]
    properties.sort(key=_byId)
    return properties


def _load_schema() -> dict:
    """
    Loads the validation schema
    """
    path = os.path.join(__rootDir, "schema.json")
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


__rootDir = os.path.dirname(__file__)

# Sort key helpers
_byId = operator.attrgetter("id")
_byName = operator.attrgetter("name")
