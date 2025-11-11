# game_framework.py

running = None
stack = None


def run(start_mode):
    global running, stack
    running = True
    stack = [start_mode]
    start_mode.init()

    while running:
        # 현재 모드의 handle_events, update, draw 함수 호출
        stack[-1].handle_events()
        stack[-1].update()
        stack[-1].draw()

    # 게임 종료 시 스택 정리
    while (len(stack) > 0):
        stack[-1].finish()
        stack.pop()


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