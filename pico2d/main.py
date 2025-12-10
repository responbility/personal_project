# 필요한 모듈 임포트
import game_framework
import os
import sys  # sys 모듈 임포트
from pico2d import *
import title_mode  # title_mode 임포트

# --- [경로 설정 수정된 부분] ---
try:
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
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
# 기존: game_framework.run(play_mode)
# 이제는 타이틀 모드에서 시작
try:
    game_framework.run(title_mode)
finally:
    # 게임 종료 후 캔버스 닫기(예외 발생 시에도 실행)
    try:
        close_canvas()
    except Exception:
        pass