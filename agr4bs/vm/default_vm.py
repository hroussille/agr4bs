
"""
    DefaultVM file class implementation
"""

from ast import Add
from enum import Enum

from agr4bs.agents.internal_agent import InternalAgentDeployement
from .execution_context import ExecutionContext
from ..state import State, Account, Receipt, StateChange
from ..state import CreateAccount, AddBalance, RemoveBalance, IncrementAccountNonce
from ..blockchain import Transaction
from ..agents import InternalAgent, InternalAgentCalldata, InternalAgentResponse


class TransactionType(Enum):
    TRANSFER = "TRANSFER"
    CALL = "CALL"
    DEPLOYEMENT = "DEPLOYEMENT"


class VM:

    """
        Default Virtual Machine class implementation

        The virtual machine process tx and executes them on a mirror State
        it should be able to process :

        - ExternalAgent to ExternalAgent transactions
        - ExternalAgent to InternalAgent transactions
        - InternalAgent to InternalAgent transactions
        - InternalAgent to ExternalAgent transactions
    """

    def __init__(self):
        pass

    @staticmethod
    def _get_transaction_type(state: State, tx: Transaction):

        if tx.to is None and len(tx.payload.data) > 0:
            return TransactionType.DEPLOYEMENT

        if state.get_account_internal_agent(tx.to) is None:
            return TransactionType.TRANSFER

        if state.get_account_internal_agent(tx.to) is not None:
            return TransactionType.CALL

    @staticmethod
    def _get_transfer_changes(ctx: ExecutionContext, create: bool = True):

        changes = []

        recipient = ctx.state.get_account(ctx.to)

        if recipient is None and create is True:
            changes.append(CreateAccount(Account(ctx.to)))

        if ctx.value > 0:
            changes.append(RemoveBalance(ctx.caller, ctx.value))
            changes.append(AddBalance(ctx.to, ctx.value))

        return changes

    @staticmethod
    def _do_deployement(state: State, tx: Transaction):
        pre_changes = []
        raw = tx.payload.data
        deployement = InternalAgentDeployement.from_serialized(raw)
        agent: InternalAgent = deployement.agent()
        account = Account(agent.name, 0, 0, agent)

        # Populate pre_changes with the account creation
        # and the value transfer if any
        pre_changes.append(CreateAccount(account))
        pre_changes += VM._do_transfer(state,
                                       tx.origin, tx.to, tx.value, create=False)
        state.apply_batch_state_change(pre_changes)

        callee: InternalAgent = state.get_account_internal_agent(tx.to)
        calldata = deployement.constructor_calldata

        context: ExecutionContext = ExecutionContext(
            tx.origin, tx.origin, tx.value, 0, state, VM)
        (response, call_changes) = callee.entry_point(calldata, context)

    def _do_call(self, state: State, tx: Transaction):
        raw = tx.payload.data
        calldata = InternalAgentCalldata.from_serialized(raw)

        pre_changes = VM._do_transfer(state, tx.origin, tx.to, tx.value)

        state.apply_batch_state_change(pre_changes)
        callee: InternalAgent = state.get_account_internal_agent(tx.to)

        context: ExecutionContext = ExecutionContext(
            tx.origin, tx.origin, tx.value, 0, state, self)
        (response, call_changes) = callee.entry_point(calldata, context)

        if response.reverted is True:
            return Receipt(tx.hash, [], response.reverted, response.revert_reason)

        changes = pre_changes + call_changes

        return Receipt(tx.hash, changes, False, "")

    @staticmethod
    def process_tx_new(state: State, tx: Transaction) -> Receipt:
        tx_type = VM._get_transaction_type(state, tx)
        context = VM._get_context_from_tx(tx)

        state.apply_state_change(IncrementAccountNonce(tx.origin))

        if tx_type == TransactionType.TRANSFER:
            changes = VM._transfer_changes()
        elif tx_type == TransactionType.DEPLOYEMENT:
            changes = VM._deployement_changes()
        elif tx_type == TransactionType.CALL:
            changes = VM._call_changes()

    def process_tx(self, state: State, tx: Transaction) -> Receipt:
        """
            Process a tx according to the given State and returns the tx Receipt
        """

        reverted = False
        revert_reason = ""

        pre_changes = [IncrementAccountNonce(tx.origin)]
        changes = []

        if tx.value > 0 and tx.to is not None:

            if state.get_account(tx.to) is None:
                pre_changes.append(CreateAccount(Account(tx.to)))

            pre_changes.append(RemoveBalance(tx.origin, tx.value))
            pre_changes.append(AddBalance(tx.to, tx.value))

        state.apply_batch_state_change(pre_changes)

        recipient_account = state.get_account(tx.to)

        if recipient_account is not None and recipient_account.internal_agent is not None:
            calldata = InternalAgentCalldata.from_serialized(tx.payload.data)
            response, internal_changes = self._top_level_internal_call(
                state, tx.origin, tx.to, tx.value, calldata)

            if response.reverted is False:
                changes = changes + internal_changes

            reverted = response.reverted
            revert_reason = response.revert_reason

        return Receipt(tx.hash, pre_changes + changes, reverted, revert_reason)

    def _top_level_internal_call(self, state: State, _from: str, to: str, value: int, calldata: InternalAgentCalldata) -> tuple[InternalAgentResponse, list[StateChange]]:
        agent: InternalAgent = state.get_account_internal_agent(to)
        context: ExecutionContext = ExecutionContext(
            _from, _from, value, 0, state, self)
        response, changes = agent.entry_point(calldata, context)
        return (response, changes)
