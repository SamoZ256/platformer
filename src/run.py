from menu import Menu
import pygame

if __name__ == "__main__":
    pygame.init()
    menu = Menu(800, 600, "F_BG.png")
    menu.main_menu()