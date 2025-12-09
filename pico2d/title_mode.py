# title_mode.py (임시 시작 모드)

from pico2d import *
import game_framework

name = "TITLE_MODE"

# 캔버스 크기는 main.py에서 이미 설정되어 있으므로, 여기서는 get_canvas_width/height 사용
font = None


def init():
    global font
    print(f"[{name}] - init")
    try:
        font = load_font('ENCR10B.TTF', 24)
    except Exception as e:
        print(f"폰트 로드 실패: {e}. 기본 폰트로 폴백.")
        font = None


def enter():
    print(f"[{name}] - enter")


def exit():
    print(f"[{name}] - exit")


def finish():
    print(f"[{name}] - finish")


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            # 스페이스바: 플레이 모드로 전환 (필요하면 play_mode import 후 change_mode 호출)
            if event.key == SDLK_SPACE:
                import play_mode
                game_framework.change_mode(play_mode)
            # ESC: 게임 종료
            elif event.key == SDLK_ESCAPE:
                game_framework.quit()


def update():
    pass


def draw():
    clear_canvas()

    w, h = get_canvas_width(), get_canvas_height()

    if font:
        font.draw(w // 2 - 120, h // 2 + 50, '게임 시작', (255, 255, 255))
        font.draw(w // 2 - 180, h // 2, '(SPACE 키를 누르세요)', (255, 255, 0))

    update_canvas()
