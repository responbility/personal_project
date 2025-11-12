# game_world.py

# 게임 객체를 저장하는 레이어 리스트
objects = []
NUM_LAYERS = 2  # 0: 배경, 1: 캐릭터/몬스터 등으로 사용


def init():
    """게임 월드를 초기화하고 레이어를 준비합니다."""
    global objects
    objects = [[] for _ in range(NUM_LAYERS)]


def add_object(obj, layer):
    """객체를 지정된 레이어에 추가합니다."""
    if layer >= NUM_LAYERS:
        # 레이어 수가 부족하면 확장
        while len(objects) <= layer:
            objects.append([])
    objects[layer].append(obj)


def update():
    """모든 객체의 update() 메서드를 호출합니다."""
    for layer in objects:
        for obj in layer:
            if hasattr(obj, 'update'):
                obj.update()


def draw():
    """모든 객체의 draw() 메서드를 호출합니다."""
    for layer in objects:
        for obj in layer:
            if hasattr(obj, 'draw'):
                obj.draw()


def clear():
    """모든 객체를 제거합니다."""
    global objects
    for layer in objects:
        layer.clear()
    init()


# 모듈이 로드될 때 바로 초기화
init()