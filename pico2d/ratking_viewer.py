from pico2d import *
import os
import time

# Ratking large-chunk viewer + WASD movement
# Usage: run this script from project root. It will open a window and show the ratking
# image split into large chunks (configurable). Arrow keys select chunk, WASD moves the
# previewed chunk. ESC or window close exits.

# --- Config ---
ASSET_PATH = os.path.join('assets', 'ratking.png')
CHUNK_W = 64   # chunk width in pixels (change to desired large cut)
CHUNK_H = 64   # chunk height in pixels
THUMB_SCALE = 2
PREVIEW_SCALE = 4
GRID_PADDING = 6
MOVE_SPEED = 240.0  # pixels per second for WASD movement
CANVAS_W = 900
CANVAS_H = 700


class LargeSheet:
    def __init__(self, path, chunk_w, chunk_h):
        if not os.path.isfile(path):
            # try assets relative to this file
            here = os.path.dirname(__file__)
            candidate = os.path.join(here, 'assets', os.path.basename(path))
            if os.path.isfile(candidate):
                path = candidate
        self.img = load_image(path)
        self.sheet_w, self.sheet_h = self.img.w, self.img.h
        # clamp chunk to image size
        self.chunk_w = min(chunk_w, self.sheet_w)
        self.chunk_h = min(chunk_h, self.sheet_h)
        self.cols = max(1, self.sheet_w // self.chunk_w)
        self.rows = max(1, self.sheet_h // self.chunk_h)
        # build chunk list (clip_x, clip_y, w, h) where clip_y is bottom-based for pico2d
        self.chunks = []
        for r in range(self.rows):
            for c in range(self.cols):
                x = c * self.chunk_w
                # convert top-based row to bottom-based clip_y
                top_y = r * self.chunk_h
                clip_y = self.sheet_h - top_y - self.chunk_h
                self.chunks.append((x, clip_y, self.chunk_w, self.chunk_h))

    def draw_chunk(self, index, x, y, target_w=None, target_h=None):
        if index < 0 or index >= len(self.chunks):
            return
        cx, cy, w, h = self.chunks[index]
        tw = target_w if target_w is not None else w
        th = target_h if target_h is not None else h
        try:
            self.img.clip_draw(cx, cy, w, h, x, y, tw, th)
        except Exception:
            # fallback without scaling
            self.img.clip_draw(cx, cy, w, h, x, y)


def main():
    open_canvas(CANVAS_W, CANVAS_H)
    try:
        hide_cursor()
    except Exception:
        pass

    # load sheet
    try:
        sheet = LargeSheet(ASSET_PATH, CHUNK_W, CHUNK_H)
    except Exception as e:
        print('Failed to load ratking asset:', e)
        close_canvas()
        return

    # grid layout
    thumb_w = int(CHUNK_W * THUMB_SCALE)
    thumb_h = int(CHUNK_H * THUMB_SCALE)
    cols = sheet.cols
    rows = sheet.rows
    grid_w = cols * (thumb_w + GRID_PADDING)
    grid_h = rows * (thumb_h + GRID_PADDING)

    grid_x0 = 20 + thumb_w // 2
    grid_y0 = CANVAS_H - 20 - thumb_h // 2

    selected = 0
    preview_x = CANVAS_W // 2
    preview_y = CANVAS_H // 2

    running = True
    paused = False
    animate = False
    frame_timer = 0.0
    frame_speed = 6.0

    last_time = time.time()

    print('ratking_viewer controls: Arrow keys select chunk, WASD move preview,')
    print('Space toggles animate, ESC to exit')

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
                    # move selection left across columns
                    r = selected // cols
                    c = selected % cols
                    c = (c - 1) % cols
                    selected = r * cols + c
                elif e.key == SDLK_RIGHT:
                    r = selected // cols
                    c = selected % cols
                    c = (c + 1) % cols
                    selected = r * cols + c
                elif e.key == SDLK_UP:
                    r = selected // cols
                    c = selected % cols
                    r = (r - 1) % rows
                    selected = r * cols + c
                elif e.key == SDLK_DOWN:
                    r = selected // cols
                    c = selected % cols
                    r = (r + 1) % rows
                    # clamp in case last row shorter
                    if r * cols + c >= len(sheet.chunks):
                        c = len(sheet.chunks) - 1 - r * cols
                    selected = r * cols + c
                elif e.key == SDLK_SPACE:
                    animate = not animate
                # WASD movement on keydown/up handled below for smooth movement

        # keyboard state for WASD movement
        keys = get_keyboard()
        vx = 0.0
        vy = 0.0
        if keys[SDLK_w] or keys[SDLK_UP]:
            vy += MOVE_SPEED
        if keys[SDLK_s] or keys[SDLK_DOWN]:
            vy -= MOVE_SPEED
        if keys[SDLK_a] or keys[SDLK_LEFT]:
            vx -= MOVE_SPEED
        if keys[SDLK_d] or keys[SDLK_RIGHT]:
            vx += MOVE_SPEED

        preview_x += vx * dt
        preview_y += vy * dt

        # animate selection if requested
        if animate:
            frame_timer += dt
            if frame_timer >= 1.0 / frame_speed:
                frame_timer -= 1.0 / frame_speed
                selected = (selected + 1) % len(sheet.chunks)

        # draw
        clear_canvas()

        # draw grid thumbnails
        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c
                if idx >= len(sheet.chunks):
                    continue
                x = grid_x0 + c * (thumb_w + GRID_PADDING)
                y = grid_y0 - r * (thumb_h + GRID_PADDING)
                sheet.draw_chunk(idx, x, y, thumb_w, thumb_h)
                # highlight
                if idx == selected:
                    try:
                        draw_rectangle(x - thumb_w/2 - 2, y - thumb_h/2 - 2, x + thumb_w/2 + 2, y + thumb_h/2 + 2)
                    except Exception:
                        pass

        # draw preview of selected chunk
        preview_w = int(CHUNK_W * PREVIEW_SCALE)
        preview_h = int(CHUNK_H * PREVIEW_SCALE)
        sheet.draw_chunk(selected, preview_x, preview_y, preview_w, preview_h)

        # small info text
        try:
            font = load_font('assets/ENCR10B.TTF', 16)
            font.draw(10, 10, f'Selected: {selected}  Chunk: {CHUNK_W}x{CHUNK_H}  Preview pos: ({preview_x:.0f},{preview_y:.0f})')
            font.draw(10, 30, 'Arrow: select chunk  WASD: move preview  Space: animate  Esc: quit')
        except Exception:
            pass

        update_canvas()
        delay(0.01)

    close_canvas()


if __name__ == '__main__':
    main()

