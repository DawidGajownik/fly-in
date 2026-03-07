from typing import Optional

class Hub:
    def __init__(
            self, hub_type: str, name: str, x: int, y: int,
            extras: Optional[str] = None):
        self.name = name
        self.hub_type = hub_type[:-1]
        self.x = int(x)
        self.y = int(y)
        self.color = None
        self.max_drones = 1
        self.zone = 'normal'
        self.process_extras(extras) if extras else None
        self.block = None
        self.drones_amount = 0
        self.connections = []

    def process_extras(self, extras):
        extras = extras.removeprefix("[").removesuffix("]")
        lines = extras.split()
        for line in lines:
            if line.split("=")[0] == "color":
                self.color = line.split("=")[1]
            elif line.split("=")[0] == "max_drones":
                self.max_drones = int(line.split("=")[1])
            elif line.split("=")[0] == "zone":
                self.zone = line.split("=")[1]
            else:
                raise ValueError

    def __str__(self):
        return f"{self.__class__.__name__}: name = {self.name}: type = {self.hub_type}: x = {self.x}, y = {self.y}, color = {self.color}, max_drones = {self.max_drones}, zone = {self.zone}"