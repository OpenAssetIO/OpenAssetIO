#!/usr/bin/env python
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
#   distributed under the License is distributed on an "AS IS" BASIS
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""
A simple CLI that demonstrates resolving an Entity Reference through
the default OpenAssetIO manager.

Simply supply a set of traits and an entity reference, and the resulting
data will be output in JSON form.
"""
import argparse
import json
import sys


from openassetio import SpecificationBase
from openassetio.hostApi import HostInterface, ManagerFactory
from openassetio.log import ConsoleLogger, SeverityFilter
from openassetio.pluginSystem import PythonPluginSystemManagerImplementationFactory


# pylint: disable=missing-function-docstring,no-self-use,invalid-name


#
## OpenAssetIO required host classes
#


class TestHost(HostInterface):
    """
    A minimal host interface implementation. This identifiers the
    calling tool or application to the API and downstream Manager.
    """

    def identifier(self):
        return "default.manager.demo.host"

    def displayName(self):
        return "Default Manager Demo Host"


class CLILocale(SpecificationBase):
    """
    A minimal locale that defines a CLI environment.
    Note: In the future, these common starting points will be moved to a
    shared repository to avoid inconsistencies/duplication.
    """

    kTraitSet = {"cli", "demo"}


#
## Batch result callbacks
#
# The API is batch-centric for entity related calls. The general
# approach supplies a list of Entity References to a method, which then
# calls the success or failure callback for each element of that list
# with the response from the manager. In the future we plan to provide
# additional conveniences for single entity tasks, or 'list in list out'
# use cases.


def print_traits_data(_, data):
    """
    A callback function that will print out the supplied entity
    TraitsData. As we only deal with a single result, we ignore the
    index.
    """
    as_dict = {
        trait_id: {
            property_key: data.getTraitProperty(trait_id, property_key)
            for property_key in data.traitPropertyKeys(trait_id)
        }
        for trait_id in data.traitSet()
    }
    print(json.dumps(as_dict))


def fail_with_message(_, batch_element_error):
    """
    A callback function that will exit with an appropriate message and
    error code As we only deal with a single result, we ignore the
    index.
    """
    sys.stderr.write(f"ERROR: {batch_element_error.message}\n")
    sys.exit(int(batch_element_error.code))


#
# main
#


def create_argparser():
    """
    Creates an argparse for the tool.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "traitset", help="A comma separated list of traits to resolve eg: trati1,trait2"
    )
    parser.add_argument("entityref", help="An entity reference to resolve")
    return parser


def main():

    # Helpers required by the API

    # A simple logger that prints messages to the console.
    logger = SeverityFilter(ConsoleLogger())

    # The Python plugin system can load manager implementations
    # defined outside of the API package.
    impl_factory = PythonPluginSystemManagerImplementationFactory(logger)

    # The HostInterface implementation we supply that identifies
    # ourselves to the manager
    host_interface = TestHost()

    # Initialize the default manager as configured by $OPENASSETIO_DEFAULT_CONFIG
    # See: https://openassetio.github.io/OpenAssetIO/classopenassetio_1_1v1_1_1host_api_1_1_manager_factory.html#a8b6c44543faebcb1b441bbf63c064c76
    # All API/Manager messaging is channeled through the supplied logger.
    manager = ManagerFactory.defaultManagerForInterface(host_interface, impl_factory, logger)

    if not manager:
        raise RuntimeError(
            "No default manager configured, "
            f"check ${ManagerFactory.kDefaultManagerConfigEnvVarName}"
        )

    # Extract the entity reference and trait set to resolve from
    # the CLI args

    parser = create_argparser()
    args = parser.parse_args()

    entity_reference = manager.createEntityReference(args.entityref)
    trait_set = set(args.traitset.split(","))

    # Create an OpenAssetIO context that describes the calling
    # environment

    context = manager.createContext()
    context.access = context.Access.kRead
    context.locale = CLILocale.create().traitsData()

    # Resolve the requested traits for the referenced entity

    manager.resolve(
        [entity_reference],  # The API is batch-centric
        trait_set,
        context,
        print_traits_data,  # success callback
        fail_with_message,  # error callback
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-except
        sys.stderr.write(f"ERROR: {exc}\n")
        sys.exit(1)
