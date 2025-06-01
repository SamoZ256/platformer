import pygame

from constants import *
from menu import Menu

if __name__ == "__main__":
    # Init
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Side-scrolling Platformer")

    # Menu
    menu = Menu(screen, "assets/F_BG.png")
    menu.main_menu()

    # Quit
    pygame.quit()
