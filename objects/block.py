from .hub import Hub
from typing import List


class Block:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.hubs: List[Hub] = []

    def add_hub(self, hub: Hub) -> None:
        self.hubs.append(hub)

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}:"
                f" {self.x} x {self.y},"
                f" {', '.join(hub.__str__() for hub in self.hubs)}")
