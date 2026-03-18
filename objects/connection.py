from .hub import Hub
from typing import Optional


class Connection:
    def __init__(
            self, start: Hub, end: Hub,
            extras: Optional[str] = None) -> None:
        self.start = start
        self.end = end
        self.drones_amount = 0
        self.max_drones = 1
        self.max_trips = 1
        self.trips = 0
        self.active = True
        self.process_extras(extras) if extras else None

    def process_extras(self, extras: str) -> None:
        extras = extras.removeprefix("[").removesuffix("]")
        lines = extras.split()
        for line in lines:
            if line.split("=")[0] == "max_link_capacity":
                self.max_trips = int(line.split("=")[1])
            else:
                raise ValueError

    def trip(self) -> None:
        self.trips += 1

    def trips_reset(self) -> None:
        self.trips = 0

    def can_go(self) -> bool:
        return self.trips < self.max_trips

    def deactivate(self) -> None:
        self.active = False

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}:"
                f" {self.start.name} - {self.end.name},"
                f" capacity = {self.max_trips}")
