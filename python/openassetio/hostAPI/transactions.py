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
@namespace openassetio.hostAPI.transactions
This module provides convenience functionality for a @ref host to aid
working managing transactions when interacting with a @ref manager.
"""

from .._core.audit import auditApiCall
from .._core.debug import debugApiCall, Debuggable


__all__ = ['TransactionCoordinator', 'ScopedActionGroup']


class TransactionCoordinator(Debuggable):
    """
    The TransactionCoordinator simplifies Host implementation by
    providing a stack-like interface around the simple start/stop/cancel
    transaction API exposed by the ManagerInterface.
    """

    def __init__(self, manager):

        self.__manager = manager
        self._debugLogFn = manager._debugLogFn

    def manager(self):
        """
        @returns the Manager for which transactions are being managed.
        """
        return self.__manager

    ## @name Action Group Management
    ## @ref action_group Management.
    ## Manages an action group stack within the Context, which in turn takes care
    ## of correctly calling the ManagerInterface's transactional API.
    ## @{

    @debugApiCall
    @auditApiCall("Transactions")
    def scopedActionGroup(self, context):
        """
        @return A python context manager that pushes an action group on
        creation, and pops it when the scope is exit. Use with a 'with'
        statement, to simplify implementing action groups in a host. for
        example:

        @code
        with transactionCoordinator.scopedActionGroup(context):
          for t in textures:
            publish(t)
        @endcode
        """
        return ScopedActionGroup(self, context)

    @debugApiCall
    @auditApiCall("Transactions")
    def pushActionGroup(self, context):
        """
        Push an ActionGroup onto the supplied Context. This will
        increase the depth by 1, and a @ref transaction started if
        necessary.

        @return int The new depth of the Action Group stack
        """
        if context.actionGroupDepth == 0:
            # pylint: disable=protected-access
            self.__manager._startTransaction(context.managerInterfaceState)

        context.actionGroupDepth += 1
        return context.actionGroupDepth

    @debugApiCall
    @auditApiCall("Transactions")
    def popActionGroup(self, context):
        """
        Pops an ActionGroup from the supplied Context. This will
        decrease the depth by 1 and the current @ref transaction will be
        finished if necessary.

        @return int The new depth of the Action Group stack

        @exception RuntimeError If pop is called before push (ie: the
        stack depth is 0)
        """
        if context.actionGroupDepth == 0:
            raise RuntimeError("Action group popped with none on the stack")

        context.actionGroupDepth -= 1
        if context.actionGroupDepth == 0:
            # pylint: disable=protected-access
            self.__manager._finishTransaction(context.managerInterfaceState)

        return context.actionGroupDepth

    @debugApiCall
    @auditApiCall("Transactions")
    def cancelActions(self, context):
        """
        Clears the current ActionGroup stack (if one has been started),
        cancelling the @ref transaction if one has been started.

        @return bool True if the current cancelled successfully and any
        actions performed since it began have been undone, or if there
        was nothing to cancel. Otherwise False - which indicates the
        Manager may not have been able to undo-unwind any actions that
        occurred since the first ActionGroup was pushed onto the stack.
        """
        status = True

        if context.actionGroupDepth == 0:
            return status

        # pylint: disable=protected-access
        status = self.__manager._cancelTransaction(context.managerInterfaceState)

        context.actionGroupDepth = 0

        return status

    @staticmethod
    def actionGroupDepth(context):
        """
        @return int The current ActionGroup depth in the context.
        @todo Should this even be public? Conceptually this is probably API-internal.
        """
        return context.actionGroupDepth

    ## @}

    ## @name State Distribution
    ## @ref stable_resolution_manager_state_distribution Management.
    ## In order to correlate a series of distributed tasks, the Manager's state
    ## held in a Context can be serialized, shared with other processes and
    ## restored. A common use of this in in distributed rendering scenarios, where
    ## it is desired to provide stable asset resolution over time.
    ## By distributing the Managers state token to each of job, the Manager can
    ## snapshot resolution at the time the originating Context was first created.
    ## @{

    @auditApiCall("Transactions")
    def freezeManagerState(self, context):
        """
        Returns a serialized representation of the @ref manager_state
        held in the supplied Context, so that it can be distributed to
        other processes/etc...

        @warning From this point, the context should not be used further
        without first thawing the state back into the context.

        @return str an ASCII compatible string

        @see @ref thawManagerState
        """
        ## @todo Ensure that other actions error after this point
        ## @todo Should this clear out the state/dept from the Context?
        # pylint: disable=protected-access
        token = self.__manager._freezeState(context.managerInterfaceState)
        return "%i_%s" % (context.actionGroupDepth, token)

    @auditApiCall("Transactions")
    def thawManagerState(self, token, context):
        """
        Restores the @ref manager_state in the supplied Context so that
        it represents the context as previously frozen.

        @param token str The string returned by @ref freezeManagerState

        @param context Context The context to restore the state into.

        @note It is perfectly legal to thaw the same context multiple
        times in parallel, as long as the ActionGroup depth is not
        changed - ie: push/pop/cancelActionGroup should not be called.
        This is because it quickly creates an incoherent state for the
        Manager.  The Host *must* guarantee that a given state has only
        been thawed to a single active Context before such actions are
        performed.

        @warning This call only handles the opaque @ref manager_state
        object, it does *not* restore other properties of the Context
        (ie: access/retention, etc...)
        """
        ## @todo Sanitize input
        depth, managerToken = token.split('_', 1)
        context.actionGroupDepth = int(depth)
        state = self.__manager._thawState(managerToken)  # pylint: disable=protected-access
        context.managerInterfaceState = state

    ## @}


class ScopedActionGroup(object):
    """
    A convenience class to push/pop an action group based on the
    lifetime of the object, useful when combined with a 'with'
    statement.
    """

    def __init__(self, transactionCoordinator, context, cancelOnException=True):

        super(ScopedActionGroup, self).__init__()
        self.cancelOnException = cancelOnException
        self.__transactionCoordinator = transactionCoordinator
        self.__context = context

    def __enter__(self):
        self.__transactionCoordinator.pushActionGroup(self.__context)

    def __exit__(self, exceptionType, exceptionValue, traceback):

        if exceptionType is not None and self.cancelOnException:
            self.__transactionCoordinator.cancelActions(self.__context)
        else:
            self.__transactionCoordinator.popActionGroup(self.__context)
