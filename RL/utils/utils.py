def print_red(skk):
    """ Print in red """
    print("\033[91m {}\033[00m" .format(skk))

def print_green(skk):
    """ Print in green """
    print("\033[92m {}\033[00m" .format(skk))


def get_blockchain(agent):
    chain = []

    head = agent.context['blockchain'].head
    current = head

    while current != None:
        # Push front
        chain.insert(0, current)
        current = agent.context["blockchain"].get_block(current.parent_hash)

    return chain

def get_forks(agent):
    successfull_forks = 0
    failed_forks = 0
    chain = get_blockchain(agent)
    for block in chain:

        children = agent.context["blockchain"].get_direct_children(block)

        if len(children) > 1:
            # Select the block with the latest slot number between the children
            forked_block = None
            latest_slot = 0

            for child in children:
                if child.slot > latest_slot:
                    forked_block = child
                    latest_slot = child.slot

            if agent.context["blockchain"].is_block_on_main_chain(forked_block):
               successfull_forks = successfull_forks + 1
            else:
                failed_forks = failed_forks + 1

    
    return successfull_forks, failed_forks


def print_blockchain(agent):
    """ Print the blockchain view of an agent """
    print("Blockchain visualization for agent " + agent.name)

    chain = []

    head = agent.context['blockchain'].head
    current = head

    while current != None:
        # Push front
        chain.insert(0, current)
        current = agent.context["blockchain"].get_block(current.parent_hash)

    for block in chain:
        print("Block : " + block.hash + " - Creator " + str(block.creator) + " - Slot : " + str(block.slot) + " - Height : " + str(block.height) + " - Contains : " + str(len(block.transactions)) + " transactions " + str(len(block.attestations)) + " attestations")
        
        for attestation in block.attestations:
            print("Attestation from : " + attestation.agent_name + " - Slot : " + str(attestation.slot))

        children = agent.context["blockchain"].get_direct_children(block)

        for child in children:
            if agent.context["blockchain"].is_block_on_main_chain(child):
                print_green("Child : " + child.hash + " - Creator " + str(child.creator) + " - Slot : " + str(child.slot) + " - Height : " + str(child.height))
            else:
                print_red("Child : " + child.hash + " - Creator " + str(child.creator) + " - Slot : " + str(child.slot) + " - Height : " + str(child.height))