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
"""
A single-class module, providing the BasicAssetLibraryInterface class.
"""

import os

from openassetio import constants, BatchElementError, EntityReference, TraitsData
from openassetio.exceptions import MalformedEntityReference, PluginError
from openassetio.managerApi import ManagerInterface

from . import bal

__all__ = [
    "BasicAssetLibraryInterface",
]

# TODO(TC): @pylint-disable
# As we are building out the implementation vertically, we have known
# fails for missing abstract methods.
# pylint: disable=abstract-method
# Methods in C++ end up with "missing docstring"
# pylint: disable=missing-docstring
# pylint: disable=no-self-use, too-many-arguments, invalid-name


class BasicAssetLibraryInterface(ManagerInterface):
    """
    This class exposes the Basic Asset Library through the OpenAssetIO
    ManagerInterface.
    """

    __reference_prefix = "bal:///"
    __lib_path_envvar_name = "BAL_LIBRARY_PATH"

    def __init__(self):
        super().__init__()
        self.__settings = bal.make_default_settings()
        self.__library = {}

    def identifier(self):
        return "org.openassetio.examples.manager.bal"

    def displayName(self):
        # Deliberately includes unicode chars to test string handling
        return "Basic Asset Library 📖"

    def info(self):
        return {constants.kField_EntityReferencesMatchPrefix: self.__reference_prefix}

    def settings(self, hostSession):
        # pylint: disable=unused-argument
        return self.__settings.copy()

    def initialize(self, managerSettings, hostSession):
        # pylint: disable=unused-argument
        bal.validate_settings(managerSettings)
        self.__settings.update(managerSettings)

        self.__library = {}

        if self.__settings.get("library_path") is None:
            hostSession.logger().log(
                hostSession.logger().Severity.kDebug,
                f"'library_path' not in settings, checking {self.__lib_path_envvar_name}",
            )
            self.__settings["library_path"] = os.environ.get(self.__lib_path_envvar_name)

        if self.__settings.get("library_path") is None:
            raise PluginError("'library_path' not set")

        hostSession.logger().log(
            hostSession.logger().Severity.kDebug,
            f"Loading library from {self.__settings['library_path']}"
        )
        self.__library = bal.load_library(self.__settings["library_path"])

    def managementPolicy(self, traitSets, context, hostSession):

        access = "read" if context.isForRead() else "write"
        return [
            self.__dict_to_traits_data(bal.management_policy(trait_set, access, self.__library))
            for trait_set in traitSets
        ]

    def isEntityReferenceString(self, someString, hostSession):
        # pylint: disable=unused-argument
        return someString.startswith(self.__reference_prefix)

    def entityExists(self, entityRefs, context, hostSession):
        results = []
        for ref in entityRefs:
            try:
                entity_info = bal.parse_entity_ref(ref.toString())
                result = bal.exists(entity_info, self.__library)
            except bal.MalformedBALReference as exc:
                result = MalformedEntityReference(str(exc))
            results.append(result)
        return results

    def resolve(
        self, entityReferences, traitSet, context, hostSession, successCallback, errorCallback
    ):
        if context.isForWrite():
            result = BatchElementError(
                BatchElementError.ErrorCode.kEntityAccessError,
                "BAL entities are read-only")
            for idx in range(len(entityReferences)):
                errorCallback(idx, result)
            return

        for idx, ref in enumerate(entityReferences):
            try:
                entity_info = bal.parse_entity_ref(ref.toString())
            except bal.MalformedBALReference as exc:
                result = BatchElementError(
                    BatchElementError.ErrorCode.kMalformedEntityReference, str(exc)
                )
                errorCallback(idx, result)
            else:
                try:
                    entity = bal.entity(entity_info, self.__library)
                except bal.UnknownBALEntity:
                    result = BatchElementError(
                        BatchElementError.ErrorCode.kEntityResolutionError,
                        f"Entity '{ref.toString()}' not found")
                    errorCallback(idx, result)
                else:
                    result = TraitsData()
                    for trait in traitSet:
                        trait_data = entity.traits.get(trait)
                        if trait_data is not None:
                            self.__add_trait_to_traits_data(trait, trait_data, result)

                    successCallback(idx, result)

    def preflight(
        self, targetEntityRefs, traitSet, context, hostSession, successCallback, errorCallback
    ):
        # Support publishing to any valid entity reference
        for idx, ref in enumerate(targetEntityRefs):
            try:
                bal.parse_entity_ref(ref.toString())
            except bal.MalformedBALReference as exc:
                result = BatchElementError(
                    BatchElementError.ErrorCode.kMalformedEntityReference, str(exc)
                )
                errorCallback(idx, result)
            else:
                successCallback(idx, ref)

    def register(
        self, targetEntityRefs, entityTraitsDatas, context, hostSession, successCallback,
        errorCallback,
    ):
        for idx, ref in enumerate(targetEntityRefs):
            try:
                entity_info = bal.parse_entity_ref(ref.toString())
            except bal.MalformedBALReference as exc:
                result = BatchElementError(
                    BatchElementError.ErrorCode.kMalformedEntityReference, str(exc)
                )
                errorCallback(idx, result)
            else:
                traits_dict = self.__traits_data_to_dict(entityTraitsDatas[idx])
                updated_entity_info = bal.create_or_update_entity(
                    entity_info, traits_dict, self.__library
                )
                successCallback(idx, self.__build_entity_ref(updated_entity_info))

    def __build_entity_ref(self, entity_info: bal.EntityInfo) -> EntityReference:
        """
        Builds an openassetio EntityReference from a BAL EntityInfo
        """
        ref_string = f"bal:///{entity_info.name}"
        return self._createEntityReference(ref_string)

    @classmethod
    def __dict_to_traits_data(cls, traits_dict: dict):
        traits_data = TraitsData()
        for trait_id, trait_properties in traits_dict.items():
            cls.__add_trait_to_traits_data(trait_id, trait_properties, traits_data)
        return traits_data

    @classmethod
    def __traits_data_to_dict(cls, traits_data: TraitsData):
        return {
            trait_id: {
                prop_key: traits_data.getTraitProperty(trait_id, prop_key)
                for prop_key in traits_data.traitPropertyKeys(trait_id)
            }
            for trait_id in traits_data.traitSet()
        }

    @staticmethod
    def __add_trait_to_traits_data(trait_id: str, trait_properties: dict, traits_data: TraitsData):
        traits_data.addTrait(trait_id)
        for name, value in trait_properties.items():
            traits_data.setTraitProperty(trait_id, name, value)
