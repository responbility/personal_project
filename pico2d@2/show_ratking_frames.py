from pico2d import *
from spritesheet import SpriteSheet
import time

# 설정
CANVAS_W, CANVAS_H = 576, 1024
CLIP_W, CLIP_H = 16, 16
GRID_SCALE = 3  # 그리드에 그릴 때의 축소/확대 비율
PREVIEW_SCALE = 8  # 미리보기 확대 비율
PADDING = 6
BOX_MARGIN_X = 40
BOX_MARGIN_Y = 40

# 초기화
open_canvas(CANVAS_W, CANVAS_H)
try:
    bg = load_image('assets/visual_grid.png')
except Exception:
    bg = None

sheet = SpriteSheet('assets/ratking.png', CLIP_W, CLIP_H)
cols = sheet.cols
rows = sheet.rows
total_frames = cols * rows

# 그리드 계산
cell_w = int(CLIP_W * GRID_SCALE)
cell_h = int(CLIP_H * GRID_SCALE)
start_x = BOX_MARGIN_X
start_y = CANVAS_H - 80

# 프리뷰 초기 위치: 왼쪽 아래 박스 중심
def get_box_center():
    w = CLIP_W * PREVIEW_SCALE
    h = CLIP_H * PREVIEW_SCALE
    cx = BOX_MARGIN_X + w / 2
    cy = BOX_MARGIN_Y + h / 2
    return cx, cy

preview_x, preview_y = get_box_center()
selected = 0
speed = 240.0  # 픽셀/초
vx = 0.0
vy = 0.0

running = True
last_time = time.time()

# 간단 UI 색상 그리기 함수
def draw_box(x, y, w, h, color=(255,0,0)):
    # draw rectangle outline centered at (x,y)
    left = x - w/2
    right = x + w/2
    bottom = y - h/2
    top = y + h/2
    set_color(color[0], color[1], color[2]) if 'set_color' in globals() else None
    # pico2d doesn't expose color change easily; use draw_rectangle
    try:
        draw_rectangle(left, bottom, right, top)
    except Exception:
        pass

# 이벤트 상수
from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_ESCAPE, SDLK_LEFT, SDLK_RIGHT, SDLK_w, SDLK_a, SDLK_s, SDLK_d, SDLK_b, SDL_QUIT

while running:
    now = time.time()
    dt = now - last_time if last_time is not None else 1/60.0
    last_time = now

    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            running = False
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                running = False
            elif e.key == SDLK_LEFT:
                selected = max(0, selected - 1)
            elif e.key == SDLK_RIGHT:
                selected = min(total_frames - 1, selected + 1)
            elif e.key == SDLK_w:
                vy = speed
            elif e.key == SDLK_s:
                vy = -speed
            elif e.key == SDLK_a:
                vx = -speed
            elif e.key == SDLK_d:
                vx = speed
            elif e.key == SDLK_b:
                preview_x, preview_y = get_box_center()
        elif e.type == SDL_KEYUP:
            if e.key == SDLK_w or e.key == SDLK_s:
                vy = 0.0
            if e.key == SDLK_a or e.key == SDLK_d:
                vx = 0.0

    # 위치 업데이트
    preview_x += vx * dt
    preview_y += vy * dt
    # 경계 클램프
    half_w = (CLIP_W * PREVIEW_SCALE) / 2
    half_h = (CLIP_H * PREVIEW_SCALE) / 2
    preview_x = max(half_w, min(CANVAS_W - half_w, preview_x))
    preview_y = max(half_h, min(CANVAS_H - half_h, preview_y))

    # 그리기
    clear_canvas()
    if bg:
        bg.draw(CANVAS_W/2, CANVAS_H/2)

    # 그리드: 모든 프레임을 격자 배치
    for idx in range(total_frames):
        col = idx % cols
        row = idx // cols
        x = start_x + col * (cell_w + PADDING) + cell_w/2
        y = start_y - row * (cell_h + PADDING) - cell_h/2
        sheet.draw_frame(idx, x, y, cell_w, cell_h, flip=False, rotate=0)

    # 왼쪽 아래 박스 표시 (outline)
    box_w = CLIP_W * PREVIEW_SCALE
    box_h = CLIP_H * PREVIEW_SCALE
    try:
        draw_rectangle(BOX_MARGIN_X, BOX_MARGIN_Y, BOX_MARGIN_X + box_w, BOX_MARGIN_Y + box_h)
    except Exception:
        pass

    # 선택 프레임 프리뷰(확대)
    sheet.draw_frame(selected, preview_x, preview_y, int(CLIP_W * PREVIEW_SCALE), int(CLIP_H * PREVIEW_SCALE), flip=False, rotate=0)

    update_canvas()
    delay(0.016)

close_canvas()

