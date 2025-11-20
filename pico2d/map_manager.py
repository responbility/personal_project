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
        self.segments = []  # 리스트의 각 아이템은 MapSegment
        self.segment_width = 0
        self.segment_height = 0
        self.load_candidates = asset_paths or []
        self._load_first_available()
        # world offset in pixels (how much we've scrolled to the right)
        self.world_offset_x = 0

    def _find_case_insensitive(self, path):
        """
        주어진 경로가 존재하지 않으면 같은 디렉터리에서 대소문자 구분 없이 매칭되는 파일을 찾아반환합니다.
        실패하면 None 반환.
        """
        try:
            if os.path.isfile(path):
                return path
            dirname = os.path.dirname(path)
            target = os.path.basename(path).lower()
            if not os.path.isdir(dirname):
                return None
            for f in os.listdir(dirname):
                if f.lower() == target:
                    return os.path.join(dirname, f)
        except Exception:
            return None
        return None

    def _find_by_keyword_in_dir(self, path, keywords=('max', 'map')):
        """디렉터리 내에서 keywords 중 하나를 파일명에 포함하는 파일을 찾아 반환
        (대소문자 무시). 실패시 None."""
        try:
            dirname = os.path.dirname(path)
            if not os.path.isdir(dirname):
                return None
            for f in os.listdir(dirname):
                low = f.lower()
                for k in keywords:
                    if k in low:
                        return os.path.join(dirname, f)
        except Exception:
            return None
        return None

    def _load_first_available(self):
        for p in self.load_candidates:
            try:
                # 먼저 경로가 실제로 존재하는지 확인하고, 존재하지 않으면 대소문자 보정을 시도
                candidate = self._find_case_insensitive(p) or p

                # 추가 폴백: 디렉터리에서 'max' 또는 'map' 키워드를 포함한 파일을 찾아본다.
                if not candidate or not os.path.isfile(candidate):
                    alt = self._find_by_keyword_in_dir(p, keywords=('max2', 'max'))
                    if alt and os.path.isfile(alt):
                        candidate = alt

                if not candidate or not os.path.isfile(candidate):
                    print(f"MapManager: candidate not found on disk: {p}")
                    continue

                # 1. Image 로드 시도 (pico2d)
                try:
                    img = load_image(candidate)
                except Exception as e:
                    print(f"MapManager: pico2d.load_image failed for {candidate}: {e}")
                    img = None

                if img is None:
                    continue

                pil_img = None
                alpha_data = None
                w = getattr(img, 'w', 0)
                h = getattr(img, 'h', 0)

                # 2. PIL을 사용한 알파 데이터 로드 시도
                if Image is not None:
                    try:
                        pil_img = Image.open(candidate).convert('RGBA')
                        alpha = pil_img.split()[3]
                        alpha_data = alpha.load()
                    except Exception as e:
                        # PIL 로드 실패는 치명적이지 않지만 충돌 판정에 영향을 줌
                        print(f"MapManager: PIL Alpha load failed for {candidate}: {e}")
                        pil_img = None
                        alpha_data = None

                seg = MapSegment(img, pil_img, alpha_data, w, h)
                self.segments.append(seg)
                self.segment_width = w
                self.segment_height = h
                print(f"MapManager: loaded map segment from {candidate} size({w}x{h})")
                return  # 성공적으로 로드했으면 종료

            except Exception as e:
                print(f"MapManager: Failed to load image candidate {p}: {e}")
                continue  # 다음 후보로 이동

        # 모든 후보 로드 실패
        print("MapManager: 🚨🚨🚨 No map image found in candidates! Check paths/files. 🚨🚨🚨")

    def ensure_segments_to_cover(self, canvas_w):
        # ensure segments cover at least canvas_w + world_offset_x
        if self.segment_width == 0: return
        needed = int((self.world_offset_x + canvas_w) / self.segment_width) + 2  # +2는 안정성을 위함
        while len(self.segments) < needed:
            # duplicate first segment
            if len(self.segments) == 0:
                break
            base = self.segments[0]
            # 깊은 복사 대신 MapSegment 인스턴스를 재사용(얕은 복사 효과)
            self.segments.append(base)
            print("MapManager: appended duplicated segment to cover width")

    def scroll_right(self, dx):
        # call when player moves right to extend world
        self.world_offset_x += dx

    def update(self):
        # placeholder
        pass

    def draw(self):
        canvas_w = get_canvas_width()
        canvas_h = get_canvas_height()
        if len(self.segments) == 0:
            # 맵 로드 실패 시 디버그 메시지 출력
            print("MapManager: Cannot draw, no segments loaded.")
            return

        # ensure enough segments
        self.ensure_segments_to_cover(canvas_w)

        # draw segments next to each other, from world_offset_x
        start_x_offset = self.world_offset_x % self.segment_width
        start_x_segment_index = int(self.world_offset_x / self.segment_width)

        x = - start_x_offset
        idx = start_x_segment_index

        # draw until covering canvas
        drawn = 0
        while x < canvas_w:
            # 리스트 인덱스를 안정적으로 가져오기: 인덱스가 범위를 벗어나면 첫 번째 세그먼트로 폴백
            seg_idx = (idx + drawn) % len(self.segments)
            seg = self.segments[seg_idx]

            try:
                # 변경: 원본 이미지의 픽셀 기준으로 좌하단(origin)에서 그려 원본 크기가 유지되도록 함
                # pico2d의 draw_to_origin(x, y, w, h) 를 우선 사용
                try:
                    seg.image.draw_to_origin(int(x), 0, seg.w, seg.h)
                except Exception:
                    # fallback: center-based draw (기존 방식)
                    seg.image.draw(int(x + seg.w / 2), canvas_h // 2, seg.w, seg.h)
            except Exception:
                print(f"MapManager: Draw failed for segment {seg_idx}")
                pass
            x += seg.w
            drawn += 1

    def is_solid_at(self, canvas_x, canvas_y):
        # 충돌 판정 (알파값 기반)
        if len(self.segments) == 0:
            return False

        global_x = canvas_x + self.world_offset_x
        seg_index = int(global_x / self.segment_width)

        # 맵이 세그먼트를 복제하지 않은 영역일 경우 폴백 처리
        if seg_index < 0:
            return False

        seg_idx = seg_index % len(self.segments)
        seg = self.segments[seg_idx]

        if seg.alpha_data is None:
            return False

        # 캔버스 크기
        try:
            canvas_w = get_canvas_width()
            canvas_h = get_canvas_height()
        except Exception:
            return False

        # 1. 세그먼트 내 로컬 좌표 계산
        local_x = int(global_x - seg_index * self.segment_width)
        local_y = canvas_y

        # 2. 로컬 캔버스 좌표를 이미지 픽셀 좌표로 스케일링
        # x 스케일링
        ix = int(float(local_x) / self.segment_width * seg.w)
        # y 스케일링 (pico2d y=0이 이미지 y=0에 매핑되도록 처리)
        iy = int(float(local_y) / canvas_h * seg.h)

        # 3. 이미지 y 좌표 변환 (pico2d는 바텀-업, PIL은 탑-다운)
        iy_img = seg.h - 1 - iy

        # 4. 경계 값 클램핑
        ix = max(0, min(seg.w - 1, ix))
        iy_img = max(0, min(seg.h - 1, iy_img))

        try:
            # 알파값이 0이 아니면 솔리드
            return seg.alpha_data[ix, iy_img] != 0
        except IndexError:
            # 좌표가 범위를 벗어났을 경우 (발생해서는 안 됨)
            return False
        except Exception:
            return False