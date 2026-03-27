import math
import sys
from copy import copy
from typing import List, Any, Dict, Tuple, Sequence, Union

import pygame
from objects import Block, Connection, Drone, Hub, Parser, Window
from objects.draw import Draw


def set_drones_coordinates(
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
            cx = x + col * cell + cell/2
            cy = y + row * cell + cell/2
            pygame.draw.circle(
                surface, pygame.Color("black"),
                (int(cx), int(cy)), radius+1)
            pygame.draw.circle(surface, color, (int(cx), int(cy)), radius)
            if drawn < len(drones_here) and current_frame == 0:
                drones_here[drawn].prev_x = copy(drones_here[drawn].x)
                drones_here[drawn].prev_y = copy(drones_here[drawn].y)
                drones_here[drawn].x = int(cx)
                drones_here[drawn].y = int(cy)
            drawn += 1


def loop_checker(hub: Hub, checked_hubs: List[Hub]) -> None:
    """
    Function that checks looped connections and make them
    inactive.
    """
    if any(hub.hub_type == "end_hub" for hub in checked_hubs):
        return
    checked_hubs.append(hub)
    for connection in hub.connections:
        if (connection.start == hub
            and connection.end not in checked_hubs
                and connection.active):
            loop_checker(connection.end, copy(checked_hubs))
        else:
            connection.deactivate()


def finished(drones: List[Drone]) -> bool:
    """Function returning True if all drones are on the end_hub."""
    for drone in drones:
        if (isinstance(drone.place, Connection)
                or drone.place.hub_type != "end_hub"
                or drone.x != drone.prev_x):
            return False
    return True


def dead_end_checker(
        hubs: List[Hub], connections: List[Connection]
) -> None:
    """
    Function finding dead ended connection and
    deactivating them.
    """
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


def get_start_pos(
        connection: Connection, x_min: int, scale: int, y_min: int,
        start_y_divider: int, start_y_offset: int) -> tuple[int, int]:
    """Function returning x andy to beginning of connection."""
    return (
        (connection.start.x - x_min) * scale + scale // 2,
        (connection.start.y - y_min) * scale + scale
        // start_y_divider + start_y_offset
    )


def get_end_pos(
        connection: Connection, x_min: int, scale: int, y_min: int,
        end_y_divider: int, end_y_offset: int) -> tuple[int, int]:
    """Function returning x and y to end of connection."""
    return (
        (connection.end.x - x_min) * scale + scale // 2,
        (connection.end.y - y_min) * scale + scale
        // end_y_divider + end_y_offset
    )


def draw_connections(
        connections: List[Connection], win: Window) -> None:
    """Function drawing connection between hubs."""
    for connection in connections:
        start_hubs = connection.start.block.hubs
        end_hubs = connection.end.block.hubs
        start_idx = start_hubs.index(connection.start)
        end_idx = end_hubs.index(connection.end)
        start_y_divider = 2 * len(start_hubs)
        start_y_offset = win.scale // len(start_hubs) * start_idx
        end_y_divider = 2 * len(end_hubs)
        end_y_offset = win.scale // len(end_hubs) * end_idx
        start_pos = get_start_pos(
            connection, win.x_min, win.scale, win.y_min,
            start_y_divider, start_y_offset)
        end_pos = get_end_pos(
            connection, win.x_min, win.scale, win.y_min,
            end_y_divider, end_y_offset)
        if connection.end.zone == 'priority':
            pygame.draw.line(
                win.screen, pygame.Color("green"),
                start_pos, end_pos, 10 if connection.active else 1)
        elif connection.end.zone == 'normal':
            pygame.draw.line(
                win.screen, pygame.Color("yellow"), start_pos, end_pos,
                10 if connection.active else 1)
        elif connection.end.zone == 'restricted':
            pygame.draw.line(
                win.screen, pygame.Color("orange"), start_pos, end_pos,
                10 if connection.active else 1)
        elif connection.end.zone == 'blocked':
            pygame.draw.line(
                win.screen, pygame.Color("red"), start_pos, end_pos,
                10 if connection.active else 1)


def draw_hubs(draw: Draw,
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
                    square_x = win.scale * (block.hubs[i].x - win.x_min) + win.scale // 8
                    square_y = (win.scale * (block.hubs[i].y - win.y_min) + win.scale // 8
                                + (win.scale // 4 * 3 - 4) * i)
                    block.hubs[i].draw(win.screen, win.square_size, square_x, square_y)
                    set_drones_coordinates(
                        win.screen, square_x + 2, square_y + 2, win.square_size - 8,
                        block.hubs[i].max_drones, (255, 255, 255),
                        len(drones), drones_here, current_frame)
                    brightness = sum(the_colors[block.hubs[i].color][:3])
                    draw.show_text(
                        win, font, block.hubs[i].name,
                        draw.utils.choose_color(brightness),
                        win.scale * (block.hubs[i].x - win.x_min) + win.scale // 2,
                        win.scale * (block.hubs[i].y - win.y_min + i) + win.scale
                        // 2)


def draw_connections_stops(
        connections: List[Connection], win: Window) -> None:
    """
    Function that draws place for drones which are
    between two hubs
    (only when connection destination is restricted hub)
    """
    for connection in connections:
        if connection.end.zone == "restricted":
            start_hubs = connection.start.block.hubs
            end_hubs = connection.end.block.hubs
            start_y_divider = 2 * len(start_hubs)
            start_idx = start_hubs.index(connection.start)
            end_idx = end_hubs.index(connection.end)
            start_y_offset = win.scale // len(start_hubs) * start_idx
            end_y_divider = 2 * len(end_hubs)
            end_y_offset = win.scale // len(end_hubs) * end_idx
            cx = (((connection.start.x - win.x_min) * win.scale + win.scale // 2) + (
                    (connection.end.x - win.x_min) * win.scale + win.scale // 2)) // 2
            cy = (((connection.start.y - win.y_min)
                   * win.scale + win.scale // start_y_divider + start_y_offset)
                  + ((connection.end.y - win.y_min) * win.scale
                     + win.scale // end_y_divider + end_y_offset)) // 2
            pygame.draw.circle(
                win.screen, pygame.Color("black"),
                (int(cx), int(cy)), win.radius + 1)
            pygame.draw.circle(
                win.screen, pygame.Color("pink"),
                (int(cx), int(cy)), win.radius)





def set_drones_coordinates_when_in_the_middle(
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
                   * win.scale + win.scale // start_y_divider + start_y_offset)
                  + (
                          (drone.place.end.y - win.y_min)
                          * win.scale + win.scale // end_y_divider
                          + end_y_offset)) // 2
            if current_frame == 0:
                drone.prev_x = copy(drone.x)
                drone.prev_y = copy(drone.y)
                drone.x = cx
                drone.y = cy


def make_moves(
        drones: List[Drone], connections: List[Connection]
) -> tuple[int, int]:
    """Loop which allows each drone to one move."""
    moved = True
    res = False
    counter = 0
    while moved:
        moved = False
        for drone in drones:
            if not drone.moved:
                moved = True if drone.move() else moved
                counter += 1 if moved else counter
                res = True if moved else res
    for connection in connections:
        connection.trips_reset()
    print("")
    return 0 if res else 1, counter


def put_hubs_to_block(
        win: Window, hubs: List[Hub]) -> List[List[Block]]:
    """Function that puts each hub to its block."""
    blocks = []
    for y in range(win.y_min, win.y_max + 1):
        blocks_line = []
        for x in range(win.x_min, win.x_max + 1):
            block = Block(x, y)
            for hub in hubs:
                if x == hub.x and y == hub.y:
                    block.add_hub(hub)
                    hub.block = block
            blocks_line.append(block)
        blocks.append(blocks_line)
    return blocks


def main() -> None:
    """
    Main program function.
    1. Parsing file.
    2. Initializing pygame
    3. Getting screen size
    4. Finding map corners coordinates.
    5. Setting scale,
    6. Setting pygame data.
    7. Rendering project in loop.
    """
    try:
        hubs, connections, drones = Parser().parse_file(sys.argv)
        pygame.init()
        win = Window(hubs, drones)
        draw = Draw()
        pygame.display.set_caption("Fly-in")
        loop_checker(hubs[0], [])
        dead_end_checker(hubs, connections)
        blocks = put_hubs_to_block(win, hubs)
        clock = pygame.time.Clock()
        the_colors = pygame.color.THECOLORS
        counter = 0
        current_frame = 0
        counter_printed = False
        move_not_made = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            draw.draw_grid(win)
            draw_connections(connections, win)
            draw_hubs(draw, blocks, drones, win, the_colors, win.font, current_frame)
            draw_connections_stops(connections, win)
            set_drones_coordinates_when_in_the_middle(drones, win, current_frame)
            draw.draw_drones(drones, win.font, win, current_frame, the_colors)
            draw.show_text(
                win, win.font_counter, str(counter),
                pygame.Color("white"), 20, (win.size_y * win.scale) - 20)
            pygame.display.flip()
            current_frame = (current_frame + 1) % win.fps
            if current_frame == 0 and not finished(drones):
                drones.sort(key=lambda dron: dron.moves, reverse=True)
                result, moves_counter = make_moves(drones, connections)
                move_not_made += result
                counter = counter + 1 if result == 0 else counter
            for drone in drones:
                drone.moved = False
            if finished(drones) and not counter_printed:
                print(counter)
                counter_printed = True
            if move_not_made == 3 and not finished(drones):
                print("Finish impossible")
                sys.exit(1)
            clock.tick(60)
    except Exception as e:
        print(e)
        sys.exit(1)
    except ZeroDivisionError:
        print("Error: Amount of drones must be above 0")
        sys.exit(1)


if __name__ == '__main__':
    main()
