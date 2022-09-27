#
#   Copyright 2013-2021 The Foundry Visionmongers Ltd
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
@namespace openassetio.hostApi.terminology
This module provides utilities for a @ref host that simplify the
integration of a @ref manager "manager's" custom terminology into its
user-facing components.
"""

from .._core.audit import auditApiCall


## @namespace openassetio.hostApi.terminology
#
# The terminology mapping mechanism allows Managers to customize
# terminology used within the host application.
# The Mapper class allows for more efficient access to term
# mapping during a Host session, and for the host to provide
# additional terminology keys.
#

## @name Terminology dict keys
## @{

kTerm_Asset = "asset"
kTerm_Assets = "assets"
kTerm_Manager = "manager"
kTerm_Publish = "publish"
kTerm_Publishing = "publishing"
kTerm_Published = "published"
kTerm_Shot = "shot"
kTerm_Shots = "shots"

## @}

## Default terminology for the API.
# Hosts may choose to add additional terminology keys when
# constructing a Mapper, but there is no expectation that
# any given manager would customize keys other than the
# defaultTerminology.
defaultTerminology = {
    kTerm_Asset: "Asset",
    kTerm_Assets: "Assets",
    kTerm_Manager: "Asset Manager",
    kTerm_Publish: "Publish",
    kTerm_Publishing: "Publishing",
    kTerm_Published: "Published",
    kTerm_Shot: "Shot",
    kTerm_Shots: "Shots",
}


class Mapper:
    """
    The Mapper class provides string substitution methods and lookups to
    determine the correct terminology for the supplied @ref manager.

    @unstable
    """

    def __init__(self, manager, terminology=defaultTerminology):
        """
        Constructs a new Mapper using terminology overrides defined
        by the supplied Manager. The manager is queried during
        construction and it's results cached for the lifetime of the
        Mapper.

        @param manager Manager, A Manager instance, whose terminology
        should be applied by the mapper.

        @param terminology A dict of terms that will be substituted by
        this instance. If left unspecified, the default API terminology
        will be used. Hosts may take a copy of this dictionary and
        append to it before passing to the Mapper to allow managers
        to customize additional host-specific terms. There is no
        expectation that a manager would handle new terms without
        specific knowledge in advance.
        """
        # As we take a copy, the default of the shared
        # dict isn't dangerous.
        # pylint: disable=dangerous-default-value
        self.__terminology = dict(terminology)
        self.__updateTerminology(manager)

    @auditApiCall("Terminology")
    def replaceTerms(self, sourceStr):
        """
        Substitutes any valid terminology tokens in the input string
        with those appropriate to the current Manager. These tokens are
        as per python format convention, using the constants defined in
        @ref openassetio.hostApi.terminology under kTerm_*. For
        example:

          @li "{publish} to {manager}..."

        @warning Escaping brace literals with `{{` is not currently
        supported.

        @param sourceStr a string to substitute.

        @return str The input string with all applicable terms
        substituted, any remaining braces ({}) will be removed.
        """
        try:
            # Make sure we dont abort if there is an unknown string
            sourceStr = sourceStr.format(**self.__terminology)
        except KeyError:
            pass
        return sourceStr.replace("{", "").replace("}", "")

    @auditApiCall("Terminology")
    def term(self, key, default=""):
        """
        Returns the term corresponding to the supplied key, @ref
        openassetio.hostApi.terminology under kTerm_*

        @return str or the supplied default if the key is unknown.
        """
        return self.__terminology.get(key, default)

    def __updateTerminology(self, manager):

        # Get any custom strings from the manager that we should use in the UI,
        # this is to allow a consistent terminology across implementations of a
        # specific asset management system.
        manager.updateTerminology(self.__terminology)
        self.__terminology[kTerm_Manager] = manager.displayName()
