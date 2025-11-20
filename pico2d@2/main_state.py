from pico2d import *
import game_framework
import title_mode  # 이전 화면으로 돌아가기 위해 import
import os

name = "MainState"

# 게임 내에서 사용될 전역 이미지 객체
_image = None
_font30 = None
_font20 = None


# --- 필수 함수: 초기화 (가장 먼저 한 번 실행) ---
def init():
    global _image, _font30, _font20
    print(f"{name} init")
    # 예시: 임시 이미지를 로드합니다. (실제 프로젝트에 맞게 파일 경로 수정 필요)
    try:
        _image = load_image(os.path.join('assets', 'background.png'))
    except Exception:
        try:
            _image = load_image('assets/desktop.ini')
        except Exception:
            print("경고: main_state에서 사용할 'assets/background.png' 이미지를 찾을 수 없습니다. 배경 없이 실행됩니다.")
            _image = None

    # 폰트 로드 (캐시)
    try:
        _font30 = load_font(os.path.join('assets', 'ENCR10B.TTF'), 30)
    except Exception:
        try:
            _font30 = load_font('ENCR10B.TTF', 30)
        except Exception:
            _font30 = None

    try:
        _font20 = load_font(os.path.join('assets', 'ENCR10B.TTF'), 20)
    except Exception:
        try:
            _font20 = load_font('ENCR10B.TTF', 20)
        except Exception:
            _font20 = None


# --- 필수 함수: 모드 진입 (init 후 또는 다른 모드에서 넘어올 때) ---
def enter():
    print(f"{name} enter")
    pass


# --- 필수 함수: 모드 종료 (다른 모드로 나갈 때) ---
def exit():
    global _image, _font30, _font20
    print(f"{name} exit")
    # 사용된 리소스 해제
    if _image:
        del _image
        _image = None
    if _font30:
        del _font30
        _font30 = None
    if _font20:
        del _font20
        _font20 = None


def finish():
    # game_framework가 기대하는 이름
    exit()


# --- 필수 함수: 이벤트 처리 ---
def handle_event():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            # ESC 키를 누르면 이전 모드(타이틀 화면)로 돌아가기
            if event.key == SDLK_ESCAPE:
                game_framework.change_mode(title_mode)  # 또는 game_framework.pop_mode()


def handle_events():
    # wrapper for framework
    return handle_event()


# --- 필수 함수: 게임 로직 업데이트 (프레임마다 실행) ---
def update():
    # 게임 캐릭터 움직임, 충돌 처리 등 로직이 여기에 들어갑니다.
    pass


# --- 필수 함수: 화면 그리기 (프레임마다 실행) ---
def draw():
    clear_canvas()

    # 캔버스 중앙 위치
    center_x, center_y = get_canvas_width() // 2, get_canvas_height() // 2

    if _image:
        _image.draw(center_x, center_y)  # 배경 이미지 그리기

    # 임시 텍스트
    draw_rectangle(center_x - 300, center_y - 150, center_x + 300, center_y + 150)
    if _font30:
        _font30.draw(center_x - 100, center_y, 'Main Game Screen', (0, 0, 0))
    if _font20:
        _font20.draw(center_x - 120, center_y - 50, 'Press ESC to return to Title', (0, 0, 0))

    update_canvas()


def pause():
    pass


def resume():
    pass