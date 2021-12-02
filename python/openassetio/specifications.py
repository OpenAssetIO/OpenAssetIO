#
#   Copyright 2013-2021 [The Foundry Visionmongers Ltd]
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

from .Specification import Specification, TypedProperty


__all__ = ['EntitySpecification', 'LocaleSpecification', 'RelationshipSpecification']


class EntitySpecification(Specification):
    """
    EntitySpecifications are used to 'type' a \ref entity. In their
    simplest form, the _type can be used as a simple string-matched
    filter. In more advanced cases, the other properties of the
    Specification may be useful to further refine selection. During
    registration, the Specification may also provide valuable
    information to the Manager to help it best represent the Hosts data.
    """
    _prefix = "core.entity"

    nameHint = TypedProperty(
        str,
        doc="A hint as to the name of the entity, used in cases where"
            " this is not implicit in the reference.")

    referenceHint = TypedProperty(
        str,
        doc="A hint for the entity reference, useful for default"
            " browser path, etc... This may, or may not ultimately be"
            " relevant. The Asset Management system should check its"
            " applicability before using it, and may freely ignore it"
            " if it has a better idea about a suitable reference.")


class LocaleSpecification(Specification):
    """
    LocaleSpecifications are used by a Host to define which part of the
    application is interacting with the Manager. For example, the
    DocumentLocale should be used when dealing with scene files,
    projects, etc... This information is generally useful to Managers as
    it allows them to better handle the resulting Entity data.
    """
    _prefix = "core.locale"


class RelationshipSpecification(Specification):
    """
    RelationshipSpecifications are used mainly with \ref
    openassetio.managerAPI.ManagerInterface.ManagerInterface.getRelatedReferences
    "ManagerInterface.getRelatedReferences", in order to describe the
    kind of relation that is being requested, when a simply
    EntitySpecification will not suffice.
    """
    _prefix = "core.relationship"
