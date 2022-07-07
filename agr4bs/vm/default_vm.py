
"""
    DefaultVM file class implementation
"""
from enum import Enum

from agr4bs.agents.internal_agent import InternalAgentDeployement, Success
from .execution_context import ExecutionContext
from ..state import State, Account, Receipt
from ..state import CreateAccount, AddBalance, RemoveBalance, IncrementAccountNonce
from ..blockchain import Transaction
from ..agents import InternalAgent, InternalAgentCalldata, InternalAgentResponse, Revert


class TransactionType(Enum):
    """
        Valid transaction types
    """
    TRANSFER = "TRANSFER"
    CALL = "CALL"
    DEPLOYEMENT = "DEPLOYEMENT"
    NOOP = "NOOP"


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

        if state.get_account_internal_agent(tx.to) is None and tx.value > 0:
            return TransactionType.TRANSFER

        if len(tx.payload.data) > 0:
            return TransactionType.CALL

        return TransactionType.NOOP

    @staticmethod
    def _get_context_from_tx(tx: Transaction, state: State) -> ExecutionContext:
        return ExecutionContext(tx.origin, tx.origin, tx.to, tx.value, 0, state, VM)

    @staticmethod
    def transfer(ctx: ExecutionContext) -> InternalAgentResponse:
        recipient = ctx.state.get_account(ctx.to)
        changes = []

        if ctx.state.get_account_balance(ctx.caller) < ctx.value:
            return Revert("VM: Invalid balance for transfer")

        if recipient is None:
            changes.append(CreateAccount(Account(ctx.to)))

        if ctx.value > 0:
            changes.append(RemoveBalance(ctx.caller, ctx.value))
            changes.append(AddBalance(ctx.to, ctx.value))

        ctx.state.apply_batch_state_change(changes)
        ctx.merge_changes(changes)

        return Success()

    @staticmethod
    def deploy(deployement: InternalAgentDeployement, ctx: ExecutionContext):
        pass

    @staticmethod
    def call(calldata: InternalAgentCalldata, ctx: ExecutionContext) -> InternalAgentResponse:
        if ctx.depth > 1024:
            return Revert("VM : Max call depth exceeded")

        if ctx.value > 0:
            result = VM.transfer(ctx)

            if result.reverted:
                return result

        callee: InternalAgent = ctx.state.get_account_internal_agent(ctx.to)

        if callee is None:
            return Revert("VM : No InternalAgent to call")

        response = callee.entry_point(calldata, ctx)

        return response

    @staticmethod
    def process_tx(state: State, tx: Transaction) -> Receipt:
        tx_type = VM._get_transaction_type(state, tx)
        context = VM._get_context_from_tx(tx, state)

        context.changes.append(IncrementAccountNonce(tx.origin))
        context.state.apply_batch_state_change(context.changes)

        intermediate_context = context.copy()
        intermediate_context.clear_changes()

        if tx_type == TransactionType.TRANSFER:
            response = VM.transfer(intermediate_context)

        elif tx_type == TransactionType.DEPLOYEMENT:
            deployement = InternalAgentDeployement.from_serialized(
                tx.payload.data)
            response = VM.deploy(deployement, intermediate_context)

        elif tx_type == TransactionType.CALL:
            calldata = InternalAgentCalldata.from_serialized(tx.payload.data)
            response = VM.call(calldata, intermediate_context)

        elif tx_type == TransactionType.NOOP:
            response = Success()

        if response.reverted is False:
            context.merge_changes(intermediate_context.changes)

        return Receipt(tx.hash, context.changes, response.reverted, response.revert_reason)
