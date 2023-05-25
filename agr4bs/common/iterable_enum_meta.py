
"""
    IterableEnumMeta file class implementation
"""

from enum import EnumMeta


class IterableEnumMeta(EnumMeta):
    """
        Meta class to allow Enum retrieval as a list
    """
    def __contains__(cls, item):
        return item in [v.value for v in cls.__members__.values()]
