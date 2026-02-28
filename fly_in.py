import sys
import pygame
from objects import Hub, Connection

def handle_file(filename):
    hubs = []
    connections = []
    try:
        if len(sys.argv) <3:
            with open(filename) as f:
                file_content = f.read().splitlines()
                for line in file_content:
                    if not line.startswith("#") and line.strip() != "":
                        parts = line.split()
                        if parts[0] == "nb_drones:":
                            print("NB_DRONES +", parts)
                        elif parts[0] == "hub:" or parts[0] == "start_hub:" or parts[0] == "end_hub:":
                            hubs.append(Hub(*parts[:4], " ".join(parts[4:])))
                        elif parts[0] == "connection:":
                            start_str, end_str = parts[1].split("-")
                            start_list = [hub for hub in hubs if hub.name == start_str]
                            end_list = [hub for hub in hubs if hub.name == end_str]

                            start = start_list[0]
                            end = end_list[0]
                            connection = Connection(start, end)
                            connections.append(connection)
                        else:
                            return
                for hub in hubs:
                    print(hub)
                for connection in connections:
                    print(connection)
        else:
            print("Too many arguments\nUsage: python fly_in.py <file_name>")
    except IndexError:
        print("No argument passed\nUsage: python fly_in.py <filename>")
    except FileNotFoundError as e:
        print(f"File \"{e.filename}\" not found")
    return hubs, connections

def main():
    hubs, connections = handle_file(sys.argv[1])
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

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(pygame.Color("white"))
        for hub in hubs:
            pygame.draw.rect(screen, pygame.Color("black"), (scale * (hub.x - x_min), scale * (hub.y - y_min), scale, scale))
            try:
                pygame.draw.rect(screen, pygame.Color(hub.color), (scale * (hub.x - x_min) + 2, scale * (hub.y - y_min) + 2, scale - 4, scale - 4))
            except ValueError as e:
                pygame.draw.rect(screen, pygame.Color("pink"),
                                 (scale * (hub.x - x_min) + 2, scale * (hub.y - y_min) + 2, scale - 4, scale - 4))

            text_1 = font.render(hub.name, True, (0, 0, 0))
            text_2 = font.render(hub.zone, True, (0, 0, 0))
            text_3 = font.render(str(hub.max_drones), True, (0, 0, 0))
            text_1_r = text_1.get_rect(center=(scale * (hub.x - x_min) + scale//2, scale * (hub.y - y_min) + scale//2 - 10))
            text_2_r = text_2.get_rect(center=(scale * (hub.x - x_min) + scale//2, scale * (hub.y - y_min) + scale//2))
            text_3_r = text_3.get_rect(center=(scale * (hub.x - x_min) + scale//2, scale * (hub.y - y_min) + scale//2 + 10))
            screen.blit(text_1, text_1_r)
            screen.blit(text_2, text_2_r)
            screen.blit(text_3, text_3_r)
        for connection in connections:
            if connection.end.zone == 'priority' and connection.start.zone != 'restricted' and connection.end.zone != 'restricted':
                pygame.draw.line(screen, pygame.Color("pink"), ((connection.start.x - x_min) * scale + scale//2, (connection.start.y - y_min) * scale + scale//2), ((connection.end.x - x_min) * scale + scale//2, (connection.end.y - y_min) * scale + scale//2), 3)
            elif connection.start.zone != 'restricted' and connection.end.zone != 'restricted':
                pygame.draw.line(screen, pygame.Color("black"), ((connection.start.x - x_min) * scale + scale//2, (connection.start.y - y_min) * scale + scale//2), ((connection.end.x - x_min) * scale + scale//2, (connection.end.y - y_min) * scale + scale//2), 3)
            else:
                pygame.draw.line(screen, pygame.Color("red"), ((connection.start.x - x_min) * scale + scale//2, (connection.start.y - y_min) * scale + scale//2), ((connection.end.x - x_min) * scale + scale//2, (connection.end.y - y_min) * scale + scale//2), 3)
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()