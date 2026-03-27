from typing import List, Any, Union, Dict
import pygame
from objects import Drone, Window, Block, Connection
from objects.utils import Utils


class Draw:

    """Draw class"""

    def __init__(self) -> None:
        self.utils = Utils()

    def render(
            self, win: Window, connections: List[Connection],
            blocks: List[List[Block]], drones: List[Drone],
            the_colors: Dict[str, tuple[int, int, int, int]],
            current_frame: int, counter: int) -> None:
        """Function starting every drawing function in order."""
        self.draw_grid(win)
        self.draw_connections(connections, win)
        self.draw_hubs(
            blocks, drones, win, the_colors, win.font, current_frame)
        self.draw_connections_stops(connections, win)
        self.utils.set_drones_coordinates_when_in_the_middle(
            drones, win, current_frame)
        self.draw_drones(drones, win.font, win, current_frame, the_colors)
        self.show_text(
            win, win.font_counter, str(counter),
            pygame.Color("white"), 20, (win.size_y * win.scale) - 20)
        pygame.display.flip()

    def draw_connections(
            self,
            connections: List[Connection], win: Window) -> None:
        """Function drawing connection between hubs."""
        for connection in connections:
            connection.draw(
                win, self.utils.get_start_pos, self.utils.get_end_pos)

    def draw_connections_stops(
            self,
            connections: List[Connection], win: Window) -> None:
        """
        Function that draws place for drones which are
        between two hubs
        (only when connection destination is restricted hub)
        """
        for connection in connections:
            if connection.end.zone == "restricted":
                connection.draw_stops(win)

    def draw_hubs(
            self,
            blocks: List[List[Block]], drones: List[Drone], win: Window,
            the_colors: Dict[str, tuple[int, int, int, int]],
            font: Any, current_frame: int) -> None:
        """
        Drawing hub function.
        Setting coordinates for drones.
        """
        for line in blocks:
            for block in line:
                if len(block.hubs) > 0:
                    for i in range(0, len(block.hubs)):
                        drones_here = []
                        for drone in drones:
                            if drone.place == block.hubs[i]:
                                drones_here.append(drone)
                        square_x = (win.scale *
                                    (block.hubs[i].x - win.x_min)
                                    + win.scale // 8)
                        square_y = (
                                win.scale * (block.hubs[i].y - win.y_min)
                                + win.scale // 8
                                + (win.scale // 4 * 3 - 4) * i)
                        block.hubs[i].draw(
                            win.screen, win.square_size, square_x,
                            square_y, self.utils.choose_hub_color)
                        self.utils.set_drones_coordinates(
                            win.screen, square_x + 2,
                            square_y + 2, win.square_size - 8,
                            block.hubs[i].max_drones, (255, 255, 255),
                            len(drones), drones_here, current_frame)
                        brightness = sum(the_colors[block.hubs[i].color][:3])
                        self.show_text(
                            win, font, block.hubs[i].name,
                            self.utils.choose_color(brightness),
                            win.scale * (block.hubs[i].x
                                         - win.x_min) + win.scale // 2,
                            win.scale * (block.hubs[i].y
                                         - win.y_min + i) + win.scale
                            // 2)

    def draw_drones(
            self,
            drones: List[Drone], font: Any, win: Window,
            frame: int,
            the_colors: dict[str, tuple[int, int, int, int]]) -> None:
        """Drawing drones function."""
        frame = int(frame * 1.2)
        if frame > win.fps:
            frame = win.fps
        for drone in drones:
            brightness = sum(the_colors[drone.color][:3])
            x, y = self.utils.compute_weighted_position(
                (drone.x, drone.y),
                (drone.prev_x, drone.prev_y),
                frame, win.fps)
            pygame.draw.circle(win.screen, drone.color, (x, y), win.radius - 2)
            self.show_text(
                win, font, str(drone.idx),
                self.utils.choose_color(brightness), x, y)

    def draw_grid(self, win: Window) -> None:
        """Drawing grid"""
        win.screen.fill(pygame.Color("darkblue"))
        for i in range(1, win.width):
            if i % 40 == 0:
                pygame.draw.line(
                    win.screen, pygame.Color("blue"),
                    (i, 0), (i, win.height), 1)
        for i in range(1, win.height):
            if i % 40 == 0:
                pygame.draw.line(
                    win.screen, pygame.Color("blue"),
                    (0, i), (win.width, i), 1)

    def show_text(
            self,
            win: Window, font: Any, content: str,
            color: Any, x: Union[float, int],
            y: Union[float, int]) -> None:
        """Function to handle all pygame functions necessary to show text."""
        text = font.render(
            content, True, color)
        text_r = text.get_rect(center=(x, y))
        win.screen.blit(text, text_r)
