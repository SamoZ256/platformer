import pygame
import sys

from constants import *
from game import *
from button import Button


class Menu:
    def __init__(self, screen, BG_PATH):
        self.BG = pygame.image.load(BG_PATH)
        self.screen = screen

    def get_font(self, size):
        return pygame.font.Font("assets/Minecraft.ttf", size)

    def main_menu(self):
        while True:
            self.screen.blit(self.BG, (0, 0))
            MENU_MOUSE_POS = pygame.mouse.get_pos()
            MENU_TEXT = self.get_font(100).render("MAIN MENU", True, "WHITE")
            MENU_RECT = MENU_TEXT.get_rect(center=(SCREEN_WIDTH // 2, 100))

            PLAY_BUTTON = Button(image=pygame.image.load("assets/11zon_resized(1).png"), pos=(SCREEN_WIDTH // 2, 300),
                                 text_input="PLAY", font=self.get_font(75), base_color="GREEN", hovering_color="WHITE")
            QUIT_BUTTON = Button(image=pygame.image.load("assets/11zon_resized(1).png"), pos=(SCREEN_WIDTH // 2, 450),
                                 text_input="QUIT", font=self.get_font(75), base_color="GREEN", hovering_color="WHITE")

            self.screen.blit(MENU_TEXT, MENU_RECT)

            for button in [PLAY_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                        exit_reason = play_game(self.screen, 1)
                        if exit_reason == EXIT_REASON_WIN:
                            self.show_end_screen(win=True)
                        elif exit_reason == EXIT_REASON_LOOSE:
                            self.show_end_screen(win=False)
                        elif exit_reason == EXIT_REASON_QUIT:
                            pass
                        return
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        return

            pygame.display.update()

    def show_end_screen(self, win):
        font = pygame.font.Font(None, 74)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False

            self.screen.fill((0, 0, 0))
            msg = "You Won!" if win else "You Lost!"
            color = (0, 255, 0) if win else (255, 0, 0)
            text = self.get_font(100).render(msg, True, color)
            self.screen.blit(text, (200, 200))
            if win == True:
                info = self.get_font(36).render(f"GOOD JOB. TRY AGAIN.\nYour total count of coin is: ", True, (200, 200, 200))
                self.screen.blit(info, (230, 300))
            elif win == False:
                info = self.get_font(36).render(f"NOT SO GOOD JOB. TRY AGAIN.\nYour total count of coin is: ", True, (200, 200, 200))
                self.screen.blit(info, (170, 300))
            pygame.display.flip()