"""
    Network file class implementation
"""

from ..common import Transaction, Block
from ..agents import Agent


class Network():

    """
        Network class implementation :

        Simulates a network, where messages can be sent (broadcast)
        with a configurable delay and message drop probability.
    """

    def __init__(self) -> None:
        pass

    def broadcast_transaction(self, tx: Transaction) -> None:
        """ Broadcast a Transaction to the whole network

            :param tx: the transaction to Broadcast
            :type tx: Transaction
        """

    def send_transaction(self, tx: Transaction, agent: Agent) -> None:
        """ Send a Transaction to a specific Agent

            :param tx: the transaction to send
            :type tx: Transaction
            :param agent: the agent who should receive the Transaction
            :type agent: Agent
        """

    def broadcast_block(self, block: Block) -> None:
        """ Broadcast a Block to the whole network

            :param block: the block to Broadcast
            :type block: Block
        """

    def send_block(self, block: Block, agent: Agent) -> None:
        """ Send a Block to a specific Agent

            :param block: the Block to send
            :type block: Block
            :param agent: the agent who should receive the Block
            :type agent: Agent
        """

    def flush_agent(self, agent: Agent) -> None:
        """ Flush an Agent out of the Network

        :param agent: The Agent to flush out
        :type agent: Agent
        """
