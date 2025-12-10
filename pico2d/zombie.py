import random
import math
import game_framework
import game_world

from pico2d import *

# Boss Run Speed (좀비보다 느리게 설정)
BOSS_RUN_SPEED_KMPH = 5.0
BOSS_RUN_SPEED_MPM = (BOSS_RUN_SPEED_KMPH * 1000.0 / 60.0)
BOSS_RUN_SPEED_MPS = (BOSS_RUN_SPEED_MPM / 60.0)
# PIXEL_PER_METER는 좀비와 동일하게 사용
BOSS_RUN_SPEED_PPS = (BOSS_RUN_SPEED_MPS * (10.0 / 0.3))


# 보스는 애니메이션이 없으므로 프레임 관련 상수는 사용하지 않습니다.

class Boss:
    image = None
    BOSS_WIDTH, BOSS_HEIGHT = 400, 300  # 보스 크기 설정

    def __init__(self):
        # 1. 이미지 로드 (제공된 'boss.png' 사용)
        if Boss.image is None:
            # './assets/boss.png' 경로를 사용하거나,
            # 프로젝트 구조에 따라 실제 경로를 지정해야 합니다.
            Boss.image = load_image('./assets/boss.png')

            # 2. 초기 월드 좌표 설정 (맵 중앙 상단 부근)
        self.x, self.y = 800, 700  # 1600x900 맵 기준 중앙 상단

        # 3. 초기 이동 방향 설정
        self.dir = random.choice([-1, 1])

        # 4. 보스가 이동할 경계 (예시: 맵 중앙 영역)
        self.left_boundary = 400
        self.right_boundary = 1200

        # 5. 화면 좌표 (스크롤링 맵에서 필요하다면 추가)
        self.screen_x, self.screen_y = 0, 0

    def get_bb(self):
        # 충돌 박스 (Bounding Box) 반환
        return (self.x - Boss.BOSS_WIDTH // 2,
                self.y - Boss.BOSS_HEIGHT // 2,
                self.x + Boss.BOSS_WIDTH // 2,
                self.y + Boss.BOSS_HEIGHT // 2)

    def update(self):
        # 1. 보스 이동
        self.x += BOSS_RUN_SPEED_PPS * self.dir * game_framework.frame_time

        # 2. 맵 경계 체크 및 방향 전환
        # 오른쪽 경계 초과 체크
        if self.x > self.right_boundary:
            self.dir = -1  # 왼쪽으로 전환
        # 왼쪽 경계 초과 체크
        elif self.x < self.left_boundary:
            self.dir = 1  # 오른쪽으로 전환

        # 3. x좌표를 경계 사이로 제한
        self.x = clamp(self.left_boundary, self.x, self.right_boundary)

    def draw(self):
        # 맵이 스크롤되는 경우, Ratking을 기준으로 화면 좌표를 계산해야 합니다.
        # (이 코드는 Ratking 클래스가 있는 PlayMode2의 draw 로직을 따라야 합니다.)

        # **현재는 맵 좌표(World Coordinate)를 그대로 화면 좌표로 가정하고 그립니다.**
        # 만약 PlayMode2의 Ratking 스크롤링 로직을 사용한다면, 아래 코드를 수정해야 합니다.

        if self.dir < 0:
            # 왼쪽 방향: 수평 반전(h)하여 그리기
            Boss.image.composite_draw(0, 'h', self.x, self.y, Boss.BOSS_WIDTH, Boss.BOSS_HEIGHT)
        else:
            # 오른쪽 방향: 그대로 그리기
            Boss.image.draw(self.x, self.y, Boss.BOSS_WIDTH, Boss.BOSS_HEIGHT)

        # 충돌 박스 그리기 (디버깅용)
        # draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        # 충돌 처리 로직 (필요 시 추가)
        pass