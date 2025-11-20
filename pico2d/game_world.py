# game_world.py

# 게임 객체를 저장하는 레이어 리스트
objects = []
NUM_LAYERS = 2  # 0: 배경, 1: 캐릭터/몬스터 등으로 사용
collision_pairs = {}


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
        for obj in list(layer):
            if hasattr(obj, 'update'):
                obj.update()
    # 간단한 충돌 검사 호출
    try:
        check_collisions()
    except Exception:
        pass


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


def remove_object(obj):
    """레이어에서 객체를 찾아 제거합니다."""
    for layer in objects:
        if obj in layer:
            try:
                layer.remove(obj)
            except Exception:
                pass


def add_collision_pair(name, a, b):
    """간단한 충돌 페어 등록(사용자 코드가 호출할 수 있도록)"""
    collision_pairs[name] = (a, b)


def remove_collision_pair(name):
    try:
        if name in collision_pairs:
            del collision_pairs[name]
    except Exception:
        pass


def check_collisions():
    """
    간단한 AABB 기반 충돌 검사:
    - 투사체(projectile) vs 적(bat, guard): 투사체가 적에 충돌하면 투사체.on_collision(target) 호출
    - 적 vs 소년(boy): 적과 boy가 충돌하면 양쪽의 충돌 핸들러를 호출
    """
    # gather lists
    all_objs = []
    for layer in objects:
        for o in layer:
            all_objs.append(o)

    # helper aabb
    def aabb(a):
        if hasattr(a, 'get_bb'):
            try:
                return a.get_bb()
            except Exception:
                return None
        return None

    # find projectiles
    projectiles = [o for o in all_objs if o.__class__.__name__.lower().find('projectile') != -1]
    enemies = [o for o in all_objs if o.__class__.__name__.lower() in ('bat', 'guard')]
    boys = [o for o in all_objs if o.__class__.__name__.lower() == 'boy']

    # projectile -> enemy
    for p in projectiles:
        p_bb = aabb(p)
        if p_bb is None:
            continue
        for e in enemies:
            e_bb = aabb(e)
            if e_bb is None:
                continue
            # overlap?
            px1, py1, px2, py2 = p_bb
            ex1, ey1, ex2, ey2 = e_bb
            if not (px2 < ex1 or px1 > ex2 or py2 < ey1 or py1 > ey2):
                try:
                    if hasattr(p, 'on_collision'):
                        p.on_collision(e)
                except Exception:
                    pass

    # enemy -> boy
    for e in enemies:
        e_bb = aabb(e)
        if e_bb is None:
            continue
        for b in boys:
            b_bb = aabb(b)
            if b_bb is None:
                continue
            ex1, ey1, ex2, ey2 = e_bb
            bx1, by1, bx2, by2 = b_bb
            if not (ex2 < bx1 or ex1 > bx2 or ey2 < by1 or ey1 > by2):
                try:
                    if hasattr(e, 'handle_collision'):
                        e.handle_collision('enemy:boy', b)
                except Exception:
                    pass
                try:
                    if hasattr(b, 'handle_collision'):
                        b.handle_collision('boy:enemy', e)
                except Exception:
                    pass


# 모듈이 로드될 때 바로 초기화
init()