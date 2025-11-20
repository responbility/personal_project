# play_mode.py

import game_framework
from pico2d import *
import title_mode

import game_world
import grass
import boy
from spritesheet import SpriteSheet
import os
import glob
from bat import Bat
from map_manager import MapManager

name = "PlayMode"

# 전역 상태 변수
music = None
boy_instance = None
bat_instance = None
grass_instance = None
_cached_font = None
toolbar_image = None
status_pane_image = None

# UI / 테스트 설정
CLIP_W, CLIP_H = 30, 30
SELECT_POS_X = None
SELECT_POS_Y = None
SELECT_SPEED = 240.0
SELECT_VX = 0.0
SELECT_VY = 0.0
SINGLE_FRAME_MODE = True
SELECT_FRAME_INDEX = 0
SELECT_SCALE = 8.0

# ratking 관련 (간단히 유지)
ratking_frames = []
ratking_sheet = None
ratking_frame = 0
ratking_timer = 0.0
RAT_CLIP_W, RAT_CLIP_H = 16, 16
RAT_FPS = 8.0
ratking_preview_scale = 8
boy_prev_x = None


# --- 보조 함수: draw_text, draw_rectangle ---

def draw_text(text, x, y, align='left'):
    font = globals().get('_cached_font', None)
    if font is None:
        return
    w = font.get_text_width(text)
    if align == 'center':
        x -= w // 2
    try:
        font.draw(x, y, text, (255, 255, 255))
    except Exception:
        pass


def draw_rectangle(x1, y1, x2, y2, color=(255, 0, 0)):
    # 경계 상자 그리기. pico2d의 draw_rectangle은 기본 색상을 사용하며,
    # 선 색상을 설정하기 위해서는 draw_line 등의 함수 조합이나 set_line_color 함수가 필요하지만,
    # 여기서는 간단히 pico2d.draw_rectangle만 사용합니다.
    try:
        pico2d.draw_rectangle(x1, y1, x2, y2)
    except Exception:
        pass


# --- 메인 함수 ---

def get_box_center():
    w = CLIP_W * SELECT_SCALE
    h = CLIP_H * SELECT_SCALE
    cx = 40 + w / 2
    cy = 40 + h / 2
    return cx, cy


def init():
    global boy_instance, grass_instance, bat_instance
    global _cached_font, SELECT_POS_X, SELECT_POS_Y
    global toolbar_image, status_pane_image

    game_world.init()

    # MapManager 사용: 후보 경로 설정
    # 파일 경로를 찾는 안정성을 높이기 위해 현재 파일의 경로를 기준으로 설정합니다.
    base_dir = os.path.dirname(__file__)

    # 1. '소녀픽셀던전' 폴더 내의 경로
    base_assets_project = os.path.join(base_dir, '..', '소녀픽셀던전', 'gpd_040_B1(1)', 'assets')
    candidates = [
        os.path.join(base_assets_project, 'MAX2.PNG'),
        os.path.join(base_assets_project, 'MAX.PNG')
    ]

    # 2. 현재 실행 디렉토리의 'assets' 폴더 내의 경로
    assets_local = os.path.join(base_dir, 'assets')
    candidates.append(os.path.join(assets_local, 'MAX2.PNG'))
    candidates.append(os.path.join(assets_local, 'MAX.PNG'))

    # MapManager 인스턴스 생성 및 레이어 0에 추가
    global map_manager
    try:
        map_manager = MapManager(candidates)
        # map_manager가 세그먼트를 성공적으로 로드했을 때만 월드에 추가합니다.
        if hasattr(map_manager, 'segments') and len(map_manager.segments) > 0:
            game_world.add_object(map_manager, 0)
        else:
            # 실패하면 map_manager를 None으로 두고 Grass를 사용하도록 처리
            map_manager = None
    except Exception as e:
        print(f"ERROR: MapManager creation failed: {e}")
        map_manager = None

    # Grass (map) - MapManager가 성공하면 사용하지 않습니다.
    grass_instance = None
    try:
        if map_manager is None or len(map_manager.segments) == 0:
            grass_instance = grass.Grass()
            game_world.add_object(grass_instance, 0)
        else:
            grass_instance = None
    except Exception:
        grass_instance = None

    # Boy
    boy_instance = boy.Boy()
    game_world.add_object(boy_instance, 1)

    # track boy previous x for scrolling
    try:
        global boy_prev_x
        boy_prev_x = boy_instance.x
    except Exception:
        boy_prev_x = None

    # Bat
    try:
        bat_instance = Bat()
        bat_instance.target = boy_instance
        # 맵(Grass) 참조 연결 — bat이 충돌 체크에 사용
        try:
            bat_instance.map = grass_instance or map_manager  # MapManager를 우선 참조
        except Exception:
            bat_instance.map = None
        try:
            bat_instance.last_target_cumulative = boy_instance.cumulative_moved
        except Exception:
            pass
        game_world.add_object(bat_instance, 1)
    except Exception as e:
        print(f"ERROR: Bat instance creation failed: {e}")
        bat_instance = None

    # 폰트 캐시
    try:
        font_path = os.path.join(base_dir, 'assets', 'ENCR10B.TTF')
        _cached_font = load_font(font_path, 16)
    except Exception:
        _cached_font = None

    # UI 이미지 로드 (툴바 / 상태판)
    try:
        toolbar_path = os.path.join(base_dir, 'assets', 'toolbar.png')
        status_pane_path = os.path.join(base_dir, 'assets', 'status_pane.png')
        toolbar_image = load_image(toolbar_path)
        status_pane_image = load_image(status_pane_path)
    except Exception:
        toolbar_image = None
        status_pane_image = None

    # 초기 SELECT_POS
    try:
        SELECT_POS_X, SELECT_POS_Y = get_box_center()
    except Exception:
        SELECT_POS_X, SELECT_POS_Y = 80, 80

    print('PlayMode initialized successfully')


def finish():
    global music, boy_instance, bat_instance, grass_instance, _cached_font
    global toolbar_image, status_pane_image

    if music:
        try:
            music.stop()
        except Exception:
            pass
        del music

    game_world.clear()

    # cleanup
    try:
        del bat_instance
    except Exception:
        pass

    try:
        del boy_instance
    except Exception:
        pass

    try:
        del grass_instance
    except Exception:
        pass

    if _cached_font:
        try:
            del _cached_font
        except Exception:
            pass

    try:
        if toolbar_image is not None: del toolbar_image
        if status_pane_image is not None: del status_pane_image
    except Exception:
        pass

    print('PlayMode finished')


def handle_events():
    global SELECT_VX, SELECT_VY
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.change_mode(title_mode)
            if e.key == SDLK_w:
                SELECT_VY = SELECT_SPEED
            elif e.key == SDLK_s:
                SELECT_VY = -SELECT_SPEED
            elif e.key == SDLK_a:
                SELECT_VX = -SELECT_SPEED
            elif e.key == SDLK_d:
                SELECT_VX = SELECT_SPEED
            elif e.key == SDLK_t:
                global SINGLE_FRAME_MODE
                SINGLE_FRAME_MODE = not SINGLE_FRAME_MODE
        elif e.type == SDL_KEYUP:
            if e.key in (SDLK_w, SDLK_s, SDLK_a, SDLK_d):
                SELECT_VX = 0.0
                SELECT_VY = 0.0

        # 전달
        try:
            if boy_instance:
                boy_instance.handle_event(e)
        except Exception:
            pass
        try:
            if bat_instance:
                bat_instance.handle_event(e)
        except Exception:
            pass


def update():
    global SELECT_POS_X, SELECT_POS_Y
    # frame dt
    try:
        dt = game_framework.frame_time
    except Exception:
        dt = 1.0 / 60.0

    # world update
    game_world.update()

    # update SELECT_POS (초기화 오류 방지)
    if SELECT_POS_X is None:
        try:
            SELECT_POS_X = get_canvas_width() // 2
        except Exception:
            SELECT_POS_X = 80
    if SELECT_POS_Y is None:
        try:
            SELECT_POS_Y = get_canvas_height() // 2
        except Exception:
            SELECT_POS_Y = 80

    # 이전 위치
    prev_x = SELECT_POS_X
    prev_y = SELECT_POS_Y

    SELECT_POS_X += SELECT_VX * dt
    SELECT_POS_Y += SELECT_VY * dt

    # 맵 매니저 스크롤 처리
    try:
        if map_manager is not None and map_manager.segment_width > 0:
            # 2) Boy movement based scroll: when boy moves right, advance world offset
            if boy_instance is not None and boy_prev_x is not None:
                bdx = boy_instance.x - boy_prev_x
                if bdx > 0:
                    map_manager.scroll_right(int(bdx))
                boy_prev_x = boy_instance.x

            # Guard 스폰 예시
            try:
                from guard import Guard  # Guard 클래스가 존재한다고 가정
                if map_manager.world_offset_x > 0:
                    segment_passed = map_manager.world_offset_x // map_manager.segment_width
                    # 세그먼트 당 하나씩만 스폰
                    existing_guards = [o for layer in game_world.objects for o in layer if
                                       o.__class__.__name__ == 'Guard']
                    if len(existing_guards) < segment_passed:
                        g = Guard(x=get_canvas_width() - 150, y=200)
                        game_world.add_object(g, 1)
                        print('DEBUG: Spawned Guard due to right scroll')
            except Exception:
                pass
    except Exception:
        pass

    # ratking timer
    global ratking_timer, ratking_frame
    ratking_timer += dt
    if ratking_timer >= 1.0 / RAT_FPS:
        ratking_timer -= 1.0 / RAT_FPS
        if len(ratking_frames) > 0:
            ratking_frame = (ratking_frame + 1) % len(ratking_frames)
        elif 'ratking_sheet' in globals() and ratking_sheet is not None:
            ratking_frame = (ratking_frame + 1) % ratking_sheet.cols


def draw():
    clear_canvas()
    canvas_w = get_canvas_width()
    canvas_h = get_canvas_height()

    # 1. Draw MapManager if present
    try:
        if 'map_manager' in globals() and map_manager is not None:
            map_manager.draw()
    except Exception:
        pass

    # 2. Draw World (Grass, Boy, Bat, other objects)
    game_world.draw()

    # 3. Draw Debug Info and UI
    debug_y = canvas_h - 40
    try:
        if 'boy_instance' in globals() and boy_instance is not None:
            # 디버그 텍스트 출력
            draw_text(f'BOY: {boy_instance.x:.1f},{boy_instance.y:.1f}', 10, debug_y, align='left')
            # 바운딩 박스 강제 그리기 (빨강)
            x1, y1, x2, y2 = boy_instance.get_bb()
            draw_rectangle(x1, y1, x2, y2, color=(255, 0, 0))  # 보조 함수 사용
            debug_y -= 20

        if 'bat_instance' in globals() and bat_instance is not None:
            draw_text(f'BAT: {bat_instance.x:.1f},{bat_instance.y:.1f}', 10, debug_y, align='left')
            debug_y -= 20

    except Exception:
        pass

    # 4. Draw large ratking preview (left-bottom)
    try:
        if len(ratking_frames) > 0:
            img = ratking_frames[ratking_frame % len(ratking_frames)]
            img.draw(SELECT_POS_X, SELECT_POS_Y)
        elif 'ratking_sheet' in globals() and ratking_sheet is not None:
            ratking_sheet.draw_frame(ratking_frame % ratking_sheet.cols, SELECT_POS_X, SELECT_POS_Y,
                                     RAT_CLIP_W * ratking_preview_scale, RAT_CLIP_H * ratking_preview_scale)
    except Exception:
        pass

    # 5. Draw UI texts
    draw_status_text(canvas_w, canvas_h)

    # 6. Draw toolbar / status pane UI images
    try:
        if status_pane_image is not None:
            sw, sh = status_pane_image.w, status_pane_image.h
            scale_up = 1.9
            display_w = int(min(sw, 240) * scale_up)
            display_h = int(sh * (display_w / sw))
            status_pane_image.draw(canvas_w - display_w // 2 - 10, canvas_h - display_h // 2 - 10, display_w, display_h)
    except Exception:
        pass

    try:
        if toolbar_image is not None:
            tw, th = toolbar_image.w, toolbar_image.h
            scale_up_ui = 1.9
            display_tw = int(min(tw, canvas_w) * scale_up_ui)
            display_th = int(th * (display_tw / tw))
            toolbar_image.draw(canvas_w // 2, display_th // 2 + 12, display_tw, display_th)
    except Exception:
        pass

    # 7. Update Canvas
    update_canvas()


def draw_status_text(canvas_w, canvas_h):
    global SINGLE_FRAME_MODE, SELECT_FRAME_INDEX, SELECT_SCALE
    base_y = canvas_h - 20
    mode_text = "모드: " + ("단일" if SINGLE_FRAME_MODE else "전체")
    frame_text = f"프레임: {SELECT_FRAME_INDEX}  스케일: {SELECT_SCALE:.1f}"
    draw_text(mode_text, canvas_w // 2, base_y, align='center')
    draw_text(frame_text, canvas_w // 2, base_y - 20, align='center')


def pause():
    pass


def resume():
    pass