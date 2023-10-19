#
#   Copyright 2023 The Foundry Visionmongers Ltd
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
Tests for deprecated functionality.

All cases must have a link to the relevant GitHub issue in their
docstrings.
"""

# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring,import-outside-toplevel


import pytest


def test_renamed_kField_constants():
    """
    https://github.com/OpenAssetIO/OpenAssetIO/issues/998
    """
    from openassetio import constants

    assert constants.kField_SmallIcon == constants.kInfoKey_SmallIcon
    assert constants.kField_Icon == constants.kInfoKey_Icon
    assert (
        constants.kField_EntityReferencesMatchPrefix
        == constants.kInfoKey_EntityReferencesMatchPrefix
    )


def test_top_level_TraitsData_import():
    """
    https://github.com/OpenAssetIO/OpenAssetIO/issues/1127
    """
    from openassetio import trait, TraitsData

    assert TraitsData is trait.TraitsData


def test_top_level_exceptions_import():
    """
    https://github.com/OpenAssetIO/OpenAssetIO/issues/1071
    https://github.com/OpenAssetIO/OpenAssetIO/issues/1073
    """
    from openassetio import (
        BatchElementError,
        BatchElementException,
        UnknownBatchElementException,
        InvalidEntityReferenceBatchElementException,
        MalformedEntityReferenceBatchElementException,
        EntityAccessErrorBatchElementException,
        EntityResolutionErrorBatchElementException,
        InvalidPreflightHintBatchElementException,
        InvalidTraitSetBatchElementException,
        errors,
    )

    assert BatchElementError is errors.BatchElementError

    assert issubclass(BatchElementException, errors.BatchElementException)
    expected_message = "a message"
    an_error = BatchElementError(BatchElementError.ErrorCode.kEntityAccessError, expected_message)
    an_exception = BatchElementException(0, an_error)
    assert str(an_exception) == expected_message

    assert UnknownBatchElementException is errors.BatchElementException
    assert InvalidEntityReferenceBatchElementException is errors.BatchElementException
    assert MalformedEntityReferenceBatchElementException is errors.BatchElementException
    assert EntityAccessErrorBatchElementException is errors.BatchElementException
    assert EntityResolutionErrorBatchElementException is errors.BatchElementException
    assert InvalidPreflightHintBatchElementException is errors.BatchElementException
    assert InvalidTraitSetBatchElementException is errors.BatchElementException

    with pytest.warns(
        DeprecationWarning, match="The exceptions module has moved to openassetio.errors"
    ):
        from openassetio import exceptions

    assert exceptions.OpenAssetIOException is errors.OpenAssetIOException
    assert exceptions.UserCanceled
    assert exceptions.ManagerException
    assert exceptions.StateError
    assert exceptions.RetryableError
    assert exceptions.BaseEntityException
    assert exceptions.InvalidEntityReference
    assert exceptions.MalformedEntityReference
    assert exceptions.EntityResolutionError
    assert exceptions.BaseEntityInteractionError
    assert exceptions.PreflightError
    assert exceptions.RegistrationError
    assert exceptions.PluginError
