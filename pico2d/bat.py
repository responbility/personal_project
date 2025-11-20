from pico2d import *
import game_framework
from spritesheet import SpriteSheet
import game_world

# 단순한 Bat 적 클래스

CLIP_W, CLIP_H = 32, 32
SCALE = 3.0
TARGET_W = int(CLIP_W * SCALE)
TARGET_H = int(CLIP_H * SCALE)

# 이동 속도 (픽셀/초)
CHASE_SPEED_PPS = 160.0

# 애니메이션 설정
TIME_PER_ACTION = 0.25
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 4.0  # 기본값

# 최소 근접 거리 (정지 임계값)
STOP_DISTANCE = 20


class Bat:
    def __init__(self):
        # 위치: 화면 상단 중앙 부근으로 배치해서 스케치 화면처럼 등장하게 함
        try:
            cw = get_canvas_width()
            ch = get_canvas_height()
        except Exception:
            cw, ch = 576, 1024
        self.x = cw // 2
        self.y = ch - 100

        self.frame = 0.0
        self.dir = -1
        self.target = None  # 외부에서 play_mode가 할당

        self.sheet = None
        self.sheet_cols = 1
        self.sheet_rows = 1

        # 스프라이트 시트 로드 시도
        try:
            self.sheet = SpriteSheet('assets/bat.png', CLIP_W, CLIP_H)
            self.sheet_cols = self.sheet.cols
            self.sheet_rows = self.sheet.rows
            FRAMES = self.sheet_cols * self.sheet_rows
        except Exception:
            try:
                self.sheet = SpriteSheet('bat.png', CLIP_W, CLIP_H)
                self.sheet_cols = self.sheet.cols
                self.sheet_rows = self.sheet.rows
                FRAMES = self.sheet_cols * self.sheet_rows
            except Exception:
                # 스프라이트 시트가 없으면 None으로 두고 폴백 그리기 사용
                self.sheet = None
                FRAMES = 1

        # FRAMES_PER_ACTION를 실제 프레임 수로 설정(더 자연스럽게)
        try:
            self.frames_count = int(FRAMES)
        except Exception:
            self.frames_count = 1

        # 플레이어가 이동한 누적 픽셀 수를 추적해서 내려오는 동작에 사용
        self.last_target_cumulative = 0

        # 수평 보정 속도 (픽셀/초)
        # **수정됨**: 추적 속도 상향
        self.horz_speed = 400.0

        # 체력
        self.hp = 3

    def get_bb(self):
        return self.x - TARGET_W // 2, self.y - TARGET_H // 2, self.x + TARGET_W // 2, self.y + TARGET_H // 2

    def take_damage(self, dmg):
        try:
            self.hp -= dmg
            print(f"DEBUG: Bat took {dmg} dmg, hp={self.hp}")
            if self.hp <= 0:
                try:
                    game_world.remove_object(self)
                except Exception:
                    pass
        except Exception:
            pass

    def update(self):
        # 애니메이션 프레임
        if self.frames_count > 0:
            self.frame = (self.frame + self.frames_count * ACTION_PER_TIME * game_framework.frame_time) % max(1,
                                                                                                              self.frames_count)

        if self.target is None:
            return

        # 1) 플레이어가 움직인 누적 픽셀 수 변화만큼 내려오기 (수직 추적)
        try:
            player_cum = getattr(self.target, 'cumulative_moved', None)
            if player_cum is not None:
                delta = int(player_cum - self.last_target_cumulative)
                if delta > 0:
                    # delta 픽만큼 아래로 이동하되, 맵의 솔리드(벽) 픽과 충돌하면 멈춤
                    move_down = 0
                    for i in range(delta):
                        next_y = self.y - 1
                        # check collision against map if available
                        blocked = False
                        try:
                            if getattr(self, 'map', None) is not None and self.map.is_solid_at(self.x, next_y):
                                blocked = True
                        except Exception:
                            blocked = False
                        if blocked:
                            break
                        self.y = next_y
                        move_down += 1
                    self.last_target_cumulative += move_down
        except Exception:
            pass

        # 2) 수평 보정: 플레이어 X에 빠르게 접근 (수평 추적)
        try:
            dx = self.target.x - self.x
            # tiny threshold
            if abs(dx) > 0.5:
                step = self.horz_speed * game_framework.frame_time
                move_x = max(-step, min(step, dx))
                # attempted new x
                new_x = self.x + move_x
                blocked = False
                try:
                    if getattr(self, 'map', None) is not None and self.map.is_solid_at(new_x, self.y):
                        blocked = True
                except Exception:
                    blocked = False
                if not blocked:
                    self.x = new_x
                    self.dir = 1 if dx > 0 else -1
        except Exception:
            pass

        # 3) 간단한 충돌 체크: Bat과 Boy의 AABB 충돌 감지
        try:
            if hasattr(self.target, 'get_bb'):
                bx1, by1, bx2, by2 = self.get_bb()
                ox1, oy1, ox2, oy2 = self.target.get_bb()
                if not (bx2 < ox1 or bx1 > ox2 or by2 < oy1 or by1 > oy2):
                    # 충돌 발생: 간단히 game_framework.quit()로 종료하거나 boy를 제거
                    print("DEBUG: Bat collided with Boy - triggering game over")
                    # 안전하게 제거: game_world.remove_object(boy) 등
                    try:
                        import game_world
                        game_world.remove_object(self.target)
                    except Exception:
                        pass
                    try:
                        game_world.remove_object(self)
                    except Exception:
                        pass
        except Exception:
            pass

    def draw(self):
        # 스프라이트가 있으면 현재 프레임을 그림
        if self.sheet:
            try:
                idx = int(self.frame) % max(1, self.frames_count)
                flip = (self.dir < 0)
                self.sheet.draw_frame(idx, self.x, self.y, TARGET_W, TARGET_H, flip=flip)
            except Exception:
                # 실패 시 폴백 그리기
                self._draw_fallback()
        else:
            self._draw_fallback()

        # 디버그용 바운딩 박스
        try:
            draw_rectangle(*self.get_bb())
        except Exception:
            pass

    def _draw_fallback(self):
        # 스프라이트 파일이 없을 때 간단히 사각형과 텍스트로 표시
        try:
            x1, y1, x2, y2 = self.get_bb()
            draw_rectangle(x1, y1, x2, y2)
            try:
                f = load_font('assets/ENCR10B.TTF', 12)
            except Exception:
                try:
                    f = load_font('ENCR10B.TTF', 12)
                except Exception:
                    f = None
            if f:
                f.draw(self.x - 10, self.y - TARGET_H // 2 - 12, 'BAT', (255, 0, 0))
        except Exception:
            pass

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        # 충돌 처리(필요 시 확장)
        if group == 'bat:boy':
            pass
        if group == 'projectile:bat':
            try:
                if hasattr(other, 'take_damage'):
                    other.take_damage(1)
            except Exception:
                pass
