# title_mode.py

import game_framework
# [최종 수정] 모든 pico2d 함수를 포함하는 *로 변경하여 NameError 및 ImportError를 해결합니다.
from pico2d import *
import play_mode

name = "TitleMode"

# 사용할 전역 변수
title_image = None
decoration_image = None  # 12.png (배경)
font = None

# 배경 스크롤 변수
bg_scroll_y = 0
SCROLL_SPEED = 150
last_time = 0.0  # delta_time 계산용


# --- 모드 함수 정의 ---

def init():
    """타이틀 모드가 시작될 때 호출됩니다."""
    global title_image, decoration_image, font, bg_scroll_y, last_time

    # 1. banners.png 로드
    try:
        title_image = load_image('assets/banners.png')
    except:
        title_image = None

    # 2. 12.png 로드
    try:
        decoration_image = load_image('assets/12.png')
    except:
        decoration_image = None

    # 3. 폰트 로드 (폰트 파일이 없을 경우 프로그램이 종료되는 것을 방지)
    try:
        font = load_font('assets/ENCR10B.TTF', 40)
    except:
        try:
            font = load_font('KOF.TTF', 40)
            print("경고: ENCR10B.TTF 로드 실패. KOF.TTF 폰트로 대체합니다.")
        except:
            print("경고: 폰트를 로드할 수 없어 시작 메시지를 그릴 수 없습니다.")
            font = None

    # 배경 Y 좌표 및 시간 초기화
    bg_scroll_y = get_canvas_height() // 2
    last_time = get_time()


def finish():
    """타이틀 모드가 종료될 때 호출됩니다."""
    global title_image, decoration_image
    if title_image:
        del title_image
    if decoration_image:
        del decoration_image


def handle_events():
    """사용자 입력을 처리합니다."""
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_SPACE:
                game_framework.change_mode(play_mode)


def update():
    """게임 상태를 업데이트합니다. (배경 스크롤 로직)"""
    global bg_scroll_y, last_time

    # delta_time 직접 계산
    current_time = get_time()
    delta_time = current_time - last_time
    last_time = current_time

    canvas_height = get_canvas_height()

    # delta_time 과도 제한
    if delta_time > 0.1:
        delta_time = 0.1

    # 1. Y 좌표 감소 (아래로 이동)
    bg_scroll_y -= SCROLL_SPEED * delta_time

    # 2. 루프 조건 확인 (무한 스크롤)
    if bg_scroll_y < -canvas_height / 2:
        bg_scroll_y += canvas_height


def draw():
    """화면에 요소를 그립니다."""
    global title_image, decoration_image, font, bg_scroll_y
    clear_canvas()

    center_x = get_canvas_width() // 2
    canvas_width = get_canvas_width()
    canvas_height = get_canvas_height()

    # 1. 배경 이미지 (12.png)를 스크롤하며 그리기
    if decoration_image is not None:
        # Image 1: 현재 스크롤 위치
        decoration_image.draw(center_x, bg_scroll_y, canvas_width, canvas_height)

        # Image 2: Image 1 위쪽에 배치하여 끊김 없이 이어지게 함
        decoration_image.draw(center_x, bg_scroll_y + canvas_height, canvas_width, canvas_height)

    # 2. 메인 타이틀 이미지 (banners.png) 그리기
    if title_image is not None:
        title_width = canvas_width * 0.8
        title_height = canvas_height * 0.5
        # y 좌표는 캔버스 상단에서 100 픽셀 아래에 배치
        title_image.draw(center_x, canvas_height - title_height / 2 - 100, title_width, title_height)

    # 3. 시작 메시지 그리기 (폰트가 로드된 경우에만)
    text_y = 150

    if font is not None:
        font.draw(center_x - 250, text_y,
                  'Press SPACE to Start', (0, 0, 0, 255))
    # [제거] 폰트 로드 실패 시 대체 텍스트를 그리는 코드를 제거했습니다.

    update_canvas()


def pause(): pass


def resume(): pass