from pico2d import load_image


class SpriteSheet:
    """
    스프라이트 시트를 로드하고 프레임 인덱스에 따라 원하는 부분을 그려주는 유틸리티 클래스입니다.
    """

    def __init__(self, image_path, clip_w, clip_h):
        self.image = load_image(image_path)
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

        if flip:
            # clip_draw_to_center_x, y, w, h, x, y, w, h
            self.image.clip_draw_to_center(
                clip_x, clip_y, self.clip_w, self.clip_h,
                x, y, target_w, target_h,
                flip='h'
            )
        else:
            self.image.draw_clip(
                clip_x, clip_y, self.clip_w, self.clip_h,
                x, y, target_w, target_h
            )