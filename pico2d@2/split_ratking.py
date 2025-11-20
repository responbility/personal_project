from pico2d import *

def main():
    open_canvas()

    # Load images
    grass = load_image('assets/terrain_features.png')
    ratking = load_image('assets/ratking.png')

    # Ratking sprite sheet dimensions
    sprite_width = 32  # Width of each sprite
    sprite_height = 32  # Height of each sprite
    sprites_per_row = 8  # Number of sprites in a row
    total_rows = 2  # Total number of rows

    frame = 0
    for x in range(0, 800, 10):
        clear_canvas()
        grass.draw(400, 30)

        # Calculate sprite position in the sheet
        row = frame // sprites_per_row
        col = frame % sprites_per_row
        clip_x = col * sprite_width
        clip_y = (total_rows - 1 - row) * sprite_height

        ratking.clip_draw(clip_x, clip_y, sprite_width, sprite_height, x, 90)

        update_canvas()
        frame = (frame + 1) % (sprites_per_row * total_rows)
        delay(0.05)

    close_canvas()

if __name__ == '__main__':
    main()
