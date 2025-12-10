from pico2d import *
import game_framework
import game_world
from ball import Ball


class Ratking:
    FRAME_W = 16
    FRAME_H = 16
    COLS = 12

    IDLE_FRAMES = [0, 1, 2, 3]
    WALK_FRAMES = [4, 5, 6, 7, 8, 9, 10, 11]
    SCALE = 4.0
    ANIMATION_SPEED = 10

    def __init__(self, x=400, y=300):
        self.x, self.y = x, y
        self.dir = 1
        self.action = 'idle'

        self.frame_index = 0
        self.frame_time = 0

        self.screen_x = x
        self.screen_y = y

        self.image = load_image('assets/ratking.png')

    def _current_frames(self):
        return Ratking.IDLE_FRAMES if self.action == 'idle' else Ratking.WALK_FRAMES

    def update(self):
        # 애니메이션
        self.frame_time += 1
        if self.frame_time >= Ratking.ANIMATION_SPEED:
            self.frame_time = 0
            frames = self._current_frames()
            self.frame_index = (self.frame_index + 1) % len(frames)

        # 이동
        if self.action == 'walk':
            self.x += self.dir * 3

        self.update_screen_position()

    def update_screen_position(self):
        try:
            import play_mode
            self.screen_x = self.x - play_mode.bg.window_left
            self.screen_y = self.y - play_mode.bg.window_bottom
        except:
            self.screen_x = self.x
            self.screen_y = self.y

    def draw(self):
        frames = self._current_frames()
        frame_no = frames[self.frame_index]

        col = frame_no % Ratking.COLS
        sx = col * Ratking.FRAME_W
        sy = 0

        dw = int(Ratking.FRAME_W * Ratking.SCALE)
        dh = int(Ratking.FRAME_H * Ratking.SCALE)

        if self.dir == 1:
            self.image.clip_draw(sx, sy, Ratking.FRAME_W, Ratking.FRAME_H,
                                 self.screen_x, self.screen_y, dw, dh)
        else:
            self.image.clip_composite_draw(
                sx, sy,
                Ratking.FRAME_W, Ratking.FRAME_H,
                0, 'h',
                self.screen_x, self.screen_y,
                dw, dh
            )

    def fire_ball(self):
        speed = 30

        if self.dir == 1:
            ball_x = self.x + 30
            angle = 0
        else:
            ball_x = self.x - 30
            angle = 180

        ball = Ball(ball_x, self.y, speed, angle)
        game_world.add_object(ball, 1)

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key in (SDLK_LEFT, SDLK_a):
                self.dir = -1
                if self.action != 'walk':
                    self.action = 'walk'
                    self.frame_index = 0

            elif event.key in (SDLK_RIGHT, SDLK_d):
                self.dir = 1
                if self.action != 'walk':
                    self.action = 'walk'
                    self.frame_index = 0

            elif event.key == SDLK_SPACE:
                self.fire_ball()

        elif event.type == SDL_KEYUP:
            if event.key in (SDLK_LEFT, SDLK_RIGHT, SDLK_a, SDLK_d):
                if self.action != 'idle':
                    self.action = 'idle'
                    self.frame_index = 0
