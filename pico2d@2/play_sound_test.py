from pico2d import *
import time

print('test: start')
# 작은 캔버스를 열어 pico2d 초기화를 확실히 함
open_canvas(1,1)
try:
    music = load_music('assets/theme.ogg')
    music.set_volume(64)
    music.repeat_play()
    print('playing: assets/theme.ogg')
except Exception as e:
    print('load/play failed:', e)

# 5초 동안 재생 대기
for i in range(5):
    print('tick', i+1)
    time.sleep(1)

try:
    music.stop()
    print('stopped')
except Exception:
    pass

close_canvas()
print('test: end')

