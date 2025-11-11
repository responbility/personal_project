# title_mode.py

import game_framework
from pico2d import *
# play_mode가 같은 폴더에 있다고 가정하고 import 합니다.
import play_mode

# 이 모드의 이름을 정의합니다.
name = "TitleMode"

# 사용할 전역 변수
title_image = None  # banners.png
decoration_image = None  # 12.png
font = None  # 폰트 객체


# --- 모드 함수 정의 ---

def init():
    """타이틀 모드가 시작될 때 호출됩니다. 이미지와 폰트를 로드합니다."""
    global title_image, decoration_image, font

    # 1. banners.png 로드 (타이틀 이미지)
    try:
        title_image = load_image('assets/banners.png')
    except:
        print("경로 오류: assets/banners.png 파일을 로드할 수 없습니다.")
        title_image = None

    # 2. 12.png 로드 (장식 이미지)
    try:
        decoration_image = load_image('assets/12.png')
    except:
        print("경로 오류: assets/12.png 파일을 로드할 수 없습니다.")
        decoration_image = None

    # 3. 폰트 로드 (ENCR10B.TTF 파일이 없을 경우 대비하여 로드 로직을 수정합니다.)
    try:
        font = load_font('assets/ENCR10B.TTF', 30)
    except:
        # assets 폴더에서 로드 실패 시, 기본 경로 시도 (KOF.TTF 또는 ENCR10B.TTF)
        try:
            font = load_font('ENCR10B.TTF', 30)
        except:
            print("경고: ENCR10B.TTF 폰트를 로드할 수 없습니다. 기본 텍스트를 사용합니다.")
            font = None  # 폰트가 없을 경우 None으로 설정


def finish():
    """타이틀 모드가 종료될 때 호출됩니다. 리소스를 해제합니다."""
    global title_image, decoration_image
    # 이미지 객체가 존재할 경우에만 del을 수행합니다.
    if title_image:
        del title_image
    if decoration_image:
        del decoration_image


def handle_events():
    """사용자 입력(키보드, 마우스)을 처리합니다. (이전 오류 해결을 위해 추가)"""
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_SPACE:
                # Space 키를 누르면 다음 모드(play_mode)로 전환
                game_framework.change_mode(play_mode)


def update():
    """게임 상태를 업데이트합니다. (타이틀 모드에서는 비워둡니다)"""
    pass


# title_mode.py의 draw() 함수 수정

# title_mode.py의 draw() 함수

# title_mode.py의 draw() 함수 수정

def draw():
    """화면에 요소를 그립니다."""
    global title_image, decoration_image, font
    clear_canvas()

    center_x = get_canvas_width() // 2
    center_y = get_canvas_height() // 2

    canvas_width = get_canvas_width()
    canvas_height = get_canvas_height()

    # 1. 배경 이미지 (decoration_image, 12.png)를 화면 전체에 꽉 채워 그리기
    if decoration_image is not None:
        decoration_image.draw(center_x, center_y, canvas_width, canvas_height)

    # ----------------------------------------------------
    # 2. 메인 타이틀 이미지 (banners.png) 그리기 (크기 확대)
    # ----------------------------------------------------
    if title_image is not None:
        title_width = canvas_width * 0.8  # 너비는 화면의 80% 유지

        # [수정] 높이 비율을 0.2(20%)에서 0.5(50%)로 크게 조정
        title_height = canvas_height * 0.5

        # 타이틀을 배경 위에 그립니다.
        # draw(x, y, w, h) 형태로 사용
        title_image.draw(center_x, center_y + 150, title_width, title_height)

    # 3. 시작 메시지 그리기
    if font is not None:
        font.draw(center_x - 200, 100,
                  'Press SPACE to Start', (255, 255, 255))
    else:
        pass

    update_canvas()


def pause():
    """다른 모드가 위에 쌓일 때 호출됩니다. (이전 오류 해결을 위해 추가)"""
    pass


def resume():
    """위에 쌓였던 모드가 제거되고 이 모드가 재개될 때 호출됩니다. (이전 오류 해결을 위해 추가)"""
    pass