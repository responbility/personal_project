# state_machine.py

class StateMachine:
    def __init__(self, start_state, transition_table):
        self.current_state = start_state
        self.transition_table = transition_table

    def start(self):
        """상태 머신을 시작하고 초기 상태로 진입합니다."""
        if self.current_state:
            self.current_state.enter(('START', 0))

    def update(self):
        """현재 상태의 do 메서드를 호출합니다."""
        # 🚨 self.current_state 사용 (오타 수정됨) 🚨
        if self.current_state:
            self.current_state.do()

    def draw(self):
        """현재 상태의 draw 메서드를 호출합니다."""
        # 🚨 self.current_state 사용 (오타 수정됨) 🚨
        if self.current_state:
            self.current_state.draw()

    def handle_state_event(self, event):
        """이벤트를 받아 상태 전이를 처리합니다."""
        state_name = self.current_state.__class__

        if state_name in self.transition_table:
            transitions = self.transition_table[state_name]

            for check_func, next_state in transitions.items():
                if check_func(event):
                    self.current_state.exit(event)
                    self.current_state = next_state
                    self.current_state.enter(event)
                    return True

        return False