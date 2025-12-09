from pico2d import *

# 게임 프레임워크: 모드(상태) 전환과 메인 루프만 담당

running = None          # 게임 루프 실행 여부
stack = []              # 모드 스택 (필요시 여러 모드 쌓을 수 있음)


def change_mode(mode):
    """현재 모드를 종료하고 새 모드로 전환"""
    global stack
    if stack:
        stack[-1].exit()
        stack.pop()

    stack.append(mode)
    mode.init()
    mode.enter()


def push_mode(mode):
    """현재 모드를 스택에 보존하고 새 모드로 진입"""
    global stack
    if stack:
        stack[-1].exit()

    stack.append(mode)
    mode.init()
    mode.enter()


def pop_mode():
    """현재 모드를 종료하고 이전 모드로 돌아감"""
    global stack, running
    if not stack:
        running = False
        return

    stack[-1].exit()
    stack.pop()

    if stack:
        stack[-1].enter()
    else:
        running = False


def quit():
    """게임 전체 종료"""
    global running
    running = False


# 프레임 시간 측정용
frame_time = 0.0


def run(start_mode):
    """메인 루프를 돌리면서 현재 모드의 핸들러를 호출"""
    global running, stack, frame_time

    running = True
    stack = [start_mode]

    start_mode.init()
    start_mode.enter()

    current_time = get_time()

    while running:
        # 프레임 시간 계산
        new_time = get_time()
        frame_time = new_time - current_time
        current_time = new_time

        # 현재 모드 하나만 사용 (스택 최상단)
        mode = stack[-1]

        mode.handle_events()
        mode.update()
        mode.draw()

    # 루프 종료 시 현재 모드 정리
    while stack:
        stack[-1].exit()
        stack.pop()
