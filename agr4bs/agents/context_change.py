"""
    ContextChange file class implementation
"""


class ContextChange():

    """
        Context changes that need to be made to the Agent when
        the associated Role is either
        mounted or unmounted.
    """

    def mount(self) -> dict:
        """
            Returns the dictionary describing the keys that should be made available
            in the agent state as well as their initial values.
        """
        return self.__dict__

    def unmount(self) -> list:
        """
            Returns the list describing the keys that should be removed from the agent
            state.
        """
        return list(self.__dict__.keys())
