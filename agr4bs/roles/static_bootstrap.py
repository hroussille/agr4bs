"""
Abstract implementation of the Peer role as per AGR4BS

PeerContextChange:

The PeerContextChange exposes changes that need to be made to the
Agent context when the Role is mounted and unmounted.

PeerEndorser:

The Peer implementation which MUST contain the following behaviors :

# TODO

"""

import random
from collections import defaultdict

from ..environment import Environment
from ..agents import AgentType, ContextChange
from ..network.messages import BootStrapStaticPeers
from ..events import REQUEST_BOOTSTRAP_STATIC_PEERS, INIT
from .role import Role, RoleType
from ..common import on


class StaticBootstrapContextChange(ContextChange):
    """
        Context changes that need to be made to the Agent when
        the associated Role (Oracle) is either
        mounted or unmounted.
    """

    def __init__(self) -> None:
        self.inbound_table = defaultdict(lambda: [])
        self.outbound_table = defaultdict(lambda: [])


class StaticBootstrap(Role):
    """
        Implementation of the StaticBootstrap Role which must
        expose the following behaviors :
        - bootstrap_peers

        This class MUST be inherited from and expanded to implement
        the actual logic of it's behaviors.
    """

    def __init__(self) -> None:
        super().__init__(RoleType.BOOTSTRAP, AgentType.EXTERNAL_AGENT)

    @staticmethod
    def context_change() -> ContextChange:
        """
            Returns the ContextChange required when mounting / unmounting the Role
        """
        return StaticBootstrapContextChange()

    @staticmethod
    def get_candidate(agent: Environment, agent_name: str):
        """
            Pick the next best peer candidate for agent_name
        """

        agent_outbounds = agent.context['outbound_table'][agent_name]
        agent_handle = agent.get_agent_by_name(agent_name)

        if len(agent_outbounds) >= agent_handle.max_outbound_peers:
            return None

        agents_names = agent.agents_names
        candidates = random.sample(agents_names, len(agents_names))

        def filter_candidates(candidate):

            # Don't match an agent with itself
            if candidate == agent_name:
                return False

            # Don't match already matched agents
            if candidate in agent.context['outbound_table'][agent_name]:
                return False

            # Don't match with saturated agents
            if len(agent.context['inbound_table'][candidate]) >= agent.get_agent_by_name(candidate).max_inbound_peers:
                return False

            return True

        def sort_candidates(candidate):
            return len(agent.context['inbound_table'][candidate])

        candidates = filter(filter_candidates, candidates)
        candidates = sorted(candidates, key=sort_candidates)

        if len(candidates) > 0:
            return candidates[0]

        return None

    @staticmethod
    @on(INIT)
    async def init_bootstrap_peers(agent: Environment):
        """
            Precomputes the network topology with all inbound and outbound peers
        """

        while True:

            filled = 0

            for agent_name in agent.agents_names:

                candidate = agent.get_candidate(agent_name)

                if candidate is None:
                    filled = filled + 1
                    continue

                agent.context['outbound_table'][agent_name].append(candidate)
                agent.context['inbound_table'][candidate].append(agent_name)

            if filled == len(agent.agents_names):
                return

    @staticmethod
    @on(REQUEST_BOOTSTRAP_STATIC_PEERS)
    async def bootstrap_peers(agent: Environment, peer: str):
        """
            Send a inbound peer request to all initial peer candidates

            :param agent: The agent on which the behavior operates
            :type agent: ExternalAgent
            :param candidates: the list of candidate peer addresses
            :type candidates: list[str]
        """
        outbounds = agent.context['outbound_table'][peer]
        inbounds = agent.context['inbound_table'][peer]

        await agent.send_message(BootStrapStaticPeers(agent.name, inbounds, outbounds), peer, no_drop=True)
