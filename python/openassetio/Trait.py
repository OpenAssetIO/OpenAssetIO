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
    @fqref{specification::Specification} "Specification" and provide
    member functions that query/mutate properties on the specification.

    This base class provides the common interface for a concrete
    trait view.

    As an example, assume a trait view called `MyTrait` and an arbitrary
    specification. Before we can extract `MyTrait` property values from
    the specification we must check that it supports `MyTrait`. We can
    then use the trait's concrete accessors to retrieve data from the
    underlying dictionary-like specification.

    A trait class inheriting from this base must have a static kId
    attribute member giving the unique string ID of that trait.

    @see TraitId

    In addition, the derived class should implement appropriate typed
    accessor / mutator methods that internally call the wrapped
    specification's @fqref{specification::Specification::getTraitProperty}
    "getTraitProperty" / @fqref{specification::Specification::setTraitProperty}
    "setTraitProperty".

    @note Attempting to access a trait's properties without first
    ensuring the specification supports that trait via `isValid`, or
    otherwise, may trigger an exception if the trait is not supported by
    the specification.
    """

    def __init__(self, specification):
        """
        Construct this trait view, wrapping the given specification.

        @param specification @fqref{specification::Specification}}
        "Specification" The target specification that holds/will hold
        the traits properties.
        """
        self._specification = specification


    def isValid(self):
        """
        Checks whether the specification this trait has been applied to
        actually supports this trait.

        @return `True` if the underlying specification suppports this
        trait, `False` otherwise.
        """
        return self._specification.hasTrait(self.kId)  # pylint: disable=no-member
