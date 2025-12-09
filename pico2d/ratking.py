from pico2d import *
import game_framework
import game_world  # Ball을 game_world에 추가하기 위해 필요합니다.
from ball import Ball  # Ball 클래스를 사용하기 위해 import 합니다.


class Ratking:
    FRAME_W = 16
    FRAME_H = 16
    COLS = 12
    ROWS = 1

    IDLE_FRAMES = [0, 1, 2, 3]
    WALK_FRAMES = [4, 5, 6, 7, 8, 9, 10, 11]

    SCALE = 4.0

    def __init__(self, x=400, y=300):
        self.x, self.y = x, y  # 월드 좌표(맵 좌표)
        self.screen_x = x  # 화면 좌표 (PlayMode2에서 덮어씀)
        self.screen_y = y
        self.frame_index = 0
        self.action = 'idle'
        self.dir = 1  # 1: 오른쪽, -1: 왼쪽
        self.frame_time = 0

        self.image = load_image('assets/ratking.png')
        print('[Ratking] created at', self.x, self.y)

    def _current_frames(self):
        return Ratking.IDLE_FRAMES if self.action == 'idle' else Ratking.WALK_FRAMES

    def update(self):
        # 애니메이션
        self.frame_time += 1
        if self.frame_time >= 5:
            self.frame_time = 0
            frames = self._current_frames()
            self.frame_index = (self.frame_index + 1) % len(frames)

        # 이동(월드 좌표)
        if self.action == 'walk':
            self.x += self.dir * 3

    def draw(self):
        frames = self._current_frames()
        frame_no = frames[self.frame_index % len(frames)]

        col = frame_no % Ratking.COLS
        row = frame_no // Ratking.COLS

        sx = col * Ratking.FRAME_W
        sy = row * Ratking.FRAME_H

        draw_w = int(Ratking.FRAME_W * Ratking.SCALE)
        draw_h = int(Ratking.FRAME_H * Ratking.SCALE)

        # 화면 좌표로 그리기 (스크롤링에서 매우 중요!)
        if self.dir == 1:
            self.image.clip_draw(
                sx, sy,
                Ratking.FRAME_W, Ratking.FRAME_H,
                self.screen_x, self.screen_y,
                draw_w, draw_h
            )
        else:
            self.image.clip_composite_draw(
                sx, sy,
                Ratking.FRAME_W, Ratking.FRAME_H,
                0, 'h',
                self.screen_x, self.screen_y,
                draw_w, draw_h
            )

    def fire_ball(self):
        # Ratking의 현재 위치를 기준으로 불덩이를 생성합니다.
        ball_x = self.x + self.dir * 30  # Ratking의 오른쪽/왼쪽으로 약간 떨어진 곳
        ball_y = self.y  # Ratking과 같은 y 높이

        throw_speed = 30  # 발사 속도 (m/s)

        # Ratking의 dir(방향)에 따라 발사 각도를 결정합니다.
        # dir = 1 (오른쪽): 각도 0도 (수평 발사)
        # dir = -1 (왼쪽): 각도 180도 (수평 발사)
        throw_angle = 0 if self.dir == 1 else 180

        # Ball 객체를 생성합니다.
        fire_ball = Ball(ball_x, ball_y, throw_speed, throw_angle)

        # 생성된 불덩이를 게임 월드에 추가하여 업데이트, 드로우 되게 합니다.
        # Ratking이 던진 Ball은 'ratking:ball' 또는 'enemy_ball' 등의 충돌 그룹에 추가할 수 있습니다.
        # 여기서는 'ball' 그룹에 추가하고, 충돌 처리는 게임 메인 루프에서 정의해야 합니다.
        game_world.add_object(fire_ball, 1)  # layer 1 (임의의 값)
        game_world.add_collision_pair('ratking:ball', None, fire_ball)  # 충돌 그룹 설정 (예시)

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_LEFT:
                self.dir = -1
                self.action = 'walk'
            elif event.key == SDLK_RIGHT:
                self.dir = 1
                self.action = 'walk'
            # 🚀 스페이스바를 누르면 불덩이를 발사합니다.
            elif event.key == SDLK_SPACE:
                self.fire_ball()
        elif event.type == SDL_KEYUP:
            if event.key in (SDLK_LEFT, SDLK_RIGHT):
                self.action = 'idle'