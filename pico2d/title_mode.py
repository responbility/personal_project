# title_mode.py

import game_framework
from pico2d import *
# 메인 게임 모드로 전환하기 위해 play_mode를 임포트해야 합니다.
# (play_mode.py 파일이 같은 폴더에 있다고 가정합니다.)
import play_mode

# 이 모드의 이름을 정의합니다.
name = "TitleMode"

# 사용할 전역 변수
image = None  # banners.png 이미지를 저장할 변수
font = None  # 폰트 객체를 저장할 변을수


# --- 모드 함수 정의 ---

def init():
    """타이틀 모드가 시작될 때 호출됩니다. 이미지와 폰트를 로드합니다."""
    global image, font

    # 'banners.png'를 타이틀 이미지로 사용 (경로를 assets 폴더로 지정)
    try:
        # 경로는 프로젝트 폴더 내의 assets 폴더를 기준으로 설정해야 합니다.
        image = load_image('assets/banners.png')
    except:
        print("경로 오류: assets/banners.png 파일을 로드할 수 없습니다.")
        image = None

    # 폰트 로드 (ENCR10B.TTF 폰트 파일이 assets 폴더에 있어야 합니다.)
    try:
        font = load_font('assets/ENCR10B.TTF', 30)
    except:
        font = load_font('ENCR10B.TTF', 30)  # assets에 없을 경우 기본 경로 시도


def finish():
    """타이틀 모드가 종료될 때 호출됩니다. 리소스를 해제합니다."""
    global image
    del image


def handle_events():
    """사용자 입력(키보드, 마우스)을 처리합니다."""
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            # 윈도우 종료 버튼
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                # ESC 키를 누르면 종료
                game_framework.quit()
            elif event.key == SDLK_SPACE:
                # Space 키를 누르면 다음 모드(play_mode)로 전환
                game_framework.change_mode(play_mode)


def update():
    """게임 상태를 업데이트합니다. (타이틀 모드에서는 비워둡니다)"""
    pass


def draw():
    """화면에 요소를 그립니다."""
    global image, font
    clear_canvas()

    # 1. 배경/타이틀 이미지 그리기
    if image is not None:
        # 캔버스 중앙에 이미지 배치
        image.draw(get_canvas_width() // 2, get_canvas_height() // 2)

    # 2. 시작 메시지 그리기
    # 텍스트 위치 계산 및 색상 설정
    if font is not None:
        font.draw(get_canvas_width() // 2 - 200, 100,
                  'Press SPACE to Start', (255, 255, 255))

    update_canvas()


def pause():
    """다른 모드가 위에 쌓일 때 호출됩니다."""
    pass


def resume():
    """위에 쌓였던 모드가 제거되고 이 모드가 재개될 때 호출됩니다."""
    pass