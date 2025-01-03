
"""
    Core Events definitions
"""

# Messages events
SEND_MESSAGE = "send_message"
RECEIVE_MESSAGE = "receive_message"

# Seed nodes events
REQUEST_BOOTSTRAP_PEERS = "request_bootstrap_peers"
REQUEST_BOOTSTRAP_STATIC_PEERS = "request_static_bootstrap_peers"
BOOTSTRAP_PEERS = "bootstrap_peers"
BOOTSTRAP_STATIC_PEERS = "bootstrap_static_peers"

# P2P update events
UPDATE_PEERS = "update_peers"
REQUEST_PEER_DISCOVERY = "request_peer_discovery"
PEER_DISCOVERY = "peer_discovery"

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
CREATE_BLOCK = "create_block"
RECEIVE_BLOCK = "receive_block"
RECEIVE_BLOCK_HEADER = "receive_block_header"
REQUEST_BLOCK = "request_block"
REQUEST_BLOCK_HEADER = "request_block_header"
RECEIVE_REQUEST_BLOCKS = "receive_request_blocks"
RECEIVE_REQUEST_BLOCKS_HEADERS = "receive_request_blocks_header"

# Block endorsement events
REQUEST_BLOCK_ENDORSEMENT = "request_block_endorsement"
ACCEPT_BLOCK_ENDORSEMENT = "accept_block_endorsement"
DENY_BLOCK_ENDORSEMENT = "deny_block_endorsement"
RECEIVE_BLOCK_ENDORSEMENT = "receive_block_endorsement"

# Transaction diffusion events
CREATE_TRANSACTION = "create_transaction"
RECEIVE_TRANSACTION = "receive_transaction"

# Transaction endorsement events
REQUEST_TRANSACTION_ENDORSEMENT = "request_transaction_endorsement"
ACCEPT_TRANSACTION_ENDORSEMENT = "accept_transaction_endorsement"
DENY_TRANSACTION_ENDORSEMENT = "deny_transaction_endorsement"
RECEIVE_TRANSACTION_ENDORSEMENT = "receive_transaction_endorsement"

# Simulation events
INIT = "init"
PAUSE_SIMULATION = "pause_simulation"
RESTART_SIMULATION = "restart_simulation"
STOP_SIMULATION = "stop_simulation"
CLEANUP = "cleanup"

# Protocol events
NEXT_EPOCH = "next_epoch"
NEXT_SLOT = "next_slot"

# Schedulable events
RUN_SCHEDULABLE = "run_schedulable"
