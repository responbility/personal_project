Split ratking sprite sheet

이 저장소의 `split_ratking_frames.py` 스크립트는 `assets/ratking.png` 같은 스프라이트 시트를 지정한 프레임 크기(예: 16x16)로 잘라 `assets/ratking_frames/` 폴더에 PNG로 저장합니다.

간단 사용법(Windows cmd):

1) Pillow 설치(한 번만):

```cmd
python -m pip install Pillow
```

2) 스플리터 실행:

```cmd
python split_ratking_frames.py --input assets/ratking.png --w 16 --h 16 --out assets/ratking_frames
```

3) 실행 후 `play_mode.py`는 `assets/ratking_frames/` 폴더에 있는 PNG를 우선으로 읽어 애니메이션을 재생합니다.

주의: 프레임 크기와 시트의 정렬(좌→우, 상→하)을 확인해주세요. 필요하면 `--w`와 `--h` 옵션을 조정하세요.
