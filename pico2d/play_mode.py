# play_mode.py

import game_framework
from pico2d import *
import title_mode

# 🚨 배경 객체 및 게임 월드 관리를 위해 반드시 필요합니다. 🚨
import game_world
import grass

# -------------------------------------------------------------

# 모드 이름 정의
name = "PlayMode"

# 캐릭터 초기 위치 (임시)
character_x, character_y = 576 // 2, 1024 // 2

# 이미지 객체 전역 변수
character_image = None
toolbar_image = None
status_pane_image = None
grass_instance = None  # grass 객체 전역 변수 선언

# UI 이미지의 추정된 원본 크기
TOOLBAR_W, TOOLBAR_H = 576, 50
STATUS_PANE_W, STATUS_PANE_H = 576, 80


def init():
    """게임 플레이 모드를 초기화하고 이미지를 로드합니다."""
    global character_image, toolbar_image, status_pane_image
    global grass_instance

    # 🚨 game_world 초기화 및 배경 객체 생성 🚨
    game_world.init()
    grass_instance = grass.Grass()
    game_world.add_object(grass_instance, 0)  # 0번 레이어(배경)에 추가
    # ---------------------------------------------------

    # 캐릭터 이미지 로드 (assets/avatars.png는 가정된 파일 이름)
    try:
        character_image = load_image('assets/avatars.png')
    except:
        print("경고: assets/avatars.png 파일을 로드할 수 없습니다.")
        character_image = None

    # 툴바 이미지 로드
    try:
        toolbar_image = load_image('assets/toolbar.png')
    except:
        print("경고: assets/toolbar.png 파일을 로드할 수 없습니다.")
        toolbar_image = None

    # 상태 창 이미지 로드
    try:
        status_pane_image = load_image('assets/status_pane.png')
    except:
        print("경고: assets/status_pane.png 파일을 로드할 수 없습니다.")
        status_pane_image = None

    print("Play Mode Started: UI/Character Loaded")


def finish():
    """모드 종료 시 리소스를 해제합니다."""
    global character_image, toolbar_image, status_pane_image

    game_world.clear()  # game_world에 등록된 모든 객체 해제

    if character_image:
        del character_image
    if toolbar_image:
        del toolbar_image
    if status_pane_image:
        del status_pane_image
    print("Play Mode Finished: UI/Character Unloaded")


def handle_events():
    """이벤트 처리 (ESC 키: 타이틀 모드로 복귀)"""
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.change_mode(title_mode)


def update():
    """게임 상태 업데이트"""
    # 🚨 game_world에 등록된 모든 객체를 업데이트합니다. 🚨
    game_world.update()
    # -----------------------------------------------------


def draw():
    """화면에 모든 요소를 그립니다."""
    global character_image, toolbar_image, status_pane_image
    clear_canvas()

    canvas_width = get_canvas_width()
    canvas_height = get_canvas_height()

    # 🚨 game_world에 등록된 모든 객체(배경 포함)를 그립니다. 🚨
    game_world.draw()
    # -----------------------------------------------------------

    # 1. 메인 캐릭터 그리기 (크기 확대 적용)
    if character_image is not None:
        # 원본 클리핑 크기
        clip_w, clip_h = 30, 30
        scale_factor = 2.0  # 2배 확대

        # 확대된 그리기 크기
        target_w = clip_w * scale_factor  # 30 * 2.0 = 60
        target_h = clip_h * scale_factor  # 30 * 2.0 = 60

        # clip_draw(left, bottom, clip_w, clip_h, draw_x, draw_y, target_w, target_h)
        character_image.clip_draw(
            0, 0,
            clip_w, clip_h,
            character_x, character_y,
            target_w, target_h  # 확대된 크기 적용
        )

    # --- UI 높이 설정 ---
    display_toolbar_height = TOOLBAR_H * 2
    display_status_pane_height = STATUS_PANE_H * 1.0
    BOTTOM_PADDING = 10
    # --------------------

    # 2. 툴바 그리기 (상단 중앙 배치, 세로 늘림 적용)
    if toolbar_image is not None:
        toolbar_center_y = canvas_height - (display_toolbar_height / 2)
        toolbar_image.draw(
            canvas_width / 2,
            toolbar_center_y,
            canvas_width,
            display_toolbar_height
        )

    # 3. 상태 창 그리기 (하단 중앙 배치, 여백 적용)
    if status_pane_image is not None:
        status_pane_center_y = (display_status_pane_height / 2) + BOTTOM_PADDING
        status_pane_image.draw(
            canvas_width / 2,
            status_pane_center_y,
            canvas_width,
            display_status_pane_height
        )

    update_canvas()


def pause():
    """모드 일시정지 시 호출"""
    pass


def resume():
    """일시정지 후 재개 시 호출"""
    pass