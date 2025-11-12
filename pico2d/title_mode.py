# title_mode.py

import game_framework
from pico2d import *
import play_mode

name = "TitleMode"

# 사용할 전역 변수
title_image = None
decoration_image = None
# --- 추가된 전역 변수 ---
dashboard_image = None
# -----------------------------

# 배경 스크롤 변수
bg_scroll_y = 0
SCROLL_SPEED = 150
last_time = 0.0


# --- 모드 함수 정의 ---

def init():
    global title_image, decoration_image, bg_scroll_y, last_time
    global dashboard_image  # dashboard_image 추가

    # 1. banners.png 로드
    try:
        # assets 폴더가 프로젝트 루트에 있다고 가정합니다.
        title_image = load_image('assets/banners.png')
    except:
        print("경고: assets/banners.png 파일을 로드할 수 없습니다.")
        title_image = None

    # 2. 12.png 로드
    try:
        decoration_image = load_image('assets/12.png')
    except:
        print("경고: assets/12.png 파일을 로드할 수 없습니다.")
        decoration_image = None

    # --- dashboard.png 로드 ---
    try:
        dashboard_image = load_image('assets/dashboard.png')
    except:
        print("경고: assets/dashboard.png 파일을 로드할 수 없습니다.")
        dashboard_image = None
    # --------------------------

    # 3. 폰트 로드 로직 전체 삭제

    # 캔버스 높이가 아직 설정되지 않았다면 기본값으로 나눕니다.
    # get_canvas_height()는 pico2d.open_canvas() 이후에만 제대로 작동합니다.
    try:
        bg_scroll_y = get_canvas_height() // 2
    except:
        bg_scroll_y = 1024 // 2 # 임시 기본값

    last_time = get_time()


def finish():
    global title_image, decoration_image, dashboard_image
    if title_image:
        del title_image
    if decoration_image:
        del decoration_image
    # --- dashboard_image 해제 ---
    if dashboard_image:
        del dashboard_image
    # ----------------------------


def handle_events():
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
    global bg_scroll_y, last_time

    current_time = get_time()
    delta_time = current_time - last_time
    last_time = current_time

    canvas_height = get_canvas_height()

    if delta_time > 0.1:
        delta_time = 0.1

    SCROLL_SPEED = 150
    bg_scroll_y -= SCROLL_SPEED * delta_time

    if bg_scroll_y < -canvas_height / 2:
        bg_scroll_y += canvas_height


def draw(): # 🌟🌟🌟 ddef -> def로 수정되었습니다! 🌟🌟🌟
    """화면에 요소를 그립니다."""
    global title_image, decoration_image, bg_scroll_y
    global dashboard_image

    clear_canvas()

    center_x = get_canvas_width() // 2
    canvas_width = get_canvas_width()
    canvas_height = get_canvas_height()

    # 1. 배경 이미지 (12.png)를 스크롤하며 그리기
    if decoration_image is not None:
        decoration_image.draw(center_x, bg_scroll_y, canvas_width, canvas_height)
        decoration_image.draw(center_x, bg_scroll_y + canvas_height, canvas_width, canvas_height)

    # 2. 메인 타이틀 이미지 (banners.png의 스프라이트 조합) 그리기
    title_height = 0
    draw_y = 0

    if title_image is not None:
        SPRITE_W, SPRITE_H = 192, 64
        if title_image.h > SPRITE_H:
            SPRITE_BOTTOM_Y = title_image.h - SPRITE_H
        else:
            SPRITE_BOTTOM_Y = 0

        # ------------------------------------------------------------------
        # 🌟 크기 및 위치 조정 로직
        # ------------------------------------------------------------------

        # [수정] 가로 이동 오프셋 정의: 오른쪽으로 120픽셀 이동 (오른쪽으로 더 가까이)
        HORIZONTAL_OFFSET = 120

        # [유지] 세로 이동 오프셋 정의 (상단에서 200픽셀 아래에 배치)
        VERTICAL_TOP_PADDING = 200

        # 1. 전체 이미지 조합이 차지할 캔버스 너비 (더 크게: 100%)
        COMBINED_WIDTH_RATIO = 1.00
        W_Combined = canvas_width * COMBINED_WIDTH_RATIO

        # 2. 크기 비율 정의: 왼쪽(3.0), 오른쪽(1.0)
        LEFT_RATIO = 3.0
        TOTAL_RATIO = LEFT_RATIO + 1.0

        # 3. 개별 너비 계산
        display_width_left = W_Combined * (LEFT_RATIO / TOTAL_RATIO)
        display_width_right = W_Combined * (1.0 / TOTAL_RATIO)

        # 4. 개별 높이 계산 (비율 유지)
        display_height_left = display_width_left * (SPRITE_H / SPRITE_W)
        display_height_right = display_width_right * (SPRITE_H / SPRITE_W)

        # 5. Y 좌표 설정
        draw_y = canvas_height - display_height_left / 2 - VERTICAL_TOP_PADDING
        title_height = display_height_left

        # 6. X 좌표 계산: 오프셋 적용
        X_Left_Edge = (center_x + HORIZONTAL_OFFSET) - W_Combined / 2
        draw_x_left = X_Left_Edge + display_width_left / 2
        draw_x_right = X_Left_Edge + display_width_left + display_width_right / 2

        # ------------------------------------------------------------------
        # --- Image 1: 맨 왼쪽 스프라이트 ---
        title_image.clip_draw(
            0, SPRITE_BOTTOM_Y, SPRITE_W, SPRITE_H,
            draw_x_left, draw_y,
            display_width_left, display_height_left
        )

        # --- Image 2: 맨 오른쪽 스프라이트 ---
        SPRITE_START_X_RIGHT = 1344
        title_image.clip_draw(
            SPRITE_START_X_RIGHT, SPRITE_BOTTOM_Y, SPRITE_W, SPRITE_H,
            draw_x_right, draw_y,
            display_width_right, display_height_right
        )

    # 3. dashboard.png만 타이틀 아래 중앙에 가로로 길게 늘려 그리기
    if dashboard_image is not None and title_image is not None:
        title_bottom_y = draw_y - (title_height / 2)

        DASHBOARD_HEIGHT = 150
        # 가로로 길게 늘림 (캔버스 너비의 90%)
        DASHBOARD_WIDTH = canvas_width * 0.9
        UI_SPACING = 50

        dashboard_center_y = title_bottom_y - UI_SPACING - (DASHBOARD_HEIGHT / 2)

        dashboard_image.draw(
            center_x,
            dashboard_center_y,
            DASHBOARD_WIDTH,
            DASHBOARD_HEIGHT
        )


    update_canvas()


def pause(): pass


def resume(): pass