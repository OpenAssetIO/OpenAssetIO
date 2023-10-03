#!/usr/bin/env python
#
#   Copyright 2022-2023 The Foundry Visionmongers Ltd
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

from openassetio.errors import BatchElementException
from openassetio.access import ResolveAccess
from openassetio.hostApi import HostInterface, ManagerFactory
from openassetio.errors import ConfigurationException
from openassetio.log import ConsoleLogger, SeverityFilter
from openassetio.pluginSystem import PythonPluginSystemManagerImplementationFactory


# pylint: disable=missing-function-docstring,no-self-use,invalid-name


#
## OpenAssetIO required host classes
#


class SimpleResolverHostInterface(HostInterface):
    """
    A minimal host interface implementation. This identifiers the
    calling tool or application to the API and downstream Manager.
    """

    def identifier(self):
        # In a real application, this is usually your organisations
        # reverse domain name plus a product or tool identifier. It
        # needs to be globally unique. e.g.:
        #
        #   com.foundry.nuke
        #   io.aswf.openrv
        #
        # See: https://en.wikipedia.org/wiki/Reverse_domain_name_notation
        return "org.openassetio.examples.host.simpleResolver"

    def displayName(self):
        # This is used my managers so should be the display name of your
        # product or tool, e.g.:
        #
        #   "Nuke"
        #   "OpenRV"
        return "Simple Resolver"


#
## Batch result callbacks
#
# The API is batch-centric for entity related calls. The general
# approach supplies a list of Entity References to a method, which then
# calls the success or failure callback for each element of that list
# with the response from the manager. In the future we plan to provide
# additional conveniences for single entity tasks, or 'list in list out'
# use cases.


def print_traits_data(data):
    """
    A function that will print out the supplied entity TraitsData.
    """
    # Note that in real tools, you should avoid working directly with
    # TraitsData. The industry-specific view classes should be used to
    # avoid fragile string literals, and ensure consistency.
    #
    # For example, the OpenAssetIO-MediaCreation project[1] provides
    # traits and specifications for common entity types found in
    # computer graphics. A tool wanting to find the URL for an image
    # would use the following trait that defines where an entity's
    # content can be found:
    #
    #   from openassetio_mediacreation.traits.content import LocatableContentTrait
    #   url = LocatableContentTrait(data).getLocation()
    #
    # The low-level API is only used here as this simple example script
    # has to work with trait ids supplied by users on the command line.
    #
    #
    # [1] https://github.com/OpenAssetIO/OpenAssetIO-MediaCreation

    as_dict = {
        trait_id: {
            property_key: data.getTraitProperty(trait_id, property_key)
            for property_key in data.traitPropertyKeys(trait_id)
        }
        for trait_id in data.traitSet()
    }
    print(json.dumps(as_dict))


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
    ###
    # API Bootstrap
    #
    # This section initializes the API. It does a non-trivial amount of
    # work, so in a typical application this should usually be done at
    # startup or similar, and the initialized manager re-used in
    # relevant parts of the code.
    ###

    # Helpers required by the API

    # A simple logger that prints messages to the console.
    # In most integrations you would derive the LoggerInterface
    # class and bridge the log method to your own messaging system.
    # ConsoleLogger/SeverityFilter are simple conveniences that can be
    # used in standalone situations such as this.
    logger = SeverityFilter(ConsoleLogger())

    # The Python plugin system can load manager implementations
    # defined outside of the API package.
    impl_factory = PythonPluginSystemManagerImplementationFactory(logger)

    # The HostInterface implementation we supply that identifies
    # ourselves to the manager
    host_interface = SimpleResolverHostInterface()

    # Initialize the default manager as configured by $OPENASSETIO_DEFAULT_CONFIG
    # See: https://openassetio.github.io/OpenAssetIO/classopenassetio_1_1v1_1_1host_api_1_1_manager_factory.html#a8b6c44543faebcb1b441bbf63c064c76
    # All API/Manager messaging is channeled through the supplied logger.
    manager = ManagerFactory.defaultManagerForInterface(host_interface, impl_factory, logger)

    if not manager:
        raise ConfigurationException(
            "No default manager configured, "
            f"check ${ManagerFactory.kDefaultManagerConfigEnvVarName}"
        )

    ###
    # Entity resolution
    #
    # This section deals with extracting the user-supplied entity
    # reference and using the manager to resolve this for the requested
    # traits.
    ###

    # Extract the entity reference and trait set to resolve from
    # the CLI args

    parser = create_argparser()
    args = parser.parse_args()

    entity_reference = manager.createEntityReference(args.entityref)
    trait_set = set(args.traitset.split(","))

    # Create an OpenAssetIO context that describes the calling
    # environment. The lifetime of this object is very important in
    # OpenAssetIO. It is used to tie together related calls into the API
    # so that the manager can ensure resolve results are stable over
    # time (if appropriate).
    #
    # Broadly speaking, the same context should be re-used for calls
    # that are part of the same logical action from the user's
    # perspective. This could be the import of a data set, or the whole
    # interactive session.

    context = manager.createContext()

    # Resolve the requested traits for the referenced entity.
    # Note that there are multiple overloaded signatures for `resolve`,
    # to aid in batch and/or exception-less workflows. See API docs for
    # more. Here we use the default single-ref exception-throwing
    # signature.
    traits_data = manager.resolve(entity_reference, trait_set, ResolveAccess.kRead, context)
    print_traits_data(traits_data)


if __name__ == "__main__":
    try:
        main()
    except BatchElementException as exc:  # pylint: disable=broad-except
        sys.stderr.write(f"ERROR: {exc}\n")
        sys.exit(int(exc.error.code))
    except Exception as exc:  # pylint: disable=broad-except
        sys.stderr.write(f"ERROR: {exc}\n")
        sys.exit(1)
