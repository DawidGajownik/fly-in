import math
import sys
from copy import copy

import pygame
from objects import *


def handle_file(filename):
    hubs = []
    connections = []
    drones_amount = 0
    drones = []
    try:
        if len(sys.argv) <3:
            with open(filename) as f:
                file_content = f.read().splitlines()
                for line in file_content:
                    if not line.startswith("#") and line.strip() != "":
                        parts = line.split()
                        if parts[0] == "nb_drones:":
                            drones_amount = int(parts[1])
                        elif parts[0] == "hub:" or parts[0] == "start_hub:" or parts[0] == "end_hub:":
                            hub = Hub(*parts[:4], " ".join(parts[4:]))
                            if parts[0] == "start_hub:" or parts[0] == "end_hub:":
                                hub.max_drones = drones_amount
                            hubs.append(hub)
                        elif parts[0] == "connection:":
                            start_str, end_str = parts[1].split("-")
                            start_list = [hub for hub in hubs if hub.name == start_str]
                            end_list = [hub for hub in hubs if hub.name == end_str]
                            start = start_list[0]
                            end = end_list[0]
                            connection = Connection(start, end, parts[2:][0] if parts[2:] != [] else None)
                            connections.append(connection)
                            start.connections.append(connection)
                        else:
                            return None
        else:
            print("Too many arguments\nUsage: python fly_in.py <filename>")
    except IndexError:
        print("No argument passed\nUsage: python fly_in.py <filename>")
    except FileNotFoundError as e:
        print(f"File \"{e.filename}\" not found")
    start_hub = [hub for hub in hubs if hub.hub_type == "start_hub"][0]
    all_colors = list(pygame.color.THECOLORS.keys())
    colors_length = len(all_colors)
    for i in range(1, drones_amount + 1):
        drones.append(Drone(start_hub, i, all_colors, colors_length))
    return hubs, connections, drones

def draw_circles_in_square(surface, x, y, size, count, color, drones, drones_here):
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
            cx = x + col * cell + cell/2
            cy = y + row * cell + cell/2
            pygame.draw.circle(surface, pygame.Color("black"), (int(cx), int(cy)), radius+1)
            pygame.draw.circle(surface, color, (int(cx), int(cy)), radius)
            font = pygame.font.Font(None, 15)
            if drawn < len(drones_here):
                pygame.draw.circle(surface, pygame.Color(drones_here[drawn].color), (int(cx), int(cy)), radius-2)
                text = font.render(str(drones_here[drawn].idx), True, (0, 0, 0))
                text_r = text.get_rect(center=(int(cx), int(cy)))
                surface.blit(text, text_r)
            drawn += 1

def loop_checker(hub, checked_hubs):
    if any(hub.hub_type == "end_hub" for hub in checked_hubs):
        return
    checked_hubs.append(hub)
    for connection in hub.connections:
        if connection.start == hub and connection.end not in checked_hubs and connection.active:
            loop_checker(connection.end, copy(checked_hubs))
        else:
            connection.deactivate()

def finished(drones):
    for drone in drones:
        if isinstance(drone.place, Connection) or drone.place.hub_type != "end_hub":
            return False
    return True

def dead_end_checker(hubs, connections):
    still_removing = True
    while still_removing:
        still_removing = False
        for hub in hubs:
            if hub.hub_type != "end_hub":
                has_end = False
                for connection in hub.connections:
                    if connection.start == hub and connection.active:
                        has_end = True
                if not has_end:
                    for connection in connections:
                        if connection.end == hub and connection.active:
                            connection.deactivate()
                            still_removing = True

def draw_connections(connections, scale, screen, x_min, y_min):
    for connection in connections:
        start_hubs = connection.start.block.hubs
        end_hubs = connection.end.block.hubs
        start_idx = start_hubs.index(connection.start)
        end_idx = end_hubs.index(connection.end)
        start_y_divider = 2 * len(start_hubs)
        start_y_offset = scale // len(start_hubs) * start_idx
        end_y_divider = 2 * len(end_hubs)
        end_y_offset = scale // len(end_hubs) * end_idx
        # if connection.active:
        if connection.end.zone == 'priority':
            # and connection.start.zone != 'restricted' and connection.end.zone != 'restricted')\
            pygame.draw.line(
                screen, pygame.Color("pink"),
                (
                    (connection.start.x - x_min) * scale + scale // 2,
                    (connection.start.y - y_min) * scale + scale // start_y_divider + start_y_offset
                ),
                (
                    (connection.end.x - x_min) * scale + scale // 2,
                    (connection.end.y - y_min) * scale + scale // end_y_divider + end_y_offset
                ), 10 if connection.active else 1)
        elif connection.end.zone != 'restricted':
            pygame.draw.line(screen, pygame.Color("black"), ((connection.start.x - x_min) * scale + scale // 2, (
                        connection.start.y - y_min) * scale + scale // start_y_divider + start_y_offset),
                             ((connection.end.x - x_min) * scale + scale // 2,
                              (connection.end.y - y_min) * scale + scale // end_y_divider + end_y_offset),
                             10 if connection.active else 1)
        else:
            pygame.draw.line(screen, pygame.Color("red"), ((connection.start.x - x_min) * scale + scale // 2, (
                        connection.start.y - y_min) * scale + scale // start_y_divider + start_y_offset),
                             ((connection.end.x - x_min) * scale + scale // 2,
                              (connection.end.y - y_min) * scale + scale // end_y_divider + end_y_offset),
                             10 if connection.active else 1)

def draw_hubs(blocks, drones, scale, x_min, y_min, screen, square_size, the_colors, font):
    for line in blocks:
        for block in line:
            if len(block.hubs) > 0:
                for i in range(0, len(block.hubs)):
                    drones_here = []
                    for drone in drones:
                        if drone.place == block.hubs[i]:
                            drones_here.append(drone)
                    zone = block.hubs[i].zone
                    square_x = scale * (block.hubs[i].x - x_min) + scale // 8
                    square_y = scale * (block.hubs[i].y - y_min) + scale // 8 + (scale // 4 * 3 - 4) * i

                    color = "orange" if zone == "normal" else "red" if zone == "restricted" else "green" if zone == "priority" else "gray" if zone == "blocked" else None
                    pygame.draw.rect(
                        screen,
                        pygame.Color(color),
                        (scale * (block.hubs[0].x - x_min) + scale // 8,
                         scale * (block.hubs[0].y - y_min) + scale // 8,
                         (scale // 4) * 3, (scale // 4) * 3))
                    try:
                        pygame.draw.rect(
                            screen, pygame.Color(block.hubs[i].color),
                            (square_x + 2, square_y + 2, square_size - 8, (square_size - 8)))
                    except ValueError:
                        block.hubs[i].color = "pink"
                        pygame.draw.rect(
                            screen, pygame.Color(block.hubs[i].color),
                            (square_x + 2, square_y + 2, square_size - 8, (square_size - 8)))
                    draw_circles_in_square(screen, square_x + 2, square_y + 2, square_size - 8,
                                           block.hubs[i].max_drones, (255, 255, 255), len(drones), drones_here)
                    brightness = sum(the_colors[block.hubs[i].color][:3])
                    text_2 = font.render(block.hubs[i].name, True,
                                         (0, 0, 0) if brightness >= (255 * 3) // 2 else (255, 255, 255))
                    text_2_r = text_2.get_rect(
                        center=(scale * (block.hubs[i].x - x_min) + scale // 2,
                                scale * (block.hubs[i].y - y_min) + (scale) // 2 + scale * i))
                    screen.blit(text_2, text_2_r)

def draw_connections_stops(connections, scale, screen, x_min, y_min, radius):
    for connection in connections:
        if connection.end.zone == "restricted":
            start_hubs = connection.start.block.hubs
            end_hubs = connection.end.block.hubs
            start_y_divider = 2 * len(start_hubs)
            start_idx = start_hubs.index(connection.start)
            end_idx = end_hubs.index(connection.end)
            start_y_offset = scale // len(start_hubs) * start_idx
            end_y_divider = 2 * len(end_hubs)
            end_y_offset = scale // len(end_hubs) * end_idx
            cx = (((connection.start.x - x_min) * scale + scale // 2) + (
                    (connection.end.x - x_min) * scale + scale // 2)) // 2
            cy = (((connection.start.y - y_min) * scale + scale // start_y_divider + start_y_offset) + (
                    (connection.end.y - y_min) * scale + scale // end_y_divider + end_y_offset)) // 2
            pygame.draw.circle(screen, pygame.Color("black"), (int(cx), int(cy)), radius + 1)
            pygame.draw.circle(screen, pygame.Color("white"), (int(cx), int(cy)), radius)

def draw_drones(drones, scale, screen, x_min, y_min, radius, font):
    for dron in drones:
        if isinstance(dron.place, Connection):
            start_hubs = dron.place.start.block.hubs
            end_hubs = dron.place.end.block.hubs
            start_y_divider = 2 * len(start_hubs)
            start_idx = start_hubs.index(dron.place.start)
            end_idx = end_hubs.index(dron.place.end)
            start_y_offset = scale // len(start_hubs) * start_idx
            end_y_divider = 2 * len(end_hubs)
            end_y_offset = scale // len(end_hubs) * end_idx
            cx = (((dron.place.start.x - x_min) * scale + scale // 2) + (
                        (dron.place.end.x - x_min) * scale + scale // 2)) // 2
            cy = (((dron.place.start.y - y_min) * scale + scale // start_y_divider + start_y_offset) + (
                        (dron.place.end.y - y_min) * scale + scale // end_y_divider + end_y_offset)) // 2
            pygame.draw.circle(screen, dron.color, (cx, cy), radius - 2)
            text = font.render(str(dron.idx), True, (0, 0, 0))
            text_r = text.get_rect(center=(int(cx), int(cy)))
            screen.blit(text, text_r)

def make_moves(drones, connections, asdi):
    if not finished(drones):
        for drone in drones:
            drone.move()
        asdi = asdi + 1
        for connection in connections:
            connection.trips_reset()
        print("")
    else:
        print(f"{asdi}")

def put_hubs_to_block(y_min, y_max, x_min, x_max, hubs):
    blocks = []
    for y in range(y_min, y_max + 1):
        blocks_line = []
        for x in range(x_min, x_max + 1):
            block = Block(x, y)
            for hub in hubs:
                if x == hub.x and y == hub.y:
                    block.add_hub(hub)
                    hub.block = block
            blocks_line.append(block)
        blocks.append(blocks_line)
    return blocks

def main():
    pygame.init()
    hubs, connections, drones = handle_file(sys.argv[1])
    width = pygame.display.Info().current_w
    height = pygame.display.Info().current_h
    x_min = 0
    y_min = 0
    x_max = 0
    y_max = 0
    for hub in hubs:
        if hub.x > x_max:
            x_max = hub.x
        if hub.y > y_max:
            y_max = hub.y
        if hub.x < x_min:
            x_min = hub.x
        if hub.y < y_min:
            y_min = hub.y
    size_x, size_y = x_max - x_min + 1, y_max - y_min + 1
    scale = width // size_x if width // size_x < height // size_y else height // size_y
    screen = pygame.display.set_mode((size_x * scale, size_y * scale))
    pygame.display.set_caption("Fly-in")
    font = pygame.font.Font(None, 15)
    loop_checker(hubs[0], [])
    dead_end_checker(hubs, connections)
    blocks = put_hubs_to_block(y_min, y_max, x_min, x_max, hubs)
    clock = pygame.time.Clock()
    the_colors = pygame.color.THECOLORS
    asdi = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(pygame.Color("white"))
        draw_connections(connections, scale, screen, x_min, y_min)
        square_size = scale - scale // 4
        draw_hubs(blocks, drones, scale, x_min, y_min, screen, square_size, the_colors, font)
        grid = math.ceil(math.sqrt(len(drones)))
        cell = (square_size - 8) / grid
        radius = int(cell * 0.4)
        draw_connections_stops(connections, scale, screen, x_min, y_min, radius)
        draw_drones(drones, scale, screen, x_min, y_min, radius, font)
        pygame.display.flip()
        clock.tick(1)
        make_moves(drones, connections, asdi)

if __name__ == '__main__':
    main()