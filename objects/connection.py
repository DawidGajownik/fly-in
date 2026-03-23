"""Module connection.py. Brief description."""


from .hub import Hub
from typing import Optional


class Connection:
    """Connection class. Brief description."""

    def __init__(
            self, start: Hub, end: Hub,
            extras: Optional[str] = None) -> None:
        """__init__ function. Brief description.

        Args:
            start (type): Description.
            end (type): Description.
            extras (type): Description.

        Returns:
            None: Description.

        """
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
        """process_extras function. Brief description.

        Args:
            extras (type): Description.

        Returns:
            None: Description.

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
        """trip function. Brief description.

        Returns:
            None: Description.

        """
        self.trips += 1

    def trips_reset(self) -> None:
        """trips_reset function. Brief description.

        Returns:
            None: Description.

        """
        self.trips = 0

    def can_go(self) -> bool:
        """can_go function. Brief description.

        Returns:
            bool: Description.

        """
        return self.trips < self.max_trips

    def deactivate(self) -> None:
        """deactivate function. Brief description.

        Returns:
            None: Description.

        """
        self.active = False

    def __str__(self) -> str:
        """__str__ function. Brief description.

        Returns:
            str: Description.

        """
        return (f"{self.__class__.__name__}:"
                f" {self.start.name} - {self.end.name},"
                f" capacity = {self.max_trips}")
