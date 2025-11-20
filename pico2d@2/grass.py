# grass.py

from pico2d import *
import game_world

# 맵의 폭과 높이 (충돌 영역에 사용됨)
MAP_WIDTH = 1600
MAP_HEIGHT = 50

class Grass:
    def __init__(self):
        # 🚨 이미지 파일 경로를 'assets/prison_exit.png'로 최종 설정합니다. 🚨
        try:
            self.image = load_image('assets/prison_exit.png')
            print("INFO: assets/prison_exit.png 파일을 성공적으로 로드했습니다.")
        except:
            # 파일 로드 실패 시 경고 출력 및 self.image를 None으로 설정
            print("경고: assets/prison_exit.png 파일을 로드할 수 없습니다. 경로를 확인하세요.")
            self.image = None

    def update(self):
        pass

    def draw(self):
        # 이미지가 성공적으로 로드된 경우에만 그리기 작업을 수행합니다.
        if self.image is None:
            return

        canvas_width = get_canvas_width()
        canvas_height = get_canvas_height()

        # 🌟 단일 배경 이미지를 캔버스 전체에 맞게 늘려서 그립니다. 🌟
        # draw_to_origin(x, y, w, h)를 사용하여 (0, 0)부터 캔버스 전체를 덮도록 합니다.
        self.image.draw_to_origin(
            0,                      # X 좌표 시작점 (왼쪽 아래)
            0,                      # Y 좌표 시작점 (왼쪽 아래)
            canvas_width,           # 캔버스 너비만큼 늘려 그림
            canvas_height           # 캔버스 높이만큼 늘려 그림
        )

    def get_bb(self):
        # 바닥의 Bounding Box를 반환합니다.
        return 0, 0, MAP_WIDTH - 1, MAP_HEIGHT


def hande_collision(group, other):
    if group == 'boy:ball':
        pass
    elif group == 'boy:floor':
        if hasattr(other, 'stopped'):
            other.stopped = True
        pass