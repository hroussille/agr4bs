
"""
    Core Events definitions
"""

# Seed nodes events
BOOTSTRAP_PEERS = "request_seed_list"

# P2P update events
UPDATE_PEERS = "update_peers"
REQUEST_PEER_DISCOVERY = "request_peer_discovery"

# Inbound peers events
REQUEST_INBOUND_PEER = "request_inbound_peer"
ACCEPT_INBOUND_PEER = "accept_inbound_peer"
DENY_INBOUND_PEER = "deny_inbound_peer"
DROP_INBOUND_PEER = "drop_inbound_peer"

# Outbound peers events
REQUEST_OUTBOUND_PEER = "request_outbound_peer"
ACCEPT_OUTBOUND_PEER = "accept_outbound_peer"
DENY_OUTBOUND_PEER = "deny_outbound_peer"
DROP_OUTBOUND_PEER = "drop_outbound_peer"

# Block events
PROPOSE_BLOCK = "propose_block"
REQUEST_BLOCK = "request_block"
REQUEST_BLOCKS = "request_blocks"

# Block endorsement events
REQUEST_BLOCK_ENDORSEMENT = "request_block_endorsement"
ACCEPT_BLOCK_ENDORSEMENT = "accept_block_endorsement"
DENY_BLOCK_ENDORSEMENT = "deny_block_endorsement"

# Transaction diffusion events
DIFFUSE_TRANSACTION = "diffuse_transaction"

# Transaction endorsement events
REQUEST_TRANSACTION_ENDORSEMENT = "request_transaction_endorsement"
ACCEPT_TRANSACTION_ENDORSEMENT = "accept_transaction_endorsement"
DENY_TRANSACTION_ENDORSEMENT = "deny_transaction_endorsement"

# Simulation events
INIT = "init"
PAUSE_SIMULATION = "pause_simulation"
RESTART_SIMULATION = "restart_simulation"
STOP_SIMULATION = "stop_simulation"
