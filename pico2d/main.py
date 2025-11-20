# main.py

# 필요한 모듈 임포트
import game_framework
import play_mode
from pico2d import *

# 캔버스 크기 및 설정
open_canvas(576, 1024)


# 디버그: 바로 PlayMode로 시작(타이틀 건너띔)
game_framework.run(play_mode)

# 게임 종료 후 캔버스 닫기
close_canvas()