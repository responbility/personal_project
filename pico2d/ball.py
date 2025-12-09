from pico2d import *
import game_world
import game_framework
import math

PIXEL_PER_METER = (1.0 / 0.03)  # 1pixel = 3cm, 1m = 33.33 pixel
GRAVITY = 9.8  # 중력 가속도 (m/s²)


class Ball:
    image = None
    BASE_DRAW_SIZE = 21  # 원본 이미지 크기 (21x21 가정)
    BASE_BB_RADIUS = 10  # 원본 충돌 반경 (10 픽셀 가정)

    def get_bb(self):
        # 1. 크기 비율에 따라 충돌 영역(BB)의 크기를 줄입니다.
        scaled_radius = self.BASE_BB_RADIUS * self.scale
        return self.x - scaled_radius, self.y - scaled_radius, \
               self.x + scaled_radius, self.y + scaled_radius

    def __init__(self, x=400, y=300, throwin_speed=15, throwin_angle=45):
        if Ball.image == None:
            # assets/ball.jpg 대신, ball.png처럼 투명 배경이 있는 작은 이미지 권장
            Ball.image = load_image('assets/ball.jpg')

        self.x, self.y = x, y

        # ⭐ 공의 크기를 제어하는 변수: 0.5 (절반 크기), 1.0 (원본 크기)
        self.scale = 0.5  # <--- 여기서 크기를 50%로 설정했습니다!

        self.xv = throwin_speed * math.cos(math.radians(throwin_angle))  # m/s
        # Ratking이 수평 발사 시, yv는 0으로 시작해야 중력의 영향을 받습니다.
        # abs()를 제거하고 각도를 처리하는 것이 더 일반적인 물리 구현 방식입니다.
        self.yv = throwin_speed * math.sin(math.radians(throwin_angle))  # m/s

        self.stopped = True if throwin_speed == 0.0 else False

    def draw(self):
        # 2. 크기 비율에 따라 실제로 그려지는 크기를 줄입니다.
        draw_width = int(self.BASE_DRAW_SIZE * self.scale)
        draw_height = int(self.BASE_DRAW_SIZE * self.scale)

        # resize_image는 없습니다. draw에 폭과 높이를 넘겨 크기를 조절합니다.
        self.image.draw(self.x, self.y, draw_width, draw_height)

    def update(self):
        if self.stopped:
            return
        # 위치 업데이트
        self.x += self.xv * game_framework.frame_time * PIXEL_PER_METER
        self.y += self.yv * game_framework.frame_time * PIXEL_PER_METER

        # y 축 속도에 중력 가속도 적용
        self.yv -= GRAVITY * game_framework.frame_time  # m/s

    def handle_collision(self, group, other):
        if group == 'boy:ball':
            game_world.remove_object(self)
        elif group == 'grass:ball':
            self.stopped = True