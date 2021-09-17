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

from .._core.audit import auditApiCall

## @namespace FnAssetAPI.localization
#
# The localization mechanism allows Managers to customise terminology
# used within the host application.
# The @ref FnAssetAPI.localization.Localizer class allows for
# more efficitent access to string localization during a Host session,
# and for the host to provide additional terminology keys.
#

## @name Localisation dict keys
## @{

kLocalizationKey_Asset = 'asset'
kLocalizationKey_Assets = 'assets'
kLocalizationKey_Manager = 'manager'
kLocalizationKey_Publish = 'publish'
kLocalizationKey_Publishing = 'publishing'
kLocalizationKey_Published = 'published'
kLocalizationKey_Shot = 'shot'
kLocalizationKey_Shots = 'shots'

## @}

## Default terminology for the API.
# Hosts may choose to add aditional terminiology keys when
# construting a @ref FnAssetAPi.localization.Localizer,
# but there is no expectation that any given manager would
# customise keys other than the defaultTerminology.
defaultTerminology = {
    kLocalizationKey_Asset: 'Asset',
    kLocalizationKey_Assets: 'Assets',
    kLocalizationKey_Manager: 'Asset Manager',
    kLocalizationKey_Publish: 'Publish',
    kLocalizationKey_Publishing: 'Publishing',
    kLocalizationKey_Published: 'Published',
    kLocalizationKey_Shot: 'Shot',
    kLocalizationKey_Shots: 'Shots',
}

class Localizer :

    def __init__(self, manager, terminology=defaultTerminology):
        """

        Constructs a new Localizer using terminology overrides defined
        by the supplied Manager. The manager is queried during construction
        and it's results cached for the lifetime of the Localizer.

        @param terminology A dict of terms that will be localized by
        this instance. If left unspecified, the default API terminology
        will be used. Hosts may take a copy of this dictionary and append
        to it before passing to the Localizer to allow managers to customise
        additional host-specific terms. There is no expectation that a manager
        would handle new terms without specific knowledge in advance.

        """
        self.__terminology = dict(terminology)
        self.__localize(manager)

    @auditApiCall("Localization")
    def localizeString(self, sourceStr):
        """

        Substitutes any valid localizable tokens in the input string with those
        appropriate to the current Manager. These tokens are as per python format
        convention, using the constants defined in @ref FnAssetAPI.constants under
        kLocalizationKey_*. For example:

          @li "{publish} to {manager}..."

        @important Escaping brace literals with `{{` is not currently supported.

        @param sourceStr a UTF-8 ASCII string to localize.

        @return str The input string with all applicable terms localized, any remaining
        braces ({}) will be removed.

        """
        try:
            # Make sure we dont abort if there is an unknown string
            sourceStr = sourceStr.format(**self.__terminology)
        except KeyError:
            pass
        return sourceStr.replace("{", "").replace("}", "")


    @auditApiCall("Localization")
    def getLocalizedString(self, key, default=''):
        """

        Returns the localized version of the supplied key, @ref FnAssetAPI.constants
        under kLocalizationKey_*

        @return str or the supplied default if the key is unknown.

        """
        return self.__terminology.get(key, default)


    def __localize(self, manager):

        # Get any custom strings from the manager that we should use in the UI,
        # this is to allow a consistent terminology across implementations of a
        # specific asset management system.
        manager.localizeStrings(self.__terminology)
        self.__terminology[kLocalizationKey_Manager] = manager.getDisplayName()