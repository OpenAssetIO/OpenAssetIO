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
Tests that cover the openassetio.hostApi.EntityReferencePager wrapper class.
"""

# pylint: disable=invalid-name,redefined-outer-name
# pylint: disable=missing-class-docstring,missing-function-docstring
import weakref

import pytest

from openassetio import EntityReference
from openassetio.hostApi import EntityReferencePager
from openassetio.log import LoggerInterface
from openassetio.managerApi import EntityReferencePagerInterface


class Test_EntityReferencePager_init:
    def test_when_constructed_with_EntityReferencePagerInterface_as_None_then_raises_TypeError(
        self, a_host_session
    ):
        # Check the message is both helpful and that the bindings
        # were loaded in the correct order such that types are
        # described correctly.
        matchExpr = (
            r".+The following argument types are supported:[^(]+"
            r"EntityReferencePager\([^,]+managerApi.EntityReferencePagerInterface,[^,]+"
            r"managerApi.HostSession.+"
        )

        with pytest.raises(TypeError, match=matchExpr):
            EntityReferencePager(None, a_host_session)


class Test_EntityReferencePager_next:
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self, an_entity_reference_pager, mock_entity_reference_pager_interface, a_host_session
    ):
        method = mock_entity_reference_pager_interface.mock.next
        an_entity_reference_pager.next()
        method.assert_called_once_with(a_host_session)


class Test_EntityReferencePager_hasNext:
    @pytest.mark.parametrize("expected", (True, False))
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        an_entity_reference_pager,
        mock_entity_reference_pager_interface,
        a_host_session,
        expected,
    ):
        method = mock_entity_reference_pager_interface.mock.hasNext
        method.return_value = expected

        assert an_entity_reference_pager.hasNext() == expected
        method.assert_called_once_with(a_host_session)


class Test_EntityReferencePager_get:
    @pytest.mark.parametrize(
        "expected",
        (
            [],
            [EntityReference("first 🌱")],
            [EntityReference("second 🌿"), EntityReference("third 🌲")],
        ),
    )
    def test_wraps_the_corresponding_method_of_the_held_interface(
        self,
        an_entity_reference_pager,
        mock_entity_reference_pager_interface,
        a_host_session,
        expected,
    ):
        method = mock_entity_reference_pager_interface.mock.get
        method.return_value = expected

        assert an_entity_reference_pager.get() == expected
        method.assert_called_once_with(a_host_session)


class FakeEntityReferencePagerInterface(EntityReferencePagerInterface):
    """
    Throwaway pager interface def, so we can create a temporary
    interface intended to fall out of scope.

    See `test_when_EntityReferencePager_holding_interface_loses_scope_then_scope_is_destructed`.
    """

    def __init__(self):
        EntityReferencePagerInterface.__init__(self)

    def hasNext(self, _hostSession):
        return False

    def get(self, _hostSession):
        return []

    def next(self, _hostSession):
        pass


class Test_EntityReferencePager_destruction:
    def test_when_EntityReferencePager_holding_interface_loses_scope_then_scope_is_destructed(
        self, a_host_session
    ):
        weak_interface_ref = None

        def makePagerInScope():
            pagerInterface = FakeEntityReferencePagerInterface()

            nonlocal weak_interface_ref
            weak_interface_ref = weakref.ref(pagerInterface)

            _pager = EntityReferencePager(pagerInterface, a_host_session)
            del pagerInterface
            assert weak_interface_ref() is not None
            # The pager is still in scope until this method exits

        makePagerInScope()
        # Once method exits, pager falls out of scope, and interface is
        # destroyed.
        assert weak_interface_ref() is None  # pylint: disable=not-callable

    def test_when_EntityReferencePager_destructed_close_is_called(
        self, a_host_session, mock_entity_reference_pager_interface
    ):
        pager = EntityReferencePager(mock_entity_reference_pager_interface, a_host_session)
        del pager
        mock_entity_reference_pager_interface.mock.close.assert_called_once_with(a_host_session)

    def test_when_exception_thrown_in_close_exception_is_caught_and_logged(
        self, a_host_session, mock_entity_reference_pager_interface, mock_logger
    ):
        exception_what = "Mocked exception"

        def raise_exception(self):
            # pylint: disable=broad-exception-raised
            raise Exception(exception_what)

        mock_entity_reference_pager_interface.mock.close.side_effect = raise_exception

        pager = EntityReferencePager(mock_entity_reference_pager_interface, a_host_session)
        del pager
        mock_entity_reference_pager_interface.mock.close.assert_called_once_with(a_host_session)
        args, _kwargs = mock_logger.mock.log.call_args

        # The .what() of the exception comes with a lot of additional
        # text about call location that would be overly verbose to check
        assert LoggerInterface.Severity.kError == args[0]
        assert exception_what in args[1]


@pytest.fixture
def an_entity_reference_pager(mock_entity_reference_pager_interface, a_host_session):
    return EntityReferencePager(mock_entity_reference_pager_interface, a_host_session)
