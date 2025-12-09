from pico2d import load_image, open_canvas, close_canvas

open_canvas()
img = load_image('assets/ratking.png')
print('ratking.png size =', img.w, 'x', img.h)
close_canvas()
