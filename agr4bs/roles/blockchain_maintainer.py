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

from ..agents import ExternalAgent, Context, ContextChange, AgentType
from ..state import State, Receipt
from ..vm import VM
from ..roles.role import Role, RoleType
from ..common import on
from ..blockchain import Block, Transaction
from ..factory import Factory


class BlockchainMaintainerContextChange(ContextChange):
    """
        Context changes that need to be made to the ExternalAgent when
        the associated Role (BlockchainMaintainer) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:

        self.receipts: dict[Receipt] = {}
        self.tx_pool: dict[Transaction] = {}
        self.tx_queue: dict[Transaction] = {}
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
        genesis: Block = context['genesis']
        vm: VM = context['vm']

        state: State = factory.build_state()

        for tx in genesis.transactions:
            changes = vm.process_tx(tx)
            state.apply_batch_state_change(changes)

        return state


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
        super().__init__(RoleType.BLOCKCHAIN_MAINTAINER, AgentType.EXTERNAL_AGENT)

    @staticmethod
    def context_change() -> ContextChange:
        """
            Returns the ContextChange required whent mounting / unmounting the Role
        """
        return BlockchainMaintainerContextChange()

    @staticmethod
    @on('validate_transaction')
    async def validate_transaction(agent: ExternalAgent, tx: Transaction) -> bool:
        """ Validate a specific transaction

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param transaction: the transaction to validate
            :type transaction: Transaction
            :returns: wether the transaction is valid or not
            :rtype: bool
        """
        sender_account = agent.state.get_account(tx.origin)

        if sender_account.balance < tx.amount + tx.fee:
            return False

        if sender_account.nonce < tx.nonce:
            return False

        return True

    @staticmethod
    @on('validate_block')
    def validate_block(agent: ExternalAgent, block: Block) -> bool:
        """ Validate a specific Block

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param block: the block to validate
            :type block: Block
            :returns: wether the block is valid or not
            :rtype: bool
        """
        for tx in block.transactions:
            if agent.behaviors.validate_transaction(tx) is False:
                return False

        return True

    @staticmethod
    @on('store_transaction')
    def store_transaction(agent: ExternalAgent, tx: Transaction) -> bool:
        """ Store a specific transaction

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param transaction: the transaction to store
            :type transaction: Transaction
            :returns: wether the transaction was stored or not
            :rtype: bool
        """
        if tx.hash in agent.tx_pool:
            return False

        agent.context["tx_pool"][tx.hash] = tx
        return True

    @staticmethod
    @on('append_block')
    def append_block(agent: ExternalAgent, block: Block) -> bool:
        """ Append a specific block to the local blockchain

            :param agent: the agent on which the behavior operates
            :type agent: ExternalAgent
            :param block: the block to append
            :type block: Block
            :returns: wether the block was appended or not
            :rtype: bool
        """
        if agent.behaviors.validate_block(agent, block):
            res, reverted_blocks, added_blocks = agent.blockchain.add_block(
                block)

            for reverted_block in reverted_blocks:
                agent.behaviors.reverse_block(agent, reverted_block)

            for added_block in added_blocks:
                agent.behaviors.execute_block(agent, added_block)

            return res

        return False

    @staticmethod
    @on('execute_block')
    async def execute_block(agent: ExternalAgent, block: Block) -> bool:
        """ Execute a specific Block

            :param block: the Block to execute
            :type block: Block
            :returns: wether the Block was executed successfully or not
            :rtype: bool
        """

        for tx in block.transactions:
            agent.behaviors.execute_transaction(agent, tx)

        return True

    @staticmethod
    @on('reverse_block')
    def reverse_block(agent: ExternalAgent, block: Block) -> bool:
        """ Reverse a specific Block

            :param block: the Block to reverse
            :type block: Block
            :returns: wether the Block was reversed successfully or not
            :rtype: bool
        """
        for tx in block.transactions.reverse():
            # Reverse the transaction state changes
            agent.behaviors.reverse_transaction(agent, tx)

            # Push the tx back onto the txpool
            agent.txpool[tx.hash] = tx

            # Delete the Receipt entry
            del agent.receipts[tx.hash]

    @staticmethod
    @on('execute_transaction')
    def execute_transaction(agent: ExternalAgent, tx: Transaction) -> bool:
        """ Execute a specific transaction

            :param transaction: the transaction to execute
            :type transaction: Transaction
            :returns: wether the transaction was executed successfully or not
            :rtype: bool
        """
        if tx.hash in agent.receipts:
            raise ValueError("Executing an already seen transaction.")

        receipt = agent.execution_environment.process_tx(
            agent.context["state"].copy(), tx)
        agent.context["state"].apply_batch_state_change(receipt.changes)
        agent.context["receipts"][tx.hash] = receipt

    @staticmethod
    @on('reverse_transaction')
    def reverse_transaction(agent: ExternalAgent, tx: Transaction) -> bool:
        """ Reverse a specific transaction

            :param transaction: the transaction to reverse
            :type transaction: Transaction
            :returns: wether the transaction was reverted successfully or not
            :rtype: bool
        """
        if tx.hash not in agent.receipts:
            raise ValueError("Reversing an uknown transaction")

        receipt: Receipt = agent.receipts[tx.hash]

        changes = receipt.state_changes.reverse()
        agent.state.apply_batch_state_change(changes)

        return True
