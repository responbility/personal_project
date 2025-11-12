# spritesheet.py
# 간단한 스프라이트 시트 래퍼: 프레임 단위로 그리기 기능 제공
from pico2d import load_image

class SpriteSheet:
    def __init__(self, path, frame_w, frame_h, frames_per_row=None):
        # 이미지 로드(파일 경로 실패 시 예외 발생)
        self.image = load_image(path)
        self.frame_w = frame_w
        self.frame_h = frame_h

        # 이미지의 픽셀 너비/높이를 알 수 있으면 cols/rows 계산
        self.image_w = getattr(self.image, 'w', None)
        self.image_h = getattr(self.image, 'h', None)

        if frames_per_row is not None:
            self.cols = frames_per_row
        else:
            if self.image_w:
                self.cols = max(1, self.image_w // frame_w)
            else:
                self.cols = 1

        if self.image_h:
            self.rows = max(1, (self.image_h + frame_h - 1) // frame_h)
        else:
            self.rows = 1

    def draw_frame(self, frame_index, x, y, target_w=None, target_h=None, flip=False, rotate=0):
        """
        frame_index: 0-based 프레임 인덱스
        x,y: 화면상의 중심 좌표
        target_w/target_h: 출력 크기(지정하지 않으면 원본 클립 크기 사용)
        flip: 좌우 반전 여부 (True -> 'h' 사용)
        rotate: 라디안 단위 회전각
        """
        if target_w is None:
            target_w = self.frame_w
        if target_h is None:
            target_h = self.frame_h

        col = int(frame_index) % self.cols
        row = int(frame_index) // self.cols

        left_x = col * self.frame_w
        # pico2d의 clip_* 함수는 이미지의 아래쪽(0)부터 Y를 셉니다.
        # 일반적으로 스프라이트 시트는 위에서부터 쌓아두므로,
        # 실제 클립의 bottom Y는 이미지 높이에서 해당 행을 역으로 계산해야 합니다.
        if self.image_h:
            bottom_y = max(0, self.image_h - (row + 1) * self.frame_h)
        else:
            bottom_y = row * self.frame_h

        # pico2d의 clip_composite_draw를 사용해 클립 영역을 그립니다.
        # rotate: 라디안, flip: 'h' 문자열 전달
        self.image.clip_composite_draw(left_x, bottom_y, self.frame_w, self.frame_h, rotate, 'h' if flip else '', x, y, target_w, target_h)
