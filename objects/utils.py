import math
from copy import copy
from typing import Tuple, Sequence, Any, List

import pygame

from objects import Drone, Connection, Window


class Utils:

    def get_start_pos(
            self,
            connection: Connection, x_min: int, scale: int, y_min: int,
            start_y_divider: int, start_y_offset: int) -> tuple[int, int]:
        """Function returning x andy to beginning of connection."""
        return (
            (connection.start.x - x_min) * scale + scale // 2,
            (connection.start.y - y_min) * scale + scale
            // start_y_divider + start_y_offset
        )

    def get_end_pos(
            self,
            connection: Connection, x_min: int, scale: int, y_min: int,
            end_y_divider: int, end_y_offset: int) -> tuple[int, int]:
        """Function returning x and y to end of connection."""
        return (
            (connection.end.x - x_min) * scale + scale // 2,
            (connection.end.y - y_min) * scale + scale
            // end_y_divider + end_y_offset
        )

    def set_drones_coordinates_when_in_the_middle(
            self,
            drones: List[Drone], win: Window,
            current_frame: int) -> None:
        """
        Function set the coordinates to drones
        where they will be rendered on the screen.
        Only for drones which are on the connection.
        """
        for drone in drones:
            if isinstance(drone.place, Connection):
                start_hubs = drone.place.start.block.hubs
                end_hubs = drone.place.end.block.hubs
                start_y_divider = 2 * len(start_hubs)
                start_idx = start_hubs.index(drone.place.start)
                end_idx = end_hubs.index(drone.place.end)
                start_y_offset = win.scale // len(start_hubs) * start_idx
                end_y_divider = 2 * len(end_hubs)
                end_y_offset = win.scale // len(end_hubs) * end_idx
                cx = (((drone.place.start.x - win.x_min)
                       * win.scale + win.scale // 2) + (
                              (drone.place.end.x - win.x_min)
                              * win.scale + win.scale // 2)) // 2
                cy = (((drone.place.start.y - win.y_min)
                       * win.scale + win.scale
                       // start_y_divider + start_y_offset)
                      + (
                              (drone.place.end.y - win.y_min)
                              * win.scale + win.scale // end_y_divider
                              + end_y_offset)) // 2
                if current_frame == 0:
                    drone.prev_x = copy(drone.x)
                    drone.prev_y = copy(drone.y)
                    drone.x = cx
                    drone.y = cy

    def set_drones_coordinates(
            self,
            surface: Any, x: int, y: int, size: int, count: int,
            color: tuple[int, int, int], drones: int,
            drones_here: List[Drone], current_frame: int) -> None:
        """
        Function set the coordinates to drones
        where they will be rendered on the screen.
        Only for drones which are on the hub.
        """
        if count <= 0:
            return

        grid = math.ceil(math.sqrt(drones))
        cell = size / grid
        radius = int(cell * 0.4)

        drawn = 0
        for row in range(grid):
            for col in range(grid):
                if drawn >= count:
                    return
                cx = x + col * cell + cell / 2
                cy = y + row * cell + cell / 2
                pygame.draw.circle(
                    surface, pygame.Color("black"),
                    (int(cx), int(cy)), radius + 1)
                pygame.draw.circle(surface, color, (int(cx), int(cy)), radius)
                if drawn < len(drones_here) and current_frame == 0:
                    drones_here[drawn].prev_x = copy(drones_here[drawn].x)
                    drones_here[drawn].prev_y = copy(drones_here[drawn].y)
                    drones_here[drawn].x = int(cx)
                    drones_here[drawn].y = int(cy)
                drawn += 1

    def compute_weighted_position(
            self,
            p1: tuple[int, int],
            p2: tuple[int | None, int | None],
            frame: int, total_frames: int) -> tuple[float, float]:
        """
        Function that returns coordinates to draw drone
        depending on actually rendered frame.
        """
        if (p2[0] is None or p2[1] is None
                or (p2[0] == 0 and p2[1] == 0) or p1 == p2):
            return p1

        x1 = float(p2[0])
        y1 = float(p2[1])
        x2 = float(p1[0])
        y2 = float(p1[1])

        t = frame / total_frames

        x = x1 * (1 - t) + x2 * t
        y = y1 * (1 - t) + y2 * t
        return x, y

    def choose_color(self, brightness: int) -> Tuple[int, int, int]:
        """Choosing color function, to make text readable"""
        if brightness >= (255 * 3) // 2:
            return 0, 0, 0
        return 255, 255, 255

    def choose_hub_color(self, zone: str) \
            -> (pygame.Color | int | str | tuple[int, int, int]
                | tuple[int, int, int, int] | Sequence[int]):
        """Choosing hub color function, to recognize the zone."""
        if zone == "normal":
            return "yellow"
        elif zone == "priority":
            return "green"
        elif zone == "restricted":
            return "orange"
        elif zone == "blocked":
            return "red"
        else:
            return "None"
