from math import *

import pygame

# Helpers
def clamp(x, a, b):
    return min(max(x, a), b)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

def world_to_screen(pos, camera_pos):
    return (pos[0] - camera_pos[0] + SCREEN_WIDTH / 2, SCREEN_HEIGHT - (pos[1] - camera_pos[1] + SCREEN_HEIGHT / 2))

TILE_SIZE = 32
CHUNK_WIDTH = 8
CHUNK_HEIGHT = 16

class Chunk:
    def __init__(self, x):
        self.x = x

        self.tiles = [0] * CHUNK_WIDTH * CHUNK_HEIGHT
        self.generate()

    def generate(self):
        for x in range(CHUNK_WIDTH):
            for y in range(CHUNK_HEIGHT):
                if y < 10:
                    self.set_tile(x, y, 1)

    def get_tile(self, rel_tile_x, rel_tile_y):
        return self.tiles[rel_tile_y * CHUNK_WIDTH + rel_tile_x]

    def set_tile(self, rel_tile_x, rel_tile_y, tile):
        self.tiles[rel_tile_y * CHUNK_WIDTH + rel_tile_x] = tile

    def draw(self, surface, camera_pos):
        for x in range(CHUNK_WIDTH):
            for y in range(CHUNK_HEIGHT):
                tile = self.get_tile(x, y)
                if tile != 0:
                    world_x = (self.x * CHUNK_WIDTH + x) * TILE_SIZE
                    world_y = y * TILE_SIZE
                    pos = world_to_screen((world_x, world_y), camera_pos)
                    pygame.draw.rect(surface, GREEN, pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE))

class World:
    def __init__(self):
        self.chunks = {}

    def update(self, camera_pos):
        visible = self.get_visible_chunk_range(camera_pos)
        for chunk_x in range(visible[0], visible[1]):
            if not chunk_x in self.chunks:
                self.chunks[chunk_x] = Chunk(chunk_x)

    def draw(self, surface, camera_pos):
        visible = self.get_visible_chunk_range(camera_pos)
        for chunk_x in range(visible[0], visible[1]):
            chunk = self.chunks[chunk_x]
            chunk.draw(surface, camera_pos)

    def get_visible_chunk_range(self, camera_pos):
        min_visible_chunk_x = floor((camera_pos[0] - SCREEN_WIDTH / 2) / TILE_SIZE / CHUNK_WIDTH)
        max_visible_chunk_x = ceil((camera_pos[1] + SCREEN_WIDTH / 2) / TILE_SIZE / CHUNK_WIDTH)
        return (min_visible_chunk_x, max_visible_chunk_x + 1)

pygame.init()

# Set the height and width of the screen
size = [SCREEN_WIDTH, SCREEN_HEIGHT]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Side-scrolling Platformer")

world = World()

clock = pygame.time.Clock()

camera_pos = (0, SCREEN_HEIGHT / 2)

# -------- Main Program Loop -----------
done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                pass

    # Update
    world.update(camera_pos)

    # Draw
    world.draw(screen, camera_pos)

    clock.tick(60)

    pygame.display.flip()

pygame.quit()
