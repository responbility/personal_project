from pico2d import load_image, get_time, load_font, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT

import game_world
import game_framework

# Ball 클래스를 임포트하는 대신, 필요한 경우 boy.py 파일 내에서 정의하거나
# play_mode에서 import 했으므로 문제없으나, 명확히 Ball을 사용함을 알립니다.
from ball import Ball
from state_machine import StateMachine


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


# 새로운 이벤트 추가: 이동 키가 눌려있는 상태에서 방향 전환을 위한 이벤트
def direction_change(e):
    # RUN 상태에서 다른 방향 키가 눌리거나, 눌려있던 키가 떼질 때 RUN 상태를 유지해야 합니다.
    # 하지만 상태 머신 로직 단순화를 위해 RUN 상태로 전이되는 모든 입력은 RUN을 유지하도록 정의합니다.
    return right_down(e) or right_up(e) or left_down(e) or left_up(e)


# --- Boy Run Speed 계산 ---
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 20.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# Boy Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8


# --- 상태 클래스 정의 ---

class Idle:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        self.boy.wait_time = get_time()
        self.boy.dir = 0  # 정지 상태이므로 dir을 0으로 설정

    def exit(self, e):
        if space_down(e):
            self.boy.fire_ball()

    def do(self):
        self.boy.frame = (self.boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8
        if get_time() - self.boy.wait_time > 3:
            self.boy.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        if self.boy.face_dir == 1:  # right
            self.boy.image.clip_draw(int(self.boy.frame) * 100, 300, 100, 100, self.boy.x, self.boy.y)
        else:  # face_dir == -1: # left
            self.boy.image.clip_draw(int(self.boy.frame) * 100, 200, 100, 100, self.boy.x, self.boy.y)


class Sleep:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        self.boy.frame = (self.boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8

    def handle_event(self, event):
        # Sleep 상태에서는 이벤트 처리 로직이 필요 없음. (StateMachine이 처리함)
        pass

    def draw(self):
        if self.boy.face_dir == 1:
            self.boy.image.clip_composite_draw(int(self.boy.frame) * 100, 300, 100, 100, 3.141592 / 2, '',
                                               self.boy.x - 25, self.boy.y - 25, 100, 100)
        else:
            self.boy.image.clip_composite_draw(int(self.boy.frame) * 100, 200, 100, 100, -3.141592 / 2, '',
                                               self.boy.x + 25, self.boy.y - 25, 100, 100)


class Run:
    def __init__(self, boy):
        self.boy = boy

    def enter(self, e):
        # 🌟 Run 진입 로직 수정: 방향을 올바르게 설정합니다. 🌟
        if right_down(e) or self.boy.face_dir == 1 and not left_down(e):
            self.boy.dir = self.boy.face_dir = 1
        elif left_down(e) or self.boy.face_dir == -1 and not right_down(e):
            self.boy.dir = self.boy.face_dir = -1
        # Run 상태에 진입할 때 Dir을 설정하는 것이 중요합니다.

    def exit(self, e):
        if space_down(e):
            self.boy.fire_ball()

    def do(self):
        self.boy.frame = (self.boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8
        self.boy.x += self.boy.dir * RUN_SPEED_PPS * game_framework.frame_time
        # 맵 경계를 벗어나지 않도록 클램프
        self.boy.x = clamp(50, self.boy.x, get_canvas_width() - 50)

    def draw(self):
        if self.boy.face_dir == 1:  # right
            self.boy.image.clip_draw(int(self.boy.frame) * 100, 100, 100, 100, self.boy.x, self.boy.y)
        else:  # face_dir == -1: # left
            self.boy.image.clip_draw(int(self.boy.frame) * 100, 0, 100, 100, self.boy.x, self.boy.y)


# --- 메인 클래스 정의 ---

class Boy:
    def __init__(self):

        self.ball_count = 10

        # 폰트 로드: 이미지를 그리기 전에 로드해야 함
        try:
            self.font = load_font('assets/ENCR10B.TTF', 16)  # assets 경로 추가 권장
        except:
            self.font = load_font('ENCR10B.TTF', 16)  # 경로 오류 시를 대비

        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        # 이미지 로드: 이전에 발생한 오류 해결을 위해 경로를 'assets/'로 수정했습니다.
        try:
            self.image = load_image('assets/animation_sheet.png')
        except:
            print("경고: assets/animation_sheet.png를 로드하지 못했습니다. 경로를 확인하세요.")
            self.image = load_image('animation_sheet.png')  # 예외 처리

        self.IDLE = Idle(self)
        self.SLEEP = Sleep(self)
        self.RUN = Run(self)

        # 🌟🌟🌟 상태 전이 로직 수정: 오류 수정 및 Run 상태 유지 로직 추가 🌟🌟🌟
        self.state_machine = StateMachine(
            self.IDLE,
            {
                # SLEEP: 스페이스바를 누르면 IDLE로 깨어남 (Sleep -> Idle)
                self.SLEEP: {space_down: self.IDLE},

                # IDLE:
                self.IDLE: {
                    space_down: self.IDLE,  # 스페이스바는 IDLE을 유지
                    time_out: self.SLEEP,  # 시간 초과 시 SLEEP
                    right_down: self.RUN,  # 오른쪽 누르면 RUN
                    left_down: self.RUN  # 왼쪽 누르면 RUN
                    # right_up, left_up은 IDLE에서 무시됨
                },

                # RUN:
                self.RUN: {
                    space_down: self.RUN,  # 스페이스바는 RUN을 유지 (공 발사만 Exit에서 처리)
                    right_up: self.IDLE,  # 오른쪽 키 떼면 IDLE
                    left_up: self.IDLE,  # 왼쪽 키 떼면 IDLE
                    # 방향 전환 및 계속 뛰는 이벤트는 RUN 상태 유지
                    right_down: self.RUN,  # 뛰는 중에 방향 키 입력 -> RUN 유지 (방향만 Run.enter에서 변경)
                    left_down: self.RUN  # 뛰는 중에 방향 키 입력 -> RUN 유지
                }
            }
        )

        # 초기 상태를 설정합니다.
        self.state_machine.start()

        # 🌟🌟🌟 BB 함수 중복 및 오류 수정: Boy의 영역을 정확히 반환합니다. 🌟🌟🌟

    def get_bb(self):
        # Boy의 중심 x, y에서 50px씩 떨어진 영역 (캐릭터 크기 100x100 가정)
        return self.x - 50, self.y - 50, self.x + 50, self.y + 50

    def update(self):
        self.state_machine.update()

    # def

    # def get_bb (self): # 중복된 함수는 삭제해야 합니다.
    # return self.x - 50, self.y - 50, self.x + 50, self.y + 50
    # ball

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()

        # 폰트가 로드되었는지 확인 후 그리기
        if self.font:
            self.font.draw(self.x - 10, self.y + 50, f'{self.ball_count:02d}', (255, 255, 0))

        # BB 그리기 (디버깅용)
        draw_rectangle(*self.get_bb())

    def fire_ball(self):
        if self.ball_count > 0:
            self.ball_count -= 1
            # 공 객체 생성 및 월드에 추가
            ball_instance = Ball(self.x + self.face_dir * 40, self.y + 100, self.face_dir * 15)
            game_world.add_object(ball_instance, 1)

            # 충돌 쌍 등록 (공이 월드에 추가될 때 등록)
            game_world.add_collision_pair('boy:ball', self, ball_instance)
            game_world.add_collision_pair('grass:ball', None, ball_instance)

    def handle_collision(self, group, other):
        # 충돌 처리 로직
        if group == 'boy:ball':
            # 공을 맞으면 카운트를 다시 얻는 로직 (공이 사라진 후 호출될 것으로 가정)
            # 이 로직은 공이 파괴될 때 공 쪽에서 호출하는 것이 일반적입니다.
            # 지금은 Boy가 공을 획득하는 로직으로 해석하겠습니다.
            self.ball_count += 1
            game_world.remove_object(other)  # 공을 제거합니다.

        elif group == 'boy:floor':
            # 바닥과의 충돌 처리 (중력 구현 시 사용)
            # 예: 충돌 시 Y좌표를 바닥 높이로 고정
            _, other_bottom, _, other_top = other.get_bb()
            self.y = other_top + 50  # 바닥 위로 올라오도록 설정 (Boy의 절반 높이 50)

        elif group == 'zombie:boy':
            # 좀비와 충돌 시
            game_world.remove_object(self)
            pass