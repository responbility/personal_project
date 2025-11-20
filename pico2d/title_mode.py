# title_mode.py (임시 시작 모드)

from pico2d import *
import game_framework

# 캔버스 크기 (main.py에서 설정된 576x1024)
CANVAS_W, CANVAS_H = 576, 1024


class TitleMode:
    name = "TITLE_MODE"  # 디버그용 이름

    # 폰트 로드는 클래스 변수로 한 번만
    font = None

    def init(self):
        print(f"[{self.name}] - 초기화")
        try:
            # assets 폴더 또는 루트에서 폰트 로드 시도
            self.font = load_font('ENCR10B.TTF', 24)
        except Exception as e:
            print(f"폰트 로드 실패: {e}. 기본 폰트로 폴백.")
            self.font = None

        # TitleMode가 다음 모드(play_mode)로 전환하는 이벤트 처리
        # 여기서는 스페이스바를 누르면 다음 모드로 넘어간다고 가정
        # (다음 모드 파일이 없으므로, 현재는 넘어가지 않음)

    def finish(self):
        print(f"[{self.name}] - 종료")
        # 여기서 사용된 리소스를 해제할 수 있습니다.
        pass

    def handle_events(self):
        events = get_events()
        for event in events:
            if event.type == SDL_QUIT:
                game_framework.quit()
            # 스페이스바를 누르면 다음 모드(play_mode)로 전환 시도
            elif event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
                # 다음 모드(예: play_mode)로 변경
                # play_mode가 없으므로 일단 아무것도 안 합니다.
                print("스페이스바 입력. 게임 시작 시도.")
                pass
            # Esc 키를 누르면 게임 종료
            elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                game_framework.quit()

    def update(self):
        # 이 모드에서는 업데이트할 것이 없습니다.
        pass

    def draw(self):
        # 1. 화면 지우기
        clear_canvas()

        # 2. 배경 그리기 (선택 사항 - 여기서는 그냥 검은색 배경)

        # 3. 텍스트 그리기
        if self.font:
            self.font.draw(CANVAS_W // 2 - 120, CANVAS_H // 2 + 50, '게임 시작', (255, 255, 255))
            self.font.draw(CANVAS_W // 2 - 180, CANVAS_H // 2, '(SPACE 키를 누르세요)', (255, 255, 0))
        else:
            # 폰트 로드 실패 시 폴백 (Fallback) 텍스트 그리기
            draw_rectangle(0, 0, CANVAS_W, CANVAS_H)  # 전체 화면에 사각형 그리기
            print(f'Warning: Cannot draw font, drawing fallback text.')
            # 여기서 더 이상의 텍스트 표시는 pico2d 폰트 로드 없이는 어렵습니다.
            # 캔버스가 제대로 플립되고 있는지 확인하려면, 이 상태에서 배경색이 바뀌는지 확인하세요.

        # 4. 화면 갱신
        update_canvas()


# TitleMode 클래스의 단일 인스턴스를 사용
init = TitleMode().init
finish = TitleMode().finish
handle_events = TitleMode().handle_events
update = TitleMode().update
draw = TitleMode().draw
name = TitleMode.name  # 모드 이름도 export