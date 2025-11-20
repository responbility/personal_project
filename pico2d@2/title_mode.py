import game_framework
from pico2d import *
import play_mode
import os  # 파일 시스템 접근을 위해 필수

name = "TitleMode"

# 사용할 전역 변수
title_image = None
decoration_image = None
dashboard_image = None
_title_music = None  # OGG 파일을 저장할 객체

# 배경 스크롤 변수
bg_scroll_y = 0
SCROLL_SPEED = 150
last_time = 0.0


# --- 모드 함수 정의 ---

def init():
    """리소스를 로드하고 초기화합니다."""
    global title_image, decoration_image, dashboard_image
    global _title_music
    global bg_scroll_y
    global last_time

    # 1. 이미지 로드
    try:
        title_image = load_image('assets/banners.png')
    except Exception:
        print("경고: assets/banners.png 파일을 로드할 수 없습니다.")
        title_image = None

    try:
        decoration_image = load_image('assets/12.png')
    except Exception:
        print("경고: assets/12.png 파일을 로드할 수 없습니다.")
        decoration_image = None

    try:
        dashboard_image = load_image('assets/dashboard.png')
    except Exception:
        print("경고: assets/dashboard.png 파일을 로드할 수 없습니다.")
        dashboard_image = None

    # 2. 배경 스크롤 및 시간 초기화
    try:
        bg_scroll_y = get_canvas_height() // 2
    except:
        bg_scroll_y = 1024 // 2

    last_time = get_time()

    # 3. 🚨 타이틀 음악 로드 핵심 로직 🚨
    # init()에서 리소스를 딱 한 번만 로드합니다.
    try:
        assets_dir = 'assets'
        chosen = None

        # 1순위: assets/theme.ogg 파일 경로 명시 및 존재 확인
        preferred = os.path.join(assets_dir, 'theme.ogg')
        if os.path.isfile(preferred):
            chosen = preferred
        else:
            # 2순위: assets 폴더에서 다른 ogg 파일 탐색 (폴백)
            candidates = [
                os.path.join(assets_dir, f) for f in os.listdir(assets_dir)
                if f.lower().endswith('.ogg')
            ]
            if candidates:
                # 'theme.ogg', 'game.ogg', 'surface.ogg' 중 우선순위로 선택
                for pref_name in ['theme.ogg', 'game.ogg', 'surface.ogg']:
                    candidate_path = os.path.join(assets_dir, pref_name)
                    if candidate_path in candidates:
                        chosen = candidate_path
                        break
                if chosen is None:
                    chosen = candidates[0]  # 아무거나 첫 번째 파일 선택

        if chosen is not None:
            # music 객체 로드
            _title_music = load_music(chosen)
            try:
                _title_music.set_volume(64)
            except Exception:
                pass
            print(f"MUSIC LOAD SUCCESS: 타이틀 음악 리소스 로드 완료: {chosen}")
        else:
            print("MUSIC LOAD FAIL: 경고: assets 폴더에 재생할 ogg 파일이 없습니다.")
    except Exception as e:
        # 파일 경로, 파일 형식(코덱) 등에 문제가 있을 경우 이 예외가 발생합니다.
        print(f"MUSIC LOAD ERROR: 로드 실패(init): {e}. 'assets/theme.ogg' 파일 경로 및 형식을 확인하세요.")
        _title_music = None


def finish():
    """모드 종료 시 로드된 리소스를 해제합니다."""
    global title_image, decoration_image, dashboard_image, _title_music

    if title_image: del title_image
    if decoration_image: del decoration_image
    if dashboard_image: del dashboard_image

    # 음악 객체 해제
    if _title_music:
        del _title_music
        print("타이틀 음악 리소스 해제 완료.")


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_SPACE:
                # Play Mode로 전환
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
        # 크기 및 위치 조정 로직
        # ------------------------------------------------------------------
        HORIZONTAL_OFFSET = 120
        VERTICAL_TOP_PADDING = 200
        COMBINED_WIDTH_RATIO = 1.00
        W_Combined = canvas_width * COMBINED_WIDTH_RATIO
        LEFT_RATIO = 3.0
        TOTAL_RATIO = LEFT_RATIO + 1.0
        display_width_left = W_Combined * (LEFT_RATIO / TOTAL_RATIO)
        display_width_right = W_Combined * (1.0 / TOTAL_RATIO)
        display_height_left = display_width_left * (SPRITE_H / SPRITE_W)
        display_height_right = display_width_right * (SPRITE_H / SPRITE_W)
        draw_y = canvas_height - display_height_left / 2 - VERTICAL_TOP_PADDING
        title_height = display_height_left
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


def pause():
    """모드가 일시 정지될 때 음악 재생을 멈춥니다."""
    global _title_music
    # _title_music 객체가 존재하고 현재 재생 중일 경우에만 멈춥니다.
    if _title_music and hasattr(_title_music, 'playing') and _title_music.playing:
        _title_music.stop()
        print("MUSIC CONTROL: 타이틀 음악 정지(pause).")


def resume():
    """모드가 다시 시작될 때 음악을 재생합니다."""
    global _title_music
    # _title_music 객체가 존재할 경우에만 반복 재생을 재개합니다.
    if _title_music:
        _title_music.repeat_play()
        print("MUSIC CONTROL: 타이틀 음악 재생 재개(resume).")


def enter():
    """모드가 시작(처음)되거나 진입될 때 호출됩니다."""
    global last_time
    print(f"{name} enter")

    # 1. 이전 시간 업데이트
    last_time = get_time()

    # 2. 타이틀 음악 재생 시작 (init에서 로드된 객체를 사용)
    global _title_music
    if _title_music:
        _title_music.repeat_play()
        print("MUSIC PLAY START: 타이틀 음악 재생 시작(enter).")
    else:
        # init()에서 로드가 실패했을 경우
        print("MUSIC PLAY FAIL: 경고: _title_music 객체가 없어 재생할 수 없습니다. (로드 실패)")