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
Utility functions to help code generation templates.
"""
import datetime
import re

from typing import List, Union
from ..datamodel import SpecificationDeclaration, TraitDeclaration


def to_upper_camel_alnum(string: str) -> str:
    """
    Reformats a string to UpperCamelCase stripping out any non
    alpha-numeric characters.

    eg
    : "ThisIs! a complex-string" -> "ThisIsAComplexString"
    """
    #                  non-alnum or UC w/subsq. LC or UC preceding UC/end
    words = re.split("([^a-zA-Z0-9]+|[A-Z](?:[a-z]+)|[A-Z](?=[A-Z]|$))", string)
    # Splits may be empty, or contain invalid characters, eg:
    #   ( '', 'This', '', 'Is', '', '! ', 'a', ' ', 'complex', '-', 'string' )
    legal_words = [word.capitalize() for word in words if (word and word.isalnum())]
    return "".join(legal_words)


def to_lower_camel_alnum(string: str) -> str:
    """
    Reformats a string to lowerCamelCase stripping out any non
    alpha-numeric characters.

    eg: "This is a complex-string" -> "thisIsAComplexString"
    """
    upper = to_upper_camel_alnum(string)
    return upper[0].lower() + upper[1:]


def default_template_globals() -> dict:
    """
    Common template variables for sundry code boilerplate

    - copyrightDate: A date range for copyright text.
    - copyrightOwner: The owner of the copyright license.
    """
    return {
        "copyrightDate": datetime.date.today().year,
        "copyrightOwner": "",
        "spdxLicenseIdentifier": "Apache-2.0",
    }


def package_dependencies(
    declarations: List[Union[SpecificationDeclaration, TraitDeclaration]]
) -> List[str]:
    """
    Returns a list of all dependent package names for the supplied
    declarations.
    """
    dependencies = set()
    for declaration in declarations:
        if isinstance(declaration, SpecificationDeclaration):
            for trait in declaration.trait_set:
                dependencies.add(trait.package)
    dependencies = list(dependencies)
    dependencies.sort()
    return dependencies
