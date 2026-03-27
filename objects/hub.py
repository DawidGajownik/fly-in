from typing import List, Any, Union
import pygame
from objects.utils import Utils


class Hub:
    """Hub class."""

    def __init__(
            self, hub_type: str, name: str, x: str, y: str,
            extras: Union[str, None]):
        """__init__ function. Brief description."""
        self.utils = Utils()
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

    def draw(
            self, screen: Any, size: int,
            x: int, y: int) -> None:
        """Function drawing single hub."""
        zone = self.zone
        color = self.utils.choose_hub_color(zone)
        try:
            pygame.draw.rect(  # out border
                screen, pygame.Color("black"),
                (x - 5, y - 5, size + 10, size + 10),
                border_radius=20)
            pygame.draw.rect(  # frame
                screen, pygame.Color(color),
                (x - 4, y - 4, size + 8, size + 8),
                border_radius=20)
            pygame.draw.rect(  # in border
                screen, pygame.Color("black"),
                (x - 1, y - 1, size + 2, size + 2),
                border_radius=20)
            pygame.draw.rect(  # hub
                screen, pygame.Color(self.color),
                (x, y, size, size),
                border_radius=20)
        except ValueError:
            self.color = "pink"
            pygame.draw.rect(
                screen, pygame.Color(self.color),
                (x + 2, y + 2, size - 8, size - 8),
                border_radius=20)

    def process_extras(self, extras: str) -> None:
        """
        process_extras function. A function that handles
        additional parameters from the map file and converts
        them into object parameters.
        """
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
                        f"Too many color attributes for line \"{extras}\""
                    )
            elif line.split("=")[0] == "max_drones":
                if not max_drones:
                    max_drones = True
                    self.max_drones = int(line.split("=")[1])
                    if self.max_drones < 1:
                        raise ValueError(
                            "Amount of drones cannot be less than 1."
                        )
                else:
                    raise ValueError(
                        f"Too many max_drones attributes for line \"{extras}\""
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
