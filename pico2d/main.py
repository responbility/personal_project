# 필요한 모듈 임포트
import game_framework
import os
import sys  # sys 모듈 임포트
from pico2d import *
import play_mode

# --- [경로 설정 수정된 부분] ---
try:
    # 1. 현재 실행 중인 스크립트 파일의 디렉토리를 얻습니다.
    # sys.argv[0]은 현재 실행 중인 스크립트 파일의 경로입니다.
    # os.path.abspath와 os.path.dirname을 사용하여 절대 경로 디렉토리를 얻습니다.
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    # 2. 작업 디렉토리(CWD)를 현재 스크립트의 디렉토리로 변경합니다.
    # 이 경우, 다른 파일들에서 'assets/ball.png'라는 상대 경로가
    # 항상 '현재_스크립트_디렉토리/assets/ball.png'를 가리키게 됩니다.
    os.chdir(current_dir)
    print(f"DEBUG: Current Working Directory changed to: {os.getcwd()}")

except Exception as e:
    print(f"Error setting directory: {e}")
    # 경로 설정 실패 시 게임 실행을 중단하지 않도록 print만 사용합니다.
# --------------------------------

open_canvas(800, 600)
try:
    hide_cursor()
except Exception:
    pass

# 디버그: 바로 PlayMode로 시작(타이틀 건너띔)
try:
    game_framework.run(play_mode)
finally:
    # 게임 종료 후 캔버스 닫기(예외 발생 시에도 실행)
    try:
        close_canvas()
    except Exception:
        pass