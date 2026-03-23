"""Module fly_in.py. Brief description."""



import math
import sys
from copy import copy
from typing import List, Any, Dict, Tuple, Union, Sequence

import pygame
from objects import Block, Connection, Drone, Hub


def handle_file(
        args: List[str]
) -> Union[Tuple[List[Hub], List[Connection], List[Drone]]]:
    """handle_file function. Brief description.

    Args:
        args (type): Description.

    Returns:
        Union[Tuple[List[Hub], List[Connection], List[Drone]]]: Description.

    """
    hubs: List[Hub] = []
    connections = []
    drones_amount = 0
    drones = []
    usage = \
        "Usage: python fly_in.py <filename>\n or:\n make run MAP=<filename>"
    if len(args) > 2:
        print("Too many arguments\n", usage)
        sys.exit(1)
    try:
        file = args[1]
        if len(sys.argv) < 3:
            with (open(file) as f):
                file_content = f.read().splitlines()
                for line in file_content:
                    if not line.startswith("#") and line.strip() != "":
                        parts = line.split()
                        if parts[0] == "nb_drones:":
                            drones_amount = int(parts[1])
                        elif parts[0] in ("hub:", "start_hub:", "end_hub:"):
                            extras = " ".join(parts[4:]
                                              )if parts is not None else None
                            try:
                                hub = Hub(
                                    parts[0], parts[1], parts[2],
                                    parts[3], extras)
                            except ValueError as e:
                                print(e, "in line:\n", line)
                                sys.exit(1)
                            if (parts[0] == "start_hub:"
                                    or parts[0] == "end_hub:"):
                                hub.max_drones = drones_amount
                            if (any(hub.hub_type == "start_hub"
                                    for hub in hubs)
                                    and hub.hub_type == "start_hub"):
                                print("Too many start_hubs")
                                sys.exit(1)
                            if (any(hub.hub_type == "end_hub"
                                    for hub in hubs)
                                    and hub.hub_type == "end_hub"):
                                print("Too many end_hubs")
                                sys.exit(1)
                            hubs.append(hub)
                        elif parts[0] == "connection:":
                            start_str, end_str = parts[1].split("-")
                            start_list = [
                                hub for hub in hubs if hub.name == start_str
                            ]
                            end_list = [
                                hub for hub in hubs if hub.name == end_str
                            ]
                            if len(start_list) != 1 or len(end_list) != 1:
                                print("No connection for start or/and end hub")
                                sys.exit(1)
                            try:
                                start = start_list[0]
                            except IndexError:
                                print("No start hub")
                                sys.exit(1)
                            try:
                                end = end_list[0]
                            except IndexError:
                                print("No end hub")
                                sys.exit(1)
                            connection = Connection(
                                start, end,
                                parts[2:][0] if parts[2:] != [] else None)
                            connections.append(connection)
                            start.connections.append(connection)
                        else:
                            print("Wrong line", line)
                            sys.exit(1)
        else:
            print("Too many arguments\nUsage: python fly_in.py <filename>")
            sys.exit(1)
    except FileNotFoundError as e:
        print(f"File \"{e.filename}\" not found")
        sys.exit(1)
    except ValueError as e:
        print("Error -", e)
        sys.exit(1)
    start_hub = [hub for hub in hubs if hub.hub_type == "start_hub"][0]
    all_colors = list(pygame.color.THECOLORS.keys())
    colors_length = len(all_colors)
    for i in range(1, drones_amount + 1):
        drones.append(Drone(start_hub, i, all_colors, colors_length))
    return hubs, connections, drones


def set_drones_coordinates(
        surface: Any, x: int, y: int, size: int, count: int,
        color: tuple[int, int, int], drones: int,
        drones_here: List[Drone], current_frame: int) -> None:
    """set_drones_coordinates function. Brief description.

    Args:
        surface (type): Description.
        x (type): Description.
        y (type): Description.
        size (type): Description.
        count (type): Description.
        color (type): Description.
        drones (type): Description.
        drones_here (type): Description.
        current_frame (type): Description.

    Returns:
        None: Description.

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
    """loop_checker function. Brief description.

    Args:
        hub (type): Description.
        checked_hubs (type): Description.

    Returns:
        None: Description.

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
    """finished function. Brief description.

    Args:
        drones (type): Description.

    Returns:
        bool: Description.

    """
    for drone in drones:
        if (isinstance(drone.place, Connection)
                or drone.place.hub_type != "end_hub"
                or drone.x != drone.prev_x):
            return False
    return True


def dead_end_checker(
        hubs: List[Hub], connections: List[Connection]
) -> None:
    """dead_end_checker function. Brief description.

    Args:
        hubs (type): Description.
        connections (type): Description.

    Returns:
        None: Description.

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
    """get_start_pos function. Brief description.

    Args:
        connection (type): Description.
        x_min (type): Description.
        scale (type): Description.
        y_min (type): Description.
        start_y_divider (type): Description.
        start_y_offset (type): Description.

    Returns:
        tuple[int, int]: Description.

    """
    return (
        (connection.start.x - x_min) * scale + scale // 2,
        (connection.start.y - y_min) * scale + scale
        // start_y_divider + start_y_offset
    )


def get_end_pos(
        connection: Connection, x_min: int, scale: int, y_min: int,
        end_y_divider: int, end_y_offset: int) -> tuple[int, int]:
    """get_end_pos function. Brief description.

    Args:
        connection (type): Description.
        x_min (type): Description.
        scale (type): Description.
        y_min (type): Description.
        end_y_divider (type): Description.
        end_y_offset (type): Description.

    Returns:
        tuple[int, int]: Description.

    """
    return (
        (connection.end.x - x_min) * scale + scale // 2,
        (connection.end.y - y_min) * scale + scale
        // end_y_divider + end_y_offset
    )


def draw_connections(
        connections: List[Connection], scale: int,
        screen: Any, x_min: int, y_min: int) -> None:
    """draw_connections function. Brief description.

    Args:
        connections (type): Description.
        scale (type): Description.
        screen (type): Description.
        x_min (type): Description.
        y_min (type): Description.

    Returns:
        None: Description.

    """
    for connection in connections:
        start_hubs = connection.start.block.hubs
        end_hubs = connection.end.block.hubs
        start_idx = start_hubs.index(connection.start)
        end_idx = end_hubs.index(connection.end)
        start_y_divider = 2 * len(start_hubs)
        start_y_offset = scale // len(start_hubs) * start_idx
        end_y_divider = 2 * len(end_hubs)
        end_y_offset = scale // len(end_hubs) * end_idx
        start_pos = get_start_pos(
            connection, x_min, scale, y_min,
            start_y_divider, start_y_offset)
        end_pos = get_end_pos(
            connection, x_min, scale, y_min,
            end_y_divider, end_y_offset)
        if connection.end.zone == 'priority':
            pygame.draw.line(
                screen, pygame.Color("green"),
                start_pos, end_pos, 10 if connection.active else 1)
        elif connection.end.zone == 'normal':
            pygame.draw.line(
                screen, pygame.Color("yellow"), start_pos, end_pos,
                10 if connection.active else 1)
        elif connection.end.zone == 'restricted':
            pygame.draw.line(
                screen, pygame.Color("orange"), start_pos, end_pos,
                10 if connection.active else 1)
        elif connection.end.zone == 'blocked':
            pygame.draw.line(
                screen, pygame.Color("red"), start_pos, end_pos,
                10 if connection.active else 1)


def choose_color(brightness: int) -> Tuple[int, int, int]:
    """choose_color function. Brief description.

    Args:
        brightness (type): Description.

    Returns:
        Tuple[int, int, int]: Description.

    """
    if brightness >= (255 * 3) // 2:
        return 0, 0, 0
    return 255, 255, 255


def choose_hub_color(zone: str)\
        -> (pygame.Color | int | str | tuple[int, int, int]
            | tuple[int, int, int, int] | Sequence[int]):
    """choose_hub_color function. Brief description.

    Args:
        zone (type): Description.

    Returns:
        pygame.Color | int | str | tuple[int, int, int] | tuple[int, int, int, int] | Sequence[int]: Description.

    """
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


def draw_hubs(
        blocks: List[List[Block]], drones: List[Drone], scale: int, x_min: int,
        y_min: int, screen: Any, square_size: int,
        the_colors: Dict[str, tuple[int, int, int, int]],
        font: Any, current_frame: int) -> None:
    """draw_hubs function. Brief description.

    Args:
        blocks (type): Description.
        drones (type): Description.
        scale (type): Description.
        x_min (type): Description.
        y_min (type): Description.
        screen (type): Description.
        square_size (type): Description.
        the_colors (type): Description.
        font (type): Description.
        current_frame (type): Description.

    Returns:
        None: Description.

    """
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
                    square_y = (scale * (block.hubs[i].y - y_min) + scale // 8
                                + (scale // 4 * 3 - 4) * i)
                    color = choose_hub_color(zone)
                    try:
                        pygame.draw.rect(
                            screen,
                            pygame.Color("black"),
                            (square_x-5,
                             square_y-5,
                             square_size+10, square_size+10), border_radius=20)
                        pygame.draw.rect(
                            screen,
                            pygame.Color(color),
                            (square_x-4,
                             square_y-4,
                             square_size+8, square_size+8), border_radius=20)
                        pygame.draw.rect(
                            screen,
                            pygame.Color("black"),
                            (square_x-1,
                             square_y-1,
                             square_size+2, square_size+2), border_radius=20)
                        pygame.draw.rect(
                            screen, pygame.Color(block.hubs[i].color),
                            (
                                square_x, square_y,
                                square_size,
                                square_size), border_radius=20)
                    except ValueError:
                        block.hubs[i].color = "pink"
                        pygame.draw.rect(
                            screen, pygame.Color(block.hubs[i].color),
                            (
                                square_x + 2, square_y + 2,
                                square_size - 8,
                                (square_size - 8)), border_radius=10)
                    set_drones_coordinates(
                        screen, square_x + 2, square_y + 2, square_size - 8,
                        block.hubs[i].max_drones, (255, 255, 255),
                        len(drones), drones_here, current_frame)
                    brightness = sum(the_colors[block.hubs[i].color][:3])
                    text_2 = font.render(
                        block.hubs[i].name, True,
                        choose_color(brightness))
                    text_2_r = text_2.get_rect(
                        center=(scale * (block.hubs[i].x - x_min) + scale // 2,
                                scale * (
                                        block.hubs[i].y - y_min) + scale
                                // 2 + scale * i))
                    screen.blit(text_2, text_2_r)


def draw_connections_stops(
        connections: List[Connection], scale: int,
        screen: Any, x_min: int, y_min: int, radius: int) -> None:
    """draw_connections_stops function. Brief description.

    Args:
        connections (type): Description.
        scale (type): Description.
        screen (type): Description.
        x_min (type): Description.
        y_min (type): Description.
        radius (type): Description.

    Returns:
        None: Description.

    """
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
            cy = (((connection.start.y - y_min)
                   * scale + scale // start_y_divider + start_y_offset)
                  + ((connection.end.y - y_min) * scale
                     + scale // end_y_divider + end_y_offset)) // 2
            pygame.draw.circle(
                screen, pygame.Color("black"),
                (int(cx), int(cy)), radius + 1)
            pygame.draw.circle(
                screen, pygame.Color("pink"),
                (int(cx), int(cy)), radius)


def compute_weighted_position(
        p1: tuple[int, int],
        p2: tuple[int | None, int | None],
        frame: int, total_frames: int) -> tuple[float, float]:
    """compute_weighted_position function. Brief description.

    Args:
        p1 (type): Description.
        p2 (type): Description.
        frame (type): Description.
        total_frames (type): Description.

    Returns:
        tuple[float, float]: Description.

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


def set_drones_coordinates_when_in_the_middle(
        drones: List[Drone], scale: int, x_min: int, y_min: int,
        current_frame: int) -> None:
    """set_drones_coordinates_when_in_the_middle function. Brief description.

    Args:
        drones (type): Description.
        scale (type): Description.
        x_min (type): Description.
        y_min (type): Description.
        current_frame (type): Description.

    Returns:
        None: Description.

    """
    for drone in drones:
        if isinstance(drone.place, Connection):
            start_hubs = drone.place.start.block.hubs
            end_hubs = drone.place.end.block.hubs
            start_y_divider = 2 * len(start_hubs)
            start_idx = start_hubs.index(drone.place.start)
            end_idx = end_hubs.index(drone.place.end)
            start_y_offset = scale // len(start_hubs) * start_idx
            end_y_divider = 2 * len(end_hubs)
            end_y_offset = scale // len(end_hubs) * end_idx
            cx = (((drone.place.start.x - x_min)
                   * scale + scale // 2) + (
                        (drone.place.end.x - x_min)
                        * scale + scale // 2)) // 2
            cy = (((drone.place.start.y - y_min)
                   * scale + scale // start_y_divider + start_y_offset)
                  + (
                          (drone.place.end.y - y_min)
                          * scale + scale // end_y_divider
                          + end_y_offset)) // 2
            if current_frame == 0:
                drone.prev_x = copy(drone.x)
                drone.prev_y = copy(drone.y)
                drone.x = cx
                drone.y = cy


def make_moves(
        drones: List[Drone], connections: List[Connection]) -> tuple[int, int]:
    """make_moves function. Brief description.

    Args:
        drones (type): Description.
        connections (type): Description.

    Returns:
        tuple[int, int]: Description.

    """
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
        y_min: int, y_max: int, x_min: int,
        x_max: int, hubs: List[Hub]) -> List[List[Block]]:
    """put_hubs_to_block function. Brief description.

    Args:
        y_min (type): Description.
        y_max (type): Description.
        x_min (type): Description.
        x_max (type): Description.
        hubs (type): Description.

    Returns:
        List[List[Block]]: Description.

    """
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


def set_corners(hubs: List[Hub]) -> tuple[int, int, int, int]:
    """set_corners function. Brief description.

    Args:
        hubs (type): Description.

    Returns:
        tuple[int, int, int, int]: Description.

    """
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
    return x_min, y_min, x_max, y_max


def set_scale(width: int, size_x: int, height: int, size_y: int) -> int:
    """set_scale function. Brief description.

    Args:
        width (type): Description.
        size_x (type): Description.
        height (type): Description.
        size_y (type): Description.

    Returns:
        int: Description.

    """
    if width // size_x < height // size_y:
        return width // size_x
    return height // size_y


def draw_drones(
        drones: List[Drone], font: Any, screen: Any,
        radius: int, frame: int, total_frames: int,
        the_colors: dict[str, tuple[int, int, int, int]]) -> None:
    """draw_drones function. Brief description.

    Args:
        drones (type): Description.
        font (type): Description.
        screen (type): Description.
        radius (type): Description.
        frame (type): Description.
        total_frames (type): Description.
        the_colors (type): Description.

    Returns:
        None: Description.

    """
    frame = int(frame * 1.2)
    if frame > total_frames:
        frame = total_frames
    for drone in drones:
        brightness = sum(the_colors[drone.color][:3])
        x, y = compute_weighted_position(
            (drone.x, drone.y),
            (drone.prev_x, drone.prev_y),
            frame, total_frames)
        pygame.draw.circle(screen, drone.color, (x, y), radius - 2)
        text = font.render(str(drone.idx), True, choose_color(brightness))
        text_r = text.get_rect(center=(x, y))
        screen.blit(text, text_r)


def main() -> None:
    """main function. Brief description.

    Returns:
        None: Description.

    """
    try:
        hubs, connections, drones = handle_file(sys.argv)
        pygame.init()
        width = pygame.display.Info().current_w
        height = pygame.display.Info().current_h
        x_min, y_min, x_max, y_max = set_corners(hubs)
        size_x, size_y = x_max - x_min + 1, y_max - y_min + 2
        scale = set_scale(width, size_x, height, size_y) - 1
        screen = pygame.display.set_mode((size_x * scale, size_y * scale))
        pygame.display.set_caption("Fly-in")
        font = pygame.font.Font(None, 15)
        font_counter = pygame.font.Font(None, 25)
        loop_checker(hubs[0], [])
        dead_end_checker(hubs, connections)
        blocks = put_hubs_to_block(y_min, y_max, x_min, x_max, hubs)
        clock = pygame.time.Clock()
        the_colors = pygame.color.THECOLORS
        counter = 0
        square_size = scale - scale // 4
        grid = math.ceil(math.sqrt(len(drones)))
        cell = (square_size - 8) / grid
        radius = int(cell * 0.4)
        ANIM_FRAMES = 60
        current_frame = 0
        counter_printed = False
        move_not_made = 0
        moves_counter = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            screen.fill(pygame.Color("darkblue"))
            for i in range(1, width):
                if i%40 == 0:
                    pygame.draw.line(screen, pygame.Color("blue"), (i, 0), (i, height), 1)
            for i in range(1, height):
                if i % 40 == 0:
                    pygame.draw.line(screen, pygame.Color("blue"), (0, i), (width, i), 1)
            draw_connections(
                connections, scale, screen, x_min, y_min)
            draw_hubs(
                blocks, drones, scale, x_min, y_min,
                screen, square_size, the_colors, font, current_frame)
            draw_connections_stops(
                connections, scale, screen, x_min, y_min, radius)
            set_drones_coordinates_when_in_the_middle(
                drones, scale, x_min,
                y_min, current_frame)
            draw_drones(
                drones, font, screen, radius,
                current_frame, ANIM_FRAMES, the_colors)
            text = font_counter.render(str(counter), True, pygame.Color("white"))
            text_r = text.get_rect(center=(20, (size_y * scale) - 20))
            screen.blit(text, text_r)
            pygame.display.flip()
            current_frame = (current_frame + 1) % ANIM_FRAMES
            clock.tick(60)
            if current_frame == 0 and not finished(drones):
                drones.sort(key=lambda dron: dron.moves, reverse=False)
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
    except ZeroDivisionError:
        print("Error: Amount of drones must be above 0")
        sys.exit(1)


if __name__ == '__main__':
    main()
