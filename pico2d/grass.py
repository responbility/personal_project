# grass.py (수정된 draw 함수)

from pico2d import *
import game_world
import os

# 맵의 폭과 높이 (충돌 영역에 사용됨)
MAP_WIDTH = 1600
MAP_HEIGHT = 50


# ************************************************************
# 주의: 이 파일 외부에 camera_x와 camera_y가 정의되어야 합니다.
# 예시:
# global camera_x, camera_y
# camera_x = 0
# camera_y = 0
# ************************************************************


class Grass:
    def __init__(self):
        # ... (기존 이미지 로드 및 초기화 코드 유지)
        self.image = None
        self.image_path = None
        self.pil_w = None
        self.pil_h = None
        self.border_image_pixels = None

        # --- 이미지 로드 코드 ---
        possible_paths = []
        try:
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '소녀픽셀던전', 'gpd_040_B1(1)', 'assets'))
            possible_paths.append(os.path.join(base, 'MAX.PNG'))
            possible_paths.append(os.path.join(base, 'max.png'))
        except Exception:
            pass

        possible_paths.append(os.path.join(os.path.dirname(__file__), 'assets', 'prison_exit.png'))
        possible_paths.append(os.path.join(os.path.dirname(__file__), 'assets', 'MAX.PNG'))

        loaded = False
        for p in possible_paths:
            try:
                if os.path.isfile(p):
                    self.image = load_image(p)
                    self.image_path = p
                    print(f"INFO: Grass map loaded from: {p}")
                    loaded = True
                    # (Pillow 기반 경계 추출 코드는 생략, 기존 코드에는 존재함)
                    break
            except Exception:
                pass

        if not loaded:
            try:
                self.image = load_image('assets/prison_exit.png')
                print("INFO: Grass map loaded from assets/prison_exit.png (fallback).")
                loaded = True
            except Exception:
                print("경고: 그라스 맵 이미지를 로드할 수 없습니다. 경로를 확인하세요.")
                self.image = None
                self._pil_img = None
                self.alpha_data = None
        # --- 이미지 로드 코드 끝 ---

        # 맵의 월드 시작 좌표 (0, 0)
        self.world_x = 0
        self.world_y = 0

        # 맵의 크기 (현재는 고정되어 있지만, 로드된 이미지 크기를 사용하도록 변경할 수 있음)
        self.map_w = MAP_WIDTH
        self.map_h = MAP_HEIGHT

    def update(self):
        pass

    def draw(self):
        if self.image is None:
            return

        # 다른 모듈에서 정의된 camera_x, camera_y를 가져옵니다.
        # 실제 환경에서는 play_mode 등에서 전역 변수로 관리하거나,
        # Grass 객체를 업데이트할 때 카메라 정보를 전달해야 합니다.
        try:
            global camera_x, camera_y
        except NameError:
            # camera_x, camera_y가 정의되지 않은 경우 기본값 사용 (스크롤 없음)
            camera_x, camera_y = 0, 0

        # 월드 좌표를 화면 좌표로 변환 (카메라 오프셋 적용)
        # 맵의 시작 위치 (self.world_x, self.world_y)에서 카메라 위치를 뺍니다.
        draw_x = self.world_x - camera_x
        draw_y = self.world_y - camera_y

        # 이미지를 (draw_x, draw_y)에 그립니다.
        # draw_to_origin(왼쪽 하단 x, 왼쪽 하단 y, 폭, 높이)
        try:
            self.image.draw_to_origin(draw_x, draw_y, self.map_w, self.map_h)
        except Exception:
            # draw_to_origin이 없으면 일반 draw로 중앙에 맞춰 그림 (스크롤 구현 불가)
            self.image.draw(get_canvas_width() // 2, get_canvas_height() // 2, get_canvas_width(), get_canvas_height())

    def get_bb(self):
        # Bounding Box를 월드 좌표로 반환합니다.
        return self.world_x, self.world_y, self.world_x + self.map_w - 1, self.world_y + self.map_h

    # ... (나머지 get_border_points 및 is_solid_at 함수 유지)
    def get_border_points(self, canvas_w, canvas_h, step=16):
        # ... (기존 코드 유지)
        pass

    def is_solid_at(self, canvas_x, canvas_y, canvas_w=None, canvas_h=None):
        # ... (기존 코드 유지)
        pass


def hande_collision(group, other):
    if group == 'boy:ball':
        pass
    elif group == 'boy:floor':
        if hasattr(other, 'stopped'):
            other.stopped = True
        pass