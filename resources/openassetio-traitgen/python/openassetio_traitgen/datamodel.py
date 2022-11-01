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
Types and structures used in the traitgen tool to define the
declaration of a package of Traits and/or Specifications.

A package declaration is consumed by one or more generators to create
language specific implementations of its constituent
Traits/Specifications to be used as concrete views around a TraitsData
instance at runtime.

It forms a well-defined intermediate representation where various
aspects of the simple text-based declaration have been unpacked, and
convention-based elements such as a Trait's ID have been
pre-calculated.

It should be assumed that all free-form strings within a Declaration may
contain unicode characters, and consequently may require conforming
before being used as identifiers within any given language.

Note: The `DICT` property type must be held by an
`openassetio.InfoDictionary` or its per-language equivalent.
"""

from enum import Enum
from typing import List, NamedTuple, Tuple


#
# Traits
#


class PropertyType(Enum):
    """
    Valid types for Trait properties
    """

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOL = "boolean"
    DICT = "dictionary"  # Note: Must be type-constrained as per openassetio.InfoDictionary


class PropertyDeclaration(NamedTuple):
    """
    Declares a (Trait) property and it's type.
    """

    # The name of the property all the properties of any given trait
    # must have unique names.
    id: str
    # The value type, constrained to those supported by the TraitsData
    # container.
    type: PropertyType
    # A user-facing description of the property.
    description: str


class TraitDeclaration(NamedTuple):
    """
    Declares a Trait, along with its properties and usage.
    """

    # The universally unique ID of the Trait that is referenced by a
    # TraitSet.
    id: str
    # A short name for the Trait that is only unique within its
    # namespace.
    name: str
    # A user-facing description of the Trait and its purpose.
    description: str
    # User-facing hints as to the usage of this trait, in relation to
    # the API. This may be empty.
    usage: List[str]
    # A list of properties. These are guaranteed to have unique ids.
    # This may be empty.
    properties: List[PropertyDeclaration]


#
# Specifications
#


class TraitReference(NamedTuple):
    """
    Describes a reference to a specific trait by its package and
    namespace.

    Note: TraitReferences currently only support Traits in other
    openassetio-traitgen generated packages.

    """

    # The universally unique ID of the Trait being referenced.
    id: str
    # The short name of the trait
    name: str
    # The trait namespace it belongs to in its parent package.
    namespace: str
    # The package the trait belongs to
    package: str
    # The shortest list of elements from package, namespace and name
    # that is required to form a unique name for this trait
    # relative to the specification. These should be used
    # when building accessor method names to retrieve a
    # Trait instance from a Specification, as it handles the
    # case where a Specification may reference two identically
    # named traits in different packages or namespaces.
    unique_name_parts: Tuple[str]


class SpecificationDeclaration(NamedTuple):
    """
    Declares a Specification, along with its TraitSet and usage.
    """

    # The unique name of Specification within its namespace.
    id: str
    # A user-facing description of the Specification and its purpose.
    description: str
    # User-facing hints as to the usage of this trait, in relation to
    # the API. This may be empty.
    usage: List[str]
    # The set of unique traits composed by the Specification.
    trait_set: List[TraitReference]


#
# Packages
#


class NamespaceDeclaration(NamedTuple):
    """
    Declares a namespace that contains Traits or Specifications.
    Namespaces are flat and cannot contain other namespaces.
    """

    # The name of this namespace, unique within the namespaces of the
    # type of class being declared (Trait or Specification).
    id: str
    # A user-facing description of the nature of the namespace and its
    # contents.
    description: str
    # A list of members of the namespace.
    members: list


class PackageDeclaration(NamedTuple):
    """
    Declares a package of Traits and/or Specifications,

    Traits and Specification declarations are listed under a namespace.
    Any given Trait/Specification name is unique within it's namespace.
    Trait IDs are formed by combining the package id, namespace and
    trait name to form a globally unique identifier (assuming package
    names are suitably unique).
    """

    # A universally unique name for the package.
    id: str
    # A user-facing description of the package and its purpose.
    description: str
    # Trait namespaces. This may be empty.
    traits: List[NamespaceDeclaration]
    # Specification namespaces. This may be empty.
    specifications: List[NamespaceDeclaration]
