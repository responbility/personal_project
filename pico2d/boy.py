from pico2d import load_image, get_time, load_font, draw_rectangle, clamp, get_canvas_width, get_canvas_height, SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT, SDL_QUIT, SDLK_w, SDLK_s, SDLK_UP, SDLK_DOWN, SDLK_f

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

# RATKING 스프라이트: 타일 크기 30x30 (프로젝트의 다른 코드와 맞춤)
# 화면에서의 스케일은 4배로 설정
CLIP_W, CLIP_H = 30, 30
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
        elif left_down(e):
            self.boy.dir = self.boy.face_dir = -1

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

        # 이동 추적용: 이전 위치와 누적 이동 픽셀 수
        self._prev_x = self.x
        self._prev_y = self.y
        self.cumulative_moved = 0

        # 이미지(스프라이트 시트) 로드: 'assets/ratking.png' 사용. 프레임 크기 30x30
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
                elif event.key in (SDLK_s, SDLK_DOWN):
                    self.vy = -self.VSPEED_PPS
                elif event.key == SDLK_f:
                    # F 키로 투사체 발사
                    self.fire_projectile()
            elif event.type == SDL_KEYUP:
                if event.key in (SDLK_w, SDLK_UP, SDLK_s, SDLK_DOWN):
                    self.vy = 0.0
        except Exception:
            pass

    def handle_collision(self, group, other):
        # Called by game_world when enemy collides with Boy
        try:
            if group in ('boy:enemy', 'boy:bat', 'boy:guard'):
                print('DEBUG: Boy collided with enemy')
                # keep boy alive; optionally handle damage here
                pass
        except Exception:
            pass

    def draw(self):
        try:
            if self.image is not None:
                # 모든 이동(수평 또는 수직)에서는 같은 RUN_ROW 애니메이션을 사용하도록 통일
                moving = (abs(self.dir) > 0) or (abs(self.vy) > 0.0)
                if moving:
                    # 프레임 진보(런 애니메이션 속도 사용)
                    try:
                        dt = game_framework.frame_time
                    except Exception:
                        dt = 1.0 / 60.0
                    try:
                        cols = self.image.cols
                    except Exception:
                        cols = FRAMES_PER_ACTION
                    # 스프라이트 시트의 cols를 사용하여 프레임을 순환
                    self.frame = (self.frame + cols * ACTION_PER_TIME * dt * RUN_ANIM_SPEED_MULTIPLIER) % cols
                    # 항상 RUN_ROW 사용해서 앞/뒤/아래 이동시 동일 스프라이트 사용
                    idx = RUN_ROW * cols + int(self.frame % cols)
                    # draw_frame expects index relative to entire sheet
                    self.image.draw_frame(idx, self.x, self.y, TARGET_W, TARGET_H, flip=(self.face_dir == -1), rotate=0)
                else:
                    # 이동이 없을 때는 상태 머신의 draw()를 사용 (Idle/Sleep 처리)
                    self.state_machine.draw()
            else:
                 # fallback: draw simple rectangle and text
                 x1, y1, x2, y2 = self.get_bb()
                 draw_rectangle(x1, y1, x2, y2)
                 try:
                     f = load_font('assets/ENCR10B.TTF', 12)
                 except Exception:
                     f = None
                 if f:
                     f.draw(self.x - 10, self.y + TARGET_H // 2, f'{self.ball_count:02d}', (255, 255, 0))
        except Exception as e:
            print(f"ERROR: Boy.draw failed: {e}")
            try:
                draw_rectangle(*self.get_bb())
            except Exception:
                pass

        if self.font:
            self.font.draw(self.x - 10, self.y + TARGET_H // 2, f'{self.ball_count:02d}', (255, 255, 0))

    def fire_projectile(self):
        # create a projectile moving in facing direction and add to game world
        try:
            from projectile import Projectile
            speed = 400.0
            vx = speed * (1 if self.face_dir >= 0 else -1)
            proj = Projectile(self.x + (TARGET_W//2 + 6) * (1 if self.face_dir >= 0 else -1), self.y, vx, 0, damage=1, owner=self)
            game_world.add_object(proj, 1)
            # debug print
            print("DEBUG: Boy fired projectile")
        except Exception as e:
            print(f"ERROR: fire_projectile failed: {e}")
