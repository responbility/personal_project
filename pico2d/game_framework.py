# game_framework.py

from pico2d import delay, open_canvas, close_canvas, hide_cursor, clear_canvas, update_canvas # time 모듈과 함께 사용
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
    start_mode.enter()

    last_time = time.time()  # 게임 시작 시간 기록

    while running:
        # 🚨 프레임 시간 계산 🚨
        current_time = time.time()
        frame_time = current_time - last_time
        last_time = current_time
        # -----------------------------

        # 디버그: 현재 최상위 모드 이름 출력 (빠르게 확인하려면 콘솔을 살펴보세요)
        try:
            top_name = stack[-1].name if (stack and hasattr(stack[-1], 'name')) else str(type(stack[-1]))
        except Exception:
            top_name = 'UNKNOWN'
        print(f"DEBUG: game_framework loop - top_mode={top_name} frame_time={frame_time:.4f}")

        # 현재 모드의 handle_events, update, draw 함수 호출
        try:
            # **주의: 대부분의 pico2d 프로젝트에서는 모드 내부의 draw()에서 clear_canvas()와 update_canvas()를 처리합니다.**
            # 여기서는 모드의 draw() 함수만 호출합니다.
            # 모드의 draw() 함수 내부에 clear_canvas()와 update_canvas()가 있는지 확인하세요.
            stack[-1].handle_events()
            stack[-1].update()
            stack[-1].draw()
        except Exception as e:
            # 예외가 발생해도 바로 종료되지 않도록 로그를 남기고 계속 진행
            print(f"ERROR: Exception in mode loop: {e}")

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
    # 새 모드 시작 및 추가
    stack.append(mode)
    mode.init()


def push_mode(mode):
    global stack
    # 새 모드 시작 및 추가
    stack.append(mode)
    mode.init()


def pop_mode():
    global stack
    if (len(stack) > 0):
        # 현재 모드 종료 및 제거
        stack[-1].finish()
        stack.pop()
    # 스택이 비어 있으면 게임 종료
    if (len(stack) == 0):
        quit()