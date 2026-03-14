import pygame
import sys

def main():
    pygame.init()
    screen = pygame.display.set_mode((500, 200))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Fly-in")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        #screen.fill(pygame.Color("white"))
        #pygame.draw.rect(screen, pygame.Color("black"), (2, 4, 6, 8))
        #pygame.draw.circle(screen, pygame.Color("black"), (50, 100), 20)
        pygame.display.flip()
        clock.tick(1)

if __name__ == "__main__":
    main()