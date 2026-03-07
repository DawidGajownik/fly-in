from .hub import Hub
from random import randint

class Drone:
    def __init__(self, hub: Hub, idx: int, all_colors, colors_length) -> None:
        self.idx = idx
        self.hub = hub
        self.color = all_colors[randint(0, colors_length)]

    def move(self):
        connections = self.hub.connections
        end = []
        for connection in connections:
            if connection.end.drones_amount < connection.end.max_drones and connection.end.zone == "priority":
                end = [connection.end]
            if len(end) == 0 and connection.end.drones_amount < connection.end.max_drones and connection.end.zone == "normal":
                end = [connection.end]
            if len(end) == 0 and connection.end.drones_amount < connection.end.max_drones and connection.end.zone == "restricted":
                end = [connection.end]
        if len(end) > 0:
            end[0].drones_amount +=1
            self.hub.drones_amount -=1
            self.hub = end[0]

    def __str__(self):
        return "Drone " + str(self.idx) + ": " + str(self.hub.x) + " x " + str(self.hub.y)