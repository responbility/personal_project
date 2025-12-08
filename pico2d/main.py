# main.py

# 필요한 모듈 임포트
import game_framework
from pico2d import *


# 캔버스와 렌더러를 먼저 열어둡니다. 이미지 로드와 드로우는 renderer가 필요하므로
# 다른 모듈(play_mode 등)을 import 하기 전에 캔버스를 연다.
open_canvas(800, 600)
try:
    hide_cursor()
except Exception:
    pass

# play_mode는 캔
# 버스가 열린 이후에 import 합니다.
import play_mode


# 디버그: 바로 PlayMode로 시작(타이틀 건너띔)
try:
    game_framework.run(play_mode)
finally:
    # 게임 종료 후 캔버스 닫기(예외 발생 시에도 실행)
    try:
        close_canvas()
    except Exception:
        pass
