class Screen:
    def show_end_screen(screen, win):
        self.screen = screen
        font = pygame.font.Font(None, 74)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False

            screen.fill((0, 0, 0))
            msg = "You Win!" if win else "You Lose!"
            color = (0, 255, 0) if win else (255, 0, 0)
            text = font.render(msg, True, color)
            screen.blit(text, (200, 200))
            info = pygame.font.Font(None, 36).render("Press any key to continue", True, (200, 200, 200))
            screen.blit(info, (170, 300))
            pygame.display.flip()