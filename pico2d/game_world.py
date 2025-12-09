# game_world.py

from pico2d import *
import game_framework
import sys

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
    except Exception as e:
        # print(f"ERROR in check_collisions: {e}", file=sys.stderr)
        pass


def draw():
    """모든 객체의 draw() 메서드를 호출합니다."""
    for layer in objects:
        for o in layer:
            if hasattr(o, 'draw'):
                o.draw()


def clear():
    """모든 객체를 제거합니다."""
    global objects
    for layer in objects:
        layer.clear()
    init()


def remove_object(obj):
    """지정된 객체를 월드에서 제거합니다."""
    for layer in objects:
        if obj in layer:
            layer.remove(obj)
            return

    # 충돌 쌍에서도 제거 (선택 사항, 충돌 로직 복잡성에 따라 다름)
    for name, pair in list(collision_pairs.items()):
        if obj in pair:
            del collision_pairs[name]
            return


def add_collision_pair(a, b, group_name):
    """충돌 쌍을 추가합니다."""
    collision_pairs[group_name] = (a, b)


def all_objects():
    """모든 레이어의 모든 객체를 반환합니다."""
    for layer in objects:
        for obj in layer:
            yield obj


def aabb(obj):
    """객체의 AABB (Axis-Aligned Bounding Box)를 반환합니다."""
    if hasattr(obj, 'get_bb'):
        return obj.get_bb()
    return None


# =========================================================================
# 충돌 처리 관련 함수 (기존 코드에서 그대로 유지)
# =========================================================================

def check_collisions():
    """간단한 AABB 충돌 검사를 수행하고 on_collision을 호출합니다."""
    all_objs = list(all_objects())

    # Example 1: Projectile -> Enemy collision
    projectiles = [o for o in all_objs if o.__class__.__name__.lower() == 'projectile']
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
                        e.handle_collision(b)
                    if hasattr(b, 'handle_collision'):
                        b.handle_collision(e)
                except Exception:
                    pass

    # ... (다른 충돌 로직이 있다면 여기에 추가)