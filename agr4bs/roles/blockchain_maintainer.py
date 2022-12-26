"""
Abstract implementation of the BlockchainMaintainer role as per AGR4BS

BlockchainMaintainerContextChange:

The BlockchainMaintainerContextChange exposes changes that need to be made to the
ExternalAgent context when the Role is mounted and unmounted.

BlockchainMaintainer:

The BlockchainMaintainer implementation which MUST contain the following behaviors :
- validate_transaction
- validate_block
- store_transaction
- execute_transaction
- append_block
"""
from agr4bs.events.events import INIT
from agr4bs.state.account import Account
from agr4bs.state.state_change import AddBalance, CreateAccount, RemoveBalance
from ..agents import ExternalAgent, Context, ContextChange, AgentType
from ..events import RECEIVE_BLOCK, RECEIVE_TRANSACTION
from ..state import State, Receipt
from ..vm import VM
from ..roles.role import Role, RoleType
from ..common import on, export
from ..blockchain import Block, Transaction
from ..factory import Factory
from ..network.messages import DiffuseBlock, DiffuseTransaction


class BlockchainMaintainerContextChange(ContextChange):

    """
        Context changes that need to be made to the ExternalAgent when
        the associated Role (BlockchainMaintainer) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:

        self.receipts: dict[Receipt] = {}

        # tx_pool holds transactions ready to be processed
        self.tx_pool: dict[dict[Transaction]] = self.init_tx_pool

        self.vm = self.init_vm
        self.blockchain = self.init_blockchain
        self.state = self.init_state

    @staticmethod
    def init_vm(context: Context):
        """
            Initialize the VM
        """
        factory: Factory = context['factory']

        return factory.build_vm()

    @staticmethod
    def init_blockchain(context: Context):
        """
            Initialize the blockchain
        """
        factory: Factory = context['factory']
        genesis: Block = context['genesis']

        return factory.build_blockchain(genesis)

    @staticmethod
    def init_state(context: Context):
        """
            Initialize the state
        """
        factory: Factory = context['factory']
        state: State = factory.build_state()

        return state

    @staticmethod
    def init_tx_pool(context: Context):
        """
            Initialize the tx pool
        """
        factory: Factory = context['factory']
        tx_pool = factory.build_tx_pool()

        return tx_pool


class BlockchainMaintainer(Role):

    """
        Implementation of the BlockchainMaintainer Role which must
        expose the following behaviors :
        - validate_transaction
        - validate_block
        - store_transaction
        - execute_transaction
        - append_block

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        dependencies = [RoleType.PEER]

        super().__init__(RoleType.BLOCKCHAIN_MAINTAINER,
                         AgentType.EXTERNAL_AGENT, dependencies)

    @staticmethod
    def context_change() -> ContextChange:
        """
            Returns the ContextChange required whent mounting / unmounting the Role
        """
        return BlockchainMaintainerContextChange()

    @staticmethod
    @export
    @on(INIT)
    def process_genesis(agent: ExternalAgent):

        genesis = agent.context['blockchain'].genesis

        for tx in genesis.transactions:
            agent.execute_transaction(tx)

    @staticmethod
    @export
    @on(RECEIVE_TRANSACTION)
    def receive_transaction(agent: ExternalAgent, tx: Transaction):
        """
            Behavior called on a RECEIVE_TRANSACTIOn event
            It is responsible for validating the transaction and storing it
            in the memory pool if it passes the checks.
        """

        tx_hash = tx.compute_hash()

        # Invalid tx hashes are not added nor propagated
        if tx.hash != tx_hash:
            return False

        # Skip invalid transactions
        if agent.validate_new_transaction(tx) is False:
            return False

        # Record transactions in the mempool
        agent.store_transaction(tx)

        # Diffuse the transaction to the outbound peers
        outbound_peers = list(agent.context['outbound_peers'])
        agent.send_message(DiffuseTransaction(agent.name, tx), outbound_peers)

        return True

    @staticmethod
    @export
    @on(RECEIVE_BLOCK)
    def receive_block(agent: ExternalAgent, block: Block):
        """
            Behavior called on RECEIVE_BLOCK event.
            It is responsible for validating the block and appending and
            triggering it's addition to the blockchain.
        """

        block_hash = block.compute_hash()

        # Block is already known
        if agent.context['blockchain'].get_block(block_hash):
            return

        # Skip invalid blocks
        if agent.validate_block(block) is False:
            return

        agent.append_block(block)

        # Diffuse the block to the outbound peers
        outbound_peers = list(agent.context['outbound_peers'])
        agent.send_message(DiffuseBlock(agent.name, block), outbound_peers)

    @staticmethod
    @export
    def validate_transaction(agent: ExternalAgent, tx: Transaction) -> bool:
        """ Validate a transaction to execute

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param transaction: the transaction to validate
            :type transaction: Transaction
            :returns: wether the transaction is valid or not
            :rtype: bool
        """

        sender_account = agent.context['state'].get_account(tx.origin)

        if tx.hash in agent.context['receipts']:
            return False

        if sender_account is None:
            return False

        if sender_account.balance < tx.value + tx.fee:
            return False

        if sender_account.nonce != tx.nonce:
            return False

        return True

    @staticmethod
    @export
    def validate_new_transaction(agent: ExternalAgent, tx: Transaction) -> bool:
        """ Validate a newly received transaction specific transaction

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param transaction: the transaction to validate
            :type transaction: Transaction
            :returns: wether the transaction is valid or not
            :rtype: bool
        """

        if tx.hash in agent.context['receipts']:
            return False

        sender_account = agent.context['state'].get_account(tx.origin)

        if sender_account is None:
            return False

        if sender_account.nonce > tx.nonce:
            return False

        # This special case may save a network diffuse on invalid tx with correct nonce
        if sender_account.nonce == tx.nonce:
            if sender_account.balance < tx.value + tx.fee:
                return False

        # Replacement is only allowed if the replacement fee is higher than the existing one
        if tx.origin in agent.context['tx_pool'] and tx.nonce in agent.context['tx_pool'][tx.origin]:
            exising_tx = agent.context['tx_pool'][tx.origin][tx.nonce]
            if (tx.fee <= exising_tx.fee):
                return False

        return True

    @staticmethod
    @export
    def validate_block(agent: ExternalAgent, block: Block) -> bool:
        """ Validate a specific Block

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param block: the block to validate
            :type block: Block
            :returns: wether the block is valid or not
            :rtype: bool
        """

        if block.compute_hash() != block.hash:
            return False

        return True

    @staticmethod
    @export
    def get_pending_transactions(agent: ExternalAgent) -> dict[list[Transaction]]:
        pending_transactions_by_account = {}

        for account in agent.context['tx_pool']:
            account_nonce = agent.context['state'].get_account_nonce(account)

            if account_nonce in agent.context['tx_pool'][account]:
                nonce = account_nonce
                pending_transactions_by_account[account] = []

                while nonce in agent.context['tx_pool'][account]:
                    pending_transactions_by_account[account].append(
                        agent.context['tx_pool'][account][nonce])
                    nonce = nonce + 1

        return pending_transactions_by_account

    @staticmethod
    @export
    def store_transaction(agent: ExternalAgent, tx: Transaction) -> bool:
        """ Store a specific transaction from the transaction pool

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param transaction: the transaction to store
            :type transaction: Transaction
            :returns: wether the transaction was stored or not
            :rtype: bool
        """

        # The sender is not known create entires in the tx_pool
        if tx.origin not in agent.context['tx_pool']:
            agent.context['tx_pool'][tx.origin] = {}

        agent.context['tx_pool'][tx.origin][tx.nonce] = tx

    @staticmethod
    @export
    def discard_transaction(agent: ExternalAgent, tx: Transaction):
        """
            discard a specific transaction from the transaction pool

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param transaction: the transaction to discard
            :type transaction: Transaction
        """

        # The transaction may be unknown if it was received in a foreign block
        if tx.origin in agent.context['tx_pool'] and tx.nonce in agent.context['tx_pool'][tx.origin]:
            del agent.context['tx_pool'][tx.origin][tx.nonce]

            # Cleanup the tx_pool when an account has no pending or queued transactions
            if len(agent.context['tx_pool'][tx.origin]) == 0:
                del agent.context['tx_pool'][tx.origin]

    @staticmethod
    @export
    def append_block(agent: ExternalAgent, block: Block) -> bool:
        """ Append a specific block to the local blockchain

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param block: the block to append
            :type block: Block
            :returns: wether the block was appended or not
            :rtype: bool
        """
        if agent.validate_block(block):
            head_changed, reverted_blocks, added_blocks = agent.context['blockchain'].add_block(
                block)

            # Only reorg if the head changed
            if head_changed:
                agent.reorg(reverted_blocks, added_blocks)

            return True

        return False

    @staticmethod
    @export
    def reorg(agent: ExternalAgent, reverted_blocks: list[Block], added_blocks: list[Block]):
        """
            Process a chain reorg by doing the adequate revert / execute
        """

        for reverted_block in reverted_blocks:
            agent.reverse_block(reverted_block)

        for added_block in added_blocks:

            # An invalid block was found during the reorg :
            # - invalidate the block and all its successors
            # - compute new candidate head
            # - reorg to the new head
            if not agent.execute_block(added_block):
                if agent.context["blockchain"].mark_invalid(added_block):
                    previous_head = agent.context["blockchain"].get_block(
                        added_block.parent_hash)
                    new_head = agent.context["blockchain"].find_new_head()

                    if previous_head.hash != new_head.hash:
                        to_revert, to_add = agent.context["blockchain"].find_path(
                            previous_head, new_head)
                        agent.reorg(to_revert, to_add)

                    else:
                        agent.context["blockchain"].head = previous_head

                    return

    @staticmethod
    @export
    def execute_block(agent: ExternalAgent, block: Block) -> bool:
        """ Execute a specific Block

            :param block: the Block to execute
            :type block: Block
            :returns: wether the Block was executed successfully or not
            :rtype: bool
        """

        for index, tx in enumerate(block.transactions):

            if agent.validate_transaction(tx) is False:

                # An invalid tx was found while executing the block
                # Revert all the previous ones from the same block
                while index > 0:
                    agent.reverse_transaction(block.transactions[index - 1])
                    agent.store_transaction(block.transactions[index - 1])
                    index = index - 1

                return False

            agent.execute_transaction(tx)
            agent.discard_transaction(tx)

        if agent.context['state'].get_account(block.creator) is None:
            change = CreateAccount(Account(block.creator, 10))
        else:
            change = AddBalance(block.creator, 10)

        agent.context["state"].apply_state_change(change)
        agent.context["blockchain"].head = block

        return True

    @staticmethod
    @export
    def reverse_block(agent: ExternalAgent, block: Block) -> bool:
        """ Reverse a specific Block

            :param block: the Block to reverse
            :type block: Block
            :returns: wether the Block was reversed successfully or not
            :rtype: bool
        """

        agent.context["state"].apply_state_change(
            RemoveBalance(block.creator, 10))

        for tx in reversed(block.transactions):

            # Reverse the transaction
            agent.reverse_transaction(tx)

            # Delete the Receipt entry
            del agent.context['receipts'][tx.hash]

        new_head = agent.context['blockchain'].get_block(block.parent_hash)
        agent.context["blockchain"].head = new_head

    @staticmethod
    @export
    def execute_transaction(agent: ExternalAgent, tx: Transaction) -> bool:
        """ Execute a specific transaction

            :param transaction: the transaction to execute
            :type transaction: Transaction
            :returns: wether the transaction was executed successfully or not
            :rtype: bool
        """
        if tx.hash in agent.context['receipts']:
            raise ValueError("Executing an already seen transaction.")

        receipt = agent.context['vm'].process_tx(
            agent.context["state"].copy(), tx)
        agent.context["state"].apply_batch_state_change(receipt.state_changes)
        agent.context["receipts"][tx.hash] = receipt

    @staticmethod
    @export
    def reverse_transaction(agent: ExternalAgent, tx: Transaction) -> bool:
        """ Reverse a specific transaction

            :param transaction: the transaction to reverse
            :type transaction: Transaction
            :returns: wether the transaction was reverted successfully or not
            :rtype: bool
        """
        if tx.hash not in agent.context['receipts']:
            raise ValueError("Reversing an uknown transaction")

        receipt: Receipt = agent.context['receipts'][tx.hash]

        changes = [sc.revert() for sc in reversed(receipt.state_changes)]
        agent.context['state'].apply_batch_state_change(changes)

        return True
