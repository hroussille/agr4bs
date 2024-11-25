from collections import namedtuple

IntermediateTransition = namedtuple('IntermediateTransition', ('state', 'action', 'slot'))
Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward', 'slot'))
