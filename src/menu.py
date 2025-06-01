from button import Button
import pygame
import sys

from src.main import play_game


class Menu:
    def __init__(self, SCREEN_WIDTH, SCREEN_HEIGHT, BG_PATH):
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.BG = pygame.image.load(BG_PATH)
        pygame.display.set_caption("Menu")
        self.SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def get_font(self, size):  # Returns the font in the desired size
        return pygame.font.Font("Minecraft.ttf", size)

    def main_menu(self):
        while True:
            self.SCREEN.blit(self.BG, (0, 0))

            MENU_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = self.get_font(100).render("MAIN MENU", True, "WHITE")
            MENU_RECT = MENU_TEXT.get_rect(center=(self.SCREEN_WIDTH // 2, 100))


            PLAY_BUTTON = Button(image=pygame.image.load("11zon_resized(1).png"), pos=(self.SCREEN_WIDTH // 2, 300),
                                 text_input="PLAY", font=self.get_font(75), base_color="GREEN", hovering_color="WHITE",)
            QUIT_BUTTON = Button(image=pygame.image.load("11zon_resized(1).png"), pos=(self.SCREEN_WIDTH // 2, 450),
                                 text_input="QUIT", font=self.get_font(75), base_color="GREEN", hovering_color="WHITE",)

            self.SCREEN.blit(MENU_TEXT, MENU_RECT)

            for button in [PLAY_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                        from src.main import play_game  # Import here to avoid circular import!
                        play_game()  # <-- THIS WILL SHOW THE GAME WORLD!
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        pygame.quit()
                        sys.exit()

            pygame.display.update()

