import pygame
import random

COSMETIC_SLOTS = {
    "hat": "head",
    "bow": "head",
    "minihat": "head",
    "littlebow": "head",
    "collar": "body",
    "bowtie": "body",
    "cape": "body",
}


def create_cat(cat_idle_surface, center):
    rect = cat_idle_surface.get_rect(center=center)
    return {
        "rect": rect,
        "clicked": False,
        "click_time": 0,
        "is_blinking": False,
        "blink_start": 0,
        "next_blink_ms": random.randint(3000, 7000),
        "active": {"head": None, "body": None},
    }


def equip_cosmetic(cat, name):
    slot = COSMETIC_SLOTS.get(name)
    if not slot:
        return
    cur = cat["active"].get(slot)
    cat["active"][slot] = None if cur == name else name


def cat_hit_test(cat, assets, pos):
    r = cat["rect"]
    if not r.collidepoint(pos):
        return False
    lx, ly = pos[0] - r.x, pos[1] - r.y
    surf = assets["cat_happy"] if cat["clicked"] else (assets["cat_blink"] if cat["is_blinking"] else assets["cat_idle"]) 
    if 0 <= lx < surf.get_width() and 0 <= ly < surf.get_height():
        return surf.get_at((lx, ly)).a > 0
    return False


def update_cat(cat):
    now = pygame.time.get_ticks()
    if cat["is_blinking"] and now - cat["blink_start"] > 150:
        cat["is_blinking"] = False
        cat["next_blink_ms"] = random.randint(3000, 7000)
    elif not cat["is_blinking"] and (now - cat.get("last_blink", 0)) > cat["next_blink_ms"]:
        cat["is_blinking"] = True
        cat["blink_start"] = now
        cat["last_blink"] = now


def draw_cat(screen, assets, cat):
    surf = assets["cat_happy"] if cat["clicked"] else (assets["cat_blink"] if cat["is_blinking"] else assets["cat_idle"]) 
    screen.blit(surf, cat["rect"])
    for slot, nm in cat["active"].items():
        if not nm:
            continue
        img = assets["cosmetic_images"].get(nm)
        off = assets["cosmetic_offsets"].get(nm)
        if img and off:
            pos = (cat["rect"].centerx + off[0], cat["rect"].centery + off[1])
            screen.blit(img, pos)