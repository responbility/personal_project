from pico2d import *
import game_world

# 맵의 폭과 타일 크기 정의
TILE_SIZE = 16  # 타일 하나의 픽셀 크기 (16x16 가정)
MAP_WIDTH = 1600  # 맵 전체의 가상 너비 (기존 코드와 일치시킴)
MAP_HEIGHT = 50  # 바닥 레이어의 높이 (기존 코드와 일치시킴)

# --- 선택된 타일의 클리핑 좌표 (tiles_prison.png 기준) ---
# 예시: 이미지 왼쪽 아래에서 (48, 48)에 위치한 16x16 크기의 벽돌 바닥 타일
TILE_LEFT = 48
TILE_BOTTOM = 48
TILE_WIDTH = TILE_SIZE
TILE_HEIGHT = TILE_SIZE


# --------------------------------------------------------

class TileFloor:
    def __init__(self):
        # 🚨 이 경로가 정확한지 확인하세요. 🚨
        try:
            self.image = load_image('assets/tiles_prison.png')
        except:
            print("경고: assets/tiles_prison.png 파일을 로드할 수 없습니다.")
            self.image = None

        # 맵의 너비에 필요한 타일 개수를 계산합니다.
        self.tile_count = MAP_WIDTH // TILE_SIZE

        # 바닥이 그려질 y 좌표 (타일 높이의 절반)
        # 기존 Grass의 중심 Y는 30이었으나, 타일 기반으로 0부터 채우기 위해 조정합니다.
        self.floor_y = MAP_HEIGHT // 2  # 바닥 레이어 중심 Y

    def update(self):
        pass

    def draw(self):
        if self.image is None:
            return

        # 맵 폭 전체에 걸쳐 타일을 반복해서 그립니다.
        for i in range(self.tile_count):
            # 캔버스에서 타일이 그려질 중심 X 좌표 계산
            # i * TILE_SIZE는 시작 X 좌표, + (TILE_SIZE / 2)는 중심 X 좌표
            draw_x = (i * TILE_SIZE) + (TILE_SIZE // 2)

            # 타일을 그립니다.
            self.image.clip_draw(
                TILE_LEFT, TILE_BOTTOM, TILE_WIDTH, TILE_HEIGHT,  # 타일셋 클리핑 정보
                draw_x, self.floor_y,  # 캔버스 상의 위치
                TILE_SIZE, TILE_SIZE  # 캔버스 상의 크기
            )

    def get_bb(self):
        # 바닥의 Bounding Box를 반환합니다.
        # 기존 코드와 동일한 맵 영역을 커버합니다.
        return 0, 0, MAP_WIDTH - 1, MAP_HEIGHT


def hande_collision(group, other):
    # 충돌 처리는 기존 로직을 유지합니다.
    if group == 'boy:ball':
        # 볼과 충돌 시 처리 로직
        pass
    elif group == 'boy:floor':
        # 소년(Boy)과 바닥(TileFloor)이 충돌했을 때 멈추는 로직
        if hasattr(other, 'stopped'):
            other.stopped = True
        pass