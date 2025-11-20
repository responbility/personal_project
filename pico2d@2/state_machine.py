class StateMachine:
    """
    게임 객체의 상태를 관리하고 이벤트에 따라 상태를 전이시키는 범용 상태 머신 클래스입니다.
    """

    def __init__(self, start_state, transition_table):
        self.cur_state = start_state
        self.transitions = transition_table  # {현재_상태: {이벤트: 다음_상태}}

    def start(self):
        """상태 머신을 시작합니다. 현재 상태의 enter()를 호출합니다."""
        self.cur_state.enter(('START', None))

    def update(self):
        """현재 상태의 do() 함수를 호출합니다."""
        self.cur_state.do()

    def draw(self):
        """현재 상태의 draw() 함수를 호출합니다."""
        self.cur_state.draw()

    def handle_state_event(self, event):
        """이벤트를 처리하고 상태 전이를 시도합니다."""
        # event는 ('이벤트_이름', 데이터) 형태 (예: ('INPUT', event_data))
        event_name = event[0]

        # 현재 상태에서 처리 가능한 전이 테이블 확인
        if self.cur_state in self.transitions:
            for event_condition, next_state in self.transitions[self.cur_state].items():

                # 이벤트 조건 검사 (함수 또는 람다)
                if event_condition(event):
                    # 상태 전이 실행
                    self.change_state(next_state, event)
                    return True  # 상태 전이 성공

        # 상태 전이가 일어나지 않은 경우, 현재 상태의 handle_event 호출 (선택적)
        if hasattr(self.cur_state, 'handle_event'):
            self.cur_state.handle_event(event)

        return False  # 상태 전이 실패

    def change_state(self, new_state, event):
        """상태를 변경합니다: exit -> enter 호출"""
        self.cur_state.exit(event)
        self.cur_state = new_state
        self.cur_state.enter(event)