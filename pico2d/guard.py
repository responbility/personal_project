from pico2d import *
import math
import game_framework
import game_world

# 스프라이트 한 칸 크기
CLIP_W, CLIP_H = 32, 32

# 확대 비율
SCALE = 3.0
TARGET_W = int(CLIP_W * SCALE)
TARGET_H = int(CLIP_H * SCALE)

# 애니메이션 및 이동 속도
MOVE_SPEED = 100
ANIM_FPS = 6


# ============================================
#  SpriteSheet 클래스 (파일 통합)
# ============================================
class SpriteSheet:
    def __init__(self, filename, frame_w, frame_h, rows=1, cols=1):
        self.image = load_image(filename)
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.rows = rows
        self.cols = cols

        self.frames = rows * cols

    def draw_frame(self, index, x, y, w=None, h=None, flip=False):
        if index < 0 or index >= self.frames:
            return

        col = index % self.cols
        row = index // self.cols

        sx = col * self.frame_w
        sy = (self.rows - 1 - row) * self.frame_h   # 상단 기준이라 이렇게 계산
        sw = self.frame_w
        sh = self.frame_h

        if flip:
            self.image.clip_composite_draw(
                sx, sy, sw, sh, 0, 'h', x, y, w, h
            )
        else:
            self.image.clip_draw(
                sx, sy, sw, sh, x, y, w, h
            )


# ============================================
#  Guard 클래스
# ============================================
class Guard:
    def __init__(self, x=400, y=400, target=None):
        self.x = x
        self.y = y
        self.frame = 0.0
        self.dir = -1  # 기본 왼쪽

        self.target = target
        self.max_hp = 2
        self.hp = self.max_hp

        self.frames_count = 6  # guard.png는 6프레임

        # SpriteSheet 로드
        try:
            self.sheet = SpriteSheet(
                'assets/guard.png',
                CLIP_W, CLIP_H,
                rows=1, cols=6
            )
        except:
            self.sheet = SpriteSheet(
                'guard.png',
                CLIP_W, CLIP_H,
                rows=1, cols=6
            )

    def get_bb(self):
        return (self.x - TARGET_W // 2, self.y - TARGET_H // 2,
                self.x + TARGET_W // 2, self.y + TARGET_H // 2)

    def update(self):
        # 1. 애니메이션
        self.frame = (self.frame + ANIM_FPS * game_framework.frame_time) % self.frames_count

        # 2. 추적 AI
        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist_sq = dx*dx + dy*dy

            if dist_sq > 0:
                dist = math.sqrt(dist_sq)
                dir_x = dx / dist
                dir_y = dy / dist

                self.x += dir_x * MOVE_SPEED * game_framework.frame_time
                self.y += dir_y * MOVE_SPEED * game_framework.frame_time

                self.dir = 1 if dir_x > 0 else -1

        # 3. 체력 0 → 제거
        if self.hp <= 0:
            print("[Guard] Dead")
            game_world.remove_object(self)

    def draw(self):
        idx = int(self.frame)
        self.sheet.draw_frame(
            idx,
            self.x, self.y,
            TARGET_W, TARGET_H,
            flip=(self.dir < 0)
        )

    def handle_collision(self, other):
        from ball import Ball
        if isinstance(other, Ball):
            self.hp -= 1
            print(f"[Guard] Hit! HP = {self.hp}")
            game_world.remove_object(other)
