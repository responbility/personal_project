from pico2d import *
import game_framework
import title_mode
import game_world
import play_mode_2
from ratking import Ratking
from guard import Guard  # 경비원 추가 임포트

# 가상 전체 맵 크기 정의
MAP_WIDTH = 1500
MAP_HEIGHT = 900

name = "PlayMode"

# 전역 배경 참조 (Ratking에서 카메라 좌표를 읽기 위함)
bg = None


# 배경 클래스
class Background:
    def __init__(self, ratking):
        global bg
        print('[Background] created')
        self.image = load_image('assets/map.jpg')
        self.canvas_width = get_canvas_width()
        self.canvas_height = get_canvas_height()

        # 카메라가 추적할 Ratking 객체 참조
        self.ratking = ratking

        # 카메라(윈도우)의 좌측 하단 월드 좌표
        self.window_left = 0
        self.window_bottom = 0

        # 전역으로도 보관 (ratking.py 에서 play_mode.bg.window_left 사용)
        bg = self

    def update(self):
        # Ratking을 화면 중앙에 두려고 하는 카메라 위치 계산
        half_w = self.canvas_width // 2
        half_h = self.canvas_height // 2

        from pico2d import clamp
        # 맵 전체 크기(MAP_WIDTH, MAP_HEIGHT)를 벗어나지 않도록 클램프
        MAP_W, MAP_H = MAP_WIDTH, MAP_HEIGHT

        self.window_left = clamp(0, int(self.ratking.x) - half_w, MAP_W - self.canvas_width)
        self.window_bottom = clamp(0, int(self.ratking.y) - half_h, MAP_H - self.canvas_height)

    def draw(self):
        # 스크롤 없이, map.jpg 전체를 화면에 꽉 차게 그리기
        self.image.draw(self.canvas_width // 2,
                        self.canvas_height // 2,
                        self.canvas_width,
                        self.canvas_height)


# 전역 상태
ratking_instance = None
guard_instance = None


def init():
    print('PlayMode init')


def enter():
    """월드 초기화 + 배경 + ratking + guard 등록"""
    global ratking_instance, bg, guard_instance
    print('PlayMode enter')

    game_world.init()

    # Ratking 먼저 생성 (Background가 참조하도록)
    ratking_instance = Ratking()

    # Guard 생성: Ratking을 추적하도록 target으로 넘김
    guard_instance = Guard(x=800, y=400, target=ratking_instance)

    # 0번 레이어: 배경 (Ratking 참조 전달)
    background = Background(ratking_instance)
    game_world.add_object(background, 0)

    # 1번 레이어: ratking과 guard
    game_world.add_object(ratking_instance, 1)
    game_world.add_object(guard_instance, 1)


def exit():
    global ratking_instance, bg, guard_instance
    print('PlayMode exit')
    game_world.clear()
    ratking_instance = None
    guard_instance = None
    bg = None


def finish():
    pass


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


def update():
    game_world.update()


def draw_ui():
    # 간단한 UI 텍스트 (왼쪽 아래에 모드 이름 표시)
    draw_text = getattr(pico2d, 'draw_text', None)
    if draw_text is not None:
        draw_text('PLAY MODE', 10, 10)


def draw():
    clear_canvas()
    game_world.draw()
    # 필요하다면 UI 호출 가능
    # draw_ui()
    update_canvas()
