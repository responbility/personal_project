from pico2d import *
import math
import game_framework
import game_world
import play_mode

PIXEL_PER_METER = 1.0 / 0.03
GRAVITY = 9.8


class Ball:
    image = None
    BASE_DRAW_SIZE = 21
    BASE_BB_RADIUS = 10

    def get_bb(self):
        scaled_radius = self.BASE_BB_RADIUS * self.scale
        return (self.x - scaled_radius, self.y - scaled_radius,
                self.x + scaled_radius, self.y + scaled_radius)

    def __init__(self, x=400, y=300, throwin_speed=30, throwin_angle=0):
        # 이미지가 아직 없으면 한 번만 로드 (png/jpg/jpeg 순서대로 시도)
        if Ball.image is None:
            candidates = [
                'assets/ball.png',
                'assets/ball.jpg',
                'assets/ball.jpeg',
            ]
            last_error = None
            for path in candidates:
                try:
                    Ball.image = load_image(path)
                    print(f"[Ball] 이미지 로드 성공: {path}")
                    last_error = None
                    break
                except Exception as e:
                    print(f"[Ball] 이미지 로드 실패: {path} -> {e}")
                    last_error = e
            if Ball.image is None:
                print(f"[Ball] 사용 가능한 ball 이미지를 찾지 못했습니다. 마지막 에러: {last_error}")

        self.x, self.y = x, y
        self.scale = 0.5

        self.xv = throwin_speed * math.cos(math.radians(throwin_angle))
        self.yv = throwin_speed * math.sin(math.radians(throwin_angle))

        self.stopped = (throwin_speed == 0.0)

    def update(self):
        if self.stopped:
            return

        # 수평 이동
        self.x += self.xv * game_framework.frame_time * PIXEL_PER_METER

        # 화면 밖 제거
        if (self.x < -100 or self.x > play_mode.MAP_WIDTH + 100 or
                self.y < -100 or self.y > play_mode.MAP_HEIGHT + 100):
            game_world.remove_object(self)

    def draw(self):
        # 이미지가 없으면 그리지 않음 (게임은 계속 진행)
        if Ball.image is None:
            return

        window_left = getattr(play_mode.bg, "window_left", 0)
        window_bottom = getattr(play_mode.bg, "window_bottom", 0)

        sx = self.x - window_left
        sy = self.y - window_bottom

        dw = int(self.BASE_DRAW_SIZE * self.scale)
        dh = int(self.BASE_DRAW_SIZE * self.scale)

        Ball.image.draw(sx, sy, dw, dh)
