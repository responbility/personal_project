from pico2d import load_image, get_time, load_font, draw_rectangle, clamp, get_canvas_width, get_canvas_height, SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDL_QUIT, SDLK_w, SDLK_s, SDLK_UP, SDLK_DOWN, SDLK_f, SDLK_a, SDLK_d

import game_world
import game_framework
# from ball import Ball  # Ball 클래스가 별도의 ball.py에 있다고 가정
# from state_machine import StateMachine  # state_machine.py 파일이 있다고 가정
# from spritesheet import SpriteSheet
from ball import Ball
from state_machine import StateMachine
from spritesheet import SpriteSheet
import os


# --- 상수 정의 ---

# RATKING 스프라이트: 실제 assets/ratking.png는 128x64이고 프레임은 16x16으로 구성되어 있음
CLIP_W, CLIP_H = 16, 16
SCALE_FACTOR = 4.0
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
FRAMES_PER_ACTION = 4

# 스프라이트 시트의 행(row) 매핑(0: 상단 행, 1: 다음 행 ...)
IDLE_ROW = 0
RUN_ROW = 1
SLEEP_ROW = 2

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
        if space_down(e): self.boy.fire_projectile()

    def do(self):
        # 스프라이트 시트의 실제 컬럼 수을 사용하여 프레임을 업데이트
        try:
            cols = self.boy.image.cols
        except Exception:
            cols = FRAMES_PER_ACTION
        # 걷기 사이클 프레임을 느린 속도로 순환시켜 유휴(Idle) 상태 애니메이션을 구현
        self.boy.frame = (
            self.boy.frame + cols * ACTION_PER_TIME * game_framework.frame_time * IDLE_ANIM_SPEED_MULTIPLIER) % cols
        if get_time() - self.boy.wait_time > 3:
            self.boy.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        # SpriteSheet에서 특정 행(row)을 사용하도록 전역 인덱스를 계산하여 그립니다.
        try:
            cols = self.boy.image.cols
        except Exception:
            cols = 7
        idx = IDLE_ROW * cols + int(self.boy.frame)
        self.boy.image.draw_frame(idx, self.boy.x, self.boy.y, TARGET_W, TARGET_H, flip=(self.boy.face_dir == -1), rotate=0)


class Sleep:
    def __init__(self, boy): self.boy = boy

    def enter(self, e): pass

    def exit(self, e): pass

    def do(self):
        try:
            cols = self.boy.image.cols
        except Exception:
            cols = FRAMES_PER_ACTION
        # 걷기 사이클 프레임을 중간 속도로 순환시켜 수면(Sleep) 상태 애니메이션을 구현
        self.boy.frame = (
            self.boy.frame + cols * ACTION_PER_TIME * game_framework.frame_time * SLEEP_ANIM_SPEED_MULTIPLIER) % cols

    def handle_event(self, event): pass

    def draw(self):
        # 누워서 자는 상태는 회전 적용; SLEEP_ROW 사용
        rotate_angle = 3.141592 / 2 if self.boy.face_dir == 1 else -3.141592 / 2
        try:
            cols = self.boy.image.cols
        except Exception:
            cols = 7
        idx = SLEEP_ROW * cols + int(self.boy.frame)
        self.boy.image.draw_frame(idx, self.boy.x, self.boy.y - HALF_TARGET_H, TARGET_W, TARGET_H, flip=(self.boy.face_dir == -1), rotate=rotate_angle)


class Run:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        if right_down(e):
            self.boy.dir = self.boy.face_dir = 1
            # update facing vector for horizontal
            self.boy.facing_x, self.boy.facing_y = 1, 0
        elif left_down(e):
            self.boy.dir = self.boy.face_dir = -1
            self.boy.facing_x, self.boy.facing_y = -1, 0

    def exit(self, e):
        if space_down(e): self.boy.fire_projectile()

    def do(self):
        try:
            cols = self.boy.image.cols
        except Exception:
            cols = FRAMES_PER_ACTION
        # 걷기 사이클 프레임을 정상 속도로 순환시켜 달리기(Run) 상태 애니메이션을 구현
        self.boy.frame = (
            self.boy.frame + cols * ACTION_PER_TIME * game_framework.frame_time * RUN_ANIM_SPEED_MULTIPLIER) % cols
        self.boy.x += self.boy.dir * RUN_SPEED_PPS * game_framework.frame_time

        try:
            canvas_width = get_canvas_width()
        except:
            canvas_width = 800

        self.boy.x = clamp(HALF_TARGET_H, self.boy.x, canvas_width - HALF_TARGET_H)

    def draw(self):
        # RUN_ROW 사용 (스프라이트 시트의 cols을 참조하여 인덱스를 계산)
        try:
            cols = self.boy.image.cols
        except Exception:
            cols = 7
        idx = RUN_ROW * cols + int(self.boy.frame % cols)
        self.boy.image.draw_frame(idx, self.boy.x, self.boy.y, TARGET_W, TARGET_H, flip=(self.boy.face_dir == -1), rotate=0)


# --- 메인 클래스 정의 ---

class Boy:
    def __init__(self):

        self.ball_count = 10

        # 폰트 로드 실패 시 None 할당 (모듈 assets 폴더에서 로드 시도)
        try:
            base_assets = os.path.join(os.path.dirname(__file__), 'assets')
            font_path = os.path.join(base_assets, 'ENCR10B.TTF')
            self.font = load_font(font_path, 16)
        except Exception:
            try:
                self.font = load_font('ENCR10B.TTF', 16)
            except Exception:
                self.font = None

        self.x, self.y = 400, 90 + HALF_TARGET_H
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        # 수직 속도 (픽셀/초) — WS 또는 화살표로 제어
        self.vy = 0.0
        self.VSPEED_PPS = RUN_SPEED_PPS  # 수평 속도와 비슷하게 설정

        # 입력 상태 추적 (WASD 및 화살표) - 발사시 방향 결정용
        self.input_up = False
        self.input_down = False
        self.input_left = False
        self.input_right = False

        # 최근 바라보는 방향 벡터 (기본: 오른쪽)
        self.facing_x = 1
        self.facing_y = 0

        # 이동 추적용: 이전 위치와 누적 이동 픽셀 수
        self._prev_x = self.x
        self._prev_y = self.y
        self.cumulative_moved = 0

        # 이미지(스프라이트 시트) 로드: 'assets/ratking.png' 사용. 프레임 크기 16x16
        try:
            self.image = SpriteSheet('assets/ratking.png', CLIP_W, CLIP_H)
            print("DEBUG: Boy sprite sheet loaded from assets/ratking.png")
            try:
                print(f"DEBUG: Boy sprite sheet cols={self.image.cols} rows={self.image.rows} clip={CLIP_W}x{CLIP_H}")
            except Exception:
                pass
        except Exception:
            # 대체 경로 시도
            try:
                self.image = SpriteSheet('ratking.png', CLIP_W, CLIP_H)
                print("DEBUG: Boy sprite sheet loaded from ratking.png fallback")
                try:
                    print(f"DEBUG: Boy sprite sheet cols={self.image.cols} rows={self.image.rows} clip={CLIP_W}x{CLIP_H}")
                except Exception:
                    pass
            except Exception:
                print("WARNING: Failed to load boy sprite sheet (ratking). Using fallback box drawing.")
                self.image = None

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
        # 이동량 추적: 한 픽 단위로 누적
        try:
            dx = self.x - self._prev_x
            dy = self.y - self._prev_y
            moved = int(round(abs(dx) + abs(dy)))
            if moved > 0:
                self.cumulative_moved += moved
                self._prev_x = self.x
                self._prev_y = self.y
        except Exception:
            pass

        # 수직 이동 적용 (vy)
        try:
            dt = getattr(game_framework, 'frame_time', 1.0/60.0)
            if abs(self.vy) > 0.0:
                self.y += self.vy * dt
                # 캔버스 경계 내로 클램프
                try:
                    ch = get_canvas_height()
                except Exception:
                    ch = 1024
                self.y = clamp(HALF_TARGET_H, self.y, ch - HALF_TARGET_H)
                # 이동량으로 누적 카운트도 증가시키기 (한 픽 단위)
                self.cumulative_moved += int(round(abs(self.vy) * dt))
        except Exception:
            pass

    def handle_event(self, event):
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        # 수평 이동은 기존 상태 머신에 위임
        self.state_machine.handle_state_event(('INPUT', event))

        # 수직 입력(WS 또는 화살표)
        try:
            if event.type == SDL_KEYDOWN:
                if event.key in (SDLK_w, SDLK_UP):
                    self.vy = self.VSPEED_PPS
                    self.input_up = True
                    # update facing vector when pressing up
                    self.facing_x, self.facing_y = 0, 1
                elif event.key in (SDLK_s, SDLK_DOWN):
                    self.vy = -self.VSPEED_PPS
                    self.input_down = True
                    self.facing_x, self.facing_y = 0, -1
                elif event.key == SDLK_f:
                    # F 키로 투사체 발사 — 현재 입력 방향에 따라 발사 방향 결정
                    self.fire_projectile_from_input()
                elif event.key == SDLK_a:
                    # A 키 또는 왼쪽 화살표로 왼쪽 이동
                    self.input_left = True
                    self.dir = self.face_dir = -1
                    self.facing_x, self.facing_y = -1, 0
                elif event.key == SDLK_d:
                    # D 키 또는 오른쪽 화살표로 오른쪽 이동
                    self.input_right = True
                    self.dir = self.face_dir = 1
                    self.facing_x, self.facing_y = 1, 0
            elif event.type == SDL_KEYUP:
                if event.key in (SDLK_w, SDLK_UP):
                    self.vy = 0.0
                    self.input_up = False
                    # if releasing up, keep last horizontal facing or default right
                    if not (self.input_left or self.input_right):
                        # keep vertical facing only if no horizontal input active
                        pass
                elif event.key in (SDLK_s, SDLK_DOWN):
                    self.vy = 0.0
                    self.input_down = False
                elif event.key == SDLK_f:
                    # keyup에선 아무 작업 안 함
                    pass
                elif event.key == SDLK_a:
                    # A 키 해제 시 왼쪽 이동 상태 종료
                    self.input_left = False
                    if not self.input_right:
                        # 오른쪽 이동이 아닐 경우에만 방향 초기화
                        self.dir = 0
                elif event.key == SDLK_d:
                    # D 키 해제 시 오른쪽 이동 상태 종료
                    self.input_right = False
                    if not self.input_left:
                        # 왼쪽 이동이 아닐 경우에만 방향 초기화
                        self.dir = 0
        except Exception:
            pass

    def fire_projectile(self):
        # create a projectile moving in facing direction and add to game world
        try:
            from projectile import Projectile
            # 기본 속도 및 방향: 최근 바라본 방향 벡터를 사용
            speed = 400.0
            fx = getattr(self, 'facing_x', 1)
            fy = getattr(self, 'facing_y', 0)
            import math
            mag = math.hypot(fx, fy)
            if mag == 0:
                fx, fy = (1, 0)
                mag = 1
            vx = speed * (fx / mag)
            vy = speed * (fy / mag)
            # 발사 위치는 바라보는 방향 기준으로 약간 앞쪽
            # 방향 부호를 명확히 하여 수직(0)일 때 기본값으로 오른쪽이 되는 문제를 제거
            sign_x = 1 if fx > 0 else (-1 if fx < 0 else 0)
            sign_y = 1 if fy > 0 else (-1 if fy < 0 else 0)
            if sign_x == 0 and sign_y != 0:
                proj_x = self.x
                proj_y = self.y + (TARGET_H // 2 + 2) * sign_y
            else:
                proj_x = self.x + (TARGET_W // 2 + 6) * (sign_x if sign_x != 0 else 1)
                proj_y = self.y + (TARGET_H // 2 + 2) * (1 if fy >= 0 else -1)
            proj = Projectile(proj_x, proj_y, vx, vy, damage=1, owner=self)
            game_world.add_object(proj, 1)
            # debug print
            print(f"DEBUG: Boy fired projectile at x={proj_x:.1f} y={proj_y:.1f} vx={vx:.1f} vy={vy:.1f}")
        except Exception as e:
            print(f"ERROR: fire_projectile failed: {e}")

    def fire_projectile_from_input(self):
        # determine direction based on WASD/arrow inputs (combination supported)
        try:
            from projectile import Projectile
            speed = 400.0
            dx = 0
            dy = 0
            if self.input_left:
                dx -= 1
            if self.input_right:
                dx += 1
            if self.input_up:
                dy += 1
            if self.input_down:
                dy -= 1

            # if no directional keys pressed, use recent facing vector
            if dx == 0 and dy == 0:
                dx = getattr(self, 'facing_x', 1)
                dy = getattr(self, 'facing_y', 0)

            # normalize to get consistent speed when diagonal
            import math
            mag = math.hypot(dx, dy)
            if mag == 0:
                dx, dy = 1, 0
                mag = 1
            vx = speed * (dx / mag)
            vy = speed * (dy / mag)

            # use facing direction to decide spawn offset sign when one axis is zero
            sign_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
            sign_y = 1 if dy > 0 else (-1 if dy < 0 else 0)
            # if horizontal is zero but vertical non-zero, spawn at player's x and offset y
            if sign_x == 0 and sign_y != 0:
                proj_x = self.x
                proj_y = self.y + (TARGET_H // 2 + 2) * sign_y
            else:
                # if both zero shouldn't happen; fallback to facing_x for horizontal sign
                if sign_x == 0:
                    sign_x = 1 if getattr(self, 'facing_x', 1) >= 0 else -1
                proj_x = self.x + (TARGET_W // 2 + 6) * sign_x
                proj_y = self.y + (TARGET_H // 2 + 2) * (sign_y if sign_y != 0 else (1 if getattr(self, 'facing_y', 0) >= 0 else -1))

            proj = Projectile(proj_x, proj_y, vx, vy, damage=1, owner=self)
            game_world.add_object(proj, 1)
            print(f"DEBUG: Boy fired projectile from input dx={dx}, dy={dy} vx={vx:.1f} vy={vy:.1f} proj_x={proj_x:.1f} proj_y={proj_y:.1f}")
        except Exception as e:
            print(f"ERROR: fire_projectile_from_input failed: {e}")
