"""Module connection.py. Brief description."""


from .hub import Hub
from typing import Optional


class Connection:
    """Connection class. A class representing a connection between hubs."""

    def __init__(
            self, start: Hub, end: Hub,
            extras: Optional[str] = None) -> None:
        """__init__ function."""
        self.start = start
        self.end = end
        self.drones_amount = 0
        self.max_drones = 1
        self.max_trips = 1
        self.trips = 0
        self.active = True
        self.process_extras(extras) if extras else None
        if self.end.max_drones < self.max_drones:
            self.max_drones = self.end.max_drones

    def process_extras(self, extras: str) -> None:
        """
        process_extras function. A function that handles
        additional parameters from the map file and converts
        them into object parameters.
        """
        extras = extras.removeprefix("[").removesuffix("]")
        lines = extras.split()
        for line in lines:
            if line.split("=")[0] == "max_link_capacity":
                self.max_drones = int(line.split("=")[1])
                self.max_trips = int(line.split("=")[1])
            else:
                raise ValueError

    def trip(self) -> None:
        """Functions adding trips made in this turn."""
        self.trips += 1

    def trips_reset(self) -> None:
        """Functions resetting trips after the turn."""
        self.trips = 0

    def can_go(self) -> bool:
        """Functions checking ability to go in this turn."""
        return self.trips < self.max_trips

    def deactivate(self) -> None:
        """Functions deactivating connection from usage."""
        self.active = False

    def __str__(self) -> str:
        """__str__ function."""
        return (f"{self.__class__.__name__}:"
                f" {self.start.name} - {self.end.name},"
                f" capacity = {self.max_trips}")
