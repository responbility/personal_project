# map_manager.py
# MAX2.PNG 기반 맵 관리기: 이미지 로드, 캔버스에 타일링하여 그리기, 알파 기반 충돌 판정, 오른쪽 이동 시 새로운 세그먼트 추가
from pico2d import *
import os

try:
    from PIL import Image
except Exception:
    Image = None

class MapSegment:
    def __init__(self, image, pil_img, alpha_data, width, height):
        self.image = image
        self.pil_img = pil_img
        self.alpha_data = alpha_data
        self.w = width
        self.h = height

class MapManager:
    def __init__(self, asset_paths=None):
        # asset_paths: list of candidate full paths to MAX2.PNG or similar
        self.segments = []  # 리스트의 각 아이템은 MapSegment
        self.segment_width = 0
        self.segment_height = 0
        self.load_candidates = asset_paths or []
        self._load_first_available()
        # world offset in pixels (how much we've scrolled to the right)
        self.world_offset_x = 0

    def _load_first_available(self):
        for p in self.load_candidates:
            try:
                if os.path.isfile(p):
                    img = load_image(p)
                    pil_img = None
                    alpha_data = None
                    w = img.w
                    h = img.h
                    if Image is not None:
                        try:
                            pil_img = Image.open(p).convert('RGBA')
                            alpha = pil_img.split()[3]
                            alpha_data = alpha.load()
                        except Exception:
                            pil_img = None
                            alpha_data = None
                    seg = MapSegment(img, pil_img, alpha_data, w, h)
                    self.segments.append(seg)
                    self.segment_width = w
                    self.segment_height = h
                    print(f"MapManager: loaded map segment from {p} size({w}x{h})")
                    return
            except Exception:
                continue
        # 실패 시 빈 세그먼트 생성(보여주기용 색상 사각형 대신 이미지를 로드 못하면 None)
        print("MapManager: no map image found in candidates")

    def ensure_segments_to_cover(self, canvas_w):
        # ensure segments cover at least canvas_w + world_offset_x
        needed = int((self.world_offset_x + canvas_w) / max(1, self.segment_width)) + 1
        while len(self.segments) < needed:
            # duplicate first segment
            if len(self.segments) == 0:
                break
            base = self.segments[0]
            self.segments.append(base)
            print("MapManager: appended duplicated segment to cover width")

    def scroll_right(self, dx):
        # call when player moves right to extend world
        self.world_offset_x += dx

    def update(self, dt):
        # placeholder for future
        pass

    def draw(self):
        canvas_w = get_canvas_width()
        canvas_h = get_canvas_height()
        if len(self.segments) == 0:
            # draw fallback grid
            clear_canvas()
            return
        # ensure enough segments
        self.ensure_segments_to_cover(canvas_w)
        # draw segments next to each other, from world_offset_x
        start_x = - (self.world_offset_x % self.segment_width)
        x = start_x
        idx = int(self.world_offset_x / self.segment_width)
        # draw until covering canvas
        drawn = 0
        while x < canvas_w:
            seg_idx = idx + drawn
            seg = self.segments[seg_idx % len(self.segments)]
            try:
                # draw image with center-based API: at x + seg.w/2
                seg.image.draw(int(x + seg.w/2), canvas_h//2, seg.w, seg.h)
            except Exception:
                # fallback: draw at top-left using draw_to_origin if available
                try:
                    seg.image.draw_to_origin(int(x), 0)
                except Exception:
                    pass
            x += seg.w
            drawn += 1

    def is_solid_at(self, canvas_x, canvas_y):
        # determine which segment corresponds to canvas_x + world_offset_x
        if len(self.segments) == 0:
            return False
        global_x = canvas_x + self.world_offset_x
        seg_index = int(global_x / self.segment_width)
        seg = self.segments[seg_index % len(self.segments)]
        # map canvas -> image pixel
        if seg.alpha_data is None:
            return False
        # compute local x within segment
        local_x = int(global_x - seg_index * self.segment_width)
        local_y = canvas_y
        # map canvas height to image pixel coordinates (assume image height drawn equals canvas height)
        try:
            canvas_w = get_canvas_width()
            canvas_h = get_canvas_height()
        except Exception:
            return False
        ix = int(float(local_x) / float(self.segment_width) * float(seg.w))
        iy = int(float(local_y) / float(canvas_h) * float(seg.h))
        iy_img = seg.h - 1 - iy
        ix = max(0, min(seg.w - 1, ix))
        iy_img = max(0, min(seg.h - 1, iy_img))
        try:
            return seg.alpha_data[ix, iy_img] != 0
        except Exception:
            return False

    def get_border_points(self, canvas_w, canvas_h, step=16):
        points = []
        if len(self.segments) == 0:
            return points
        # sample along visible segments
        self.ensure_segments_to_cover(canvas_w)
        start_seg = int(self.world_offset_x / max(1, self.segment_width))
        seg_pixels = []
        for i in range(int((canvas_w + self.segment_width -1)/ self.segment_width)+1):
            seg = self.segments[(start_seg + i) % len(self.segments)]
            # sample border of each segment's alpha if available
            if seg.alpha_data is not None:
                for iy in range(0, seg.h, max(1, int(step/2))):
                    for ix in range(0, seg.w, max(1, int(step/2))):
                        try:
                            if seg.alpha_data[ix, iy] != 0:
                                # check neighbor to see if border
                                is_border = False
                                for nx, ny in ((ix-1, iy), (ix+1, iy), (ix, iy-1), (ix, iy+1)):
                                    if nx < 0 or ny < 0 or nx >= seg.w or ny >= seg.h:
                                        is_border = True
                                        break
                                    if seg.alpha_data[nx, ny] == 0:
                                        is_border = True
                                        break
                                if is_border:
                                    # map to canvas coords
                                    seg_offset_x = (start_seg + i) * self.segment_width - self.world_offset_x
                                    cx = int(seg_offset_x + ix * (self.segment_width / seg.w))
                                    cy = int((seg.h - 1 - iy) * (canvas_h / seg.h))
                                    points.append((cx, cy))
                        except Exception:
                            continue
        return points

