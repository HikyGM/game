import os
import sys
import pygame

size = width, height = 500, 700
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Игра')
clock = pygame.time.Clock()
tile_width = tile_height = 20

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
hero_group = pygame.sprite.Group()


def load_level(filename):
    filename = "data/rooms/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


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


def generate_level(level):
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '0':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
    return x, y


class Tile(pygame.sprite.Sprite):
    tile_images = {
        'wall': pygame.transform.scale(load_image('rooms/tiles/box.png'), (20, 20)),
        'empty': pygame.transform.scale(load_image('rooms/tiles/grass.png'), (20, 20))
    }

    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = Tile.tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)

    def dead(self):
        self.kill()


class Hero(Enemy):
    tile_images = {
        'wall': pygame.transform.scale(load_image('rooms/tiles/box.png'), (20, 20)),
        'empty': pygame.transform.scale(load_image('rooms/tiles/grass.png'), (20, 20))
    }

    def __init__(self, *groups):
        super().__init__(hero_group, all_sprites)
        self.x_pos, self.y_pos = 200, 100
        self.speed = 10
        self.hero = pygame.draw.circle(screen, (255, 0, 0), (self.x_pos, self.y_pos), 20)

    def idle(self):
        pass



    def move_(self):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.y_pos -= self.speed
            if event.key == pygame.K_s:
                self.y_pos += self.speed
            if event.key == pygame.K_a:
                self.x_pos -= self.speed
            if event.key == pygame.K_d:
                self.x_pos += self.speed
        self.hero.move(self.x_pos, self.y_pos)
        print(self.x_pos, self.y_pos)

    def update(self, *args, **kwargs):
        self.move_()


class Monster(Enemy):
    def __init__(self, *groups):
        super().__init__(*groups)


class Object(Enemy):
    def __init__(self, *groups):
        super().__init__(*groups)


running = True

level_x, level_y = generate_level(load_level('room_1.txt'))

while running:
    clock.tick(30)
    all_sprites.draw(screen)
    hero_group.draw(screen)
    all_sprites.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()
