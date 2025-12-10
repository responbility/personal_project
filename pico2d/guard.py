from pico2d import *
import math
import game_framework
from spritesheet import SpriteSheet
import game_world

CLIP_W, CLIP_H = 32, 32
SCALE = 3.0
TARGET_W = int(CLIP_W * SCALE)
TARGET_H = int(CLIP_H * SCALE)
MOVE_SPEED = 100  # 경비원의 이동 속도 (픽셀/초)


class Guard:
    def __init__(self, x=400, y=400, target=None):
        self.x = x
        self.y = y
        self.frame = 0.0
        self.dir = -1  # 초기 방향 (왼쪽)
        self.sheet = None
        self.frames_count = 1

        # 추적할 플레이어 객체
        self.target = target

        # HP: 2번 맞으면 죽도록 설정
        self.max_hp = 2
        self.hp = self.max_hp

        # 스프라이트 시트 로드
        try:
            self.sheet = SpriteSheet('assets/guard.png', CLIP_W, CLIP_H)
            self.frames_count = max(1, self.sheet.cols * self.sheet.rows)
        except Exception:
            try:
                self.sheet = SpriteSheet('guard.png', CLIP_W, CLIP_H)
                self.frames_count = max(1, self.sheet.cols * self.sheet.rows)
            except Exception as e:
                print(f"[Guard] 스프라이트 시트 로드 실패: {e}")
                self.sheet = None
                self.frames_count = 1

    def get_bb(self):
        return (self.x - TARGET_W // 2, self.y - TARGET_H // 2,
                self.x + TARGET_W // 2, self.y + TARGET_H // 2)

    def update(self):
        # 1. 애니메이션 (frames_count 전체를 순환)
        try:
            self.frame = (self.frame + self.frames_count * 1.0 * game_framework.frame_time) % self.frames_count
        except Exception:
            pass

        # 2. 플레이어 추적 로직
        if self.target:
            tx, ty = self.target.x, self.target.y
            dx = tx - self.x
            dy = ty - self.y
            dist_sq = dx * dx + dy * dy

            if dist_sq > 0:
                distance = math.sqrt(dist_sq)
                dir_x = dx / distance
                dir_y = dy / distance

                move_x = dir_x * MOVE_SPEED * game_framework.frame_time
                move_y = dir_y * MOVE_SPEED * game_framework.frame_time

                self.x += move_x
                self.y += move_y

                # 방향 설정 (x축 기준)
                if dir_x > 0:
                    self.dir = 1
                elif dir_x < 0:
                    self.dir = -1

        # HP가 0 이하이면 월드에서 제거
        if self.hp <= 0:
            game_world.remove_object(self)

    def draw(self):
        if self.sheet:
            try:
                idx = int(self.frame) % self.frames_count
                # dir<0 이면 좌우 반전해서 그림
                self.sheet.draw_frame(idx, self.x, self.y,
                                       TARGET_W, TARGET_H,
                                       flip=(self.dir < 0))
                # 디버그용 충돌 박스
                # draw_rectangle(*self.get_bb())
            except Exception as e:
                print(f"[Guard] draw 실패: {e}")
        else:
            # 스프라이트 시트가 없으면 단순 박스로 표시
            draw_rectangle(*self.get_bb())

    # Ratking의 공격 등과 충돌했을 때 호출될 함수
    def handle_collision(self, other):
        # Ball 등에 맞았을 때 HP 감소
        from ball import Ball
        if isinstance(other, Ball):
            self.hp -= 1
            print(f"[Guard] Hit! HP = {self.hp}")

            # 맞은 공은 제거
            game_world.remove_object(other)

            if self.hp <= 0:
                print("[Guard] Dead")
