"""
Stack class for the EVM.
"""

from . import word

class Stack:

    def __init__(self):
        self._stack = []

    def push_int(self, value: int) -> None:
        """
        Pushes a value onto the stack.
        """

        self._stack.append(word.int_to_word(value))

    def push(self, value: bytes) -> None:
        """
            Pushes a 32 bytes word onto the stack
        """
        assert len(value) == 32
        self._stack.append(value)
        

    def pop(self) -> bytes:
        """
        Pops a value from the stack.
        """
        return self._stack.pop()
    
    def peek(self) -> bytes:
        """
        Peeks at the top of the stack.
        """
        return self._stack[-1]
    
    def dup(self, index: int) -> None:
        """
        Duplicates the value at the given index.
        """
        self._stack.append(self._stack[-index])

    def swap(self, index: int) -> None:
        """
        Swaps the value at the given index with the top of the stack.
        """
        self._stack[-index], self._stack[-1] = self._stack[-1], self._stack[-index]

    def __len__(self) -> int:
        return len(self._stack)