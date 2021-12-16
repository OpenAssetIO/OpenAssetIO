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
Defines exceptions used in the OpenAssetIO codebase.
@todo [tc] Should these all live here, or in their respective homes
eg: pluginSystem, ManagerInterface, etc.
"""


class OpenAssetIOException(RuntimeError):
    """
    The OpenAssetIOException class should be used for all exceptions raise by
    Managers and any API-related exceptions raised in a Host. These
    exceptions are guaranteed to properly bridge across the C plugin
    divide...
    """


class UserCanceled(OpenAssetIOException):
    """
    Thrown by the progress mechanism to interrupt execution whenever the
    user cancels an action (perhaps using an on-screen button).
    """

    def __str__(self):
        return "Operation Canceled"


##
# @name Entity related Exceptions
#
## @{

class BaseEntityException(OpenAssetIOException):
    """
    A base Exception for any @ref entity related errors to ensure
    consistent presentation and encapsulation of the associated @ref
    entity_reference.
    """

    def __init__(self, message, entityReference=None):
        """
        @param message str, The message of the exception.

        @param entityReference str, The entity reference associated with
        the error. This should be provided wherever known, and will be
        printed along with the message in any traceback/etc... As such,
        there is no need to embedded the entity reference in the message
        when using this exception type.
        """
        OpenAssetIOException.__init__(self, message)
        self.ref = entityReference

    def __str__(self):
        string = OpenAssetIOException.__str__(self)
        return "%s (%s)" % (string, self.ref)


class InvalidEntityReference(BaseEntityException):
    """
    Thrown whenever an Entity-based action is performed on a mal-formed
    or unrecognized @ref entity_reference.
    """

    def __init__(self, message="Invalid Entity Reference", entityReference=None):
        super(InvalidEntityReference, self).__init__(message, entityReference)


class EntityResolutionError(BaseEntityException):
    """
    Thrown during @ref entity resolution,  if the Entity is valid, but
    has no meaningful @ref primary_string, or it can't be retrieved for
    some other reason. It is also used during version finalisation and
    any other entity-based operations on a valid @ref entity_reference
    that fail for some reason.
    """

    def __init__(self, message="Error resolving entity", entityReference=None):
        super(EntityResolutionError, self).__init__(message, entityReference)


class BaseEntityInteractionError(BaseEntityException):
    """
    A base class for errors relating to entity-centric actions.
    """


class PreflightError(BaseEntityInteractionError):
    """
    Thrown to represent some error during pre-flight that isn't due to
    any specific of the @ref entity_reference itself.
    """


class RegistrationError(BaseEntityInteractionError):
    """
    Thrown to represent some error during registration that isn't due to
    any specific of the @ref entity_reference itself.
    """


## @}


class ManagerError(OpenAssetIOException):
    A base class for exceptions relating to, or raised by a manager.
    """
    """


class StateError(OpenAssetIOException):
    """
    Thrown by managers in error situations relating to the
    managerInterfaceState object.
    """


class RetryableError(OpenAssetIOException):
    """
    Thrown by managers in error situations that can be safely retried
    with idempotent behavior.
    """


class PluginError(OpenAssetIOException):
    """
    Thrown by the plugin system in relation to errors encountered
    during the loading/initialization of plugins.
    """
