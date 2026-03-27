import math
from typing import List
import pygame

from objects import Hub, Drone


class Window:
    def __init__(self, hubs: List[Hub], drones: List[Drone]) -> None:
        """Initializing window"""
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h
        self.x_min = 0
        self.y_min = 0
        self.x_max = 0
        self.y_max = 0
        self.scale = 0
        self.set_corners(hubs)
        self.size_x, self.size_y = (
            self.x_max - self.x_min + 1, self.y_max - self.y_min + 2)
        self.set_scale()
        self.screen = pygame.display.set_mode(
            (self.size_x * self.scale, self.size_y * self.scale))
        self.square_size = self.scale - self.scale // 4
        self.grid = math.ceil(math.sqrt(len(drones)))
        self.cell = (self.square_size - 8) / self.grid
        self.radius = int(self.cell * 0.4)
        self.fps = 60
        self.font = pygame.font.Font(None, 15)
        self.font_counter = pygame.font.Font(None, 25)

    def set_corners(self, hubs: List[Hub]) -> None:
        """finding minimal/maximal coordinates for hubs"""
        for hub in hubs:
            if hub.x > self.x_max:
                self.x_max = hub.x
            if hub.y > self.y_max:
                self.y_max = hub.y
            if hub.x < self.x_min:
                self.x_min = hub.x
            if hub.y < self.y_min:
                self.y_min = hub.y

    def set_scale(self) -> None:
        """Setting scale"""
        if self.width // self.size_x < self.height // self.size_y:
            self.scale = self.width // self.size_x - 1
        else:
            self.scale = self.height // self.size_y - 1
