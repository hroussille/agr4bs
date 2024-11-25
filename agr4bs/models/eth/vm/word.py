"""
This module contains functions for converting between python integers and 32-byte words.
"""

def int_to_word(value: int) -> bytes:
    """
    Converts an integer to a 32-byte word.
    """
    return value.to_bytes(32, byteorder='big')

def word_to_int(word: bytes) -> int:
    """
    Converts a 32-byte word to an integer.
    """
    return int.from_bytes(word, byteorder='big')