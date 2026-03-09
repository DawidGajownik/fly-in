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
                            connection = Connection(start, end)
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

def main():
    hubs, connections, drones = handle_file(sys.argv[1])
    pygame.init()
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
    blocks = []
    checked_hubs = []
    loop_checker(hubs[0], checked_hubs)
    # for hub in checked_hubs:
    #     print('checked', hub)
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
                            #if connection in connection.start.connections:
                                #connection.start.connections.remove(connection)
                            #connections.remove(connection)
                            still_removing = True
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
    # for line in blocks:
    #     for block in line:
    #         print(block)
    clock = pygame.time.Clock()
    the_colors = pygame.color.THECOLORS
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(pygame.Color("white"))
        for connection in connections:
            start_hubs = connection.start.block.hubs
            end_hubs = connection.end.block.hubs
            start_idx = start_hubs.index(connection.start)
            end_idx = end_hubs.index(connection.end)
            start_y_divider = 2 * len(start_hubs)
            start_y_offset = scale//len(start_hubs) * start_idx
            end_y_divider = 2 * len(end_hubs)
            end_y_offset = scale//len(end_hubs) * end_idx
            # if connection.active:
            if connection.end.zone == 'priority' and connection.start.zone != 'restricted' and connection.end.zone != 'restricted':
                pygame.draw.line(screen, pygame.Color("pink"), ((connection.start.x - x_min) * scale + scale//2, (connection.start.y - y_min) * scale + scale//start_y_divider + start_y_offset), ((connection.end.x - x_min) * scale + scale//2, (connection.end.y - y_min) * scale + scale//end_y_divider + end_y_offset), 10 if connection.active else 1)
            elif connection.start.zone != 'restricted' and connection.end.zone != 'restricted':
                pygame.draw.line(screen, pygame.Color("black"), ((connection.start.x - x_min) * scale + scale//2, (connection.start.y - y_min) * scale + scale//start_y_divider + start_y_offset), ((connection.end.x - x_min) * scale + scale//2, (connection.end.y - y_min) * scale + scale//end_y_divider + end_y_offset), 10 if connection.active else 1)
            else:
                pygame.draw.line(screen, pygame.Color("red"), ((connection.start.x - x_min) * scale + scale//2, (connection.start.y - y_min) * scale + scale//start_y_divider + start_y_offset), ((connection.end.x - x_min) * scale + scale//2, (connection.end.y - y_min) * scale + scale//end_y_divider + end_y_offset), 10 if connection.active else 1)
            # else:
            #     pygame.draw.line(screen, pygame.Color("gray"), ((connection.start.x - x_min) * scale + scale // 2, (
            #                 connection.start.y - y_min) * scale + scale // start_y_divider + start_y_offset),
            #                      ((connection.end.x - x_min) * scale + scale // 2,
            #                       (connection.end.y - y_min) * scale + scale // end_y_divider + end_y_offset), 3)

        for line in blocks:
            for block in line:
                if len(block.hubs) > 0:
                    for i in range(0, len(block.hubs)):
                        #drones_amount = 0
                        drones_here = []
                        for drone in drones:
                            if drone.hub == block.hubs[i]:
                                drones_here.append(drone)
                                #drones_amount +=1
                        zone = block.hubs[i].zone
                        square_x = scale * (block.hubs[i].x - x_min) + scale//8
                        square_y = scale * (block.hubs[i].y - y_min) + scale//8 + (scale//4*3 - 4)//len(block.hubs)*i
                        square_size = scale - scale//4
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
                                (square_x + 2, square_y + 2, square_size - 8, (square_size - 8)//len(block.hubs)))
                        except ValueError:
                            block.hubs[i].color = "pink"
                            pygame.draw.rect(
                                screen, pygame.Color(block.hubs[i].color),
                                (square_x + 2, square_y + 2, square_size - 8, (square_size - 8)//len(block.hubs)))
                        draw_circles_in_square(screen, square_x + 2, square_y + 2, square_size - 8, block.hubs[i].max_drones, (255, 255, 255), len(drones), drones_here)
                        text_1 = font.render(block.hubs[i].name, True, (0, 0, 0))
                        brightness = sum(the_colors[block.hubs[i].color][:3])
                        text_2 = font.render(block.hubs[i].name, True, (0, 0, 0) if brightness >= (255*3)//2 else (255,255,255))
                        text_3 = font.render("Max drones: " + str(block.hubs[i].max_drones), True, (0, 0, 0))
                        text_1_r = text_1.get_rect(
                            center=(scale * (block.hubs[i].x - x_min) + scale//2,
                                    scale * (block.hubs[i].y - y_min) + (scale//len(block.hubs))//2 +scale//len(block.hubs)*i - 10))
                        text_2_r = text_2.get_rect(
                            center=(scale * (block.hubs[i].x - x_min) + scale//2,
                                    scale * (block.hubs[i].y - y_min) + (scale//len(block.hubs))//2 +scale//len(block.hubs)*i))
                        text_3_r = text_3.get_rect(
                            center=(scale * (block.hubs[i].x - x_min) + scale//2,
                                    scale * (block.hubs[i].y - y_min) + (scale//len(block.hubs))//2 +scale//len(block.hubs)*i + 10))
                        #screen.blit(text_1, text_1_r)
                        screen.blit(text_2, text_2_r)
                        #screen.blit(text_3, text_3_r)

        pygame.display.flip()
        clock.tick(1)
        for drone in drones:
            drone.move()

if __name__ == '__main__':
    main()