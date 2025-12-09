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
        if self.frame_time >= 10:
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
        throw_speed = 30  # 발사 속도 (m/s)

        if self.dir == 1:  # 오른쪽 방향
            # Ratking의 오른쪽으로 약간 떨어진 곳에서 시작
            ball_x = self.x + 30
            ball_y = self.y
            throw_angle = 0  # 0도 (수평 오른쪽)
        else:  # 왼쪽 방향 (self.dir == -1)
            # Ratking의 왼쪽으로 약간 떨어진 곳에서 시작
            ball_x = self.x - 30
            ball_y = self.y
            throw_angle = 180  # 180도 (수평 왼쪽)
        fire_ball = Ball(ball_x, ball_y, throw_speed, throw_angle)


        game_world.add_object(fire_ball, 1)  # layer 1 (임의의 값)
        game_world.add_collision_pair('ratking:ball', None, fire_ball)  # 충돌 그룹 설정 (예시)

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            # 왼쪽: ← 또는 A
            if event.key in (SDLK_LEFT, SDLK_a):
                self.dir = -1
                self.action = 'walk'
            # 오른쪽: → 또는 D
            elif event.key in (SDLK_RIGHT, SDLK_d):
                self.dir = 1
                self.action = 'walk'
            # 스페이스바: 불덩이 발사
            elif event.key == SDLK_SPACE:
                self.fire_ball()

        elif event.type == SDL_KEYUP:
            # 좌우 관련 키를 떼면 멈춤
            if event.key in (SDLK_LEFT, SDLK_RIGHT, SDLK_a, SDLK_d):
                self.action = 'idle'
