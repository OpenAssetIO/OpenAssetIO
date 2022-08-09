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
A single-class module, providing the SampleAssetManagerInterface class.

The manager currently ignores all entity types.
"""

# Note that it should always be light-weight to construct instances of
# the this class. See the notes under the "Initialization" section of:
#   https://openassetio.github.io/OpenAssetIO/classopenassetio_1_1manager_a_p_i_1_1_manager_interface_1_1_manager_interface.html#details (pylint: disable=line-too-long)
# As such, any expensive module imports should be deferred.
from openassetio import constants, TraitsData
from openassetio.managerApi import ManagerInterface

__all__ = ['SampleAssetManagerInterface', ]

# TODO(TC): @pylint-disable
# As we are building out the implementation vertically, we have known
# fails for missing abstract methods.
# pylint: disable=abstract-method

class SampleAssetManagerInterface(ManagerInterface):
    """
    Binds the SampleAssetManager to the OpenAssetIO ManagerInterface.

    This class contains none of the actual business logic implementing
    asset management, just bindings to the OpenAssetIO interface
    methods.
    """

    def identifier(self):
        return "org.openassetio.examples.manager.sam"

    def initialize(self, managerSettings, hostSession):
        pass

    def displayName(self):
        return "Sample Asset Manager (SAM)"

    def info(self):
        # This hint allows the API middleware to short-circuit calls to
        # `isEntityReferenceString` using string prefix comparisons. If
        # your implementation's entity reference format supports this
        # kind of matching, you should set this key. It allows for
        # multi-threaded reference testing in C++ as it avoids the need
        # to acquire the GIL and enter Python.
        return {
            constants.kField_EntityReferencesMatchPrefix: "sam:///"
        }

    def managementPolicy(self, traitSets, context, hostSession):
        # pylint: disable=unused-argument
        return [TraitsData() for _ in traitSets]
