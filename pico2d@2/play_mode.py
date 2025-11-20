import game_framework
from pico2d import *
import title_mode
import pico2d

import game_world
import grass
import boy  # boy.py의 Boy 클래스 임포트
from spritesheet import SpriteSheet
import os
import glob

# -------------------------------------------------------------

# 모드 이름 정의
name = "PlayMode"

# 🚨 ogg 파일 재생을 위한 전역 변수 추가 🚨
music = None

# 캐릭터 객체 전역 변수
boy_instance = None

# UI 이미지의 추정된 원본 크기
TOOLBAR_W, TOOLBAR_H = 576, 50
STATUS_PANE_W, STATUS_PANE_H = 576, 80
# 상태 창 세로 확대 스케일 (기본 1.0 -> 1.5 등으로 늘릴 수 있음)
STATUS_PANE_SCALE = 1.5

# UI 이미지 전역 변수
toolbar_image = None
status_pane_image = None
grass_instance = None

# 🚨 스프라이트 분할 테스트를 위한 전역 변수 🚨
test_image = None
# CLIP_W, CLIP_H를 30x30으로 수정 (boy.py와 일치)
CLIP_W, CLIP_H = 30, 30
SCALE_FACTOR_DEFAULT = 3.0
NUM_FRAMES = None

# Ratking 애니메이션(게임에서 자연스럽게 재생할 전용 시트)
ratking_sheet = None
RAT_CLIP_W, RAT_CLIP_H = 16, 16
RAT_FPS = 8.0
ratking_frame = 0
ratking_timer = 0.0
# 게임 내에 크게 보여줄 스케일 (스크린샷처럼 크게 보이게)
ratking_preview_scale = 8  # 더 크게 보여주기 (스크린샷처럼)

# 단일 프레임을 크게 잘라서 표시할지 여부
SINGLE_FRAME_MODE = True
# 보여줄 프레임 인덱스(0-based). 필요하면 이 값을 변경하세요.
SELECT_FRAME_INDEX = 0
# 단일 프레임을 그릴 때의 스케일 (프레임 원본 크기에 곱해지는 값) — 기본을 더 크게 설정
SELECT_SCALE = 8.0

# 스프라이트 물리(위치/속도)
# 화면상의 중심 좌표로 사용할 초기 위치는 캔버스 중앙으로 설정합니다. init()에서 덮어쓸 수 있습니다.
SELECT_POS_X = None
SELECT_POS_Y = None
# 스프라이트 속도(픽셀/초)
SELECT_SPEED = 240.0
# 현재 속도 (픽셀/초)
SELECT_VX = 0.0
SELECT_VY = 0.0

# 왼쪽 아래 박스(사용자가 말한 빨간 박스) 기준
# 좌측 여백, 하단 여백(픽셀)
BOX_MARGIN_X = 40
BOX_MARGIN_Y = 40


# 박스 크기(프레임 출력 크기와 동일하게 처리)
def get_box_center():
    # 박스의 중심 좌표를 반환 (프레임 출력 크기의 반을 더해 중심으로 맞춤)
    w = CLIP_W * SELECT_SCALE
    h = CLIP_H * SELECT_SCALE
    cx = BOX_MARGIN_X + w / 2
    cy = BOX_MARGIN_Y + h / 2
    return cx, cy


def init():
    """게임 플레이 모드를 초기화하고 객체를 로드합니다."""
    global toolbar_image, status_pane_image
    global grass_instance, boy_instance
    global test_image  # 테스트 이미지 전역 변수 사용 선언
    global music # 🚨 전역 음악 변수 사용 선언

    game_world.init()

    # 1. 풀 객체 추가 (배경 레이어 0)
    grass_instance = grass.Grass()
    game_world.add_object(grass_instance, 0)

    # 2. Boy 객체 생성 및 추가 (캐릭터 레이어 1)
    boy_instance = boy.Boy()
    game_world.add_object(boy_instance, 1)

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

    # 테스트용 스프라이트 시트 로드 (SpriteSheet 사용)
    try:
        test_image = SpriteSheet('assets/ratking.png', CLIP_W, CLIP_H)
    except Exception:
        try:
            test_image = SpriteSheet('assets/ratking1.png', CLIP_W, CLIP_H)
        except Exception:
            print("경고: ratking 스프라이트 시트 로드 실패. assets/ratking.png 경로를 확인하세요.")
            test_image = None

    # ratking 전용 시트(정확한 클립 사이즈로 로드)
    global ratking_sheet, ratking_frame, ratking_timer
    try:
        ratking_sheet = SpriteSheet('assets/ratking.png', RAT_CLIP_W, RAT_CLIP_H)
    except Exception:
        ratking_sheet = None
    ratking_frame = 0
    ratking_timer = 0.0

    # 우선: PNG로 분리된 프레임들이 있는지 확인해 로드
    global ratking_frames
    frames_dir = os.path.join('assets', 'ratking_frames')
    ratking_frames = []
    if os.path.isdir(frames_dir):
        # 파일명 정렬
        files = sorted(glob.glob(os.path.join(frames_dir, '*.png')))
        for f in files:
            try:
                img = load_image(f)
                ratking_frames.append(img)
            except Exception:
                pass

    # -------------------------------------------------------------
    # 🚨 ogg 파일 로드 및 반복 재생 핵심 로직 추가 🚨
    # -------------------------------------------------------------
    try:
        # load_music을 사용하여 ogg 파일을 로드합니다.
        music = load_music('assets/theme.ogg')
        music.set_volume(120) # 볼륨 설정 (0~128)
        # 반복 재생을 시작합니다.
        music.repeat_play()
        print("MUSIC: 'theme.ogg' 파일 로드 및 반복 재생 시작.")
    except Exception as e:
        print(f"MUSIC ERROR: ogg 파일을 로드하거나 재생할 수 없습니다. 파일을 확인하세요. {e}")
        music = None
    # -------------------------------------------------------------

    print("Play Mode Started: Boy/Grass/UI Loaded")
    # 초기 단일 프레임 위치를 캔버스 중앙으로 설정
    global SELECT_POS_X, SELECT_POS_Y
    # 기본 위치를 왼쪽 아래 박스 중심으로 설정
    try:
        SELECT_POS_X, SELECT_POS_Y = get_box_center()
    except Exception:
        SELECT_POS_X, SELECT_POS_Y = 80, 80

    # 폰트 캐시: draw_text에서 매 프레임 로드하는 대신 init에서 한 번만 로드
    global _cached_font
    _cached_font = None
    try:
        _cached_font = load_font('assets/Consolas.ttf', 16)
    except Exception:
        try:
            _cached_font = load_font('assets/ENCR10B.TTF', 16)
        except Exception:
            _cached_font = None


def finish():
    """모드 종료 시 리소스를 해제합니다."""
    global toolbar_image, status_pane_image
    global test_image
    global music # 🚨 전역 음악 변수 사용 선언

    # -------------------------------------------------------------
    # 🚨 ogg 파일 재생 중지 및 해제 로직 추가 🚨
    # -------------------------------------------------------------
    if music:
        music.stop()
        del music
        print("MUSIC: 음악 재생 중지 및 해제.")
    # -------------------------------------------------------------

    game_world.clear()

    if toolbar_image:
        del toolbar_image
    if status_pane_image:
        del status_pane_image
    if test_image:
        del test_image

    print("Play Mode Finished: Unloaded")


def handle_events():
    """이벤트 처리 (W/A/S/D로 선택 프레임 이동)"""
    global SELECT_VX, SELECT_VY, SELECT_FRAME_INDEX, SINGLE_FRAME_MODE
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()

        # 키 눌림
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.change_mode(title_mode)

            # 모드 토글: 't'
            if event.key == SDLK_t:
                SINGLE_FRAME_MODE = not SINGLE_FRAME_MODE

            # 프레임 인덱스 조절 (좌/우)
            try:
                total_frames = test_image.cols * test_image.rows if test_image is not None else 1
            except Exception:
                # SpriteSheet 객체가 아니거나 로드 실패 시, 기본값 7을 사용
                total_frames = 7
            if event.key == SDLK_LEFT:
                SELECT_FRAME_INDEX = max(0, SELECT_FRAME_INDEX - 1)
            elif event.key == SDLK_RIGHT:
                SELECT_FRAME_INDEX = min(total_frames - 1, SELECT_FRAME_INDEX + 1)

            # WASD (키다운) -> 속도 설정
            if event.key == SDLK_w:
                SELECT_VY = SELECT_SPEED
            elif event.key == SDLK_s:
                SELECT_VY = -SELECT_SPEED
            elif event.key == SDLK_a:
                SELECT_VX = -SELECT_SPEED
            elif event.key == SDLK_d:
                SELECT_VX = SELECT_SPEED

            # 'b' 키: 왼쪽 아래 박스로 이동
            if event.key == SDLK_b:
                try:
                    SELECT_POS_X, SELECT_POS_Y = get_box_center()
                except Exception:
                    SELECT_POS_X, SELECT_POS_Y = 80, 80

        # 키 뗌(릴리즈)
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_w or event.key == SDLK_s:
                SELECT_VY = 0.0
            if event.key == SDLK_a or event.key == SDLK_d:
                SELECT_VX = 0.0

        # 항상 boy 이벤트도 전달
        if boy_instance:
            boy_instance.handle_event(event)


def update():
    """게임 상태 업데이트"""
    global SELECT_POS_X, SELECT_POS_Y, SELECT_VX, SELECT_VY

    # 게임 월드 업데이트
    game_world.update()

    # dt 확보
    try:
        dt = game_framework.frame_time
    except Exception:
        dt = 1.0 / 60.0

    # 초기 위치가 None이면 캔버스 중심으로 초기화
    try:
        cw = get_canvas_width()
        ch = get_canvas_height()
    except Exception:
        cw, ch = 576, 1024
    if SELECT_POS_X is None:
        SELECT_POS_X = cw // 2
    if SELECT_POS_Y is None:
        SELECT_POS_Y = ch // 2

    # 위치 갱신 (속도는 픽셀/초)
    SELECT_POS_X += SELECT_VX * dt
    SELECT_POS_Y += SELECT_VY * dt

    # 경계 검사(프레임 중심 기준)
    half_w = (CLIP_W * SELECT_SCALE) / 2
    half_h = (CLIP_H * SELECT_SCALE) / 2
    SELECT_POS_X = max(half_w, min(cw - half_w, SELECT_POS_X))
    SELECT_POS_Y = max(half_h, min(ch - half_h, SELECT_POS_Y))

    # ratking 애니메이션 타이머 업데이트 (ratking_frames 우선)
    global ratking_timer, ratking_frame
    try:
        dt = game_framework.frame_time
    except Exception:
        dt = 1.0 / 60.0
    ratking_timer += dt
    if ratking_timer >= 1.0 / RAT_FPS:
        ratking_timer -= 1.0 / RAT_FPS
        if len(ratking_frames) > 0:
            ratking_frame = (ratking_frame + 1) % len(ratking_frames)
        elif ratking_sheet is not None:
            ratking_frame = (ratking_frame + 1) % ratking_sheet.cols
        else:
            ratking_frame = (ratking_frame + 1) % 1


def draw():
    """화면에 모든 요소를 그립니다."""
    global toolbar_image, status_pane_image
    global test_image  # 테스트 이미지 전역 변수 사용 선언

    clear_canvas()

    canvas_width = get_canvas_width()
    canvas_height = get_canvas_height()

    game_world.draw()

    # ----------------------------------------------------
    # 단일 애니메이션(크게) 출력: 왼쪽 아래 박스 중심에 표시
    # ----------------------------------------------------
    try:
        # 큰 애니메이션을 SELECT_POS_X/Y 위치로 그려서 WASD로 이동 가능하게 함
        display_w = RAT_CLIP_W * ratking_preview_scale
        display_h = RAT_CLIP_H * ratking_preview_scale

        # SELECT_POS_X/Y는 프레임 중심 좌표로 사용되도록 init에서 설정됩니다.
        display_x = SELECT_POS_X if SELECT_POS_X is not None else (40 + display_w / 2)
        display_y = SELECT_POS_Y if SELECT_POS_Y is not None else (canvas_height - 120 - display_h / 2)

        if len(ratking_frames) > 0:
            img = ratking_frames[ratking_frame % len(ratking_frames)]
            img.draw(display_x, display_y, display_w, display_h)
        elif ratking_sheet is not None:
            idx = ratking_frame % (ratking_sheet.cols if ratking_sheet else 1)
            ratking_sheet.draw_frame(idx, display_x, display_y, display_w, display_h)
        else:
            pass
    except Exception:
        pass

    # --- UI 높이 설정 ---
    display_toolbar_height = TOOLBAR_H * 2
    # 상태창 세로 크기에 스케일 적용
    display_status_pane_height = STATUS_PANE_H * STATUS_PANE_SCALE
    BOTTOM_PADDING = 10

    # ----------------------------------------------------
    # 🚨 UI 위치 교체 수정 시작 🚨
    # ----------------------------------------------------

    # 1. 상태 창 그리기 (상단 중앙 배치)
    if status_pane_image is not None:
        # 🚨 상단 위치로 변경 🚨
        status_pane_center_y = canvas_height - (display_status_pane_height / 2)
        status_pane_image.draw(
            canvas_width / 2,
            status_pane_center_y,
            canvas_width,
            display_status_pane_height
        )

    # 2. 툴바 그리기 (하단 중앙 배치)
    if toolbar_image is not None:
        # 🚨 하단 위치로 변경 🚨
        toolbar_center_y = (display_toolbar_height / 2) + BOTTOM_PADDING
        toolbar_image.draw(
            canvas_width / 2,
            toolbar_center_y,
            canvas_width,
            display_toolbar_height
        )

    # ----------------------------------------------------
    # 🚨 UI 위치 교체 수정 완료 🚨
    # ----------------------------------------------------

    # 상태 텍스트 표시 (FPS 및 모드 정보)
    draw_status_text(canvas_width, canvas_height)

    update_canvas()


def draw_status_text(canvas_width, canvas_height):
    """상태 텍스트를 화면에 그립니다. (상단 상태 창 아래에 배치)"""
    global SINGLE_FRAME_MODE, SELECT_FRAME_INDEX, SELECT_SCALE

    # 상단에 위치한 상태 창(Status Pane) 영역 바로 아래에 텍스트를 배치합니다.
    # STATUS_PANE_SCALE에 맞춰 위치 보정
    status_pane_height = STATUS_PANE_H * STATUS_PANE_SCALE

    # 텍스트가 상태 창 바로 아래에 위치하도록 조정
    base_y = canvas_height - status_pane_height - 10
    line_height = 20

    # 상태 텍스트 생성
    mode_text = "모드: " + ("단일 프레임 모드" if SINGLE_FRAME_MODE else "전체 프레임 모드")
    frame_text = f"프레임: {SELECT_FRAME_INDEX} / 스케일: {SELECT_SCALE:.1f}"

    # 텍스트 그리기
    draw_text(mode_text, canvas_width // 2, base_y, align="center")
    draw_text(frame_text, canvas_width // 2, base_y - line_height, align="center")


def draw_text(text, x, y, align="left"):
    """주어진 텍스트를 주어진 위치에 그립니다."""
    # init()에서 로드한 캐시 폰트 사용(없으면 조용히 리턴)
    global _cached_font
    font = globals().get('_cached_font', None)
    if font is None:
        return

    text_width = font.get_text_width(text)
    text_height = font.get_text_height(text)

    if align == "center":
        x -= text_width // 2

    # 텍스트 배경 사각형 그리기 (가독성을 위해)
    try:
        # pico2d 모듈을 직접 사용해 사각형을 그림
        pico2d.draw_rectangle(x - 2, y - text_height, x + text_width + 2, y + 2)
    except Exception:
        pass

    # 텍스트 그리기
    try:
        font.draw(x, y, text, (255, 255, 255))
    except Exception:
        pass


def draw_rectangle(x1, y1, x2, y2, color=None):
    """사각형을 그립니다. (pico2d.draw_rectangle 래퍼)"""
    try:
        pico2d.draw_rectangle(x1, y1, x2, y2)
    except Exception:
        pass


def pause():
    pass


def resume():
    pass