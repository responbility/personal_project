from pico2d import *

class UIManager:
    def __init__(self, canvas_width, canvas_height):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        # UI 이미지 로드
        self.status_pane = load_image('status_pane.png')   # 상단 UI
        self.toolbar = load_image('toolbar.png')           # 하단 UI

        # 크기 설정 (이미지 크기 자동 사용)
        self.status_width = self.status_pane.w
        self.status_height = self.status_pane.h

        self.toolbar_width = self.toolbar.w
        self.toolbar_height = self.toolbar.h

    def draw(self):
        # 상단 UI (화면 맨 위 중앙)
        self.status_pane.draw(
            self.canvas_width // 2,
            self.canvas_height - self.status_height // 2
        )

        offset_y = 100

        self.toolbar.draw(
            self.canvas_width // 2,
            self.toolbar_height // 2 + offset_y
        )
