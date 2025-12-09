from pico2d import *
import game_framework
import title_mode
import game_world
from ratking import Ratking

name = "PlayMode2"


# 배경 스크롤링 맵
class Map:
    def __init__(self):
        print("[Map] created")

        import os
        if os.path.exists('assets/map2.jpg'):
            path = 'assets/map2.jpg'
        else:
            path = 'assets/map.jpg'

        self.image = load_image(path)

        self.w = self.image.w   # 맵 전체 폭
        self.h = self.image.h   # 맵 전체 높이

        self.cw = get_canvas_width()
        self.ch = get_canvas_height()

        self.window_left = 0
        self.window_bottom = 0

    def update(self):
        global ratking_instance
        rk = ratking_instance

        # window_left / bottom = Ratking 중심
        self.window_left = clamp(0, int(rk.x) - self.cw // 2, self.w - self.cw)
        self.window_bottom = clamp(0, int(rk.y) - self.ch // 2, self.h - self.ch)

    def draw(self):
        # 클리핑으로 화면 영역만 그리기
        self.image.clip_draw_to_origin(
            self.window_left,
            self.window_bottom,
            self.cw,
            self.ch,
            0, 0
        )


# 전역 상태
ratking_instance = None
map_instance = None


def init():
    print('PlayMode2 init')


def enter():
    global ratking_instance, map_instance
    print('PlayMode2 enter')

    game_world.init()

    map_instance = Map()
    game_world.add_object(map_instance, 0)

    ratking_instance = Ratking(400, 300)
    game_world.add_object(ratking_instance, 1)


def exit():
    global ratking_instance, map_instance
    print('PlayMode2 exit')
    game_world.clear()
    ratking_instance = None
    map_instance = None


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
            ratking_instance.handle_event(event)


def update():
    game_world.update()


def draw():
    clear_canvas()

    # (1) 맵부터 그린다
    map_instance.draw()

    # (2) Ratking은 화면 중앙에 그려야 한다 = screen_x, screen_y 설정
    ratking_instance.screen_x = get_canvas_width() // 2
    ratking_instance.screen_y = get_canvas_height() // 2

    # (3) 나머지 draw 실행
    game_world.draw()

    update_canvas()
