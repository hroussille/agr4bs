"""
Memory class for the Ethereum Virtual Machine.
"""

class Memory:

    def __init__(self):
        self.memory = bytearray()

    def load_n(self, offset: int, size: int) -> bytes:
        """
        Loads a byte array from memory.
        """
        if offset + size > len(self.memory):
            return b''
        return bytes(self.memory[offset:offset + size])
    
    def load(self, offset: int) -> bytes:
        """
            Loads 32 bytes from memory.
        """
        return self.load_n(offset, 32)
    
    def load_8(self, offset: int) -> int:
        """
        Loads a single byte from memory.
        """
        return self.load_n(offset, 1)[0]
    
    def store_n(self, offset: int, data: bytes) -> None:
        """
        Stores a byte array into memory.
        """
        if offset + len(data) > len(self.memory):
            self.memory += bytearray(offset + len(data) - len(self.memory))
        self.memory[offset:offset + len(data)] = data

    def store(self, offset: int, data: bytes) -> None:
        """
        Stores 32 bytes into memory.
        """
        self.store_n(offset, data)

    def store_8(self, offset: int, data: int) -> None:
        """
        Stores a single byte into memory.
        """
        self.store_n(offset, bytes([data]))