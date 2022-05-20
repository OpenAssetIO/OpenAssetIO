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

from openassetio import constants, TraitsData
from openassetio.exceptions import InvalidEntityReference, PluginError, EntityResolutionError
from openassetio.managerAPI import ManagerInterface

from . import bal

__all__ = [
    "BasicAssetLibraryInterface",
]

# TODO(TC): @pylint-disable
# As we are building out the implementation vertically, we have known
# fails for missing abstract methods.
# pylint: disable=abstract-method


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

    def setSettings(self, settings, hostSession):
        # pylint: disable=unused-argument
        bal.validate_settings(settings)
        self.__settings.update(settings)

    def getSettings(self, hostSession):
        # pylint: disable=unused-argument
        return self.__settings.copy()

    def initialize(self, hostSession):

        self.__library = {}

        if not self.__settings["library_path"]:
            hostSession.log(
                f"'library_path' not in settings, checking {self.__lib_path_envvar_name}",
                hostSession.kDebug,
            )
            self.__settings["library_path"] = os.environ.get(self.__lib_path_envvar_name)

        if not self.__settings["library_path"]:
            raise PluginError("'library_path' not set")

        hostSession.log(
            f"Loading library from {self.__settings['library_path']}", hostSession.kDebug
        )
        self.__library = bal.load_library(self.__settings["library_path"])

    def managementPolicy(self, traitSets, context, hostSession):
        # pylint: disable=unused-argument
        policy = constants.kManaged if context.isForRead() else constants.kIgnored
        return [policy for _ in traitSets]

    def isEntityReference(self, tokens, hostSession):
        # pylint: disable=unused-argument
        return [token.startswith(self.__reference_prefix) for token in tokens]

    def entityExists(self, entityRefs, context, hostSession):
        results = []
        for ref in entityRefs:
            try:
                entity_info = bal.parse_entity_ref(ref)
                result = bal.exists(entity_info, self.__library)
            except InvalidEntityReference as exc:
                result = exc
            results.append(result)
        return results

    def resolve(self, entityRefs, traitSet, context, hostSession):
        if context.isForWrite():
            return [EntityResolutionError("BAL entities are read-only", ref) for ref in entityRefs]
        results = []
        for ref in entityRefs:
            try:
                entity_info = bal.parse_entity_ref(ref)
                entity = bal.entity(entity_info, self.__library)
                result = TraitsData()
                for trait in traitSet:
                    trait_data = entity.traits.get(trait)
                    if trait_data is not None:
                        result.addTrait(trait)
                        for property_, value in trait_data.items():
                            result.setTraitProperty(trait, property_, value)
            except Exception as exc:  # pylint: disable=broad-except
                exc_name = exc.__class__.__name__
                result = EntityResolutionError(f"{exc_name}: {exc}", ref)
            results.append(result)
        return results
