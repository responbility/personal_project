from pico2d import *
from spritesheet import SpriteSheet
import time

# Brief: Play ratking sprite-sheet animations per row (each row is one animation)
# Controls:
#  - Left/Right: previous/next animation row
#  - Up/Down: speed +/-
#  - Space: pause/play
#  - Esc or window close: exit

CANVAS_W, CANVAS_H = 576, 1024
CLIP_W, CLIP_H = 16, 16
PREVIEW_SCALE = 8  # large preview scale
THUMB_SCALE = 3    # small grid thumbnail scale
PADDING = 6

open_canvas(CANVAS_W, CANVAS_H)
try:
    bg = load_image('assets/visual_grid.png')
except Exception:
    bg = None

sheet = SpriteSheet('assets/ratking.png', CLIP_W, CLIP_H)
cols = sheet.cols
rows = sheet.rows
total_frames = cols * rows

# Each row is an animation sequence of length=cols
current_row = 0
frame_speed = 10.0  # frames per second
paused = False
frame_timer = 0.0
frame_index = 0

last_time = time.time()

# load font once to avoid repeated error prints
font = None
for font_path in ('assets/ENCR10B.TTF', 'ENCR10B.TTF', 'assets/pixelfont.ttf'):
    try:
        font = load_font(font_path, 18)
        break
    except Exception:
        font = None

# helper to draw thumbnails grid (top area)
def draw_grid():
    start_x = 40
    start_y = CANVAS_H - 60
    cw = int(CLIP_W * THUMB_SCALE)
    ch = int(CLIP_H * THUMB_SCALE)
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            x = start_x + c * (cw + PADDING) + cw/2
            y = start_y - r * (ch + PADDING) - ch/2
            sheet.draw_frame(idx, x, y, cw, ch)
            # highlight selected row's frames
            if r == current_row:
                # draw small rectangle around
                try:
                    draw_rectangle(x - cw/2, y - ch/2, x + cw/2, y + ch/2)
                except Exception:
                    pass

# main loop
running = True
while running:
    now = time.time()
    dt = now - last_time
    last_time = now

    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            running = False
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                running = False
            elif e.key == SDLK_LEFT:
                current_row = (current_row - 1) % rows
                frame_index = 0
                frame_timer = 0.0
            elif e.key == SDLK_RIGHT:
                current_row = (current_row + 1) % rows
                frame_index = 0
                frame_timer = 0.0
            elif e.key == SDLK_UP:
                frame_speed = min(60.0, frame_speed + 1.0)
            elif e.key == SDLK_DOWN:
                frame_speed = max(1.0, frame_speed - 1.0)
            elif e.key == SDLK_SPACE:
                paused = not paused

    # update animation timer
    if not paused:
        frame_timer += dt
        if frame_timer >= 1.0 / frame_speed:
            frame_timer -= 1.0 / frame_speed
            frame_index = (frame_index + 1) % cols

    # draw
    clear_canvas()
    if bg:
        bg.draw(CANVAS_W/2, CANVAS_H/2)

    # draw thumbnails
    draw_grid()

    # draw preview (center)
    preview_w = int(CLIP_W * PREVIEW_SCALE)
    preview_h = int(CLIP_H * PREVIEW_SCALE)
    preview_x = CANVAS_W // 2
    preview_y = CANVAS_H // 2
    sheet.draw_frame(current_row * cols + frame_index, preview_x, preview_y, preview_w, preview_h)

    # draw UI text
    if font is not None:
        try:
            font.draw(10, 10, f'Row {current_row+1}/{rows}  Frame {frame_index+1}/{cols}  Speed {frame_speed:.1f}fps  (←/→ row, ↑/↓ speed, Space pause)')
        except Exception:
            pass

    update_canvas()
    delay(0.01)

close_canvas()
