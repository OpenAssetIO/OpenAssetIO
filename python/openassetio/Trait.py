#
#   Copyright 2013-2022 The Foundry Visionmongers Ltd
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
A single-class module that provides the Trait class.
"""


class Trait:
    """
    A trait view provides a way to hide the underlying dictionary-like
    data access from hosts and managers. Trait view classes wrap a
    @fqref{TraitsData} "TraitsData" instance and provide member
    functions that query/mutate properties on the data.

    This base class provides the common interface for a concrete
    trait view.

    As an example, assume a trait view called `MyTrait` and an arbitrary
    TraitsData instance. Before we can extract `MyTrait` property values
    from the data we must check that it supports `MyTrait`. We can then
    use the trait's concrete accessors to retrieve data from the
    underlying dictionary-like data.

    A trait class inheriting from this base must have a static kId
    attribute member giving the unique string ID of that trait.

    @see kTraitId

    In addition, the derived class should implement appropriate typed
    accessor / mutator methods that internally call the wrapped
    data's @fqref{TraitsData.getTraitProperty}
    "getTraitProperty" / @fqref{TraitsData.setTraitProperty}
    "setTraitProperty".

    @note Attempting to access a trait's properties without first
    ensuring the data holds that trait via `isValid`, or
    otherwise, may trigger an exception if the trait is not set in
    the data.
    """

    def __init__(self, traitsData):
        """
        Construct this trait view, wrapping the given data.

        @param traitsData @fqref{TraitsData}} "TraitsData" The target
        data that holds/will hold the traits properties.
        """
        self._data = traitsData

    def isValid(self):
        """
        Checks whether the data this trait has been applied to
        actually has this trait.

        @return `True` if the underlying data has this
        trait, `False` otherwise.
        """
        return self._data.hasTrait(self.kId)  # pylint: disable=no-member

    def imbue(self):
        """
        Adds this trait to the held data.

        If the data already has this trait, it is a no-op.
        """
        self._data.addTrait(self.kId)  # pylint: disable=no-member

    @classmethod
    def imbueTo(cls, traitsData):
        """
        Adds this trait to the provided data.

        If the data already has this trait, it is a no-op.
        """
        traitsData.addTrait(cls.kId)  # pylint: disable=no-member
