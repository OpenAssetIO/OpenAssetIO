#
#   Copyright 2013-2022 The Foundry Visionmongers Ltd
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
Tests for public API of the manager test harness.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring


import importlib
import inspect
import io
import os
import sys
from unittest import mock
from unittest.case import SkipTest
import uuid
import pytest

from openassetio import constants, EntityReference, errors
from openassetio.test.manager.harness import (
    executeSuite,
    fixturesFromPyFile,
    moduleFromFile,
    FixtureAugmentedTestCase,
)


#
# Tests
#


class Test_fixturesFromPyFile:
    def test_when_called_with_missing_path_then_raises_Exception(self):
        invalid_path = "/i/do/not/exist"
        with pytest.raises(errors.InputValidationException) as exc:
            fixturesFromPyFile(invalid_path)
        assert str(exc.value) == f"Unable to parse '{invalid_path}'"

    def test_when_called_with_non_python_file_then_raises_exception(self, tmpdir):
        text_file = tempfile_with_contents(tmpdir, ".txt", "Hello!")
        with pytest.raises(errors.InputValidationException) as exc:
            fixturesFromPyFile(text_file)
        assert str(exc.value) == f"Unable to parse '{text_file}'"

    def test_when_called_with_python_file_missing_fixtures_var_then_raises_exception(self, tmpdir):
        malformed = tempfile_with_contents(tmpdir, ".py", "cabbages = {}")
        with pytest.raises(errors.ConfigurationException) as exc:
            fixturesFromPyFile(malformed)
        assert str(exc.value) == f"Missing top-level 'fixtures' variable in '{malformed}'"

    def test_when_called_with_valid_path_then_returns_expected_fixture_dict(self, tmpdir):
        valid = tempfile_with_contents(
            tmpdir,
            ".py",
            inspect.cleandoc(
                """
                                from openassetio import constants
                                fixtures = {
                                    'reference_prefix_field':
                                        constants.kInfoKey_EntityReferencesMatchPrefix
                                }
                                """
            ),
        )
        expected_dict = {"reference_prefix_field": constants.kInfoKey_EntityReferencesMatchPrefix}
        assert fixturesFromPyFile(valid) == expected_dict


class Test_moduleFromFile:
    def test_when_called_with_missing_path_then_raises_Exception(self):
        invalid_path = "/i/do/not/exist"
        with pytest.raises(errors.InputValidationException) as exc:
            moduleFromFile(invalid_path)
        assert str(exc.value) == f"Unable to parse '{invalid_path}'"

    def test_when_called_with_non_python_file_then_raises_exception(self, tmpdir):
        text_file = tempfile_with_contents(tmpdir, ".txt", "Hello!")
        with pytest.raises(errors.InputValidationException) as exc:
            moduleFromFile(text_file)
        assert str(exc.value) == f"Unable to parse '{text_file}'"

    def test_when_called_with_valid_path_then_returns_expected_module(self, tmpdir):
        valid = tempfile_with_contents(
            tmpdir,
            ".py",
            inspect.cleandoc(
                """
                                from openassetio import constants
                                some_var = {
                                    'reference_prefix_field':
                                        constants.kInfoKey_EntityReferencesMatchPrefix
                                }
                                some_class = str
                                """
            ),
        )
        module = moduleFromFile(valid)
        assert module.some_var == {
            "reference_prefix_field": constants.kInfoKey_EntityReferencesMatchPrefix
        }
        assert module.some_class is str


class Test_executeSuite:
    def test_when_called_with_failing_module_then_false_is_returned(
        self, a_failing_tests_module, executeSuiteTests_fixtures
    ):
        assert executeSuite(a_failing_tests_module, executeSuiteTests_fixtures) is False

    def test_when_called_with_passing_module_then_true_is_returned(
        self, a_passing_tests_module, executeSuiteTests_fixtures
    ):
        assert executeSuite(a_passing_tests_module, executeSuiteTests_fixtures) is True

    def test_when_called_with_executeSuiteTests_module_then_all_tests_pass(
        self, executeSuiteTests_module, executeSuiteTests_fixtures
    ):
        assert executeSuite(executeSuiteTests_module, executeSuiteTests_fixtures) is True

    def test_when_called_with_extra_args_then_they_are_passed_to_unittest_main(
        self, monkeypatch, a_passing_tests_module, executeSuiteTests_fixtures
    ):
        dummyStderr = io.StringIO()
        monkeypatch.setattr(sys, "stderr", dummyStderr)
        executeSuite(a_passing_tests_module, executeSuiteTests_fixtures, ["-v"])
        assert "test_that_will_always_pass" in dummyStderr.getvalue()


class Test_FixtureAugmentedTestCase:
    def test_when_constructed_then_objects_are_exposed_via_protected_members(
        self, a_fixture_dict, a_locale, mock_manager
    ):
        case = FixtureAugmentedTestCase(a_fixture_dict, mock_manager, a_locale)
        # pylint: disable=protected-access
        assert case._fixtures == a_fixture_dict
        assert case._manager == mock_manager


class Test_FixtureAugmentedTestCase_createTestContext:
    def test_has_test_harness_locale(self, a_test_case):
        context = a_test_case.createTestContext()
        assert context.locale is a_test_case._locale  # pylint: disable=protected-access


class Test_FixtureAugmentedTestCase_assertIsStringKeyPrimitiveValueDict:
    def test_when_not_dict_then_fails(self, a_test_case):
        with pytest.raises(AssertionError):
            a_test_case.assertIsStringKeyPrimitiveValueDict("something")

    def test_when_dict_empty_then_passes(self, a_test_case):
        a_test_case.assertIsStringKeyPrimitiveValueDict({})

    def test_when_dict_ok_then_passes(self, a_test_case):
        a_test_case.assertIsStringKeyPrimitiveValueDict(
            {"k1": 1, "k2": 1.1, "k3": "v", "k4": True}
        )

    def test_when_dict_has_non_string_key_then_fails(self, a_test_case):
        with pytest.raises(AssertionError):
            a_test_case.assertIsStringKeyPrimitiveValueDict({1: 1})

    def test_when_dict_has_nested_dict_then_fails(self, a_test_case):
        with pytest.raises(AssertionError):
            a_test_case.assertIsStringKeyPrimitiveValueDict({"k": {}})

    def test_when_dict_has_None_then_fails(self, a_test_case):
        with pytest.raises(AssertionError):
            a_test_case.assertIsStringKeyPrimitiveValueDict({"k": None})

    def test_when_dict_has_object_then_fails(self, a_test_case):
        with pytest.raises(AssertionError):
            a_test_case.assertIsStringKeyPrimitiveValueDict({"k": object()})


class Test_FixtureAugmentedTestCase_assertValuesOfType:
    def test_when_list_empty_then_passes(self, a_test_case):
        a_test_case.assertValuesOfType([], int)

    def test_when_list_empty_and_none_allowed_then_passes(self, a_test_case):
        a_test_case.assertValuesOfType([], int, allowNone=True)

    def test_when_all_int_values_match_then_passes(self, a_test_case):
        a_test_case.assertValuesOfType([1, 2, 3], int)

    def test_when_all_str_values_match_then_passes(self, a_test_case):
        a_test_case.assertValuesOfType(["as", "they", "should"], str)

    def test_when_all_class_values_match_then_passes(self, a_test_case):
        import datetime  # pylint: disable=import-outside-toplevel

        values = [datetime.date.today() for x in range(3)]
        a_test_case.assertValuesOfType(values, datetime.date)

    def test_when_values_contain_none_then_fails(self, a_test_case):
        with pytest.raises(AssertionError):
            a_test_case.assertValuesOfType([1, None, 3], int)

    def test_when_values_contain_none_and_none_allowed_then_passes(self, a_test_case):
        a_test_case.assertValuesOfType([1, None, 3], int, allowNone=True)

    def test_when_called_with_tuple_then_passes(self, a_test_case):
        a_test_case.assertValuesOfType((1, 2, 3), int)

    def test_when_called_with_iterable_then_passes(self, a_test_case):
        a_test_case.assertValuesOfType(range(10), int)


class Test_FixtureAugmentedTestCase_requireEntityReferenceFixture:
    def test_when_fixture_present_then_returns_expected_value(self, a_test_case, mock_manager):
        required = "a_string"
        expected = EntityReference("mock://a")
        mock_manager.createEntityReference.return_value = expected

        try:
            assert a_test_case.requireEntityReferenceFixture(required) == expected
        except SkipTest:
            pytest.fail("Test should not be skipped")

        mock_manager.createEntityReference.assert_called_once_with("a")

    def test_when_invalid_reference_then_exception_propagates(self, a_test_case, mock_manager):
        required = "a_string"

        class StubException(Exception):
            pass

        mock_manager.createEntityReference.side_effect = StubException()

        with pytest.raises(StubException):
            assert a_test_case.requireEntityReferenceFixture(required)

    def test_when_fixture_missing_then_fails_test_with_expected_message(self, a_test_case):
        required = "missing_key"
        expected_message = "Required fixtures not found: missing_key"
        with pytest.raises(AssertionError, match=expected_message):
            try:
                a_test_case.requireEntityReferenceFixture(required)
            except SkipTest:
                pytest.fail("Test skipped not failed")

    def test_when_fixture_missing_and_skip_set_then_skips_test_with_expected_message(
        self, a_test_case
    ):
        required = "missing_key"
        expected_message = "Required fixtures not found: missing_key"
        with pytest.raises(SkipTest, match=expected_message):
            a_test_case.requireEntityReferenceFixture(required, skipTestIfMissing=True)


class Test_FixtureAugmentedTestCase_requireEntityReferencesFixture:
    def test_when_fixture_present_then_returns_expected_value(self, a_test_case, mock_manager):
        required = "a_list_of_strings"
        expected = [
            EntityReference("mock://b"),
            EntityReference("mock://c"),
        ]
        mock_manager.createEntityReference.side_effect = expected

        try:
            assert a_test_case.requireEntityReferencesFixture(required) == expected
        except SkipTest:
            pytest.fail("Test should not be skipped")

        mock_manager.createEntityReference.assert_has_calls([mock.call("b"), mock.call("c")])

    def test_when_invalid_reference_then_exception_propagates(self, a_test_case, mock_manager):
        required = "a_list_of_strings"

        class StubException(Exception):
            pass

        mock_manager.createEntityReference.side_effect = StubException()

        with pytest.raises(StubException):
            assert a_test_case.requireEntityReferencesFixture(required)

    def test_when_fixture_missing_then_fails_test_with_expected_message(self, a_test_case):
        required = "missing_key"
        expected_message = "Required fixtures not found: missing_key"
        with pytest.raises(AssertionError, match=expected_message):
            try:
                a_test_case.requireEntityReferencesFixture(required)
            except SkipTest:
                pytest.fail("Test skipped not failed")

    def test_when_fixture_missing_and_skip_set_then_skips_test_with_expected_message(
        self, a_test_case
    ):
        required = "missing_key"
        expected_message = "Required fixtures not found: missing_key"
        with pytest.raises(SkipTest, match=expected_message):
            a_test_case.requireEntityReferencesFixture(required, skipTestIfMissing=True)


class Test_FixtureAugmentedTestCase_requireFixtures:
    def test_when_fixtures_present_then_returns_expected_values(self, a_test_case):
        required = ("key1", "key2")
        # pylint: disable=protected-access
        expected = [a_test_case._fixtures[name] for name in required]
        try:
            assert a_test_case.requireFixtures(required) == expected
        except SkipTest:
            pytest.fail("Test incorrectly skipped")

    def test_when_fixtures_missing_then_fails_test_with_expected_message(self, a_test_case):
        required = ("key2", "key4")
        expected_message = "Required fixtures not found: key4"
        with pytest.raises(AssertionError, match=expected_message):
            try:
                a_test_case.requireFixtures(required)
            except SkipTest:
                pytest.fail("Test skipped not failed")

    def test_when_fixtures_missing_and_skip_set_then_skips_test_with_expected_message(
        self, a_test_case
    ):
        required = ("key1", "key3", "key5")
        expected_message = "Required fixtures not found: key3, key5"
        with pytest.raises(SkipTest, match=expected_message):
            a_test_case.requireFixtures(required, skipTestIfMissing=True)


class Test_FixtureAugmentedTestCase_collectRequiredFixtures:
    def test_when_fixtures_present_then_sets_expected_values(self, a_test_case):
        required = ("key1", "key2")
        try:
            a_test_case.collectRequiredFixtures(required)
        except SkipTest:
            pytest.fail("Test incorrectly skipped")
        for key in required:
            # pylint: disable=protected-access
            assert getattr(a_test_case, key, a_test_case._fixtures[key])

    def test_when_fixtures_missing_then_fails_test_with_expected_message(self, a_test_case):
        required = ("key2", "key4")
        expected_message = "Required fixtures not found: key4"
        with pytest.raises(AssertionError, match=expected_message):
            try:
                a_test_case.collectRequiredFixtures(required)
            except SkipTest:
                pytest.fail("Test skipped not failed")
        for key in required:
            assert not hasattr(self, key)

    def test_when_fixtures_missing_and_skip_set_then_skips_test_and_no_values_set(
        self, a_test_case
    ):
        required = ("key1", "key3", "key5")
        expected_message = "Required fixtures not found: key3, key5"
        with pytest.raises(SkipTest, match=expected_message):
            a_test_case.collectRequiredFixtures(required, skipTestIfMissing=True)
        for key in required:
            assert not hasattr(self, key)


class Test_FixtureAugmentedTestCase_requireFixture:
    def test_when_fixture_present_then_returns_expected_value(self, a_test_case):
        required = "key1"
        # pylint: disable=protected-access
        expected = a_test_case._fixtures[required]
        try:
            assert a_test_case.requireFixture(required) == expected
        except SkipTest:
            pytest.fail("Test should not be skipped")

    def test_when_fixture_missing_then_fails_test_with_expected_message(self, a_test_case):
        required = "key4"
        expected_message = "Required fixtures not found: key4"
        with pytest.raises(AssertionError, match=expected_message):
            try:
                a_test_case.requireFixture(required)
            except SkipTest:
                pytest.fail("Test skipped not failed")

    def test_when_fixture_missing_and_skip_set_then_skips_test_with_expected_message(
        self, a_test_case
    ):
        required = "key5"
        expected_message = "Required fixtures not found: key5"
        with pytest.raises(SkipTest, match=expected_message):
            a_test_case.requireFixture(required, skipTestIfMissing=True)


class Test_FixtureAugmentedTestCase_collectRequiredFixture:
    def test_when_fixture_present_then_sets_expected_value(self, a_test_case):
        required = "key1"
        a_test_case.collectRequiredFixture(required)
        # pylint: disable=protected-access
        assert getattr(a_test_case, required, a_test_case._fixtures[required])

    def test_when_fixture_missing_then_fails_test_with_expected_message(self, a_test_case):
        required = "key4"
        expected_message = "Required fixtures not found: key4"
        with pytest.raises(AssertionError, match=expected_message):
            try:
                a_test_case.collectRequiredFixture(required)
            except SkipTest:
                pytest.fail("Test skipped not failed")
        assert not hasattr(self, required)

    def test_when_fixture_missing_and_skip_set_then_skips_test_and_no_values_set(
        self, a_test_case
    ):
        required = "key5"
        expected_message = "Required fixtures not found: key5"
        with pytest.raises(SkipTest, match=expected_message):
            a_test_case.collectRequiredFixture(required, skipTestIfMissing=True)
        assert not hasattr(self, required)


#
# Fixtures
#


@pytest.fixture
def a_passing_tests_module(resources_dir):
    """
    Returns a test suite that always passes.
    """
    module_path = os.path.join(resources_dir, "suite_alwaysPass.py")
    return suite_module(module_path)


@pytest.fixture
def a_failing_tests_module(resources_dir):
    """
    Returns a test suite that always fails.
    """
    module_path = os.path.join(resources_dir, "suite_alwaysFail.py")
    return suite_module(module_path)


@pytest.fixture
def executeSuiteTests_module(resources_dir):
    """
    Returns the test suite to validate the executeSuiteTests method.
    """
    module_path = os.path.join(resources_dir, "suite_executeSuiteTests.py")
    return suite_module(module_path)


@pytest.fixture
def executeSuiteTests_fixtures(resources_dir):
    """
    Returns the fixtues for the executeSuiteTests suite.
    """
    fixtures_path = os.path.join(resources_dir, "fixtures_executeSuiteTests.py")
    return fixturesFromPyFile(fixtures_path)


@pytest.fixture
def some_case_fixtures():
    return {"key1": 1, "key2": "2", "a_string": "a", "a_list_of_strings": ["b", "c"]}


@pytest.fixture
def a_test_case(some_case_fixtures, mock_manager, a_locale):
    return FixtureAugmentedTestCase(some_case_fixtures, mock_manager, a_locale)


#
# Helpers
#


def suite_module(module_path):
    """
    Loads and returns the specified test suite module
    """
    # Just load it directly, to save faffing around with sys.path
    spec = importlib.util.spec_from_file_location("tests", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tempfile_with_contents(tmpdir, suffix, contents):
    """
    Returns a uniquely named temporary file, created in the specified
    dir, with the supplied contents.

    It is suggested that the caller makes use of the pytest
    tmpdir fixture as the first parameter, which provides a life-time
    managed, test-case-specific directory.

    See: https://docs.pytest.org/en/6.2.x/tmpdir.html

    @param tmpdir `pathlib.Path` An existing directory to create the
      uniquely named file within.
    @param suffix `str` The filename suffix to append to the unique
      component, e.g. an extension.
    @param contents `str` The contents of the file.

    @return `pathlib.Path` The path to the newly created file.
    """
    # We used to return a tempfile.NamedTemporaryFile here, and you
    # could use this method as a context manager. Sadly, Windows only
    # allows a single open handle for any file at one time. This meant
    # that any other code that tried to re-open the file whilst the
    # context manager was alive (eg: fixturesFromPyFile) would be
    # denied [Errno 13].

    # We can't guarantee that this dir hasn't been used in a previous
    # call, so make sure the filename is unique anyway.
    path = tmpdir / f"{uuid.uuid4().hex}{suffix}"
    with open(path, "wb") as tmp_file:
        tmp_file.write(contents.encode())
        tmp_file.flush()
    return path
