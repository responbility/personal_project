import game_framework
from pico2d import *
import title_mode

name = "PlayMode"
character_x, character_y = 576 // 2, 1024 // 2
character_image = None
toolbar_image = None
status_pane_image = None

# UI 이미지의 추정된 원본 크기
TOOLBAR_W, TOOLBAR_H = 576, 50
STATUS_PANE_W, STATUS_PANE_H = 576, 80


def init():
    """게임 플레이 모드를 초기화하고 이미지를 로드합니다."""
    global character_image, toolbar_image, status_pane_image

    try:
        # 캐릭터 이미지 로드 (기존 로직 유지)
        character_image = load_image('assets/avatars.png')
    except:
        print("경고: assets/avatars.png 파일을 로드할 수 없습니다.")
        character_image = None

    try:
        # 툴바 이미지 로드
        toolbar_image = load_image('assets/toolbar.png')
    except:
        print("경고: assets/toolbar.png 파일을 로드할 수 없습니다.")
        toolbar_image = None

    try:
        # 상태 창 이미지 로드
        status_pane_image = load_image('assets/status_pane.png')
    except:
        print("경고: assets/status_pane.png 파일을 로드할 수 없습니다.")
        status_pane_image = None

    print("Play Mode Started: UI/Character Loaded")


def finish():
    """모드 종료 시 리소스를 해제합니다."""
    global character_image, toolbar_image, status_pane_image
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
    pass


def draw():
    """화면에 모든 요소를 그립니다."""
    global character_image, toolbar_image, status_pane_image
    clear_canvas()

    canvas_width = get_canvas_width()
    canvas_height = get_canvas_height()

    # 1. 메인 캐릭터 그리기 (임시)
    if character_image is not None:
        # 캔버스 중앙에 배치
        character_image.clip_draw(0, 0, 32, 32, character_x, character_y)

    # 2. 툴바 그리기 (상단 중앙 배치)
    if toolbar_image is not None:
        # 툴바의 중심 Y 좌표 계산: 캔버스 높이 - (툴바 높이 / 2)
        toolbar_center_y = canvas_height - (TOOLBAR_H / 2)

        # 툴바 이미지 전체를 캔버스 너비와 툴바 높이에 맞게 늘려 그립니다.
        toolbar_image.draw(
            canvas_width / 2,  # X: 중앙에 위치
            toolbar_center_y,  # Y: 상단에 위치
            canvas_width,  # W: 캔버스 너비에 맞춤 (576)
            TOOLBAR_H  # H: 원본 높이 (50)
        )

    # 3. 상태 창 그리기 (하단 중앙 배치)
    if status_pane_image is not None:
        # 상태 창의 중심 Y 좌표 계산: (상태 창 높이 / 2)
        status_pane_center_y = STATUS_PANE_H / 2

        # 상태 창 이미지 전체를 캔버스 너비와 상태 창 높이에 맞게 늘려 그립니다.
        status_pane_image.draw(
            canvas_width / 2,  # X: 중앙에 위치
            status_pane_center_y,  # Y: 하단에 위치
            canvas_width,  # W: 캔버스 너비에 맞춤 (576)
            STATUS_PANE_H  # H: 원본 높이 (80)
        )

    update_canvas()


def pause(): pass


def resume(): pass