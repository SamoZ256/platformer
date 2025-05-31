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

GRAVITY = 3000
PLAYER_SPEED = 400
PLAYER_JUMP_HEIGHT = 1000

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
            self.ensure_chunk(chunk_x)

    def draw(self, surface, camera_pos):
        visible = self.get_visible_chunk_range(camera_pos)
        for chunk_x in range(visible[0], visible[1]):
            chunk = self.chunks[chunk_x]
            chunk.draw(surface, camera_pos)

    def ensure_chunk(self, chunk_x):
        if not chunk_x in self.chunks:
            self.chunks[chunk_x] = Chunk(chunk_x)

    def get_chunk(self, chunk_x):
        self.ensure_chunk(chunk_x)
        return self.chunks[chunk_x]

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

class MovableObject:
    def __init__(self):
        self.size = (40, 60) # TODO: don't hardcode
        self.image = pygame.Surface(self.size)
        self.image.fill(RED)

        self.position = [0.0, 0.0]
        self.movement = [0.0, 0.0]
        self.y_momentum = 0.0
        self.is_on_ground = False

    def update(self, world, dt):
        self.y_momentum += GRAVITY * dt
        self.movement[1] += self.y_momentum

        # X
        if self.movement[0] != 0:
            self.position[0] += self.movement[0] * dt
            tile_rect = self.collide(world)
            if tile_rect:
                if self.movement[0] > 0:
                    self.position[0] = tile_rect.left - self.size[0]
                else:
                    self.position[0] = tile_rect.right
            self.movement[0] = 0

        # Y
        if self.movement[1] != 0:
            self.position[1] += self.movement[1] * dt
            tile_rect = self.collide(world)
            if tile_rect:
                if self.movement[1] > 0:
                    self.position[1] = tile_rect.top - self.size[1]
                    self.is_on_ground = True
                else:
                    self.position[1] = tile_rect.bottom
                self.y_momentum = 0
            self.movement[1] = 0

    def collide(self, world):
        rect = self.get_rect()
        chunk_range = world.chunk_manager.get_chunk_range(rect.left, rect.right)
        for chunk_x in range(chunk_range[0], chunk_range[1]):
            chunk = world.chunk_manager.get_chunk(chunk_x)
            tile_x_range = chunk.get_tile_x_range(rect.left, rect.right)
            tile_y_range = chunk.get_tile_y_range(rect.top, rect.bottom)
            for tile_x in range(tile_x_range[0], tile_x_range[1]):
                for tile_y in range(tile_y_range[0], tile_y_range[1]):
                    if chunk.get_tile(tile_x, tile_y) == 0:
                        continue

                    tile_rect = chunk.get_tile_rect(tile_x, tile_y)
                    collide = pygame.Rect.colliderect(rect, tile_rect)
                    if collide:
                        return tile_rect

        return None

    def draw(self, surface, camera_pos):
        rect = self.get_rect()
        rect.topleft = world_to_screen(rect.topleft, camera_pos)
        surface.blit(self.image, rect)

    def get_rect(self):
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])

    def move(self, m):
        self.movement[0] += m[0]
        self.movement[1] += m[1]

    def try_jump(self, height):
        if self.is_on_ground:
            self.y_momentum = -height
            self.is_on_ground = False

pygame.init()

# Set the height and width of the screen
size = [SCREEN_WIDTH, SCREEN_HEIGHT]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Side-scrolling Platformer")

# World
world = World()

# Player
player = MovableObject()
player.position = [0, CHUNK_HEIGHT * TILE_SIZE - SCREEN_HEIGHT / 2 - 100]

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
                player.try_jump(PLAYER_JUMP_HEIGHT)

    dt = clock.tick(60) / 1000

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player.move([-PLAYER_SPEED, 0])
    if keys[pygame.K_d]:
        player.move([PLAYER_SPEED, 0])

    # Update
    world.update(camera_pos)
    player.update(world, dt)

    # Draw
    screen.fill((0, 0, 0))

    world.draw(screen, camera_pos)
    player.draw(screen, camera_pos)

    pygame.display.flip()

pygame.quit()
