# title_mode.py

import game_framework
from pico2d import *  # 모든 pico2d 함수를 포함
import play_mode

name = "TitleMode"

# 사용할 전역 변수
title_image = None  # banners.png
decoration_image = None  # 12.png (배경)
# [삭제] 폰트 변수를 삭제했습니다.
# font = None

# 배경 스크롤 변수
bg_scroll_y = 0
SCROLL_SPEED = 150
last_time = 0.0  # delta_time 계산용


# --- 모드 함수 정의 ---

def init():
    """타이틀 모드가 시작될 때 호출됩니다."""
    global title_image, decoration_image, bg_scroll_y, last_time
    # [삭제] global font 삭제

    # 1. banners.png 로드 (타이틀 이미지)
    try:
        title_image = load_image('assets/banners.png')
    except:
        print("경고: assets/banners.png 파일을 로드할 수 없습니다.")
        title_image = None

    # 2. 12.png 로드 (배경 이미지)
    try:
        decoration_image = load_image('assets/12.png')
    except:
        print("경고: assets/12.png 파일을 로드할 수 없습니다.")
        decoration_image = None

    # 3. [삭제] 폰트 로드 로직 전체 삭제

    # 배경 Y 좌표 및 시간 초기화
    bg_scroll_y = get_canvas_height() // 2
    last_time = get_time()


def finish():
    """타이틀 모드가 종료될 때 호출됩니다. 리소스를 해제합니다."""
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

    current_time = get_time()
    delta_time = current_time - last_time
    last_time = current_time

    canvas_height = get_canvas_height()

    if delta_time > 0.1:
        delta_time = 0.1

    bg_scroll_y -= SCROLL_SPEED * delta_time

    if bg_scroll_y < -canvas_height / 2:
        bg_scroll_y += canvas_height


# title_mode.py의 draw() 함수 수정

def draw():
    """화면에 요소를 그립니다."""
    global title_image, decoration_image, bg_scroll_y
    clear_canvas()

    center_x = get_canvas_width() // 2
    canvas_width = get_canvas_width()
    canvas_height = get_canvas_height()

    # 1. 배경 이미지 (12.png)를 스크롤하며 그리기
    if decoration_image is not None:
        decoration_image.draw(center_x, bg_scroll_y, canvas_width, canvas_height)
        decoration_image.draw(center_x, bg_scroll_y + canvas_height, canvas_width, canvas_height)

    # 2. [수정] 메인 타이틀 이미지 (banners.png 전체) 그리기
    if title_image is not None:

        # banners.png 전체를 통째로 캔버스 상단 중앙에 그립니다.
        title_width = canvas_width * 0.9
        # 이미지의 원래 비율을 유지하며 높이 계산 (title_image.h와 .w는 로드 후 사용 가능)
        if title_image.w > 0:
            title_height = title_width * (title_image.h / title_image.w)
        else:
            title_height = canvas_height * 0.1  # 안전값

        # Y 좌표: 상단에 가깝게 배치
        draw_y = canvas_height - title_height / 2 - 100

        # 통째로 그리기 (clip_draw 대신 draw 사용)
        title_image.draw(center_x, draw_y, title_width, title_height)

    # 3. 폰트 로직은 삭제된 상태로 유지

    update_canvas()


def pause(): pass


def resume(): pass