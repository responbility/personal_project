# main.py

# 필요한 모듈 임포트
import game_framework
import title_mode
# set_canvas_draw_mode를 제거합니다.
from pico2d import *

# 캔버스 크기 및 설정
open_canvas(576,1024)


# title_mode를 게임의 시작 모드로 실행
game_framework.run(title_mode)

# 게임 종료 후 캔버스 닫기
close_canvas()