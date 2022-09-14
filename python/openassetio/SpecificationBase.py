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
A single-class module that provides the SpecificationBase class.
"""

from ._openassetio import TraitsData  # pylint: disable=import-error


class SpecificationBase:
    """
    Specifications form a template for working with @fqref{TraitsData}
    "TraitsData" instances.

    This base class should never be used directly.

    @see @ref entities_traits_and_specifications
    """

    def __init__(self, traitsData):
        """
        Constructs the specification as a view on the supplied
        shared @fqref{TraitsData} "TraitsData" instance.

        @param traitsData @fqref{TraitsData} "TraitsData"

        @warning Specifications are always a view on the supplied data,
        which is held by reference. Any changes made to the data will be
        visible to any other specifications or @ref trait "traits" that
        wrap the same TraitsData instance.
        """
        if not isinstance(traitsData, TraitsData):
            raise TypeError("Specifications must be constructed with a TraitsData instance")
        self._data = traitsData

    def traitsData(self):
        """
        Returns the underlying (shared) @fqref{TraitsData} "TraitsData"
        instance held by this specification.
        """
        return self._data

    @classmethod
    def create(cls):
        """
        Returns a new instance of the Specification, holding a new
        @fqref{TraitsData} "TraitsData" instance, pre-populated with all
        of the specifications traits.
        """
        data = TraitsData(cls.kTraitSet)  # pylint: disable=no-member
        return cls(data)
