# game_framework.py

from pico2d import delay, open_canvas, close_canvas, hide_cursor  # time 모듈과 함께 사용
import time

running = None
stack = None

# 🚨 프레임 시간 관련 전역 변수 🚨
frame_time = 0.0
last_time = 0.0


def run(start_mode):
    global running, stack
    global frame_time, last_time

    # 캔버스 열기는 main.py에 있을 수도 있지만, 안전을 위해 여기에 남겨둡니다.
    # open_canvas(800, 600)
    # hide_cursor()

    running = True
    stack = [start_mode]
    start_mode.init()

    last_time = time.time()  # 게임 시작 시간 기록

    while running:
        # 🚨 프레임 시간 계산 🚨
        current_time = time.time()
        frame_time = current_time - last_time
        last_time = current_time
        # -----------------------------

        # 현재 모드의 handle_events, update, draw 함수 호출
        stack[-1].handle_events()
        stack[-1].update()
        stack[-1].draw()

        # 프레임 속도 조절 (예: 60 FPS)
        if frame_time < 1 / 60.0:
            delay(1 / 60.0 - frame_time)

    # 게임 종료 시 스택 정리
    while (len(stack) > 0):
        stack[-1].finish()
        stack.pop()

    # close_canvas()


def quit():
    global running
    running = False


def change_mode(mode):
    global stack
    # 현재 모드 종료 및 제거
    if (len(stack) > 0):
        stack[-1].finish()
        stack.pop()

    # 새 모드 추가 및 초기화
    stack.append(mode)
    mode.init()


def push_mode(mode):
    global stack
    # 현재 모드 일시 정지
    if (len(stack) > 0):
        stack[-1].pause()

    # 새 모드 추가 및 초기화
    stack.append(mode)
    mode.init()


def pop_mode():
    global stack
    # 현재 모드 종료 및 제거
    if (len(stack) > 0):
        stack[-1].finish()
        stack.pop()

    # 이전 모드 재개
    if (len(stack) > 0):
        stack[-1].resume()