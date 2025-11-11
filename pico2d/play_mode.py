# play_mode.py

import game_framework
from pico2d import *

# title_mode로 돌아가기 위해 임포트
import title_mode

name = "PlayMode"
character_image = None
character_x, character_y = 640, 512


def init():
    global character_image
    # 'avatars.png'를 캐릭터 스프라이트 시트로 사용 (경로 수정 필요)
    try:
        character_image = load_image('assets/avatars.png')
    except:
        character_image = None
    print("Play Mode Started: Character Loaded")


def finish():
    global character_image
    del character_image
    print("Play Mode Finished: Character Unloaded")


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                # ESC 키를 누르면 타이틀 화면으로 돌아감 (mode change)
                game_framework.change_mode(title_mode)
            # TODO: 여기에 캐릭터 이동/점프 등 게임 로직 추가


def update():
    # 게임의 상태 변화 로직 (예: 캐릭터 이동, 물리 계산)
    pass


def draw():
    global character_image
    clear_canvas()

    # 1. 배경 (간단하게 검은색)
    # 2. 캐릭터 그리기
    if character_image is not None:
        # avatars.png에서 특정 스프라이트(예: 첫 번째 캐릭터)를 잘라서 그립니다.
        # avatars.png가 그리드 형태라고 가정하고, (0, 0) 위치의 32x32 픽셀을 그립니다.
        character_image.clip_draw(0, 0, 32, 32, character_x, character_y)

    update_canvas()


def pause(): pass


def resume(): pass