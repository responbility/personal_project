from pico2d import load_image, get_time, load_font, draw_rectangle, clamp, get_canvas_width
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDL_QUIT

import game_world
import game_framework
from ball import Ball  # Ball 클래스가 별도의 ball.py에 있다고 가정
from state_machine import StateMachine  # state_machine.py 파일이 있다고 가정
from spritesheet import SpriteSheet

# --- 상수 정의 ---

CLIP_W, CLIP_H = 30, 30
SCALE_FACTOR = 2.0
TARGET_W = int(CLIP_W * SCALE_FACTOR)
TARGET_H = int(CLIP_H * SCALE_FACTOR)
HALF_TARGET_H = TARGET_H // 2

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 20.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION

# 걷기 애니메이션 (ratking.png의 첫 번째 줄 7프레임: 0~6)
FRAMES_PER_ACTION = 7

# 상태별 애니메이션 속도 설정 (걷기 사이클을 이용)
IDLE_ANIM_SPEED_MULTIPLIER = 0.3  # 유휴 상태에서는 애니메이션 속도를 늦춤
SLEEP_ANIM_SPEED_MULTIPLIER = 0.5  # 수면 상태에서는 애니메이션 속도를 중간으로 설정
RUN_ANIM_SPEED_MULTIPLIER = 1.0  # 달리기 상태에서는 정상 속도


# --- 이벤트 정의 함수 ---

def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


time_out = lambda e: e[0] == 'TIMEOUT'


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


# --- 상태 클래스 정의 ---

class Idle:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        self.boy.wait_time = get_time()
        self.boy.dir = 0

    def exit(self, e):
        if space_down(e): self.boy.fire_ball()

    def do(self):
        # 걷기 사이클 프레임(0-6)을 느린 속도로 순환시켜 유휴(Idle) 상태 애니메이션을 구현
        self.boy.frame = (
                                     self.boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time * IDLE_ANIM_SPEED_MULTIPLIER) % FRAMES_PER_ACTION
        if get_time() - self.boy.wait_time > 3:
            self.boy.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        # SpriteSheet의 draw_frame 사용 (frame 인덱스는 0-based)
        self.boy.image.draw_frame(int(self.boy.frame), self.boy.x, self.boy.y, TARGET_W, TARGET_H, flip=(self.boy.face_dir == -1), rotate=0)


class Sleep:
    def __init__(self, boy): self.boy = boy

    def enter(self, e): pass

    def exit(self, e): pass

    def do(self):
        # 걷기 사이클 프레임(0-6)을 중간 속도로 순환시켜 수면(Sleep) 상태 애니메이션을 구현
        self.boy.frame = (
                                     self.boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time * SLEEP_ANIM_SPEED_MULTIPLIER) % FRAMES_PER_ACTION

    def handle_event(self, event): pass

    def draw(self):
        # 누워서 자는 상태는 회전 적용
        rotate_angle = 3.141592 / 2 if self.boy.face_dir == 1 else -3.141592 / 2
        self.boy.image.draw_frame(int(self.boy.frame), self.boy.x, self.boy.y - HALF_TARGET_H, TARGET_W, TARGET_H, flip=(self.boy.face_dir == -1), rotate=rotate_angle)


class Run:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        if right_down(e):
            self.boy.dir = self.boy.face_dir = 1
        elif left_down(e):
            self.boy.dir = self.boy.face_dir = -1

    def exit(self, e):
        if space_down(e): self.boy.fire_ball()

    def do(self):
        # 걷기 사이클 프레임(0-6)을 정상 속도로 순환시켜 달리기(Run) 상태 애니메이션을 구현
        self.boy.frame = (
                                     self.boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time * RUN_ANIM_SPEED_MULTIPLIER) % FRAMES_PER_ACTION
        self.boy.x += self.boy.dir * RUN_SPEED_PPS * game_framework.frame_time

        try:
            canvas_width = get_canvas_width()
        except:
            canvas_width = 800

        self.boy.x = clamp(HALF_TARGET_H, self.boy.x, canvas_width - HALF_TARGET_H)

    def draw(self):
        self.boy.image.draw_frame(int(self.boy.frame), self.boy.x, self.boy.y, TARGET_W, TARGET_H, flip=(self.boy.face_dir == -1), rotate=0)


# --- 메인 클래스 정의 ---

class Boy:
    def __init__(self):

        self.ball_count = 10

        # 폰트 로드 실패 시 None 할당
        try:
            self.font = load_font('assets/ENCR10B.TTF', 16)
        except:
            self.font = None

        self.x, self.y = 400, 90 + HALF_TARGET_H
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        # 이미지(스프라이트 시트) 로드: 'assets/ratking.png' 사용. 프레임 크기 30x30
        try:
            self.image = SpriteSheet('assets/ratking.png', CLIP_W, CLIP_H)
        except Exception:
            # 대체 경로 시도
            self.image = SpriteSheet('ratking.png', CLIP_W, CLIP_H)

        self.IDLE = Idle(self)
        self.SLEEP = Sleep(self)
        self.RUN = Run(self)

        # 상태 전이 로직
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.SLEEP: {space_down: self.IDLE},
                self.IDLE: {
                    space_down: self.IDLE,
                    time_out: self.SLEEP,
                    right_down: self.RUN,
                    left_down: self.RUN
                },
                self.RUN: {
                    space_down: self.RUN,
                    right_up: self.IDLE,
                    left_up: self.IDLE,
                    right_down: self.RUN,
                    left_down: self.RUN
                }
            }
        )

        self.state_machine.start()

    def get_bb(self):
        return self.x - TARGET_W // 2, self.y - TARGET_H // 2, self.x + TARGET_W // 2, self.y + TARGET_H // 2

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()

        if self.font:
            self.font.draw(self.x - 10, self.y + TARGET_H // 2, f'{self.ball_count:02d}', (255, 255, 0))

        draw_rectangle(*self.get_bb())

    def fire_ball(self):
        if self.ball_count > 0:
            self.ball_count -= 1
            ball_instance = Ball(self.x + self.face_dir * 40, self.y + 10, self.face_dir * 15)
            game_world.add_object(ball_instance, 1)

            game_world.add_collision_pair('boy:ball', self, ball_instance)
            game_world.add_collision_pair('grass:ball', None, ball_instance)

    def handle_collision(self, group, other):
        if group == 'boy:ball':
            self.ball_count += 1
            game_world.remove_object(other)
        elif group == 'boy:floor':
            _, other_bottom, _, other_top = other.get_bb()
            self.y = other_top + HALF_TARGET_H
        elif group == 'zombie:boy':
            game_world.remove_object(self)
            pass