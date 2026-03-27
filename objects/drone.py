from .hub import Hub
from .connection import Connection
from random import randint
from typing import Union, List


class Drone:
    """Drone class"""

    def __init__(
            self, hub: Hub, idx: int,
            all_colors: List[str], colors_length: int) -> None:
        """__init__ function."""
        self.idx = idx
        self.place: Union[Hub, Connection] = hub
        self.prev_place: Union[Hub, Connection] = hub
        self.color = all_colors[randint(0, colors_length)]
        self.x = 0
        self.y = 0
        self.prev_x: Union[int, None] = None
        self.prev_y: Union[int, None] = None
        self.moved = False
        self.moves = 0

    def move(self) -> bool:
        """
        Function which moves drone in the most efficient way.
        First it checks is there any priority connection,
        second - normal connection, third - restricted connection.
        And it moves the dron to the best available option.
        If only restricted connection is available, the function
        moves the drone to the middle of connection as it is
        described in subject.
        """
        possible_destinations: List[Union[Hub, Connection]] = []
        if isinstance(self.place, Connection):
            if self.place.end.drones_amount < self.place.end.max_drones:
                possible_destinations = [self.place.end]
        else:
            possible_destinations = []
            connections = self.place.connections
            for connection in connections:
                if connection.priority_available():
                    connection.trip()
                    possible_destinations = [connection.end]
            for connection in connections:
                if (connection.normal_available()
                        and len(possible_destinations) == 0):
                    connection.trip()
                    possible_destinations = [connection.end]
            for connection in connections:
                if (connection.restricted_available()
                        and len(possible_destinations) == 0):
                    possible_destinations = [connection]
        if len(possible_destinations) > 0:
            possible_destinations[0].drones_amount += 1
            self.place.drones_amount -= 1
            self.prev_place = self.place
            self.place = possible_destinations[0]
            print(f"D{self.idx}-"
                  f"{self.destination()}"
                  f"", end=' ')
            self.moves += 1
            self.moved = True
            return True
        return False

    def destination(self) -> str:
        """
        Function return proper string to program output.
        If it is a Hub it returns it's name, if it is a Connection
        it returns "connection"
        """
        if isinstance(self.place, Hub):
            return self.place.name
        return "connection"
