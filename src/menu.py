import pygame
import sys

from constants import *
from game import play_game
from button import Button


class Menu:
    def __init__(self, screen, BG_PATH):
        self.BG = pygame.image.load(BG_PATH)
        self.screen = screen

    def get_font(self, size):  # Returns the font in the desired size
        return pygame.font.Font("assets/Minecraft.ttf", size)

    def main_menu(self):
        while True:
            self.screen.blit(self.BG, (0, 0))

            MENU_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = self.get_font(100).render("MAIN MENU", True, "WHITE")
            MENU_RECT = MENU_TEXT.get_rect(center=(SCREEN_WIDTH // 2, 100))


            PLAY_BUTTON = Button(image=pygame.image.load("assets/11zon_resized(1).png"), pos=(SCREEN_WIDTH // 2, 300),
                                 text_input="PLAY", font=self.get_font(75), base_color="GREEN", hovering_color="WHITE",)
            QUIT_BUTTON = Button(image=pygame.image.load("assets/11zon_resized(1).png"), pos=(SCREEN_WIDTH // 2, 450),
                                 text_input="QUIT", font=self.get_font(75), base_color="GREEN", hovering_color="WHITE",)

            self.screen.blit(MENU_TEXT, MENU_RECT)

            for button in [PLAY_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                        play_game(self.screen)
                        return
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        return

            pygame.display.update()
