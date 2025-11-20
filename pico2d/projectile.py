from pico2d import *
import game_world
import game_framework

TARGET_W = 12
TARGET_H = 12

class Projectile:
    def __init__(self, x, y, vx, vy=0, damage=1, owner=None, life_time=3.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.owner = owner
        self.life = life_time
        self.image = None
        try:
            self.image = load_image('assets/projectile.png')
        except Exception:
            try:
                self.image = load_image('projectile.png')
            except Exception:
                self.image = None

    def get_bb(self):
        return self.x - TARGET_W//2, self.y - TARGET_H//2, self.x + TARGET_W//2, self.y + TARGET_H//2

    def update(self):
        dt = getattr(game_framework, 'frame_time', 1.0/60.0)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        # remove when life ended or out of canvas
        try:
            cw = get_canvas_width()
            ch = get_canvas_height()
        except Exception:
            cw, ch = 800, 600
        if self.life <= 0 or self.x < -50 or self.x > cw + 50 or self.y < -50 or self.y > ch + 50:
            try:
                game_world.remove_object(self)
            except Exception:
                pass

    def draw(self):
        if self.image:
            try:
                self.image.draw(self.x, self.y)
            except Exception:
                pass
        else:
            draw_rectangle(*self.get_bb())

    def on_collision(self, other):
        # When colliding with an enemy, deal damage and remove self
        try:
            if hasattr(other, 'take_damage'):
                other.take_damage(self.damage)
        except Exception:
            pass
        try:
            game_world.remove_object(self)
        except Exception:
            pass

