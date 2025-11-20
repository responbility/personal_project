from pico2d import *
import game_framework
from spritesheet import SpriteSheet
import game_world

CLIP_W, CLIP_H = 32, 32
SCALE = 3.0
TARGET_W = int(CLIP_W * SCALE)
TARGET_H = int(CLIP_H * SCALE)

class Guard:
    def __init__(self, x=400, y=400):
        try:
            cw = get_canvas_width()
            ch = get_canvas_height()
        except Exception:
            cw, ch = 576, 1024
        self.x = x
        self.y = y
        self.frame = 0.0
        self.dir = -1
        self.sheet = None
        self.frames_count = 1
        try:
            self.sheet = SpriteSheet('assets/guard.png', CLIP_W, CLIP_H)
            self.frames_count = self.sheet.cols * self.sheet.rows
        except Exception:
            try:
                self.sheet = SpriteSheet('guard.png', CLIP_W, CLIP_H)
                self.frames_count = self.sheet.cols * self.sheet.rows
            except Exception:
                self.sheet = None
                self.frames_count = 1
        self.hp = 5

    def get_bb(self):
        return self.x - TARGET_W // 2, self.y - TARGET_H // 2, self.x + TARGET_W // 2, self.y + TARGET_H // 2

    def update(self):
        # animation
        try:
            self.frame = (self.frame + self.frames_count * 1.0 * game_framework.frame_time) % max(1, self.frames_count)
        except Exception:
            pass

    def draw(self):
        if self.sheet:
            try:
                idx = int(self.frame) % max(1, self.frames_count)
                self.sheet.draw_frame(idx, self.x, self.y, TARGET_W, TARGET_H, flip=(self.dir<0))
            except Exception:
                pass
        else:
            draw_rectangle(*self.get_bb())

    def take_damage(self, dmg):
        try:
            self.hp -= dmg
            print(f"DEBUG: Guard took {dmg} dmg, hp={self.hp}")
            if self.hp <= 0:
                try:
                    game_world.remove_object(self)
                except Exception:
                    pass
        except Exception:
            pass

    def handle_event(self, e):
        pass

    def on_collision(self, other):
        pass

