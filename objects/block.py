from .hub import Hub
from typing import List


class Block:
    """
    Block Class. A class representing a single location on the map,
    located by x and y coordinates.
    """

    def __init__(self, x: int, y: int) -> None:
        """__init__ function."""
        self.x = x
        self.y = y
        self.hubs: List[Hub] = []

    def add_hub(self, hub: Hub) -> None:
        """add_hub function"""
        self.hubs.append(hub)

    def __str__(self) -> str:
        """printing string representation"""
        return (f"{self.__class__.__name__}:"
                f" {self.x} x {self.y},"
                f" {', '.join(hub.__str__() for hub in self.hubs)}")
