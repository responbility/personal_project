from pico2d import *

import game_world


class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(400, 30)
        self.image.draw(1200, 30)

    def get_bb(self):
        return 0, 0, 1600 - 1, 50


def hande_collision(self, group, other):
        if group == 'boy:ball':
            game_world.remove_object(self)
        elif group == 'boy:ball':
            self.stopped = True
