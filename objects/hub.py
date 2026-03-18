from typing import Optional, List, Any

class Hub:
    def __init__(
            self, hub_type: str, name: str, x: int, y: int,
            extras: Optional[str] = None):
        self.name = name
        self.hub_type = hub_type[:-1]
        self.x = int(x)
        self.y = int(y)
        self.color = ""
        self.max_drones = 1
        self.zone = 'normal'
        self.process_extras(extras) if extras else None
        self.block = None
        self.drones_amount = 0
        self.connections: List[Any] = []

    def process_extras(self, extras: str) -> None:
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
                raise ValueError("Wrong format")

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}:"
                f" name = {self.name}: type = {self.hub_type}:"
                f" x = {self.x}, y = {self.y}, color = {self.color},"
                f" max_drones = {self.max_drones}, zone = {self.zone}")
