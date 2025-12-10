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
    """간단한 AABB 충돌 검사를 수행하고 on_collision/handle_collision을 호출합니다."""
    all_objs = list(all_objects())

    # 기존 projectile/enemy/boy, Ball-Guard 충돌 로직 그대로 유지
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

    # Ball -> Guard 충돌 (Ratking이 쏜 공이 경비에게 맞는 경우)
    from ball import Ball
    balls = [o for o in all_objs if isinstance(o, Ball)]
    guards = [o for o in all_objs if o.__class__.__name__.lower() == 'guard']

    for b in balls:
        b_bb = aabb(b)
        if b_bb is None:
            continue
        bx1, by1, bx2, by2 = b_bb
        for g in guards:
            g_bb = aabb(g)
            if g_bb is None:
                continue
            gx1, gy1, gx2, gy2 = g_bb
            if not (bx2 < gx1 or bx1 > gx2 or by2 < gy1 or by1 > gy2):
                try:
                    if hasattr(g, 'handle_collision'):
                        g.handle_collision(b)
                except Exception:
                    pass

    # Guard -> Ratking 충돌 (경비가 Ratking을 잡으면 게임 종료)
    ratkings = [o for o in all_objs if o.__class__.__name__.lower() == 'ratking']

    for g in guards:
        g_bb = aabb(g)
        if g_bb is None:
            continue
        gx1, gy1, gx2, gy2 = g_bb
        for rk in ratkings:
            rk_bb = aabb(rk) if hasattr(rk, 'get_bb') else None
            # Ratking에 get_bb가 없다면 간단히 화면 좌표 기준으로 박스를 만들어 사용
            if rk_bb is None:
                half_w, half_h = 16 * 2, 16 * 2  # Ratking SCALE=4.0 기준 대략적인 크기
                rk_bb = (rk.x - half_w, rk.y - half_h, rk.x + half_w, rk.y + half_h)

            rx1, ry1, rx2, ry2 = rk_bb
            if not (gx2 < rx1 or gx1 > rx2 or gy2 < ry1 or gy1 > ry2):
                # 충돌 발생: Guard가 Ratking을 잡은 것으로 간주하고 게임 종료
                print("[Collision] Guard caught Ratking -> quit game")
                game_framework.quit()

    # ...existing other collision logic...
