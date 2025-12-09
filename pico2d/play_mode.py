from pico2d import *
import game_framework
import title_mode
import game_world
from ratking import Ratking

name = "PlayMode"

# 배경 클래스
class Background:
    def __init__(self):
        self.image = load_image('assets/map.jpg')
        self.canvas_width = get_canvas_width()
        self.canvas_height = get_canvas_height()

    def update(self):
        pass

    def draw(self):
        # 화면 전체에 배경을 꽉 채워서 그림
        self.image.draw(self.canvas_width // 2,
                        self.canvas_height // 2,
                        self.canvas_width,
                        self.canvas_height)

# 전역 상태 변수
ratking_instance = None


def init():
    print("PlayMode init")


def enter():
    """모드 진입 시: 월드 초기화 + 배경 + ratking 추가"""
    global ratking_instance
    print("PlayMode enter")

    game_world.init()

    # 배경 추가 (레이어 0)
    bg = Background()
    game_world.add_object(bg, 0)

    # ratking 추가 (레이어 1)
    ratking_instance = Ratking()
    game_world.add_object(ratking_instance, 1)


def exit():
    global ratking_instance
    print("PlayMode exit")
    game_world.clear()
    ratking_instance = None


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


def draw():
    clear_canvas()
    game_world.draw()
    update_canvas()
