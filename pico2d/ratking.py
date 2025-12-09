from pico2d import *

class Ratking:
    def __init__(self):
        self.x, self.y = 400, 300
        self.frame = 0
        self.action = 0  # 0: idle, 1: walk
        self.dir = 1  # 1: right, -1: left
        self.image = load_image('assets/ratking.png')
        self.frame_width = 48
        self.frame_height = 48

    def update(self):
        self.frame = (self.frame + 1) % 8  # 각 액션은 8프레임으로 가정
        if self.action == 1: # walk
            self.x += self.dir * 5

    def draw_with_camera(self, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # 액션에 따라 y 위치 결정 (0: walk, 1: idle)
        # ratking.png 스프라이트 시트에서 걷는 동작이 첫 번째 줄, 서 있는 동작이 두 번째 줄에 있다고 가정
        y_offset = (1 - self.action) * self.frame_height

        if self.dir == 1: # 오른쪽
            self.image.clip_draw(self.frame * self.frame_width, y_offset, self.frame_width, self.frame_height, screen_x, screen_y)
        else: # 왼쪽
            self.image.clip_composite_draw(self.frame * self.frame_width, y_offset, self.frame_width, self.frame_height, 0, 'h', screen_x, screen_y, self.frame_width, self.frame_height)

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_LEFT:
                self.dir = -1
                self.action = 1
            elif event.key == SDLK_RIGHT:
                self.dir = 1
                self.action = 1
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_LEFT or event.key == SDLK_RIGHT:
                self.action = 0 # idle


