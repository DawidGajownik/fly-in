from .hub import Hub
from .connection import Connection
from random import randint
from typing import Union, List


def priority_available(connection: Connection) -> bool:
    """Function returning true if priority connection is available."""
    return (connection.end.drones_amount
            < connection.end.max_drones
            and connection.end.zone == "priority"
            and connection.can_go())


def normal_available(
        connection: Connection,
        end: List[Hub | Connection]) -> bool:
    """Function returning true if normal connection is available."""
    return (len(end) == 0
            and connection.end.drones_amount
            < connection.end.max_drones
            and connection.end.zone == "normal"
            and connection.can_go())


def restricted_available(
        connection: Connection,
        end: List[Hub | Connection]) -> bool:
    """Function returning true if restricted connection is available."""
    return (len(end) == 0
            and connection.drones_amount < connection.max_drones
            and connection.end.zone == "restricted"
            and connection.end.drones_amount < connection.end.max_drones)


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
        end: List[Union[Hub, Connection]] = []
        if isinstance(self.place, Connection):
            if self.place.end.drones_amount < self.place.end.max_drones:
                end = [self.place.end]
        else:
            end = []
            connections = self.place.connections
            for connection in connections:
                if connection.active and priority_available(connection):
                    connection.trip()
                    end = [connection.end]
            for connection in connections:
                if connection.active and normal_available(connection, end):
                    connection.trip()
                    end = [connection.end]
            for connection in connections:
                if connection.active and restricted_available(connection, end):
                    end = [connection]
        if len(end) > 0:
            end[0].drones_amount += 1
            self.place.drones_amount -= 1
            self.prev_place = self.place
            self.place = end[0]
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
