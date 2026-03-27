from typing import Tuple, Sequence

import pygame


class Utils:

    def compute_weighted_position(self,
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