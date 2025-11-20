# grass.py

from pico2d import *
import game_world
import os

# 맵의 폭과 높이 (충돌 영역에 사용됨)
MAP_WIDTH = 1600
MAP_HEIGHT = 50

class Grass:
    def __init__(self):
        # 우선: 사용자가 제공한 경로에서 MAX.PNG 로드 시도
        self.image = None
        self.image_path = None
        self.pil_w = None
        self.pil_h = None
        self.border_image_pixels = None  # list of (x,y) in image space (top-left origin)
        possible_paths = []
        try:
            # 절대 경로(사용자 제공 위치)
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '소녀픽셀던전', 'gpd_040_B1(1)', 'assets'))
            possible_paths.append(os.path.join(base, 'MAX.PNG'))
            possible_paths.append(os.path.join(base, 'max.png'))
        except Exception:
            pass

        # 프로젝트의 assets 폴백
        possible_paths.append(os.path.join(os.path.dirname(__file__), 'assets', 'prison_exit.png'))
        possible_paths.append(os.path.join(os.path.dirname(__file__), 'assets', 'MAX.PNG'))

        loaded = False
        for p in possible_paths:
            try:
                if os.path.isfile(p):
                    # 이미지 로드
                    self.image = load_image(p)
                    self.image_path = p
                    print(f"INFO: Grass map loaded from: {p}")
                    loaded = True
                    # 시도: Pillow로 열어 알파 기반 경계 추출
                    try:
                        try:
                            from PIL import Image
                        except Exception:
                            Image = None
                        if Image is not None:
                            pil_img = Image.open(p).convert('RGBA')
                        else:
                            pil_img = None
                        if pil_img is not None:
                            self.pil_w, self.pil_h = pil_img.size
                            alpha = pil_img.split()[3]
                            alpha_data = alpha.load()
                            # 인스턴스에 저장하여 나중에 충돌 판정에 사용
                            self._pil_img = pil_img
                            self.alpha_data = alpha_data
                        else:
                            alpha_data = None
                        border_pixels = []
                        # 테두리 픽셀: 비투명 픽 중 4-이웃 중 하나 이상이 투명한 픽
                        if alpha_data is not None:
                            for iy in range(self.pil_h):
                                for ix in range(self.pil_w):
                                    try:
                                        if alpha_data[ix, iy] != 0:
                                            # check neighbors
                                            is_border = False
                                            for nx, ny in ((ix-1, iy), (ix+1, iy), (ix, iy-1), (ix, iy+1)):
                                                if nx < 0 or ny < 0 or nx >= self.pil_w or ny >= self.pil_h:
                                                    is_border = True
                                                    break
                                                if alpha_data[nx, ny] == 0:
                                                    is_border = True
                                                    break
                                            if is_border:
                                                border_pixels.append((ix, iy))
                                    except Exception:
                                        continue
                        # 중복 제거 및 저장
                        if border_pixels:
                            # downsample a bit to avoid too many points
                            self.border_image_pixels = border_pixels
                            print(f"INFO: Extracted {len(border_pixels)} border pixels from {p}")
                    except Exception as e:
                        # Pillow not available or failed -> keep border_image_pixels = None
                        # print a small notice but don't fail
                        print(f"INFO: Pillow border extraction skipped or failed: {e}")
                    break
            except Exception:
                pass

        if not loaded:
            # 최종 폴백: try relative asset name
            try:
                self.image = load_image('assets/prison_exit.png')
                print("INFO: Grass map loaded from assets/prison_exit.png (fallback).")
                loaded = True
            except Exception:
                print("경고: 그라스 맵 이미지를 로드할 수 없습니다. 경로를 확인하세요.")
                self.image = None
                self._pil_img = None
                self.alpha_data = None

    def update(self):
        pass

    def draw(self):
        # 이미지가 성공적으로 로드된 경우에만 그리기 작업을 수행합니다.
        if self.image is None:
            return

        canvas_width = get_canvas_width()
        canvas_height = get_canvas_height()

        # 전체 캔버스를 덮도록 원점(0,0)에서 그림
        try:
            self.image.draw_to_origin(0, 0, canvas_width, canvas_height)
        except Exception:
            # draw_to_origin가 없으면 일반 draw로 중앙에 맞춰 그림
            self.image.draw(canvas_width // 2, canvas_height // 2, canvas_width, canvas_height)

    def get_bb(self):
        # 바닥의 Bounding Box를 반환합니다.
        return 0, 0, MAP_WIDTH - 1, MAP_HEIGHT

    def get_border_points(self, canvas_w, canvas_h, step=16):
        """
        MAX.PNG(또는 로드된 이미지)가 화면에 표시되는 영역의 테두리 점 리스트를 반환합니다.
        현재 구현은 이미지가 캔버스 전체에 맞춰 그려졌다고 가정하고
        캔버스 사각형의 테두리 포인트(일정 간격)를 반환합니다.
        반환값: [(x1,y1), (x2,y2), ...]
        """
        points = []
        if canvas_w <= 0 or canvas_h <= 0:
            return points

        # 우선: PIL 기반 테두리 픽셀이 있으면 그것을 캔버스 스케일로 매핑
        if self.border_image_pixels and self.pil_w and self.pil_h:
            sx = float(canvas_w) / float(self.pil_w)
            sy = float(canvas_h) / float(self.pil_h)
            s = max(1, int(step))
            seen = set()
            for (ix, iy) in self.border_image_pixels:
                # 샘플링: 공간적으로 일정 간격으로만 추가
                if (ix % s != 0) and (iy % s != 0):
                    continue
                # map image-space (top-left origin) -> canvas-space (bottom-left origin for pico2d)
                cx = int(ix * sx)
                cy = int((self.pil_h - 1 - iy) * sy)
                if (cx, cy) not in seen:
                    seen.add((cx, cy))
                    points.append((cx, cy))
            return points

        # 폴백: 캔버스 전체 테두리 샘플링
        s = max(4, int(step))
        x = 0
        while x <= canvas_w:
            points.append((x, 0))
            points.append((x, canvas_h))
            x += s
        y = s
        while y < canvas_h:
            points.append((0, y))
            points.append((canvas_w, y))
            y += s
        return points

    def is_solid_at(self, canvas_x, canvas_y, canvas_w=None, canvas_h=None):
        """
        주어진 캔버스 좌표가 맵 이미지에서 불투명(벽) 픽셀인지 검사합니다.
        - canvas_w, canvas_h가 None이면 현재 캔버스 크기를 가져와 사용합니다.
        반환값: True(불투명/벽), False(투명/통과 가능)
        """
        try:
            if self.image is None:
                return False
            if getattr(self, 'alpha_data', None) is None:
                return False
            if canvas_w is None:
                canvas_w = get_canvas_width()
            if canvas_h is None:
                canvas_h = get_canvas_height()

            # clamp input
            if canvas_x < 0 or canvas_y < 0 or canvas_x > canvas_w or canvas_y > canvas_h:
                return False

            # map canvas -> image pixel coords
            ix = int(float(canvas_x) / float(canvas_w) * float(self.pil_w))
            iy = int(float(canvas_y) / float(canvas_h) * float(self.pil_h))
            # convert pico2d(bottom-left origin) canvas y to PIL top-left origin
            iy_img = self.pil_h - 1 - iy
            ix = max(0, min(self.pil_w - 1, ix))
            iy_img = max(0, min(self.pil_h - 1, iy_img))

            return self.alpha_data[ix, iy_img] != 0
        except Exception:
            return False


def hande_collision(group, other):
    if group == 'boy:ball':
        pass
    elif group == 'boy:floor':
        if hasattr(other, 'stopped'):
            other.stopped = True
        pass