import random
import pygame
import csv
from pygame import mixer
from assets import Slider
from assets import Button
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

BGs = list(listdir("assets/Background"))
BG = BGs[random.randint(0, len(BGs) - 1)]
slider_color = BG.removeprefix(".png")
skins = list(listdir("assets/MainCharacters"))
player_skin = skins[random.randint(0, len(skins) - 1)]

CK = {
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'up': pygame.K_UP,
    'down': pygame.K_DOWN,
    'space': pygame.K_SPACE,
    'esc': pygame.K_ESCAPE,
    'w': pygame.K_w,
    'a': pygame.K_a,
    's': pygame.K_s,
    'd': pygame.K_d
}


def load_assets():
    assets = {
        "backgrounds": [f for f in listdir("assets/Background") if isfile(join("assets/Background", f))],
        "skins": [f for f in listdir("assets/MainCharacters") if isfile(join("assets/MainCharacters", f))],
        "sounds": {
            "bg_music": "assets/Sounds/bg_music.mp3",
            "jump": "assets/Sounds/quick_jump.wav",
            "double_jump": "assets/Sounds/double_jump.wav",
            "hit": "assets/Sounds/small_hit.wav"
        },
        "menu": {
            "buttons": {
                "play": "assets/Menu/Buttons/Play.png",
                "settings": "assets/Menu/Buttons/Settings.png",
                "quit": "assets/Menu/Buttons/Close.png",
                "volume": "assets/Menu/Buttons/Volume.png"
            }
        }
    }
    return assets


assets = load_assets()

mixer.init()
bg_music = mixer.music.load(assets["sounds"]["bg_music"])
mixer.music.set_volume(0.5)
mixer.music.play(-1)
jump_sound = mixer.Sound(assets["sounds"]["jump"])
double_jump_sound = mixer.Sound(assets["sounds"]["double_jump"])
hit_sound = mixer.Sound(assets["sounds"]["hit"])

FONT = pygame.font.SysFont("Comic Sans", 50)

window = pygame.display.set_mode((WIDTH, HEIGHT))

size_scale = 100
play_image = pygame.transform.scale(
        pygame.image.load(assets["menu"]["buttons"]["play"]).convert_alpha(), (size_scale, size_scale))
settings_image = pygame.transform.scale(
        pygame.image.load(assets["menu"]["buttons"]["settings"]).convert_alpha(), (size_scale, size_scale))
quit_image = pygame.transform.scale(
        pygame.image.load(assets["menu"]["buttons"]["quit"]).convert_alpha(), (size_scale, size_scale))
volume_image = pygame.transform.scale(
    pygame.image.load(assets["menu"]["buttons"]["volume"]).convert_alpha(), (size_scale, size_scale))

level1_img = pygame.image.load("assets/Menu/Levels/01.png").convert_alpha()
level2_img = pygame.image.load("assets/Menu/Levels/02.png").convert_alpha()
level3_img = pygame.image.load("assets/Menu/Levels/03.png").convert_alpha()


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


def save_blocks(blocks, filename="level_data.csv"):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for block in blocks:
            writer.writerow([block.rect.x, block.rect.y])


def load_blocks(filename="level_data.csv"):
    blocks = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            x, y = int(row[0]), int(row[1])
            blocks.append(Block(x, y, 96))
    return blocks


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", player_skin, 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.dead = False

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
            jump_sound.play()
        elif self.jump_count == 2:
            double_jump_sound.play()

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y, idle_image_path, anim_image_path, frame_count):
        super().__init__()
        self.idle_image = pygame.transform.scale2x(pygame.image.load(idle_image_path).convert_alpha())
        self.anim_images = self.load_anim_images(anim_image_path, frame_count)
        self.image = self.idle_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animating = False
        self.current_frame = 0
        self.frame_count = frame_count
        self.name = "checkpoint"

    def load_anim_images(self, path, frame_count):
        full_image = pygame.transform.scale2x(pygame.image.load(path).convert_alpha())
        frame_width = full_image.get_width() // frame_count
        frame_height = full_image.get_height()
        frames = [full_image.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                  for i in range(frame_count)]
        return frames

    def animate(self):
        self.animating = True

    def update(self):
        if self.animating:
            self.image = self.anim_images[self.current_frame]
            self.current_frame += 1
            if self.current_frame >= self.frame_count:
                self.current_frame = 0
                self.animating = False

    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[CK['left']] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[CK['right']] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()
            hit_sound.play()
            player.dead = True


def draw_text(window, text, pos, action=None):
    font = FONT
    Text = font.render(text, True, (255, 255, 255))
    text_rect = Text.get_rect(center=pos)

    mouse_pos = pygame.mouse.get_pos()
    clicked = pygame.mouse.get_pressed(3)

    if (mouse_pos[0] in range(text_rect.left, text_rect.right)
            and mouse_pos[1] in range(text_rect.top, text_rect.bottom)):
        Text = font.render(text, True, (220, 220, 220))
        if pos[0] in range(text_rect.left, text_rect.right) and pos[1] in range(text_rect.top, text_rect.bottom):
            if clicked[0] and action:
                action()
    else:
        Text = font.render(text, True, (255, 255, 255))

    window.blit(Text, text_rect)


def draw_button(window, button, action=None):
    mouse_pos = pygame.mouse.get_pos()
    clicked = pygame.mouse.get_pressed(3)

    if button.checkForInput(mouse_pos):
        if clicked[0] and action:
            action()

    button.update(window)


def draw_levels(window, background, bg_image, level1_button, level2_button, level3_button):
    for tile in background:
        window.blit(bg_image, tile)

    draw_button(window, level1_button, action=lambda: level1(window, background, bg_image))
    draw_button(window, level2_button, action=lambda: level2(window, background, bg_image))
    draw_button(window, level3_button)

    draw_text(window, "Simple Parkour", (level1_button.x + 230, level1_button.y),
              action=lambda: level1(window, background, bg_image))

    pygame.display.update()


def draw_settings(window, background, bg_image, bg_music_slider, sfx_slider, volume_image, volume_image_pos):
    for tile in background:
        window.blit(bg_image, tile)

    window.blit(volume_image, volume_image_pos)
    bg_music_slider.draw(window)
    sfx_slider.draw(window)
    draw_text(window, "music", (670, 200))
    draw_text(window, "sounds", (685, 250))

    pygame.display.update()


def draw_menu(window, background, bg_image, play_button, settings_button, quit_button):
    for tile in background:
        window.blit(bg_image, tile)

    draw_text(window, "Play", (play_button.x + 110, play_button.y),
              action=lambda: levels(window, background, bg_image))
    draw_text(window, "Settings", (settings_button.x + 160, settings_button.y),
              action=lambda: settings_menu(window, background, bg_image))
    draw_text(window, "Quit", (quit_button.x + 115, quit_button.y),
              action=lambda: q())

    draw_button(window, play_button,
                action=lambda: levels(window, background, bg_image))
    draw_button(window, settings_button,
                action=lambda: settings_menu(window, background, bg_image))
    draw_button(window, quit_button,
                action=lambda: q())

    pygame.display.update()


def draw_game(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def draw_background(window, background, bg_image):
    for tile in background:
        window.blit(bg_image, tile)


def levels(window, background, bg_image):
    level1_image = pygame.transform.scale(level1_img, (size_scale, size_scale))
    level2_image = pygame.transform.scale(level2_img, (size_scale, size_scale))
    level3_image = pygame.transform.scale(level3_img, (size_scale, size_scale))

    level1_pos = (WIDTH // 2 - 200, HEIGHT // 2 - 250)
    level2_pos = (WIDTH // 2 - 200, HEIGHT // 2 - 150)
    level3_pos = (WIDTH // 2 - 200, HEIGHT // 2 - 50)

    level1_button = Button.Button(level1_image, level1_pos)
    level2_button = Button.Button(level2_image, level2_pos)
    level3_button = Button.Button(level3_image, level3_pos)

    levels_run = True

    while levels_run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                levels_run = False
                q()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    levels_run = False
                    main_menu(window)

        draw_levels(window, background, bg_image, level1_button, level2_button, level3_button)


def settings_menu(window, background, bg_image):
    bg_music_slider = Slider.Slider(400, 200, 200, 20, initial_val=mixer.music.get_volume())
    sfx_slider = Slider.Slider(400, 250, 200, 20, initial_val=jump_sound.get_volume())
    volume_icon = volume_image
    volume_icon_pos = (285, 185)

    settings_run = True
    while settings_run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                settings_run = False
                q()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                settings_run = False
                main_menu(window)
            elif bg_music_slider.handle_event(event):
                mixer.music.set_volume(bg_music_slider.val)
            elif sfx_slider.handle_event(event):
                jump_sound.set_volume(sfx_slider.val)
                double_jump_sound.set_volume(sfx_slider.val)
                hit_sound.set_volume(sfx_slider.val)
                jump_sound.play()

        draw_settings(window, background, bg_image, bg_music_slider, sfx_slider, volume_icon, volume_icon_pos)


def main_menu(window):
    background, bg_image = get_background(BG)

    play_button_pos = (WIDTH // 2 - 150, HEIGHT // 2 - 50)
    settings_button_pos = (WIDTH // 2 - 150, HEIGHT // 2 + 50)
    quit_button_pos = (WIDTH // 2 - 150, HEIGHT // 2 + 150)

    play_button_image = play_image
    settings_button_image = settings_image
    quit_button_image = quit_image

    play_button = Button.Button(play_button_image, play_button_pos)
    settings_button = Button.Button(settings_button_image, settings_button_pos)
    quit_button = Button.Button(quit_button_image, quit_button_pos)

    menu_run = True

    while menu_run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_run = False
                q()

        draw_menu(window, background, bg_image, play_button, settings_button, quit_button)


def add_blocks(parkour, objects):
    for i in parkour:
        objects.append(i)


def end_game(window, background, bg_image):

    end = True
    while end:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == CK["esc"]:
                    end = False
                    levels(window, background, bg_image)

        draw_background(window, background, bg_image)
        draw_text(window, "YOU WON!", (WIDTH // 2, HEIGHT // 2 - 50),
                  action=lambda: levels(window, background, bg_image))
        pygame.display.update()


def level1(window, background, bg_image):
    clock = pygame.time.Clock()

    block_size = 96

    player = Player(220, 100, 50, 50)
    fire = Fire(100 + block_size * 7, HEIGHT - block_size - 64, 16, 32)
    fire.on()

    start_point = Checkpoint(100, HEIGHT - block_size - 128, "assets/Items/Checkpoints/Start/Start (Idle).png",
                             "assets/Items/Checkpoints/Start/Start (Moving) (64x64).png", 17)
    end_point = Checkpoint(1700, HEIGHT - block_size - 128, "assets/Items/Checkpoints/End/End (Idle).png",
                           "assets/Items/Checkpoints/End/End (Pressed) (64x64).png", 8)

    checkpoints = [start_point, end_point]
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(0, (WIDTH * 2) // block_size)]
    left_wall = [Block(0, i, block_size)
                 for i in range(HEIGHT - 2 * block_size, -block_size, -block_size)]
    right_wall = [Block((WIDTH * 2) // block_size * block_size - block_size, i, block_size)
                  for i in range(HEIGHT - 2 * block_size, -block_size, -block_size)]
    items = [fire]
    parkour = load_blocks()
    objects = [*floor, *left_wall, *right_wall, *items, *parkour, *checkpoints]
    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                q()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    mx, my = pygame.mouse.get_pos()
                    block_x = (mx + offset_x) // block_size * block_size
                    block_y = my // block_size * block_size + 32

                    new_block = Block(block_x, block_y, block_size)
                    parkour.append(new_block)
                    objects.append(new_block)

                elif event.button == 3:
                    mx, my = pygame.mouse.get_pos()
                    for block in parkour[:]:
                        if block.rect.collidepoint(mx + offset_x, my):
                            parkour.remove(block)
                            objects.remove(block)
                            break

            if event.type == pygame.KEYDOWN:
                if event.key == CK['space'] and player.jump_count < 2:
                    player.jump()
                if event.key == CK['esc']:
                    main_menu(window)

        player.loop(FPS)

        if pygame.sprite.collide_rect(player, start_point) and not start_point.animating:
            start_point.animate()

        if pygame.sprite.collide_rect(player, end_point) and not end_point.animating:
            end_point.animate()
            end_game(window, background, bg_image)

        start_point.update()
        end_point.update()

        for item in items:
            item.loop()

        if player.dead:
            levels(window, background, bg_image)

        handle_move(player, objects)
        draw_game(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel


def level2(window, background, bg_image):
    clock = pygame.time.Clock()

    block_size = 96

    player = Player(220, 100, 50, 50)

    start_point = Checkpoint(100, HEIGHT - block_size - 128, "assets/Items/Checkpoints/Start/Start (Idle).png",
                             "assets/Items/Checkpoints/Start/Start (Moving) (64x64).png", 17)
    end_point = Checkpoint(1700, HEIGHT - 5 * block_size - 128, "assets/Items/Checkpoints/End/End (Idle).png",
                           "assets/Items/Checkpoints/End/End (Pressed) (64x64).png", 8)

    checkpoints = [start_point, end_point]

    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(0, (WIDTH * 2) // block_size)]
    left_wall = [Block(0, i, block_size)
                 for i in range(HEIGHT - 2 * block_size, -block_size, -block_size)]
    right_wall = [Block((WIDTH * 2) // block_size * block_size - block_size, i, block_size)
                  for i in range(HEIGHT - 2 * block_size, -block_size, -block_size)]
    items = [Fire(130 + block_size * 9, HEIGHT - block_size - 64, 16, 32),
             Fire(130 + block_size * 11, HEIGHT - block_size - 64, 16, 32)]
    parkour = load_blocks(filename="level2_data.csv")
    objects = [*floor, *left_wall, *right_wall, *items, *parkour, *checkpoints]
    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                q()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    mx, my = pygame.mouse.get_pos()
                    block_x = (mx + offset_x) // block_size * block_size
                    block_y = my // block_size * block_size + 32

                    new_block = Block(block_x, block_y, block_size)
                    parkour.append(new_block)
                    objects.append(new_block)

                elif event.button == 3:
                    mx, my = pygame.mouse.get_pos()
                    for block in parkour[:]:
                        if block.rect.collidepoint(mx + offset_x, my):
                            parkour.remove(block)
                            objects.remove(block)
                            break

            if event.type == pygame.KEYDOWN:
                if event.key == CK['space'] and player.jump_count < 2:
                    player.jump()
                if event.key == CK['esc']:
                    main_menu(window)
                if event.key == pygame.K_i:
                    save_blocks(parkour, filename="level2_data.csv")

        player.loop(FPS)

        if pygame.sprite.collide_rect(player, start_point) and not start_point.animating:
            start_point.animate()

        if pygame.sprite.collide_rect(player, end_point) and not end_point.animating:
            end_point.animate()
            end_game(window, background, bg_image)

        start_point.update()
        end_point.update()

        for item in items:
            item.on()
            item.loop()

        if player.dead:
            levels(window, background, bg_image)

        handle_move(player, objects)
        draw_game(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel


def q():
    pygame.quit()
    quit()


if __name__ == "__main__":
    main_menu(window)
