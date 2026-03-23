"""Module hub.py. Brief description."""


from typing import List, Any, Union


class Hub:
    """Hub class. Brief description."""

    def __init__(
            self, hub_type: str, name: str, x: str, y: str,
            extras: Union[str, None]):
"""__init__ function. Brief description."""
        self.name = name
        self.hub_type = hub_type[:-1]
        self.x = int(x)
        self.y = int(y)
        self.color = ""
        self.max_drones = 1
        self.zone = 'normal'
        self.process_extras(extras) if extras else None
        self.block: Any = None
        self.drones_amount = 0
        self.connections: List[Any] = []

    def process_extras(self, extras: str) -> None:
"""process_extras function. Brief description."""
        extras = extras.removeprefix("[").removesuffix("]")
        lines = extras.split()
        color = False
        max_drones = False
        zone = False
        for line in lines:
            if line.split("=")[0] == "color":
                if not color:
                    color = True
                    self.color = line.split("=")[1]
                else:
                    raise ValueError(
                        f"Too many color atributes for line \"{extras}\""
                    )
            elif line.split("=")[0] == "max_drones":
                if not max_drones:
                    max_drones = True
                    self.max_drones = int(line.split("=")[1])
                else:
                    raise ValueError(
                        f"Too many max_drones atributes for line \"{extras}\""
                    )
            elif line.split("=")[0] == "zone":
                if not zone:
                    zone = True
                    if line.split("=")[1] in (
                            "normal", "priority", "restricted", "blocked"
                    ):
                        self.zone = line.split("=")[1]
                    else:
                        raise ValueError(
                            f"Invalid zone \"{line.split('=')[1]}\"")
                else:
                    raise ValueError(
                        f"Too many zone atributes for line \"{extras}\""
                    )
            else:
                raise ValueError("Wrong format")

    def __str__(self) -> str:
"""__str__ function. Brief description."""
        return (f"{self.__class__.__name__}:"
                f" name = {self.name}: type = {self.hub_type}:"
                f" x = {self.x}, y = {self.y}, color = {self.color},"
                f" max_drones = {self.max_drones}, zone = {self.zone}")
