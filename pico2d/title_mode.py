# title_mode.py

import game_framework
from pico2d import *
import play_mode

name = "TitleMode"

# 사용할 전역 변수
title_image = None  # banners.png
decoration_image = None  # 12.png (배경으로 사용)
font = None  # 폰트 객체

# 배경 스크롤을 위한 변수
bg_scroll_y = 0  # 배경 이미지의 현재 Y 좌표 (중앙 기준)
SCROLL_SPEED = 150  # 스크롤 속도 (픽셀/초)

# [수정] 시간 계산을 위한 전역 변수 추가
last_time = 0.0  # 이전 프레임 시간을 저장


# --- 모드 함수 정의 ---

def init():
    """타이틀 모드가 시작될 때 호출됩니다."""
    global title_image, decoration_image, font, bg_scroll_y, last_time

    # 1. banners.png 로드
    try:
        title_image = load_image('assets/banners.png')
    except:
        print("경로 오류: assets/banners.png 파일을 로드할 수 없습니다.")
        title_image = None

    # 2. 12.png 로드
    try:
        decoration_image = load_image('assets/12.png')
    except:
        print("경로 오류: assets/12.png 파일을 로드할 수 없습니다.")
        decoration_image = None

    # 3. 폰트 로드 (ENCR10B.TTF 및 KOF.TTF 모두 로드 실패하는 문제 방지)
    try:
        font = load_font('assets/ENCR10B.TTF', 30)
    except:
        try:
            # KOF.TTF 로드 시도
            font = load_font('KOF.TTF', 30)
            print("경고: ENCR10B.TTF 로드 실패. KOF.TTF 폰트로 대체합니다.")
        except:
            # 두 폰트 모두 로드 실패 시, 강제 종료 방지
            print("경고: 폰트를 로드할 수 없어 시작 메시지를 그릴 수 없습니다.")
            font = None

    # 배경 Y 좌표 초기화
    bg_scroll_y = get_canvas_height() // 2

    # [수정] last_time 초기화: init 시점에 현재 시간으로 설정
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

    # -----------------------------------------------------------------
    # [수정] delta_time 직접 계산 (NameError 해결)
    current_time = get_time()
    delta_time = current_time - last_time
    last_time = current_time
    # -----------------------------------------------------------------

    canvas_height = get_canvas_height()

    # delta_time이 비정상적으로 클 경우 (예: 디버깅)를 대비해 제한
    if delta_time > 0.1:
        delta_time = 0.1

    # 1. Y 좌표 감소 (아래로 이동)
    bg_scroll_y -= SCROLL_SPEED * delta_time

    # 2. 루프 조건 확인 (무한 스크롤)
    if bg_scroll_y < -canvas_height / 2:
        bg_scroll_y += canvas_height  # 높이만큼 더해서 맨 위로 순간 이동


def draw():
    """화면에 요소를 그립니다."""
    global title_image, decoration_image, font, bg_scroll_y
    clear_canvas()

    center_x = get_canvas_width() // 2
    center_y = get_canvas_height() // 2
    canvas_width = get_canvas_width()
    canvas_height = get_canvas_height()

    # 1. 배경 이미지 (12.png)를 스크롤하며 그리기 (draw(x, y, w, h) 사용)
    if decoration_image is not None:
        # Image 1: 현재 스크롤 위치
        decoration_image.draw(center_x, bg_scroll_y, canvas_width, canvas_height)

        # Image 2: Image 1 위쪽에 배치하여 끊김 없이 이어지게 함
        decoration_image.draw(center_x, bg_scroll_y + canvas_height, canvas_width, canvas_height)

    # 2. 메인 타이틀 이미지 (banners.png) 그리기 (높이 50%로 설정)
    if title_image is not None:
        title_width = canvas_width * 0.8
        title_height = canvas_height * 0.5
        title_image.draw(center_x, center_y + 150, title_width, title_height)

    # 3. 시작 메시지 그리기 (폰트 로드 성공 시에만)
    if font is not None:
        font.draw(center_x - 200, 100,
                  'Press SPACE to Start', (255, 255, 255))

    update_canvas()


def pause(): pass


def resume(): pass