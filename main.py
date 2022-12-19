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
mob_group = pygame.sprite.Group()
missile_group = pygame.sprite.Group()
block_group = pygame.sprite.Group()


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
                    block_group.add(Tile('wall', x, y))
        return x, y

    def get_tile_check(self, position):
        x = (position[0]) // tile_width
        y = (position[1]) // tile_height
        return self.map[y][x]


class Mob(pygame.sprite.Sprite):
    image = load_image("characters/character.png")

    def __init__(self, x, y, *groups):
        super().__init__(mob_group, all_sprites)
        self.image = Mob.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 30
        self.frames_run_down = []
        self.frames_run_count_down = 0
        self.run_down = 'characters/character_down.png'
        self.cut_sheet(load_image(self.run_down), 3, 1, self.frames_run_down, x, y)

    def cut_sheet(self, sheet, columns, rows, frames, x, y):
        self.rect = pygame.Rect(x, y, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def get_damage(self, hp):
        self.hp -= hp
        if self.hp <= 0:
            self.kill()


class Missile(pygame.sprite.Sprite):
    def __init__(self, map, char, direction):
        super().__init__(missile_group, all_sprites)

        self.map = map
        self.map_size = self.map.get_size_map()
        self.speed = 10
        self.char, self.direction = char, direction
        print(self.char, self.direction)
        self.image = pygame.Surface((2 * 5, 2 * 5),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("white"),
                           (5, 5), 5)
        self.rect = pygame.Rect(self.char[0], self.char[1], 2 * 5, 2 * 5)

        self.mask = pygame.mask.from_surface(self.image)
        self.rect.centerx = self.char[0]
        self.rect.centery = self.char[1]

    def update(self):
        if self.direction == 'd':
            self.rect.centerx += self.speed
        if self.direction == 'a':
            self.rect.centerx -= self.speed
        if self.direction == 'w':
            self.rect.centery -= self.speed
        if self.direction == 's':
            self.rect.centery += self.speed

        for mob in pygame.sprite.spritecollide(self, mob_group, dokill=False):
            mob.get_damage(10)
            self.kill()
        if pygame.sprite.spritecollideany(self, block_group):
            self.kill()


class Hero(pygame.sprite.Sprite):
    # 48x60
    image = load_image("characters/character.png")
    image_d = load_image("characters/character_d.png")
    image_a = load_image("characters/character_a.png")
    image_w = load_image("characters/character_w.png")
    image_s = load_image("characters/character.png")

    def __init__(self, map):
        super().__init__(hero_group, all_sprites)
        self.map = map
        self.map_size = self.map.get_size_map()
        self.health_point = 100
        self.speed = 6
        self.direction = 's'
        self.idle()
        self.attack_speed = 5
        self.timer = 0
        self.rect = self.image.get_rect()
        self.x, self.y = self.rect.centerx, self.rect.centery

        self.mask = pygame.mask.from_surface(self.image)

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
                frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def idle(self):
        if self.direction == 'd':
            self.image = Hero.image_d
        elif self.direction == 'a':
            self.image = Hero.image_a
        elif self.direction == 'w':
            self.image = Hero.image_w
        elif self.direction == 's':
            self.image = Hero.image_s

    def get_rect_center(self):
        return self.rect.center

    def take_damage(self, damage):
        self.health_point -= damage

    def attack(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.timer = (self.timer + 1) % self.attack_speed
            if self.timer == 0:
                Missile(self.map, self.rect.center, self.direction)

    def animated_move(self, frames_run_count, frames_run):
        frames_run_count = (frames_run_count + 1) % len(frames_run)
        self.image = frames_run[frames_run_count]
        return frames_run_count, frames_run

    def check_move(self, position):
        print(self.rect)
        return self.map.get_tile_check(position)

    def get_direction(self):
        return self.direction

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.direction = 'd'
            self.frames_run_count_right, self.frames_run_right = self.animated_move(self.frames_run_count_right,
                                                                                    self.frames_run_right)
            if self.check_move((self.x + tile_width // 2 + 1, self.y)) != '#':
                self.rect.x += self.speed
        if keys[pygame.K_a]:
            self.direction = 'a'
            self.frames_run_count_left, self.frames_run_left = self.animated_move(self.frames_run_count_left,
                                                                                  self.frames_run_left)
            if self.check_move((self.x - tile_width // 2 - 1, self.y)) != '#':
                self.rect.x -= self.speed
        if keys[pygame.K_w]:
            self.direction = 'w'
            self.frames_run_count_up, self.frames_run_up = self.animated_move(self.frames_run_count_up,
                                                                              self.frames_run_up)
            if self.check_move((self.x, self.y - tile_height // 2 - 1)) != '#':
                self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.direction = 's'
            self.frames_run_count_down, self.frames_run_down = self.animated_move(self.frames_run_count_down,
                                                                                  self.frames_run_down)
            if self.check_move((self.x, self.y + tile_height // 2 + 1)) != '#':
                self.rect.y += self.speed
        self.x += camera.dx
        self.y += camera.dy

    def update(self, *args, **kwargs):
        self.idle()
        self.move()
        self.attack()


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


camera = Camera()
running = True
m = Map('room_1.txt')
character = Hero(m)
for i in range(200, 600, 100):
    Mob(200, i)
while running:
    screen.fill('black')
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # изменяем ракурс камеры
    camera.update(character)
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        camera.apply(sprite)
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()
    clock.tick(30)
pygame.quit()
