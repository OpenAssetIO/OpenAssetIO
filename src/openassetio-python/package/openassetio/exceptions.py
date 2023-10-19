#
#   Copyright 2013-2023 The Foundry Visionmongers Ltd
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
@namespace openassetio.exceptions
Defines exceptions used in the OpenAssetIO codebase.

@deprecated See @ref fqref{openassetio.errors}
"""
import warnings


from openassetio import errors as _errors

OpenAssetIOException = _errors.OpenAssetIOException

del _errors

warnings.warn("The exceptions module has moved to openassetio.errors", DeprecationWarning)


class UserCanceled(OpenAssetIOException):
    """
    Thrown by the progress mechanism to interrupt execution whenever the
    user cancels an action (perhaps using an on-screen button).

    @unstable
    """

    def __str__(self):
        return "Operation Canceled"


##
# @name Manager related Exceptions
#
## @{


class ManagerException(OpenAssetIOException):
    """
    A base class for exceptions relating to, or raised by a manager.

    @unstable
    """


class StateError(ManagerException):
    """
    Thrown by managers in error situations relating to the
    managerState object.

    @unstable
    """


class RetryableError(ManagerException):
    """
    Thrown by managers in error situations that can be safely retried
    with idempotent behavior.

    @unstable
    """


## @}


##
# @name Entity related Exceptions
#
## @{


class BaseEntityException(ManagerException):
    """
    A base Exception for any @ref entity related errors to ensure
    consistent presentation and encapsulation of the associated @ref
    entity_reference.

    @unstable
    """

    def __init__(self, message, entityReference=None):
        """
        @param message str, The message of the exception.

        @param entityReference @fqref{EntityReference} "EntityReference"
        The entity reference associated with the error. This should be
        provided wherever known, and will be printed along with the
        message in any traceback/etc... As such, there is no need to
        embedded the entity reference in the message when using this
        exception type.
        """
        super(BaseEntityException, self).__init__(message)
        self.ref = entityReference

    def __str__(self):
        string = OpenAssetIOException.__str__(self)
        return "%s (%s)" % (string, self.ref)


class InvalidEntityReference(BaseEntityException):
    """
    Thrown whenever an Entity-based action is performed on an
    unrecognized @ref entity_reference.

    @unstable
    """

    def __init__(self, message="Invalid Entity Reference", entityReference=None):
        super(InvalidEntityReference, self).__init__(message, entityReference)


class MalformedEntityReference(BaseEntityException):
    """
    Thrown whenever an Entity-based action is performed on a
    malformed @ref entity_reference.

    @unstable
    """

    def __init__(self, message="Malformed Entity Reference", entityReference=None):
        super(MalformedEntityReference, self).__init__(message, entityReference)


class EntityResolutionError(BaseEntityException):
    """
    Thrown during @ref entity resolution,  if the Entity is valid, but
    has no meaningful data to be resolved, or it can't be retrieved for
    some other reason. It is also used during version finalisation and
    any other entity-based operations on a valid @ref entity_reference
    that fail for some reason.

    @unstable
    """

    def __init__(self, message="Error resolving entity", entityReference=None):
        super(EntityResolutionError, self).__init__(message, entityReference)


class BaseEntityInteractionError(BaseEntityException):
    """
    A base class for errors relating to entity-centric actions.

    @unstable
    """


class PreflightError(BaseEntityInteractionError):
    """
    Thrown to represent some error during pre-flight that isn't due to
    any specific of the @ref entity_reference itself.

    @unstable
    """


class RegistrationError(BaseEntityInteractionError):
    """
    Thrown to represent some error during registration that isn't due to
    any specific of the @ref entity_reference itself.

    @unstable
    """


## @}


class PluginError(OpenAssetIOException):
    """
    Thrown by the plugin system in relation to errors encountered
    during the loading/initialization of plugins.

    @unstable
    """
