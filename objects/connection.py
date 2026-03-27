from typing import Optional, Callable, Any
import pygame

from objects import Hub


class Connection:
    """Connection class. A class representing a connection between hubs."""

    def __init__(
            self, start: Hub, end: Hub,
            extras: Optional[str] = None) -> None:
        """__init__ function."""
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

    def draw(
            self, win: Any, get_start_pos: Callable,
            get_end_pos: Callable) -> None:
        start_hubs = self.start.block.hubs
        end_hubs = self.end.block.hubs
        start_idx = start_hubs.index(self.start)
        end_idx = end_hubs.index(self.end)
        start_y_divider = 2 * len(start_hubs)
        start_y_offset = win.scale // len(start_hubs) * start_idx
        end_y_divider = 2 * len(end_hubs)
        end_y_offset = win.scale // len(end_hubs) * end_idx
        start_pos = get_start_pos(
            self, win.x_min, win.scale, win.y_min,
            start_y_divider, start_y_offset)
        end_pos = get_end_pos(
            self, win.x_min, win.scale, win.y_min,
            end_y_divider, end_y_offset)
        if self.end.zone == 'priority':
            pygame.draw.line(
                win.screen, pygame.Color("green"),
                start_pos, end_pos, 10 if self.active else 1)
        elif self.end.zone == 'normal':
            pygame.draw.line(
                win.screen, pygame.Color("yellow"), start_pos, end_pos,
                10 if self.active else 1)
        elif self.end.zone == 'restricted':
            pygame.draw.line(
                win.screen, pygame.Color("orange"), start_pos, end_pos,
                10 if self.active else 1)
        elif self.end.zone == 'blocked':
            pygame.draw.line(
                win.screen, pygame.Color("red"), start_pos, end_pos,
                10 if self.active else 1)

    def draw_stops(self, win: Any) -> None:
        start_hubs = self.start.block.hubs
        end_hubs = self.end.block.hubs
        start_y_divider = 2 * len(start_hubs)
        start_idx = start_hubs.index(self.start)
        end_idx = end_hubs.index(self.end)
        start_y_offset = win.scale // len(start_hubs) * start_idx
        end_y_divider = 2 * len(end_hubs)
        end_y_offset = win.scale // len(end_hubs) * end_idx
        cx = (((self.start.x - win.x_min) * win.scale + win.scale // 2) + (
                (self.end.x - win.x_min) * win.scale + win.scale // 2)) // 2
        cy = (((self.start.y - win.y_min)
               * win.scale + win.scale // start_y_divider + start_y_offset)
              + ((self.end.y - win.y_min) * win.scale
                 + win.scale // end_y_divider + end_y_offset)) // 2
        pygame.draw.circle(
            win.screen, pygame.Color("black"),
            (int(cx), int(cy)), win.radius + 1)
        pygame.draw.circle(
            win.screen, pygame.Color("pink"),
            (int(cx), int(cy)), win.radius)

    def process_extras(self, extras: str) -> None:
        """
        process_extras function. A function that handles
        additional parameters from the map file and converts
        them into object parameters.
        """
        extras = extras.removeprefix("[").removesuffix("]")
        lines = extras.split()
        for line in lines:
            if line.split("=")[0] == "max_link_capacity":
                if int(line.split("=")[1]) < 1:
                    raise Exception("max_link_capacity must be >= 1")
                self.max_drones = int(line.split("=")[1])
                self.max_trips = int(line.split("=")[1])
            else:
                raise ValueError(
                    "Field can be only 'max_link_capacity'"
                )

    def priority_available(self) -> bool:
        """Function returning true if priority connection is available."""
        return (self.active and self.end.drones_amount
                < self.end.max_drones
                and self.end.zone == "priority"
                and self.can_go())

    def normal_available(self) -> bool:
        """Function returning true if normal connection is available."""
        return (self.active and self.end.drones_amount
                < self.end.max_drones
                and self.end.zone == "normal"
                and self.can_go())

    def restricted_available(self) -> bool:
        """Function returning true if restricted connection is available."""
        result = (
                self.active and self.drones_amount < self.max_drones
                and self.end.zone == "restricted"
                and self.end.max_drones > self.end.drones_amount)
        return result

    def trip(self) -> None:
        """Functions adding trips made in this turn."""
        self.trips += 1

    def trips_reset(self) -> None:
        """Functions resetting trips after the turn."""
        self.trips = 0

    def can_go(self) -> bool:
        """Functions checking ability to go in this turn."""
        return self.trips < self.max_trips

    def deactivate(self) -> None:
        """Functions deactivating connection from usage."""
        self.active = False

    def get_start_pos(
            self, x_min: int, scale: int, y_min: int,
            start_y_divider: int, start_y_offset: int) -> tuple[int, int]:
        """Function returning x andy to beginning of self."""
        return (
            (self.start.x - x_min) * scale + scale // 2,
            (self.start.y - y_min) * scale + scale
            // start_y_divider + start_y_offset
        )

    def get_end_pos(
            self, x_min: int, scale: int, y_min: int,
            end_y_divider: int, end_y_offset: int) -> tuple[int, int]:
        """Function returning x and y to end of self."""
        return (
            (self.end.x - x_min) * scale + scale // 2,
            (self.end.y - y_min) * scale + scale
            // end_y_divider + end_y_offset
        )

    def __str__(self) -> str:
        """__str__ function."""
        return (f"{self.__class__.__name__}:"
                f" {self.start.name} - {self.end.name},"
                f" capacity = {self.max_trips}")
