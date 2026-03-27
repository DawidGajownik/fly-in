import sys
from typing import List
import pygame
from objects import Hub, Connection, Drone


def parse_connections(
        parts: list[str], hubs: List[Hub],
        connections: List[Connection]) -> List[Connection]:
    """If line is connection info - add connection to connections list."""
    start_str, end_str = parts[1].split("-")
    start_list = [
        hub for hub in hubs if hub.name == start_str
    ]
    end_list = [
        hub for hub in hubs if hub.name == end_str
    ]
    if len(start_list) != 1 or len(end_list) != 1:
        print("Error")
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
    return connections


def name_repeated(
        name: str, elements: List[Hub]) -> bool:
    for element in elements:
        if element.name == name:
            return True
    return False


def parse_hubs(
        parts: list[str], drones_amount: int,
        line: str, hubs: List[Hub]) -> List[Hub]:
    """If line is hub info - add hub to hubs list."""
    extras = " ".join(parts[4:]
                      ) if parts is not None else None
    if name_repeated(parts[1], hubs):
        raise Exception("Duplicate hub name")
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
    return hubs


class Parser:
    def parse_file(
            self, args: List[str]
    ) -> tuple[list[Hub], list[Connection], list[Drone]]:
        """
        Function to parse the file and return
        lists of hubs, connections and drones.
        """
        hubs: List[Hub] = []
        connections: List[Connection] = []
        drones_amount = 0
        drones = []
        usage = \
            ("Usage: python fly_in.py <filename>\n"
             " or:\n make run MAP=<filename>")
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
                                if int(parts[1]) < 1:
                                    raise ValueError(
                                        "Amount of drones must be > 0."
                                    )
                                drones_amount = int(parts[1])
                            elif parts[0] in (
                                    "hub:", "start_hub:", "end_hub:"):
                                hubs = parse_hubs(
                                    parts, drones_amount, line, hubs)
                            elif parts[0] == "connection:":
                                connections = parse_connections(
                                    parts, hubs, connections)
                            else:
                                print("Wrong line", line)
                                sys.exit(1)
            else:
                print("Too many arguments\n", usage)
                sys.exit(1)
        except IndexError:
            print(usage)
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
