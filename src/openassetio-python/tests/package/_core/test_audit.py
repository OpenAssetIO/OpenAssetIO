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
Minimal tests of the core API auditing functionality. These tests are
left fairly basic as this aspect of the API is subject to significant
change when moved to C++. This hopefully is enough to check that it
works at a basic level.
"""

import os

import pytest


# pylint: disable=invalid-name
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-class-docstring,missing-function-docstring


audit_env_var_name = "OPENASSETIO_AUDIT"
audit_args_capture_env_var_name = "OPENASSETIO_AUDIT_ARGS"


@pytest.fixture(autouse=True)
def always_unload_openassetio_modules(
    unload_openassetio_modules,  # pylint: disable=unused-argument
):
    """
    Removes openassetio modules from the sys.modules cache to
    ensure we have a clean module state for each test.
    """


class Test_global_toggles:
    def test_when_imported_with_no_env_set_then_auditing_is_disabled(self, monkeypatch):

        if audit_env_var_name in os.environ:
            monkeypatch.delenv(audit_env_var_name)

        from openassetio._core import audit

        assert audit.auditCalls is False

    def test_when_imported_with_env_var_set_to_zero_then_auditing_is_disabled(self, monkeypatch):

        monkeypatch.setenv(audit_env_var_name, "0")

        from openassetio._core import audit

        assert audit.auditCalls is False

    def test_when_imported_with_env_var_set_to_not_zero_then_auditing_is_enabled(
        self, monkeypatch
    ):

        monkeypatch.setenv(audit_env_var_name, "1")

        from openassetio._core import audit

        assert audit.auditCalls is True

    def test_when_imported_with_env_var_empty_then_auditing_is_enabled(self, monkeypatch):

        monkeypatch.setenv(audit_env_var_name, "")

        from openassetio._core import audit

        assert audit.auditCalls is True

    def test_when_imported_with_no_env_set_then_args_capture_is_disabled(self, monkeypatch):

        if audit_args_capture_env_var_name in os.environ:
            monkeypatch.delenv(audit_args_capture_env_var_name)

        from openassetio._core import audit

        assert audit.captureArgs is False

    def test_when_imported_with_env_var_set_to_zero_then_args_capture_is_disabled(
        self, monkeypatch
    ):

        monkeypatch.setenv(audit_args_capture_env_var_name, "0")

        from openassetio._core import audit

        assert audit.captureArgs is False

    def test_when_imported_with_env_var_set_to_not_zero_then_args_capture_is_enabled(
        self, monkeypatch
    ):

        monkeypatch.setenv(audit_args_capture_env_var_name, "1")

        from openassetio._core import audit

        assert audit.captureArgs is True

    def test_when_imported_with_env_var_empty_then_args_capture_is_enabled(self, monkeypatch):

        monkeypatch.setenv(audit_args_capture_env_var_name, "")

        from openassetio._core import audit

        assert audit.captureArgs is True


class Test_singleton_access:
    def test_when_called_multiple_times_then_returns_the_same_object(self):
        from openassetio._core import audit

        the_auditor = audit.auditor()
        assert audit.auditor() is the_auditor


class Test_auditing:
    def test_when_decorator_applied_usage_is_captured(self):
        from openassetio._core import audit

        audit.auditCalls = True

        @audit.auditCall
        def a_method(an_arg):
            return an_arg

        a_method(1)
        a_method("cat")

        assert (
            audit.auditor().sprintCoverage()
            == """Coverage:

  function (2)
    a_method (2)
"""
        )

    def test_when_api_decorator_applied_usage_and_args_are_captured(self):
        from openassetio._core import audit

        audit.auditCalls = True
        audit.captureArgs = True

        @audit.auditApiCall(group="test", static=True)
        def a_method(an_arg):
            return an_arg

        a_method(1)
        a_method("cat")
        a_method(["a", "list"])
        a_method(object)

        assert (
            audit.auditor().sprintCoverage()
            == """Coverage:

  function (4)
    a_method (4)
        ((1,), {})
        (('cat',), {})
        ((['a', 'list'],), {})
        ((<class 'object'>,), {})


Groups:

  test:
    a_method (4)

"""
        )
