from pico2d import *
import game_framework
import title_mode
import game_world
from ratking import Ratking
from guard import Guard

# 가상 전체 맵 크기
MAP_WIDTH = 1500
MAP_HEIGHT = 900

name = "PlayMode"

# 전역 배경 참조
bg = None

# HUD 이미지
status_pane_image = None
toolbar_image = None


# -----------------------------
# 배경 클래스
# -----------------------------
class Background:
    def __init__(self, ratking):
        global bg
        print('[Background] created')

        self.image = load_image('assets/map.jpg')
        self.canvas_width = get_canvas_width()
        self.canvas_height = get_canvas_height()

        self.ratking = ratking

        self.window_left = 0
        self.window_bottom = 0

        # 다른 파일에서도 접근 가능하도록 저장
        bg = self

    def update(self):
        half_w = self.canvas_width // 2
        half_h = self.canvas_height // 2

        from pico2d import clamp

        self.window_left = clamp(
            0,
            int(self.ratking.x) - half_w,
            MAP_WIDTH - self.canvas_width
        )

        self.window_bottom = clamp(
            0,
            int(self.ratking.y) - half_h,
            MAP_HEIGHT - self.canvas_height
        )

    def draw(self):
        # 스크롤 없이 전체 맵을 화면에 표시
        self.image.draw(
            self.canvas_width // 2,
            self.canvas_height // 2,
            self.canvas_width,
            self.canvas_height
        )


# -----------------------------
# 전역 상태
# -----------------------------
ratking_instance = None
guard_instance = None


# -----------------------------
# 초기화 함수
# -----------------------------
def init():
    print('PlayMode init')


# -----------------------------
# 모드 진입
# -----------------------------
def enter():
    global ratking_instance, guard_instance
    global status_pane_image, toolbar_image

    print('PlayMode enter')

    game_world.init()

    # HUD 이미지 로드
    # 참고: UIManager.py와 play_mode.py에서 로드하는 이미지 경로가 다릅니다.
    # UIManager: 'status_pane.png', 'toolbar.png'
    # play_mode: 'assets/status_pane.png', 'assets/toolbar.png'
    # 현재 코드에서는 play_mode 경로를 사용합니다.
    if status_pane_image is None:
        try:
            status_pane_image = load_image('assets/status_pane.png')
        except Exception as e:
            print(f"[HUD] status_pane.png 로드 실패: {e}")

    if toolbar_image is None:
        try:
            toolbar_image = load_image('assets/toolbar.png')
        except Exception as e:
            print(f"[HUD] toolbar.png 로드 실패: {e}")

    # Ratking 생성
    ratking_instance = Ratking()

    # Guard 생성 (Ratking 추적)
    guard_instance = Guard(x=800, y=400, target=ratking_instance)

    # 배경 생성
    background = Background(ratking_instance)
    game_world.add_object(background, 0)

    # ratking 및 guard 추가
    game_world.add_object(ratking_instance, 1)
    game_world.add_object(guard_instance, 1)


# -----------------------------
# 모드 종료 처리
# -----------------------------
def exit():
    global ratking_instance, guard_instance, bg
    print('PlayMode exit')
    game_world.clear()
    ratking_instance = None
    guard_instance = None
    bg = None


def finish():
    pass


# -----------------------------
# 이벤트 처리
# -----------------------------
def handle_events():
    global ratking_instance
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
        else:
            if ratking_instance:
                ratking_instance.handle_event(event)


# -----------------------------
# 업데이트
# -----------------------------
def update():
    game_world.update()


# -----------------------------
# 화면 그리기
# -----------------------------
from pico2d import *
import game_framework
import title_mode
import game_world
from ratking import Ratking
from guard import Guard

# 가상 전체 맵 크기
MAP_WIDTH = 1500
MAP_HEIGHT = 900

name = "PlayMode"

# 전역 배경 참조
bg = None

# HUD 이미지
status_pane_image = None
toolbar_image = None


# -----------------------------
# 배경 클래스
# -----------------------------
class Background:
    def __init__(self, ratking):
        global bg
        print('[Background] created')

        self.image = load_image('assets/map.jpg')
        self.canvas_width = get_canvas_width()
        self.canvas_height = get_canvas_height()

        self.ratking = ratking

        self.window_left = 0
        self.window_bottom = 0

        # 다른 파일에서도 접근 가능하도록 저장
        bg = self

    def update(self):
        half_w = self.canvas_width // 2
        half_h = self.canvas_height // 2

        from pico2d import clamp

        self.window_left = clamp(
            0,
            int(self.ratking.x) - half_w,
            MAP_WIDTH - self.canvas_width
        )

        self.window_bottom = clamp(
            0,
            int(self.ratking.y) - half_h,
            MAP_HEIGHT - self.canvas_height
        )

    def draw(self):
        # 스크롤 없이 전체 맵을 화면에 표시
        self.image.draw(
            self.canvas_width // 2,
            self.canvas_height // 2,
            self.canvas_width,
            self.canvas_height
        )


# -----------------------------
# 전역 상태
# -----------------------------
ratking_instance = None
guard_instance = None


# -----------------------------
# 초기화 함수
# -----------------------------
def init():
    print('PlayMode init')


# -----------------------------
# 모드 진입
# -----------------------------
def enter():
    global ratking_instance, guard_instance
    global status_pane_image, toolbar_image

    print('PlayMode enter')

    game_world.init()

    # HUD 이미지 로드
    # 참고: UIManager.py와 play_mode.py에서 로드하는 이미지 경로가 다릅니다.
    # UIManager: 'status_pane.png', 'toolbar.png'
    # play_mode: 'assets/status_pane.png', 'assets/toolbar.png'
    # 현재 코드에서는 play_mode 경로를 사용합니다.
    if status_pane_image is None:
        try:
            status_pane_image = load_image('assets/status_pane.png')
        except Exception as e:
            print(f"[HUD] status_pane.png 로드 실패: {e}")

    if toolbar_image is None:
        try:
            toolbar_image = load_image('assets/toolbar.png')
        except Exception as e:
            print(f"[HUD] toolbar.png 로드 실패: {e}")

    # Ratking 생성
    ratking_instance = Ratking()

    # Guard 생성 (Ratking 추적)
    guard_instance = Guard(x=800, y=400, target=ratking_instance)

    # 배경 생성
    background = Background(ratking_instance)
    game_world.add_object(background, 0)

    # ratking 및 guard 추가
    game_world.add_object(ratking_instance, 1)
    game_world.add_object(guard_instance, 1)


# -----------------------------
# 모드 종료 처리
# -----------------------------
def exit():
    global ratking_instance, guard_instance, bg
    print('PlayMode exit')
    game_world.clear()
    ratking_instance = None
    guard_instance = None
    bg = None


def finish():
    pass


# -----------------------------
# 이벤트 처리
# -----------------------------
def handle_events():
    global ratking_instance
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
        else:
            if ratking_instance:
                ratking_instance.handle_event(event)


# -----------------------------
# 업데이트
# -----------------------------
def update():
    game_world.update()



def draw():
    clear_canvas()

    game_world.draw()

    # HUD 그리기
    global status_pane_image, toolbar_image
    w, h = get_canvas_width(), get_canvas_height()

    # ---------------------------------------------
    # ✅ 이미지 확대 설정 (여기를 수정)
    scale_factor = 1.5  # 1.5배 확대

    # 툴바를 화면 맨 아래에서 띄울 간격 (픽셀) 설정
    # Note: 툴바 자체의 크기가 커지므로, offset_y 값도 조절이 필요할 수 있습니다.
    toolbar_offset_y = 50
    # ---------------------------------------------

    # 1. status_pane 화면 맨 위 (확대 적용)
    if status_pane_image:
        # 확대된 너비와 높이 계산
        status_width_scaled = status_pane_image.w * scale_factor
        status_height_scaled = status_pane_image.h * scale_factor

        status_pane_image.draw(
            w // 2,
            h - status_height_scaled // 2,  # 높이가 커진 만큼 Y좌표도 조정
            status_width_scaled,
            status_height_scaled
        )

    # 2. toolbar는 화면 맨 아래에서 띄워서 배치 (확대 적용)
    if toolbar_image:
        # 확대된 너비와 높이 계산
        toolbar_width_scaled = toolbar_image.w * scale_factor
        toolbar_height_scaled = toolbar_image.h * scale_factor

        toolbar_image.draw(
            w // 2,
            toolbar_height_scaled // 2 + toolbar_offset_y,  # 높이가 커진 만큼 Y좌표 조정
            toolbar_width_scaled,
            toolbar_height_scaled
        )

    update_canvas()