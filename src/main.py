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
    return (pos[0] - camera_pos[0] + SCREEN_WIDTH / 2, pos[1] - camera_pos[1] + SCREEN_HEIGHT / 2)

GRAVITY = 1

TILE_SIZE = 32
CHUNK_WIDTH = 8
CHUNK_HEIGHT = 32

class Chunk:
    def __init__(self, x):
        self.x = x

        self.tiles = [0] * CHUNK_WIDTH * CHUNK_HEIGHT
        self.generate()

    def generate(self):
        for x in range(CHUNK_WIDTH):
            for y in range(CHUNK_HEIGHT):
                if y > CHUNK_HEIGHT - 7:
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
                    rect = self.get_tile_rect(x, y)
                    rect.topleft = world_to_screen(rect.topleft, camera_pos)
                    pygame.draw.rect(surface, GREEN, rect)

    def get_tile_rect(self, tile_x, tile_y):
        return pygame.Rect((self.x * CHUNK_WIDTH + tile_x) * TILE_SIZE, tile_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def get_tile_x_range(self, left, right):
        begin = clamp(floor(left / TILE_SIZE) - self.x * CHUNK_WIDTH, 0, CHUNK_WIDTH)
        end = clamp(ceil(right / TILE_SIZE) - self.x * CHUNK_WIDTH, 0, CHUNK_WIDTH)
        return (begin, end)

    def get_tile_y_range(self, top, bottom):
        begin = clamp(floor(top / TILE_SIZE), 0, CHUNK_HEIGHT)
        end = clamp(ceil(bottom / TILE_SIZE), 0, CHUNK_HEIGHT)
        return (begin, end)

class ChunkManager:
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

    def get_chunk_range(self, left, right):
        begin = floor(left / TILE_SIZE / CHUNK_WIDTH)
        end = ceil(right / TILE_SIZE / CHUNK_WIDTH)
        return (begin, end)

    def get_visible_chunk_range(self, camera_pos):
        return self.get_chunk_range(camera_pos[0] - SCREEN_WIDTH / 2, camera_pos[1] + SCREEN_WIDTH / 2)

class World:
    def __init__(self):
        self.chunk_manager = ChunkManager()

    def update(self, camera_pos):
        self.chunk_manager.update(camera_pos)

    def draw(self, surface, camera_pos):
        self.chunk_manager.draw(surface, camera_pos)

class MovableObject(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface([40, 60])
        self.image.fill(RED)

        self.rect = self.image.get_rect()

        self.move_x = 0
        self.move_y = 0
        self.y_momentum = 0

    # TODO: clean up
    def update(self, world):
        self.y_momentum += GRAVITY
        self.move_y += self.y_momentum

        # X
        if self.move_x != 0:
            self.rect.x += self.move_x
            rect = self.collide(world)
            if rect:
                if self.move_x > 0:
                    self.rect.right = rect.left
                else:
                    self.rect.left = rect.right
            self.move_x = 0

        # Y
        if self.move_y != 0:
            self.rect.y += self.move_y
            rect = self.collide(world)
            if rect:
                if self.move_y > 0:
                    self.rect.bottom = rect.top
                else:
                    self.rect.top = rect.bottom
                self.y_momentum = 0
            self.move_y = 0

    def collide(self, world):
        chunk_range = world.chunk_manager.get_chunk_range(self.rect.left, self.rect.right)
        for chunk_x in range(chunk_range[0], chunk_range[1]):
            chunk = world.chunk_manager.chunks[chunk_x]
            tile_x_range = chunk.get_tile_x_range(self.rect.left, self.rect.right)
            tile_y_range = chunk.get_tile_y_range(self.rect.top, self.rect.bottom)
            for tile_x in range(tile_x_range[0], tile_x_range[1]):
                for tile_y in range(tile_y_range[0], tile_y_range[1]):
                    if chunk.get_tile(tile_x, tile_y) == 0:
                        continue

                    tile_rect = chunk.get_tile_rect(tile_x, tile_y)
                    collide = pygame.Rect.colliderect(self.rect, tile_rect)
                    if collide:
                        return tile_rect

        return None

    def draw(self, surface, camera_pos):
        rect = self.rect.copy()
        rect.topleft = world_to_screen(rect.topleft, camera_pos)
        surface.blit(self.image, rect)

pygame.init()

# Set the height and width of the screen
size = [SCREEN_WIDTH, SCREEN_HEIGHT]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Side-scrolling Platformer")

# World
world = World()

# Player
player = MovableObject()
player.rect.center = (0, CHUNK_HEIGHT * TILE_SIZE - SCREEN_HEIGHT / 2 - 100)

clock = pygame.time.Clock()

camera_pos = (0, CHUNK_HEIGHT * TILE_SIZE - SCREEN_HEIGHT / 2)

# -------- Main Program Loop -----------
done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.y_momentum = -20

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player.move_x -= 5
    if keys[pygame.K_d]:
        player.move_x += 5

    # Update
    world.update(camera_pos)
    player.update(world)

    # Draw
    screen.fill((0, 0, 0))

    world.draw(screen, camera_pos)
    player.draw(screen, camera_pos)

    clock.tick(60)

    pygame.display.flip()

pygame.quit()
