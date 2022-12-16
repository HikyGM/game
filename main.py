import os
import sys
import pygame

size = width, height = 500, 700
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Игра')
clock = pygame.time.Clock()
tile_width = tile_height = 50

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
hero_group = pygame.sprite.Group()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Tile(pygame.sprite.Sprite):
    tile_images = {
        'wall': pygame.transform.scale(load_image('rooms/tiles/box.png'), (50, 50)),
        'empty': pygame.transform.scale(load_image('rooms/tiles/grass.png'), (50, 50))
    }

    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = Tile.tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def get_tile_id(self, position):
        return


class Enemy(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)

    def dead(self):
        self.kill()


class Map:
    def __init__(self, filename):
        self.map_row = self.load_level(filename)
        self.map = [list(row) for row in self.map_row]

        self.size_map_x = width // tile_width
        self.size_map_y = height // tile_height
        self.tile_free = '0'

        self.generate_level(self.map)

    def load_level(self, filename):
        filename = "data/rooms/" + filename
        # читаем уровень, убирая символы перевода строки
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        return level_map

    def get_size_map(self):
        return self.size_map_x, self.size_map_y

    def generate_level(self, level):
        x, y = None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '0':
                    Tile('empty', x, y)
                elif level[y][x] == '#':
                    Tile('wall', x, y)
        return x, y

    def get_tile_check(self, position):
        x = position[0] // tile_width
        y = position[1] // tile_height
        return self.map[y][x]


class Hero(Enemy):
    # 48x60
    image = load_image("characters/character_down.png")

    def __init__(self, map, *groups):
        super().__init__(hero_group, all_sprites)
        self.map = map
        self.map_size = self.map.get_size_map()
        # print(self.map_size)
        self.speed = 10
        self.image = Hero.image
        self.rect = self.image.get_rect()
        self.rect.x = 500
        self.rect.y = 500

        self.frames_run_down = []
        self.frames_run_count_down = 0
        self.run_down = 'characters/character_down.png'
        self.cut_sheet(load_image(self.run_down), 3, 1, self.frames_run_down)

        self.frames_run_left = []
        self.frames_run_count_left = 0
        self.run_left = 'characters/character_left.png'
        self.cut_sheet(load_image(self.run_left), 3, 1, self.frames_run_left)

        self.frames_run_right = []
        self.frames_run_count_right = 0
        self.run_right = 'characters/character_right.png'
        self.cut_sheet(load_image(self.run_right), 3, 1, self.frames_run_right)

        self.frames_run_up = []
        self.frames_run_count_up = 0
        self.run_up = 'characters/character_up.png'
        self.cut_sheet(load_image(self.run_up), 3, 1, self.frames_run_up)

    def cut_sheet(self, sheet, columns, rows, frames):
        self.rect = pygame.Rect(100, 100, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def idle(self):
        pass

    def animated_move(self, frames_run_count, frames_run):
        frames_run_count = (frames_run_count + 1) % len(frames_run)
        self.image = frames_run[frames_run_count]
        return frames_run_count, frames_run

    def check_move(self, position):
        return self.map.get_tile_check(position)

    def update(self, *args, **kwargs):

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.frames_run_count_right, self.frames_run_right = self.animated_move(self.frames_run_count_right,
                                                                                    self.frames_run_right)
            if self.check_move((self.rect.right + 1, self.rect.centery)) != '#':
                self.rect.x += self.speed
        if keys[pygame.K_a]:
            self.frames_run_count_left, self.frames_run_left = self.animated_move(self.frames_run_count_left,
                                                                                  self.frames_run_left)
            if self.check_move((self.rect.left - 1, self.rect.centery)) != '#':
                self.rect.x -= self.speed
        if keys[pygame.K_w]:
            self.frames_run_count_up, self.frames_run_up = self.animated_move(self.frames_run_count_up,
                                                                              self.frames_run_up)
            if self.check_move((self.rect.centerx, self.rect.top - 1)) != '#':
                self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.frames_run_count_down, self.frames_run_down = self.animated_move(self.frames_run_count_down,
                                                                                  self.frames_run_down)
            if self.check_move((self.rect.centerx, self.rect.bottom + 1)) != '#':
                self.rect.y += self.speed


running = True

m = Map('room_2.txt')
b = Hero(m)
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
