#
#   Copyright 2013-2022 [The Foundry Visionmongers Ltd]
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
The implementation of the "basic asset library" manager.

See __init__.py for more details on it's high-level approach.

@info This code is a sketch to facilitate testing and sample workflows.
It should never be considered in any way a "good example of how to write
an asset management system". Consequently, it omits a plethora of "good
engineering practice".
"""

import json

from collections import namedtuple
from urllib.parse import urlparse


from openassetio.exceptions import InvalidEntityReference


EntityInfo = namedtuple("EntityInfo", ("name"), defaults=("",))
Entity = namedtuple("Entity", ("traits"), defaults=({},))


def make_default_settings() -> dict:
    """
    Generates a default settings dict for BAL.
    Note: as a library is required, the default settings are not enough
    to initialize the manager.
    """
    return {
        "library_path": ""
    }


def validate_settings(settings: dict):
    """
    Parses the supplied settings dict, raising if there are any
    unrecognized keys present.
    """

    defaults = make_default_settings()

    for key in settings:
        if key not in defaults:
            raise KeyError(f"Unknown setting '{key}'")


def load_library(path: str) -> dict:
    """
    Loads a library from the supplied path
    """
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_entity_ref(entity_ref: str) -> EntityInfo:
    """
    Decomposes an entity reference into bal fields.
    """
    uri_parts = urlparse(entity_ref)

    if not uri_parts.path:
        raise InvalidEntityReference("Missing entity name in path component", entity_ref)

    # path will start with a /
    name = uri_parts.path[1:]

    return EntityInfo(name=name)


def exists(entity_info: EntityInfo, library: dict) -> bool:
    """
    Determines if the supplied entity exists in the library
    """
    return entity_info.name in library["entities"]


def entity(entity_info: EntityInfo, library: dict) -> Entity:
    """
    Retrieves the Entity data addressed by the supplied EntityInfo
    """
    return Entity(**library["entities"][entity_info.name]["versions"][-1])
