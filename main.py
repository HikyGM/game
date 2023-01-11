from __future__ import annotations

from pathlib import Path
from typing import List

import pygame
from pygame.locals import K_MINUS, K_EQUALS, K_ESCAPE, K_r, K_w, K_s, K_a, K_d
from pygame.locals import KEYDOWN, VIDEORESIZE, QUIT
from pytmx.util_pygame import load_pygame

import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup

# define configuration variables here
CURRENT_DIR = Path(__file__).parent
RESOURCES_DIR = CURRENT_DIR / "data"
HERO_MOVE_SPEED = 50  # pixels per second


# simple wrapper to keep the screen resizeable
def init_screen(width: int, height: int) -> pygame.Surface:
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    return screen


# make loading images a little easier
def load_image(filename: str) -> pygame.Surface:
    return pygame.image.load(str(RESOURCES_DIR / filename))


class Hero(pygame.sprite.Sprite):
    """
    Our Hero
    The Hero has three collision rects, one for the whole sprite "rect"
    and "old_rect", and another to check collisions with walls, called
    "feet".
    The position list is used because pygame rects are inaccurate for
    positioning sprites; because the values they get are 'rounded down'
    as integers, the sprite would move faster moving left or up.
    Feet is 1/2 as wide as the normal rect, and 8 pixels tall.  This
    size allows the top of the sprite to overlap walls.  The feet rect
    is used for collisions, while the 'rect' rect is used for drawing.
    There is also an old_rect that is used to reposition the sprite if
    it collides with level walls.
    """

    # 48x60
    image = load_image("characters/character.png")
    image_d = load_image("characters/character_d.png")
    image_a = load_image("characters/character_a.png")
    image_w = load_image("characters/character_w.png")
    image_s = load_image("characters/character.png")

    def __init__(self, position) -> None:
        super().__init__()
        self.image = load_image("characters/Girl-idle.png").convert_alpha()
        self.velocity = [0, 0]
        self._position = [0.0, 0.0]
        self._old_position = self.position
        self.rect = self.image.get_rect()
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, 8)
        self.speed_animation = 50
        self.timer = 0
        self.x, self.y = position
        self.direction = 's'
        # Анимации пресонажа
        # 1.Список спрайтов анимации
        # 2.Счётчик спрайта для вывода на экран
        # 3.Изображение спрайтов
        # 4.Функция генерирующая список спрайтов из изображения
        # (изображение, кол-во колонок, кол-во строк, список добавления)

        # Движение
        self.frames_run_down = []
        self.frames_run_count_down = 0
        self.run_down = 'characters/Girl-move-down.png'
        self.cut_sheet(load_image(self.run_down), 6, 1, self.frames_run_down)

        self.frames_run_left = []
        self.frames_run_count_left = 0
        self.run_left = 'characters/Girl-move-left.png'
        self.cut_sheet(load_image(self.run_left), 6, 1, self.frames_run_left)

        self.frames_run_right = []
        self.frames_run_count_right = 0
        self.run_right = 'characters/Girl-move-right.png'
        self.cut_sheet(load_image(self.run_right), 6, 1, self.frames_run_right)

        self.frames_run_up = []
        self.frames_run_count_up = 0
        self.run_up = 'characters/Girl-move-up.png'
        self.cut_sheet(load_image(self.run_up), 6, 1, self.frames_run_up)

        # Ожидание
        self.frames_idle_down = []
        self.frames_idle_count_down = 0
        self.idle_down = 'characters/Girl-idle-down.png'
        self.cut_sheet(load_image(self.idle_down), 4, 1, self.frames_idle_down)

        self.frames_idle_up = []
        self.frames_idle_count_up = 0
        self.idle_up = 'characters/Girl-idle-up.png'
        self.cut_sheet(load_image(self.idle_up), 4, 1, self.frames_idle_up)

        self.frames_idle_left = []
        self.frames_idle_count_left = 0
        self.idle_left = 'characters/Girl-idle-left.png'
        self.cut_sheet(load_image(self.idle_left), 4, 1, self.frames_idle_left)

        self.frames_idle_right = []
        self.frames_idle_count_right = 0
        self.idle_right = 'characters/Girl-idle-right.png'
        self.cut_sheet(load_image(self.idle_right), 4, 1, self.frames_idle_right)

    def cut_sheet(self, sheet, columns, rows, frames):
        self.rect = pygame.Rect(self.x, self.y, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def animated_move(self, direction):
        self.timer += 1
        if direction == 'i':
            self.idle()
            return
        if self.timer > self.speed_animation:
            if direction == 'w':
                self.frames_run_count_up = (self.frames_run_count_up + 1) % len(self.frames_run_up)
                self.image = self.frames_run_up[self.frames_run_count_up]
            elif direction == 's':
                self.frames_run_count_down = (self.frames_run_count_down + 1) % len(self.frames_run_down)
                self.image = self.frames_run_down[self.frames_run_count_down]
            elif direction == 'a':
                self.frames_run_count_left = (self.frames_run_count_left + 1) % len(self.frames_run_left)
                self.image = self.frames_run_left[self.frames_run_count_left]
            elif direction == 'd':
                self.frames_run_count_right = (self.frames_run_count_right + 1) % len(self.frames_run_right)
                self.image = self.frames_run_right[self.frames_run_count_right]
            self.direction = direction
            self.timer = 0

    def idle(self):
        self.timer += 1
        if self.timer > self.speed_animation // 4 * 15:
            if self.direction == 'd':
                self.frames_idle_count_right = (self.frames_idle_count_right + 1) % len(self.frames_idle_right)
                self.image = self.frames_idle_right[self.frames_idle_count_right]
            elif self.direction == 'a':
                self.frames_idle_count_left = (self.frames_idle_count_left + 1) % len(self.frames_idle_left)
                self.image = self.frames_idle_left[self.frames_idle_count_left]
            elif self.direction == 'w':
                self.frames_idle_count_up = (self.frames_idle_count_up + 1) % len(self.frames_idle_up)
                self.image = self.frames_idle_up[self.frames_idle_count_up]
            elif self.direction == 's':
                self.frames_idle_count_down = (self.frames_idle_count_down + 1) % len(self.frames_idle_down)
                self.image = self.frames_idle_down[self.frames_idle_count_down]
            self.timer = 0

    @property
    def position(self) -> List[float]:
        return list(self._position)

    @position.setter
    def position(self, value: List[float]) -> None:
        self._position = list(value)

    def update(self, dt: float) -> None:
        self._old_position = self._position[:]
        self._position[0] += self.velocity[0] * dt
        self._position[1] += self.velocity[1] * dt
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom

    def move_back(self, dt: float) -> None:
        """        If called after an update, the sprite can move back        """
        self._position = self._old_position
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom


class QuestGame:
    """
    This class is a basic game.
    This class will load data, create a pyscroll group, a hero object.
    It also reads input and moves the Hero around the map.
    Finally, it uses a pyscroll group to render the map and Hero.
    """
    map_path = RESOURCES_DIR / "maps/map_1/map.tmx"

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

        # true while running
        self.running = False

        # load data from pytmx
        tmx_data = load_pygame(self.map_path)

        # setup level geometry with simple pygame rects, loaded from pytmx
        self.obec = []
        self.walls = []
        for obj in tmx_data.objects:
            if obj.name == 'asd':
                self.obec.append(obj)
            self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        if self.obec:
            print(self.obec)
            print(self.obec[0].name)
        # create new renderer (camera)
        self.map_layer = pyscroll.BufferedRenderer(
            data=pyscroll.data.TiledMapData(tmx_data),
            size=screen.get_size(),
            clamp_camera=True,
        )
        self.map_layer.zoom = 3

        # pyscroll supports layered rendering.  our map has 3 'under'
        # layers.  layers begin with 0.  the layers are 0, 1, and 2.
        # sprites are always drawn over the tiles of the layer they are
        # on.  since we want the sprite to be on top of layer 2, we set
        # the default layer for sprites as 2.
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=1)

        # put the hero in the center of the map
        self.hero = Hero((200, 200))
        self.hero.position = self.map_layer.map_rect.center

        # add our hero to the group
        self.group.add(self.hero)

    def draw(self) -> None:
        # center the map/screen on our Hero
        self.group.center(self.hero.rect.center)
        # draw the map and all sprites
        self.group.draw(self.screen)

    def handle_input(self) -> None:
        """        Handle pygame input events        """
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                break
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                    break
                elif event.key == K_r:
                    self.map_layer.reload()

                elif event.key == K_EQUALS:
                    self.map_layer.zoom += 0.25
                elif event.key == K_MINUS:
                    value = self.map_layer.zoom - 0.25
                    if value > 0:
                        self.map_layer.zoom = value
            # this will be handled if the window is resized
            elif event.type == VIDEORESIZE:
                self.screen = init_screen(event.w, event.h)
                self.map_layer.set_size((event.w, event.h))

        # use `get_pressed` for an easy way to detect held keys
        pressed = pygame.key.get_pressed()
        direction = 's'
        if pressed[K_w] or pressed[K_s] or pressed[K_a] or pressed[K_d]:
            if pressed[K_w]:
                self.hero.velocity[1] = -HERO_MOVE_SPEED
                direction = 'w'
            elif pressed[K_s]:
                self.hero.velocity[1] = HERO_MOVE_SPEED
                direction = 's'
            else:
                self.hero.velocity[1] = 0
            if pressed[K_a]:
                self.hero.velocity[0] = -HERO_MOVE_SPEED
                direction = 'a'
            elif pressed[K_d]:
                self.hero.velocity[0] = HERO_MOVE_SPEED
                direction = 'd'
            else:
                self.hero.velocity[0] = 0
        else:
            direction = 'i'
            self.hero.velocity[1] = 0
            self.hero.velocity[0] = 0
        self.hero.animated_move(direction)

    def update(self, dt: float):
        """        Tasks that occur over time should be handled here        """
        self.group.update(dt)

        # check if the sprite's feet are colliding with wall
        # sprite must have a rect called feet, and move_back method,
        # otherwise this will fail
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back(dt)

    def run(self):
        """        Run the game loop        """
        clock = pygame.time.Clock()
        self.running = True
        try:
            while self.running:
                dt = clock.tick() / 1000.0
                self.handle_input()
                self.update(dt)
                self.draw()
                pygame.display.flip()
        except KeyboardInterrupt:
            self.running = False


def main() -> None:
    pygame.init()
    pygame.font.init()
    screen = init_screen(960, 800)
    pygame.display.set_caption("Quest - An epic journey.")
    try:
        game = QuestGame(screen)
        game.run()
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
