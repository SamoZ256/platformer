from math import *

import os
import json
import pygame
from pygame import font

from constants import *

# Helpers
def clamp(x, a, b):
    return min(max(x, a), b)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

def world_to_screen(pos, camera_pos):
    return (pos[0] - camera_pos[0] + SCREEN_WIDTH / 2, pos[1] - camera_pos[1] + SCREEN_HEIGHT / 2)

FRICTION = 0.07
GRAVITY = 2500
PLAYER_SPEED = 1800
PLAYER_JUMP_HEIGHT = 800

IMAGE_SCALE = 3
NONE_TILE = 0

def load_image_scaled(filename, scale):
    image = pygame.image.load(filename).convert_alpha()
    size = [image.get_width() * scale, image.get_height() * scale]
    image = pygame.transform.scale(image, size)

    return image

def load_image_scaled_default(filename):
    return load_image_scaled(filename, IMAGE_SCALE)

class Tileset:
    def __init__(self, filename):
        count = 0
        for entry in os.scandir(filename):
            if entry.path.split(".")[1] == "png":
                count += 1

        self.images = [None] * (count + 1) # + 1 because of the empty image number 0
        for entry in os.scandir(filename):
            base_name = os.path.basename(entry.path)
            (name, ext) = base_name.split(".")
            if ext == "png":
                self.images[int(name)] = load_image_scaled_default(entry.path)

    def get_image(self, tile):
        return self.images[tile]

class Map:
    def __init__(self, filename):
        self.tiles = []
        with open(filename) as file:
            for line in file.readlines():
                line = line.strip()
                tile_row = [None] * len(line)
                for i in range(len(line)):
                    tile_row[i] = int(line[i])
                self.tiles.append(tile_row)

    def get_tile(self, x, y):
        if y < 0 or y >= len(self.tiles):
            return NONE_TILE

        tile_row = self.tiles[y]
        if x < 0 or x >= len(tile_row):
            return NONE_TILE

        return tile_row[x]

TILE_SIZE = 16 * IMAGE_SCALE
CHUNK_WIDTH = 8
CHUNK_HEIGHT = 32

class Chunk:
    def __init__(self, x, map):
        self.x = x

        self.tiles = [0] * CHUNK_WIDTH * CHUNK_HEIGHT
        self.load(map)

    def load(self, map):
        for tile_x in range(CHUNK_WIDTH):
            for tile_y in range(CHUNK_HEIGHT):
                x = self.x * CHUNK_WIDTH + tile_x
                tile = map.get_tile(x, tile_y)
                self.set_tile(tile_x, tile_y, tile)

    def get_tile(self, rel_tile_x, rel_tile_y):
        return self.tiles[rel_tile_y * CHUNK_WIDTH + rel_tile_x]

    def set_tile(self, rel_tile_x, rel_tile_y, tile):
        self.tiles[rel_tile_y * CHUNK_WIDTH + rel_tile_x] = tile

    def draw_with_tileset(self, surface, camera_pos, tileset):
        for x in range(CHUNK_WIDTH):
            for y in range(CHUNK_HEIGHT):
                tile = self.get_tile(x, y)
                if tile != 0:
                    rect = self.get_tile_rect(x, y)
                    rect.topleft = world_to_screen(rect.topleft, camera_pos)
                    surface.blit(tileset.get_image(tile), rect.topleft)

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
    def __init__(self, map):
        self.map = map
        self.tileset = Tileset("assets/super_mango/tileset")
        self.chunks = {}

    def update(self, camera_pos):
        visible = self.get_visible_chunk_range(camera_pos)
        for chunk_x in range(visible[0], visible[1]):
            self.ensure_chunk(chunk_x)

    def draw(self, surface, camera_pos):
        visible = self.get_visible_chunk_range(camera_pos)
        for chunk_x in range(visible[0], visible[1]):
            chunk = self.chunks[chunk_x]
            chunk.draw_with_tileset(surface, camera_pos, self.tileset)

    def ensure_chunk(self, chunk_x):
        if not chunk_x in self.chunks:
            self.chunks[chunk_x] = Chunk(chunk_x, self.map)

    def get_chunk(self, chunk_x):
        self.ensure_chunk(chunk_x)
        return self.chunks[chunk_x]

    def get_chunk_range(self, left, right):
        begin = floor(left / TILE_SIZE / CHUNK_WIDTH)
        end = ceil(right / TILE_SIZE / CHUNK_WIDTH)
        return (begin, end)

    def get_visible_chunk_range(self, camera_pos):
        return self.get_chunk_range(camera_pos[0] - SCREEN_WIDTH / 2, camera_pos[0] + SCREEN_WIDTH / 2)

class World:
    def __init__(self, map_filename):
        self.map = Map(map_filename)
        self.chunk_manager = ChunkManager(self.map)

    def update(self, camera_pos):
        self.chunk_manager.update(camera_pos)

    def draw(self, surface, camera_pos):
        self.chunk_manager.draw(surface, camera_pos)


class Collectible:
    def __init__(self, pos, image):
        self.pos = pos
        self.collected = False
        self.image = image
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.image.get_width(), self.image.get_height())

    def draw(self, surface, camera_pos):
        if not self.collected:
            screen_pos = world_to_screen(self.pos, camera_pos)
            surface.blit(self.image, screen_pos)


class MovableObject:
    def __init__(self, size, gravity):
        self.size = size
        self.gravity = gravity

        self.position = [0.0, 0.0]
        self.momentum = [0.0, 0.0]
        self.flip = False
        self.is_on_ground = False

    def update(self, world, dt):
        # Friction
        self.momentum[0] *= 1.0 - FRICTION # TODO: better
        if abs(self.momentum[0]) < 2.0:
            self.momentum[0] = 0.0

        # Gravity
        self.momentum[1] += self.gravity * dt

        # X
        if self.momentum[0] != 0.0:
            if self.momentum[0] > 0.0:
                self.flip = False
            else:
                self.flip = True

            self.position[0] += self.momentum[0] * dt
            tile_rect = self.collide(world)
            if tile_rect:
                if self.momentum[0] > 0.0:
                    self.position[0] = tile_rect.left - self.size[0]
                else:
                    self.position[0] = tile_rect.right
                self.momentum[0] = 0.0

        # Y
        if self.momentum[1] != 0.0:
            self.is_on_ground = False
            self.position[1] += self.momentum[1] * dt
            tile_rect = self.collide(world)
            if tile_rect:
                if self.momentum[1] > 0.0:
                    self.position[1] = tile_rect.top - self.size[1]
                    self.is_on_ground = True
                else:
                    self.position[1] = tile_rect.bottom
                self.momentum[1] = 0.0

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

    def draw_with_image(self, surface, camera_pos, image):
        rect = self.get_rect()
        rect.topleft = world_to_screen(rect.topleft, camera_pos)
        if self.flip:
            image = pygame.transform.flip(image, True, False)
        surface.blit(image, rect)

    def get_rect(self):
        # Ceil the position so as to avoid undetected collision on the ground
        return pygame.Rect(self.position[0], ceil(self.position[1]), self.size[0], self.size[1])

    def move(self, movement):
        self.momentum[0] += movement[0]
        self.momentum[1] += movement[1]

    def try_jump(self, height):
        if self.is_on_ground:
            self.momentum[1] = -height

class Animation:
    def __init__(self, filename):
        with open(filename + "/rules.json") as file:
            rules = json.load(file)

            self.frames = rules["frames"]
            self.speed = rules["speed"]
            self.loop = rules["loop"]

            count = 0
            for entry in os.scandir(filename):
                if entry.path.split(".")[1] == "png":
                    count += 1

            self.images = [None] * count
            for entry in os.scandir(filename):
                base_name = os.path.basename(entry.path)
                (name, ext) = base_name.split(".")
                if ext == "png":
                    self.images[int(name)] = load_image_scaled_default(entry.path)

    def get_size(self):
        return [self.images[0].get_width(), self.images[0].get_height()]

class AnimatableObject(MovableObject):
    def __init__(self, filename, gravity):
        self.animations = {}
        size = [0, 0]
        for entry in os.scandir(filename):
            base_name = os.path.basename(entry.path)
            if base_name == ".DS_Store":
                continue

            anim = Animation(entry.path)
            self.animations[base_name] = anim
            size = anim.get_size()

        self.active_animation = None
        self.time_since_anim_start = 0.0

        super().__init__(size, gravity)

    def update(self, world, dt):
        super().update(world, dt)
        self.time_since_anim_start += dt

    def draw(self, surface, camera_pos):
        anim = self.active_animation
        frame = floor(self.time_since_anim_start / anim.speed)
        if anim.loop:
            frame %= len(anim.images) # Loop
        else:
            frame = min(frame, len(anim.images) - 1) # Cap
        self.draw_with_image(surface, camera_pos, anim.images[anim.frames[frame]])

    def play_animation(self, name):
        self.active_animation = self.animations[name]
        self.time_since_anim_start = 0.0

    def ensure_animation(self, name):
        if self.active_animation != self.animations[name]:
            self.play_animation(name)

PLAYER_INVINCIBILITY_PERIOD = 2.0
PLAYER_INVINCIBILITY_BLINK_PERIOD = 0.05
PLAYER_MAX_LIVES = 3

class Player(AnimatableObject):
    def __init__(self, filename):
        super().__init__(filename, GRAVITY)
        self.collect_count = 0
        self.lives = PLAYER_MAX_LIVES
        self.invincibility_timer = 0.0

    def update(self, world, dt):
        super().update(world, dt)
        self.invincibility_timer -= dt
        if self.invincibility_timer < 0.0:
            self.invincibility_timer = 0.0

    def draw(self, surface, camera_pos):
        if self.invincibility_timer % (PLAYER_INVINCIBILITY_BLINK_PERIOD * 2) < PLAYER_INVINCIBILITY_BLINK_PERIOD:
            super().draw(surface, camera_pos)

    def take_damage(self):
        self.lives -= 1
        self.invincibility_timer = PLAYER_INVINCIBILITY_PERIOD

BIRD_SPEED = 400
BIRD_DIR_SWAP_TIME = 3.0

class Bird(AnimatableObject):
    def __init__(self):
        super().__init__("assets/super_mango/bird", 0.0)
        self.timer = 0.0
        self.going_left = True
        self.play_animation("fly")

    def update(self, world, dt):
        if self.going_left:
            self.move([-BIRD_SPEED * dt, 0])
        else:
            self.move([BIRD_SPEED * dt, 0])
        self.timer += dt
        if self.timer > BIRD_DIR_SWAP_TIME:
            self.timer = 0.0
            self.going_left = not self.going_left

        super().update(world, dt)

SPIDER_SPEED = 600

class Spider(AnimatableObject):
    def __init__(self):
        super().__init__("assets/super_mango/spider", GRAVITY)
        self.going_left = True
        self.play_animation("walk")

    def update(self, world, dt):
        if self.going_left:
            self.move([-SPIDER_SPEED * dt, 0])
        else:
            self.move([SPIDER_SPEED * dt, 0])

        super().update(world, dt)

        if self.momentum[0] == 0.0: # Bumped into a wall
            self.going_left = not self.going_left

BACKGROUND_SCROLL = 0.2

class Background:
    def __init__(self, filename):
        self.image = load_image_scaled_default(filename)

    def draw(self, surface, camera_pos):
        pos_x = -camera_pos[0] * BACKGROUND_SCROLL
        pos_x = pos_x % self.image.get_width()
        self.draw_impl(surface, pos_x)
        if pos_x > 0.0:
            self.draw_impl(surface, pos_x - self.image.get_width())
        else:
            self.draw_impl(surface, pos_x + self.image.get_width())

    def draw_impl(self, surface, pos_x):
        surface.blit(self.image, (pos_x, 0))
        surface.blit(self.image, (pos_x, self.image.get_height()))

CAMERA_DIFF_LIMIT = SCREEN_WIDTH / 15
CAMERA_OFFSET = -SCREEN_WIDTH / 8

EXIT_REASON_WIN = 0
EXIT_REASON_LOOSE = 1
EXIT_REASON_QUIT = 2

def play_game(screen, map_number):
    # Assets
    font = pygame.font.Font("assets/Minecraft.ttf", 36)
    heart_empty = load_image_scaled("assets/heart/empty.png", 4)
    heart_full = load_image_scaled("assets/heart/full.png", 4)

    # World
    world = World(f"assets/maps/{map_number}.txt")

    # Background
    background = Background("assets/super_mango/Forest_Background_0.png")

    # Player
    player = Player("assets/super_mango/player")
    player.position = [0, CHUNK_HEIGHT * TILE_SIZE - SCREEN_HEIGHT / 2 - 100]
    player.play_animation("idle")

    # Camera
    camera_pos = [player.position[0] + player.size[0] / 2 - CAMERA_OFFSET, CHUNK_HEIGHT * TILE_SIZE - SCREEN_HEIGHT / 2]

    # Coins
    coin_image= load_image_scaled("assets/super_mango/coin.png",2)# same for spiders and birds
    coins = []
    coins.append(Collectible((96, 1200), coin_image))#1
    coins.append(Collectible((140, 1200), coin_image))
    coins.append(Collectible((170, 1200), coin_image))
    coins.append(Collectible((600, 1200), coin_image))
    coins.append(Collectible((759, 1150), coin_image))#5
    coins.append(Collectible((1176, 1150), coin_image))
    coins.append(Collectible((1309, 1150), coin_image))
    coins.append(Collectible((1603, 1150), coin_image))
    coins.append(Collectible((1668, 1150), coin_image))
    coins.append(Collectible((1799, 1100), coin_image))#10
    coins.append(Collectible((1957, 1050), coin_image))
    coins.append(Collectible((2493, 1150), coin_image))
    coins.append(Collectible((2678, 1150), coin_image))
    coins.append(Collectible((3000, 1150), coin_image))
    coins.append(Collectible((3500, 1080), coin_image))#15
    coins.append(Collectible((4000, 1050), coin_image))
    coins.append(Collectible((4500, 1050), coin_image))
    coins.append(Collectible((5000, 1150), coin_image))
    coins.append(Collectible((5500, 1050), coin_image))
    coins.append(Collectible((6000, 970), coin_image))#20
    coins.append(Collectible((6500, 1150), coin_image))
    coins.append(Collectible((7000, 1150), coin_image))
    coins.append(Collectible((7500, 1450), coin_image))
    coins.append(Collectible((8000, 1150), coin_image))
    coins.append(Collectible((8500, 1150), coin_image))#25
    coins.append(Collectible((9000, 1150), coin_image))
    coins.append(Collectible((9500, 1150), coin_image))
    coins.append(Collectible((10000, 1150), coin_image))
    coins.append(Collectible((10500, 1150), coin_image))
    coins.append(Collectible((11500, 1150), coin_image))#30
    coins.append(Collectible((12000, 1150), coin_image))

    print("Bird")
    # Birds
    birds = []
    positions_b = [[550, 1150],[4350,1160],[4230,1170],[9800, 1350]]  # List of positions for each bird

    for pos_b in positions_b:
        bird = Bird()
        bird.position = pos_b
        birds.append(bird)
        print(pos_b)
    # Spiders
    spiders = []
    positions_s = [[500, 1000], [1100, 1400],[5050,1250],[4050,1200],[4400,1200],[11500,1100]]
    for pos_s in positions_s:
        spider = Spider()
        spider.position = pos_s
        spiders.append(spider)

    clock = pygame.time.Clock()

    # -------- Main Program Loop -----------
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return EXIT_REASON_QUIT
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.try_jump(PLAYER_JUMP_HEIGHT)

        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.033) # Limit delta time to 33 milliseconds

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player.move([-PLAYER_SPEED * dt, 0])
        if keys[pygame.K_d]:
            player.move([PLAYER_SPEED * dt, 0])

        # Animations

        # Player
        if abs(player.momentum[1]) < 1.0:
            if abs(player.momentum[0]) < 10.0:
                player.ensure_animation("idle")
            else:
                player.ensure_animation("walk")
        else:
            if player.momentum[1] > 0:
                player.ensure_animation("fall")
            else:
                player.ensure_animation("jump")

        # Update

        # Sprites
        player.update(world, dt)
        for bird in birds:
            bird.update(world, dt)
            if player.invincibility_timer == 0.0 and player.get_rect().colliderect(bird.get_rect()):
                player.take_damage()
        for spider in spiders:
            spider.update(world, dt)
            if player.invincibility_timer == 0.0 and player.get_rect().colliderect(spider.get_rect()):
                player.take_damage()

        if player.lives == 0:
            return EXIT_REASON_LOOSE

        # Camera
        player_center_x = player.position[0] + player.size[0] / 2
        camera_follow_x = player_center_x - CAMERA_OFFSET
        camera_diff_x = camera_follow_x - camera_pos[0]
        if abs(camera_diff_x) > CAMERA_DIFF_LIMIT: # If player has moved too far away from the camera
            camera_pos[0] = camera_follow_x + (-CAMERA_DIFF_LIMIT if camera_diff_x > 0.0 else CAMERA_DIFF_LIMIT)

        # World
        world.update(camera_pos)

        # Coins
        for coin in coins:
            if not coin.collected and player.get_rect().colliderect(coin.rect):
                coin.collected = True
                player.collect_count += 1

        # Draw

        # Background
        background.draw(screen, camera_pos)

        # World
        world.draw(screen, camera_pos)

        # Sprites
        for bird in birds:
            bird.draw(screen, camera_pos)
        for spider in spiders:
            spider.draw(screen, camera_pos)
        for coin in coins:
            coin.draw(screen, camera_pos)
        player.draw(screen, camera_pos)

        # HUD

        # Coins
        coin_text = font.render(f"Collected: {player.collect_count}", True, (255, 255, 0))
        screen.blit(coin_text, (20, 20))

        # Lives
        for i in range(PLAYER_MAX_LIVES):
            image = heart_full if i < player.lives else heart_empty
            screen.blit(image, (SCREEN_WIDTH - (image.get_width() + 20) * (PLAYER_MAX_LIVES - i), 20))

        pygame.display.flip()
