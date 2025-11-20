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
    base_assets = os.path.join(os.path.dirname(__file__), '..', '소녀픽셀던전', 'gpd_040_B1(1)', 'assets')
    candidates = [os.path.join(base_assets, 'MAX2.PNG'), os.path.join(base_assets, 'MAX.PNG')]
    try:
        # 프로젝트 내부 assets도 후보에 넣음
        candidates.append(os.path.join(os.path.dirname(__file__), 'assets', 'MAX2.PNG'))
        candidates.append(os.path.join(os.path.dirname(__file__), 'assets', 'MAX.PNG'))
    except Exception:
        pass

    # MapManager 인스턴스 생성 및 레이어 0에 추가
    try:
        global map_manager
        map_manager = MapManager(candidates)
        game_world.add_object(map_manager, 0)
    except Exception:
        map_manager = None

    # Grass (map) - 기존 호환을 위해 남겨둡니다
    # 만약 MapManager가 성공적으로 로드되었다면, map 이미지를 사용하므로
    # 기존의 grass 전체 캔버스 이미지는 추가하지 않습니다(덮어씌우는 문제 방지).
    grass_instance = None
    try:
        if map_manager is None:
            grass_instance = grass.Grass()
            game_world.add_object(grass_instance, 0)
        else:
            # MapManager가 있으면 grass는 사용하지 않음
            grass_instance = None
    except Exception:
        grass_instance = None

    # Boy
    boy_instance = boy.Boy()
    game_world.add_object(boy_instance, 1)
    print(
        f"DEBUG: Added boy_instance to game_world layer 1. Layers sizes: {[len(layer) for layer in game_world.objects]}")
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
            bat_instance.map = grass_instance
        except Exception:
            bat_instance.map = None
        try:
            bat_instance.last_target_cumulative = boy_instance.cumulative_moved
        except Exception:
            pass
        game_world.add_object(bat_instance, 1)
        print(
            f"DEBUG: Added bat_instance to game_world layer 1. Layers sizes: {[len(layer) for layer in game_world.objects]}")
    except Exception:
        bat_instance = None

    # 폰트 캐시
    try:
        base_assets = os.path.join(os.path.dirname(__file__), 'assets')
        font_path = os.path.join(base_assets, 'ENCR10B.TTF')
        _cached_font = load_font(font_path, 16)
    except Exception:
        _cached_font = None

    # UI 이미지 로드 (툴바 / 상태판)
    try:
        toolbar_path = os.path.join(os.path.dirname(__file__), 'assets', 'toolbar.png')
        status_pane_path = os.path.join(os.path.dirname(__file__), 'assets', 'status_pane.png')
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

    print('PlayMode initialized')


def finish():
    global music, boy_instance, bat_instance, grass_instance, _cached_font
    if music:
        try:
            music.stop()
        except Exception:
            pass
        del music

    game_world.clear()

    # cleanup
    try:
        if 'bat_instance' in globals() and bat_instance:
            del bat_instance
    except Exception:
        pass

    try:
        if 'boy_instance' in globals() and boy_instance:
            del boy_instance
    except Exception:
        pass

    try:
        if 'grass_instance' in globals() and grass_instance:
            del grass_instance
    except Exception:
        pass

    if _cached_font:
        try:
            del _cached_font
        except Exception:
            pass
    try:
        global toolbar_image, status_pane_image
        if toolbar_image is not None:
            del toolbar_image
        if status_pane_image is not None:
            del status_pane_image
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
    # world update
    game_world.update()

    # frame dt
    try:
        dt = game_framework.frame_time
    except Exception:
        dt = 1.0 / 60.0

    # update SELECT_POS
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

    # 맵 매니저 오른쪽 스크롤 처리: 왼쪽->오른쪽 이동이면 world offset 증가
    try:
        if map_manager is not None:
            # world scroll: 플레이어가 오른쪽으로 움직이면 맵이 좌측으로 움직이는 대신 world_offset을 증가시킴
            # 1) SELECT cursor based scroll (editor-style)
            dx = SELECT_POS_X - prev_x
            if dx > 0:
                map_manager.scroll_right(int(dx))
            # 2) Boy movement based scroll: when boy moves right, advance world offset
            try:
                if boy_instance is not None and boy_prev_x is not None:
                    bdx = boy_instance.x - boy_prev_x
                    if bdx > 0:
                        map_manager.scroll_right(int(bdx))
                    boy_prev_x = boy_instance.x
            except Exception:
                pass
                # Guard 스폰 예시: world_offset_x가 일정값 이상이면 Guard 스폰
                try:
                    from guard import Guard
                    # spawn when crossing multiples of segment width
                    seg_index = int(map_manager.world_offset_x // max(1, map_manager.segment_width))
                    if seg_index > 0:
                        # spawn one guard per crossed segment
                        existing_guards = [o for layer in game_world.objects for o in layer if o.__class__.__name__ == 'Guard']
                        if len(existing_guards) < seg_index:
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
        elif ratking_sheet is not None:
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

    # 2. Draw World (Grass, Boy, Bat) - Boy는 Layer 1에 있으므로 여기서 그려져야 합니다.
    game_world.draw()

    # 3. Draw Debug Info and UI (Force-drawing the Boy's BB for visibility check)
    try:
        debug_y = canvas_h - 40
        if 'boy_instance' in globals() and boy_instance is not None:
            # 디버그 텍스트 출력
            draw_text(f'BOY: {boy_instance.x:.1f},{boy_instance.y:.1f}', 10, debug_y, align='left')
            # 바운딩 박스 강제 그리기 (빨강)
            try:
                x1, y1, x2, y2 = boy_instance.get_bb()
                draw_rectangle(x1, y1, x2, y2)
            except Exception:
                pass
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
        elif ratking_sheet is not None:
            ratking_sheet.draw_frame(ratking_frame % ratking_sheet.cols, SELECT_POS_X, SELECT_POS_Y,
                                     RAT_CLIP_W * ratking_preview_scale, RAT_CLIP_H * ratking_preview_scale)
    except Exception:
        pass

    # 5. Draw UI texts
    draw_status_text(canvas_w, canvas_h)

    # 6. Draw toolbar / status pane UI images
    try:
        if status_pane_image is not None:
            # draw at top-left corner aligned
            sw = status_pane_image.w
            sh = status_pane_image.h
            # scale to fit width ~ 240 px if larger, then increase slightly for better visibility
            display_w = min(sw, 240)
            display_h = int(sh * (display_w / sw))
            scale_up = 1.9
            display_w = int(display_w * scale_up)
            display_h = int(display_h * scale_up)
            status_pane_image.draw(canvas_w - display_w // 2 - 10, canvas_h - display_h // 2 - 10, display_w, display_h)
    except Exception:
        pass

    try:
        if toolbar_image is not None:
            tw = toolbar_image.w
            th = toolbar_image.h
            display_tw = min(tw, canvas_w)
            display_th = int(th * (display_tw / tw))
            # increase UI size slightly
            scale_up_ui = 1.9
            display_tw = int(display_tw * scale_up_ui)
            display_th = int(display_th * scale_up_ui)
            # place at bottom center with small upward offset
            toolbar_image.draw(canvas_w // 2, display_th // 2 + 12, display_tw, display_th)
    except Exception:
        pass

    # 7. Update Canvas
    update_canvas()


# --- 보조 함수들은 이제 모듈 레벨에 정의되어야 합니다. ---

def draw_status_text(canvas_w, canvas_h):
    global SINGLE_FRAME_MODE, SELECT_FRAME_INDEX, SELECT_SCALE
    base_y = canvas_h - 20
    mode_text = "모드: " + ("단일" if SINGLE_FRAME_MODE else "전체")
    frame_text = f"프레임: {SELECT_FRAME_INDEX}  스케일: {SELECT_SCALE:.1f}"
    draw_text(mode_text, canvas_w // 2, base_y, align='center')
    draw_text(frame_text, canvas_w // 2, base_y - 20, align='center')


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


def draw_rectangle(x1, y1, x2, y2, color=None):
    try:
        # pico2d.draw_rectangle은 색상 인자를 받지 않으므로 기본 바운딩 박스를 그립니다.
        pico2d.draw_rectangle(x1, y1, x2, y2)
    except Exception:
        pass


def pause():
    pass


def resume():
    pass