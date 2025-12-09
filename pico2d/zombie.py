import random
import math
import game_framework
import game_world

from pico2d import *

# zombie Run Speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 10.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# zombie Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10.0

animation_names = ['Walk']


class Zombie:
    images = None

    def load_images(self):
        if Zombie.images == None:
            Zombie.images = {}
            for name in animation_names:
                # 좀비 애니메이션 이미지를 'zombie' 폴더에서 로드
                Zombie.images[name] = [load_image("./zombie/" + name + " (%d)" % i + ".png") for i in range(1, 11)]

    def __init__(self):
        # 초기 위치 설정 (1600x900 맵의 오른쪽 절반 영역, y=150)
        self.x, self.y = random.randint(1600 - 800, 1600), 150
        self.load_images()
        self.frame = random.randint(0, 9)
        # 초기 이동 방향 설정
        self.dir = random.choice([-1, 1])

    def get_bb(self):
        # 충돌 박스 (Bounding Box) 반환
        return self.x - 100, self.y - 100, self.x + 100, self.y + 100

    def update(self):
        # 애니메이션 프레임 업데이트
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION

        # 좀비 이동
        self.x += RUN_SPEED_PPS * self.dir * game_framework.frame_time

        # 맵 경계 체크 및 방향 전환
        if self.x > 1600:
            self.dir = -1  # 오른쪽 경계 초과 시 왼쪽으로
        elif self.x < 800:
            self.dir = 1  # 왼쪽 경계(맵 중앙) 초과 시 오른쪽으로

        # x좌표를 800과 1600 사이로 제한
        self.x = clamp(800, self.x, 1600)
        pass

    def draw(self):
        # 방향에 따라 이미지를 좌우 반전하여 그림
        if self.dir < 0:
            # 왼쪽 방향: 수평 반전(h)하여 그리기
            Zombie.images['Walk'][int(self.frame)].composite_draw(0, 'h', self.x, self.y, 200, 200)
        else:
            # 오른쪽 방향: 그대로 그리기
            Zombie.images['Walk'][int(self.frame)].draw(self.x, self.y, 200, 200)

        # 충돌 박스 그리기 (디버깅용)
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        # 충돌 처리 로직
        if group == 'zombies:boy':
            game_world.remove_object(other)
            print("hit boy")