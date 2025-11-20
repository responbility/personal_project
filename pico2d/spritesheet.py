from pico2d import load_image
import os


class SpriteSheet:
    """
    스프라이트 시트를 로드하고 프레임 인덱스에 따라 원하는 부분을 그려주는 유틸리티 클래스입니다.
    """

    def __init__(self, image_path, clip_w, clip_h):
        # image_path may be relative to project root; try module-relative assets folder if not found
        resolved = image_path
        try:
            if not os.path.isfile(resolved):
                base_assets = os.path.join(os.path.dirname(__file__), 'assets')
                candidate = os.path.join(base_assets, image_path)
                if os.path.isfile(candidate):
                    resolved = candidate
                else:
                    # if image_path already contains 'assets/', try stripping it
                    candidate2 = os.path.join(base_assets, os.path.basename(image_path))
                    if os.path.isfile(candidate2):
                        resolved = candidate2
        except Exception:
            pass

        try:
            self.image = load_image(resolved)
            print(f"DEBUG: SpriteSheet loaded: {resolved}")
        except Exception as e:
            print(f"ERROR: SpriteSheet failed to load '{image_path}' -> tried '{resolved}': {e}")
            raise
        self.clip_w = clip_w
        self.clip_h = clip_h
        self.cols = self.image.w // clip_w
        self.rows = self.image.h // clip_h

    def draw_frame(self, index, x, y, target_w, target_h, flip=False, rotate=0):
        """
        주어진 인덱스에 해당하는 프레임을 캔버스에 그립니다.

        :param index: 0부터 시작하는 프레임 인덱스 (왼쪽 위에서 오른쪽 아래로)
        :param x: 캔버스 X 좌표
        :param y: 캔버스 Y 좌표
        :param target_w: 그릴 너비
        :param target_h: 그릴 높이
        :param flip: 좌우 반전 여부
        :param rotate: 회전 각도 (라디안)
        """

        # 클립 영역 계산 (pico2d는 왼쪽 아래를 0,0으로 간주)
        col = index % self.cols
        row = index // self.cols

        # clip_draw는 왼쪽 아래를 기준으로 클립 영역의 Y 시작점을 계산해야 합니다.
        # 이미지 전체 높이 - (현재 행 * 클립 높이) - 클립 높이
        clip_x = col * self.clip_w
        clip_y = self.image.h - (row * self.clip_h) - self.clip_h

        # rotate는 라디안으로 들어올 수 있으므로, pico2d의 clip_composite_draw는 degree 단위를 사용합니다.
        # 변환: degree = rotate * (180.0 / pi)
        try:
            from math import degrees
            deg = degrees(rotate)
        except Exception:
            deg = 0

        if flip:
            # 좌우 반전은 clip_composite_draw의 flip 파라미터에 'h'를 전달
            try:
                self.image.clip_composite_draw(clip_x, clip_y, self.clip_w, self.clip_h, deg, 'h', x, y, target_w, target_h)
            except Exception:
                # clip_composite_draw가 없으면 fallback으로 그냥 clip_draw
                self.image.clip_draw(clip_x, clip_y, self.clip_w, self.clip_h, x, y, target_w, target_h)
        else:
            # 일반적으로는 clip_draw 사용
            self.image.clip_draw(clip_x, clip_y, self.clip_w, self.clip_h, x, y, target_w, target_h)
