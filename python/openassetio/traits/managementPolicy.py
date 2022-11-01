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
Traits returned by @fqref{hostApi.Manager.managementPolicy}
"Manager.managementPolicy"
"""
from typing import Union

from ..TraitBase import TraitBase


class ManagedTrait(TraitBase):
    """
    @fqref{hostApi.Manager.managementPolicy} "managementPolicy"
    trait specifying that a given @ref trait_set can be managed by the
    @ref manager plugin.

    There are three possible policies determined by applying/querying
    this trait
    * If a @fqref{TraitsData} "TraitsData" is not imbued with this
      trait, then the Manager has no interest in participating in the
      management of entities that match the queried trait set, for
      either read or write.
    * If the TraitsData is imbued with this trait, then the Manager
      would like the opportunity to manage the entity, but the user
      should still be presented with standard Host UI for the type as an
      option.
    * If the "exclusive" property is set to true, then the Manager
      takes exclusive control over entities that match the queried trait
      set, and any host interfaces etc should be suppressed.
    """

    kId = "openassetio.Managed"

    __kExclusive = "exclusive"

    def setExclusive(self, exclusive: bool):
        """
        Set the "exclusive" property.
        """
        if not isinstance(exclusive, bool):
            raise TypeError("exclusive must be a bool")

        self._data.setTraitProperty(self.kId, self.__kExclusive, exclusive)

    def getExclusive(self, defaultValue=None) -> Union[bool, None]:
        """
        Get the "exclusive" property.
        """
        value = self._data.getTraitProperty(self.kId, self.__kExclusive)

        if value is None:
            return defaultValue

        if not isinstance(value, bool):
            if defaultValue is None:
                raise TypeError(f"Invalid stored value type: '{value}' [{type(value).__name__}]")
            return defaultValue
        return value


class WillManagePathTrait(TraitBase):
    """
    @fqref{hostApi.Manager.managementPolicy} "managementPolicy"
    policy trait for determining whether a @ref manager can determine
    URLs for a new @ref entity "entity's" data.

    If not imbued, the manager is not capable of determining the URL for
    a new entity's data, and will only keep track of existing data. If
    this trait is imbued, the manager will determine the URL to use for
    writing data for new entities.
    """

    kId = "openassetio.WillManagePath"
