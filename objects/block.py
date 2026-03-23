"""Module block.py. Brief description."""


from .hub import Hub
from typing import List


class Block:
    """Block class. Brief description."""

    def __init__(self, x: int, y: int) -> None:
        """__init__ function. Brief description.

        Args:
            x (type): Description.
            y (type): Description.

        Returns:
            None: Description.

        """
        self.x = x
        self.y = y
        self.hubs: List[Hub] = []

    def add_hub(self, hub: Hub) -> None:
        """add_hub function. Brief description.

        Args:
            hub (type): Description.

        Returns:
            None: Description.

        """
        self.hubs.append(hub)

    def __str__(self) -> str:
        """__str__ function. Brief description.

        Returns:
            str: Description.

        """
        return (f"{self.__class__.__name__}:"
                f" {self.x} x {self.y},"
                f" {', '.join(hub.__str__() for hub in self.hubs)}")
