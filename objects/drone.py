from .hub import Hub
from .connection import Connection
from random import randint
from typing import Union

class Drone:
    def __init__(self, hub: Hub, idx: int, all_colors, colors_length) -> None:
        self.idx = idx
        self.place: Union[Hub, Connection] = hub
        self.color = all_colors[randint(0, colors_length)]

    def move(self):
        end = []
        if isinstance(self.place, Connection):
            if self.place.end.drones_amount < self.place.end.max_drones:
                end = [self.place.end]
        else:
            connections = self.place.connections
            for connection in connections:
                if connection.active:
                    if connection.end.drones_amount < connection.end.max_drones and connection.end.zone == "priority" and connection.can_go():
                        connection.trip()
                        end = [connection.end]
                    if len(end) == 0 and connection.end.drones_amount < connection.end.max_drones and connection.end.zone == "normal" and connection.can_go():
                        connection.trip()
                        end = [connection.end]
                    if len(end) == 0 and connection.drones_amount < connection.max_drones and connection.end.zone == "restricted" and connection.end.drones_amount < connection.end.max_drones:
                        end = [connection]
        if len(end) > 0:
            end[0].drones_amount +=1
            self.place.drones_amount -=1
            self.place = end[0]
            print(f"D{self.idx}-{self.place.name if isinstance(self.place, Hub) else 'connection'}", end=' ')

    def __str__(self):
        return "Drone " + str(self.idx) + ": " + str(self.hub.x) + " x " + str(self.hub.y)