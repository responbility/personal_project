"""
작업: assets/ratking.png 스프라이트 시트를 지정된 프레임 크기(기본 16x16)로 잘라서
assets/ratking_frames/ 폴더에 frame_000.png, frame_001.png ... 형태로 저장합니다.

사용법:
1) 터미널에서 프로젝트 루트로 이동:
   cd "C:\2DGP_\2DGP\MY POWERPOINT\personal_project\pico2d"
2) Pillow 설치 (한 번만):
   python -m pip install Pillow
3) 스플리터 실행:
   python split_ratking_frames.py --input assets/ratking.png --w 16 --h 16 --out assets/ratking_frames

옵션:
  --input : 입력 스프라이트 시트 파일 경로
  --w     : 각 프레임의 너비 (px)
  --h     : 각 프레임의 높이 (px)
  --out   : 출력 디렉터리 경로

동작: 출력 디렉터리가 없으면 생성합니다. 파일명은 frame_000.png 형식으로 정렬 가능하게 저장합니다.
"""
from PIL import Image
import os
import argparse


def split_sheet(input_path, frame_w, frame_h, out_dir):
    if not os.path.isfile(input_path):
        print(f"입력 파일이 없습니다: {input_path}")
        return 1

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    img = Image.open(input_path).convert('RGBA')
    sheet_w, sheet_h = img.size
    cols = sheet_w // frame_w
    rows = sheet_h // frame_h

    idx = 0
    for r in range(rows):
        for c in range(cols):
            left = c * frame_w
            upper = r * frame_h
            right = left + frame_w
            lower = upper + frame_h
            frame = img.crop((left, upper, right, lower))
            out_name = os.path.join(out_dir, f"frame_{idx:03d}.png")
            frame.save(out_name)
            idx += 1
    print(f"완료: {idx}개의 프레임을 '{out_dir}'에 저장했습니다.")
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', default='assets/ratking.png')
    parser.add_argument('--w', '-W', type=int, default=16)
    parser.add_argument('--h', '-H', type=int, default=16)
    parser.add_argument('--out', '-o', default='assets/ratking_frames')
    args = parser.parse_args()

    split_sheet(args.input, args.w, args.h, args.out)

