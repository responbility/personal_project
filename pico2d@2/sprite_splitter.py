from pico2d import *


# 이전에 정의된 함수를 그대로 사용합니다.
def split_sprite_sheet(image_path, sprite_width, sprite_height):
    """스프라이트 시트의 크기를 기준으로 각 스프라이트의 클립 영역을 계산합니다."""
    sprite_sheet = load_image(image_path)
    sheet_width, sheet_height = sprite_sheet.w, sprite_sheet.h

    sprites = []
    # y축을 따라 sprite_height 간격으로, x축을 따라 sprite_width 간격으로 클립 영역을 계산합니다.
    for y in range(0, sheet_height, sprite_height):
        for x in range(0, sheet_width, sprite_width):
            sprites.append((x, y, sprite_width, sprite_height))

    # clip_draw의 y 좌표는 이미지의 '아래쪽'을 기준으로 계산해야 합니다.
    final_sprites = []
    for x, y_start_top, width, height in sprites:
        # sheet_height - y_start_top - height 가 실제 바닥 기준 시작 Y 좌표입니다.
        y_start_bottom = sheet_sheet.h - y_start_top - height
        final_sprites.append((x, y_start_bottom, width, height))

    return final_sprites


# 특정 인덱스의 스프라이트만 그리는 함수로 수정
def draw_single_sprite(sprite_data, sprite_sheet, index):
    """지정된 인덱스의 스프라이트만 캔버스 중앙에 그립니다."""

    # 출력 크기 (원본보다 3배 확대)
    draw_width, draw_height = 16 * 3, 16 * 3

    # 캔버스 중앙 계산
    canvas_x = get_canvas_width() // 2
    canvas_y = get_canvas_height() // 2

    # sprites 리스트에서 해당 인덱스의 스프라이트 정보를 가져옵니다.
    try:
        # sprite는 (클립 x, 클립 y, 클립 너비, 클립 높이)
        clip_x, clip_y, clip_w, clip_h = sprite_data[index]
    except IndexError:
        print(f"Error: Index {index} is out of bounds for the sprite list.")
        return

    sprite_sheet.clip_draw(
        clip_x,
        clip_y,
        clip_w,
        clip_h,
        canvas_x,
        canvas_y,
        draw_width,
        draw_height
    )


if __name__ == "__main__":
    open_canvas(400, 300)  # 캔버스 크기를 단일 스프라이트에 맞게 조정

    # --- 설정 변경 ---
    sprite_sheet_path = 'ratking.png'  # ratking.png 사용
    sprite_width, sprite_height = 16, 16  # 각 스프라이트의 크기는 16x16

    # 🚨 출력할 스프라이트의 인덱스를 지정합니다. (0부터 시작)
    # ratking.png의 첫 번째 프레임을 출력하려면 index = 0
    SPRITE_INDEX_TO_DRAW = 0
    # ------------------

    try:
        sprites = split_sprite_sheet(sprite_sheet_path, sprite_width, sprite_height)
        sprite_sheet = load_image(sprite_sheet_path)

        clear_canvas()

        # 수정된 단일 출력 함수를 호출합니다.
        draw_single_sprite(sprites, sprite_sheet, SPRITE_INDEX_TO_DRAW)

        # 텍스트 정보 출력
        font = load_font('assets/ENCR10B.TTF', 16)
        font.draw(20, 270, f"ratking.png - Frame {SPRITE_INDEX_TO_DRAW} (16x16)", (255, 255, 255))

        update_canvas()

    except Exception as e:
        # 파일을 찾을 수 없거나 로드할 수 없을 때 에러 메시지 출력
        print(f"Error loading or drawing sprites: {e}")
        print(f"Please ensure '{sprite_sheet_path}' and 'assets/ENCR10B.TTF' are in the correct directory.")

    delay(5)
    close_canvas()