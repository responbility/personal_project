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

    bg_scroll_y = get_canvas_height() // 2
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


def draw():
    """화면에 요소를 그립니다."""
    global title_image, decoration_image, bg_scroll_y
    global dashboard_image  # dashboard_image 추가

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
        # 스프라이트 크기 (banners.png가 8개의 192x64 타일로 구성되었다고 가정)
        SPRITE_W, SPRITE_H = 192, 64

        # 스프라이트 시트의 맨 윗줄만 그리도록 'bottom' 좌표를 계산
        if title_image.h > SPRITE_H:
            SPRITE_BOTTOM_Y = title_image.h - SPRITE_H
        else:
            SPRITE_BOTTOM_Y = 0

        # [수정] 가로 이동 오프셋 정의 (오른쪽으로 80픽셀 이동)
        HORIZONTAL_OFFSET = 80
        # [수정] 세로 이동 오프셋 정의 (상단에서 200픽셀 아래에 배치)
        VERTICAL_TOP_PADDING = 200

        # 1. 전체 이미지 조합이 차지할 캔버스 너비 (95% 유지)
        COMBINED_WIDTH_RATIO = 0.95
        W_Combined = canvas_width * COMBINED_WIDTH_RATIO

        # 2. 크기 비율 정의: 왼쪽(3.0), 오른쪽(1.0) -> 총 비율 4.0
        LEFT_RATIO = 3.0
        TOTAL_RATIO = LEFT_RATIO + 1.0  # 4.0

        # 3. 개별 너비 계산
        display_width_left = W_Combined * (LEFT_RATIO / TOTAL_RATIO)
        display_width_right = W_Combined * (1.0 / TOTAL_RATIO)

        # 4. 개별 높이 계산 (비율 유지)
        display_height_left = display_width_left * (SPRITE_H / SPRITE_W)
        display_height_right = display_width_right * (SPRITE_H / SPRITE_W)

        # 5. Y 좌표 설정 (더 아래로 이동)
        draw_y = canvas_height - display_height_left / 2 - VERTICAL_TOP_PADDING
        title_height = display_height_left  # 타이틀의 최종 높이 저장

        # 6. X 좌표 계산
        X_Left_Edge = (center_x + HORIZONTAL_OFFSET) - W_Combined / 2
        draw_x_left = X_Left_Edge + display_width_left / 2
        draw_x_right = X_Left_Edge + display_width_left + display_width_right / 2

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
        # 타이틀의 맨 아래쪽 Y 좌표 계산
        title_bottom_y = draw_y - (title_height / 2)

        # 이미지의 표시 크기 및 간격 설정
        DASHBOARD_HEIGHT = 150  # 원하는 높이 (예: 150px)

        # 🌟 가로로 길게 늘립니다: 캔버스 너비의 90%로 설정
        DASHBOARD_WIDTH = canvas_width * 0.9

        UI_SPACING = 50  # 타이틀과의 간격 50px

        # 새로운 UI가 그려질 중심 Y 좌표
        dashboard_center_y = title_bottom_y - UI_SPACING - (DASHBOARD_HEIGHT / 2)

        # dashboard.png 그리기
        dashboard_image.draw(
            center_x,  # X: 캔버스 중앙
            dashboard_center_y,  # Y: 타이틀 아래 지정된 위치
            DASHBOARD_WIDTH,  # W: 조정된 너비 (가로로 길게 늘어남)
            DASHBOARD_HEIGHT  # H: 지정된 높이
        )

    update_canvas()


def pause(): pass


def resume(): pass