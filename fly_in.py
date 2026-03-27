import sys
import pygame
from copy import copy
from typing import List
from objects import Block, Connection, Drone, Hub, Parser, Window, Draw


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
            draw.render(win, connections, blocks, drones,
                        the_colors, current_frame, counter)
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
