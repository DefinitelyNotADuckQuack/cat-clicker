import pygame

from assets import load_assets
from shop import shop_items
from music import (
    init_music,
    music_toggle,
    music_next,
    music_prev,
    update_music,
    music_is_enabled,
    music_is_paused,
)
from cat import create_cat, draw_cat, cat_hit_test, update_cat, equip_cosmetic

WIDTH, HEIGHT = 600, 700
SHOP_ORIGIN = (20, 570)
SHOP_BUTTON_SIZE = (130, 40)
MUSIC_BUTTON_POS = (460, 20)
MUSIC_BUTTON_SIZE = (120, 40)
TRACK_BTN_Y = 70
TRACK_BTN_W, TRACK_BTN_H = 50, 30
COSMETIC_SPACING = 10
COSMETIC_ICON_SIZE = (40, 40)
COSMETIC_STRIP_Y = 620


WHITE = (255, 255, 255)
LABEL_DARK = (50, 20, 20)
PINK = (255, 223, 243)
PINK_HOVER = (255, 200, 230)
SHADOW = (180, 180, 180)

screen = None
clock = None
assets = None

score = 0
owned = []              # items bought
placed = []             # decor placed in scene
item_positions = {}     # name -> (x, y)
selected_decor = None   # currently dragged decor
clicked_button_name = None  # last pressed button name

# cat bundle
cat = {
    "rect": None,
    "clicked": False,
    "click_time": 0,
    "is_blinking": False,
    "blink_start": 0,
    "next_blink_ms": 4000,
    "active": {"head": None, "body": None},
}

def draw_label(text, pos, fancy_font):
    # simple shadowed label for contrast
    screen.blit(fancy_font.render(text, True, WHITE), (pos[0] + 1, pos[1] + 1))
    screen.blit(fancy_font.render(text, True, LABEL_DARK), pos)


def draw_button(rect: pygame.Rect, text: str, button_font: pygame.font.Font):
    # shadow border
    pygame.draw.rect(screen, SHADOW, rect.move(2, 2), border_radius=10)
    # body
    hovered = rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, PINK_HOVER if hovered else PINK, rect, border_radius=10)
    # text with slight white offset for “emboss”
    label = button_font.render(text, True, (60, 30, 50))
    outline = button_font.render(text, True, WHITE)
    lrect = label.get_rect(center=rect.center)
    screen.blit(outline, lrect.move(1, 1))
    screen.blit(label, lrect)


def draw_icon_button_rect(rect: pygame.Rect, icon_surf: pygame.Surface):
    # shadow border
    pygame.draw.rect(screen, SHADOW, rect.move(2, 2), border_radius=8)
    # background
    hovered = rect.collidepoint(pygame.mouse.get_pos())
    bg = (255, 255, 255) if hovered else (220, 220, 220)
    pygame.draw.rect(screen, bg, rect, border_radius=8)
    # center the icon inside the rect
    icon_rect = icon_surf.get_rect()
    icon_rect.center = rect.center
    screen.blit(icon_surf, icon_rect.topleft)


def cosmetic_button_rect(x: int, y: int) -> pygame.Rect:
    pad = 6
    w, h = COSMETIC_ICON_SIZE
    return pygame.Rect(x - pad, y - pad, w + pad * 2, h + pad * 2)


def get_cheapest_items(n=4):
    remaining = {k: v for k, v in shop_items.items() if k not in owned}
    return [k for k, _ in sorted(remaining.items(), key=lambda kv: kv[1]["price"])[:n]]


def run_game():
    global screen, clock, assets
    global score, owned, placed, item_positions, selected_decor, clicked_button_name
    global cat

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cat Clicker")
    clock = pygame.time.Clock()

    # assets (images, fonts, sounds)
    assets = load_assets(WIDTH, HEIGHT)
    if assets["icon"]:
        pygame.display.set_icon(assets["icon"])

    # music system on/off depending on mixer
    init_music()

    # cat setup
    cat = create_cat(assets["cat_idle"], center=(WIDTH // 2, 350))

    items_to_show = get_cheapest_items()
    running = True

    while running:
        screen.blit(assets["background"], (0, 0))
        buttons_this_frame = []
        ui_draw_list = []

        # Shop buttons
        if items_to_show:
            ui_draw_list.append(("label", pygame.Rect(20, 520, 0, 0), "Shop"))

        x, y = SHOP_ORIGIN
        w, h = SHOP_BUTTON_SIZE
        for i, name in enumerate(items_to_show):
            if name in owned:
                continue
            rect = pygame.Rect(x, y, w, h)
            buttons_this_frame.append((rect, name))
            ui_draw_list.append(("shop", rect, name))
            x += w + 10
            if (i + 1) % 4 == 0:
                x, y = SHOP_ORIGIN[0], y + h + 10

        # Music buttons
        mbtn = pygame.Rect(*MUSIC_BUTTON_POS, *MUSIC_BUTTON_SIZE)
        buttons_this_frame.append((mbtn, "toggle_music"))
        ui_draw_list.append(("music_toggle", mbtn, None))

        prevb = pygame.Rect(460, TRACK_BTN_Y, TRACK_BTN_W, TRACK_BTN_H)
        nextb = pygame.Rect(530, TRACK_BTN_Y, TRACK_BTN_W, TRACK_BTN_H)
        buttons_this_frame.extend([(prevb, "prev_track"), (nextb, "next_track")])
        ui_draw_list.append(("music_prev", prevb, None))
        ui_draw_list.append(("music_next", nextb, None))

        # Cosmetics bar buttons
        xi = 20
        yi = COSMETIC_STRIP_Y
        for nm in [n for n in owned if shop_items[n]["type"] == "cosmetic"]:
            ic = assets["cosmetic_icons"].get(nm)
            if not ic:
                continue
            rect = cosmetic_button_rect(xi, yi)
            buttons_this_frame.append((rect, f"equip:{nm}"))
            ui_draw_list.append(("equip", rect, nm))
            # add icon width + spacing to x
            xi += COSMETIC_ICON_SIZE[0] + COSMETIC_SPACING + 12  # 12 = padding inside button_rect
            if xi > screen.get_width() - COSMETIC_ICON_SIZE[0]:
                xi = 20
                yi += COSMETIC_ICON_SIZE[1] + COSMETIC_SPACING + 12

        # ---------------- events ----------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # remember which button was pressed
                clicked_button_name = None
                for rect, name in buttons_this_frame:
                    if rect.collidepoint((mx, my)):
                        clicked_button_name = name
                        break

                # cat click -> +1 treat
                if cat_hit_test(cat, assets, (mx, my)):
                    cat["clicked"] = True
                    cat["click_time"] = pygame.time.get_ticks()
                    score += 1
                    continue

                # decor picking
                for nm in placed:
                    img = assets["decor_images"].get(nm)
                    if not img:
                        continue
                    r = pygame.Rect(item_positions[nm], img.get_size())
                    if r.collidepoint((mx, my)):
                        lx, ly = mx - r.x, my - r.y
                        if 0 <= lx < img.get_width() and 0 <= ly < img.get_height() and img.get_at((lx, ly)).a > 0:
                            selected_decor = nm
                            if assets["pickup_sound"]:
                                assets["pickup_sound"].play()
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                mx, my = event.pos
                if clicked_button_name:
                    for rect, name in buttons_this_frame:
                        if name == clicked_button_name and rect.collidepoint((mx, my)):
                            if name == "toggle_music":
                                music_toggle()
                            elif name == "prev_track":
                                music_prev()
                            elif name == "next_track":
                                music_next()
                            elif name.startswith("equip:"):
                                # equip/unequip cosmetic via button
                                cosmetic_name = name.split(":", 1)[1]
                                equip_cosmetic(cat, cosmetic_name)
                            else:
                                # buy flow
                                itm = name
                                price = shop_items[itm]["price"]
                                if itm not in owned and score >= price:
                                    owned.append(itm)
                                    score -= price
                                    if assets["buy_sound"]:
                                        assets["buy_sound"].play()
                                    if shop_items[itm]["type"] == "decor":
                                        placed.append(itm)
                                        item_positions[itm] = (WIDTH // 2, 400)
                                        selected_decor = itm
                                    else:
                                        # cosmetic: equip immediately, it will appear in the bar
                                        equip_cosmetic(cat, itm)
                                    items_to_show = get_cheapest_items()
                            break
                    clicked_button_name = None
                selected_decor = None

            elif event.type == pygame.MOUSEMOTION:
                if selected_decor:
                    img = assets["decor_images"].get(selected_decor)
                    if img:
                        item_positions[selected_decor] = (
                            event.pos[0] - img.get_width() // 2,
                            event.pos[1] - img.get_height() // 2,
                        )

            elif event.type == pygame.KEYDOWN:
                pass

        # ---------------- updates ----------------
        # release happy face after a short delay
        if cat["clicked"] and pygame.time.get_ticks() - cat["click_time"] > 200:
            cat["clicked"] = False

        update_music()
        update_cat(cat)  # blink update

        # ---------------- world draw ----------------
        draw_cat(screen, assets, cat)

        # placed decors
        for nm in placed:
            img = assets["decor_images"].get(nm)
            if img:
                screen.blit(img, item_positions.get(nm, (0, 0)))

        # HUD
        draw_label(f"Treats: {score}", (20, 20), assets["fancy_font"])

        # ---------------- draw UI----------------
        for kind, rect, payload in ui_draw_list:
            if kind == "label":
                draw_label(payload, (rect.x, rect.y), assets["fancy_font"])
            elif kind == "shop":
                draw_button(rect, f"{payload.title()} ({shop_items[payload]['price']})", assets["button_font"])
            elif kind == "music_toggle":
                mlabel = "Music On" if (music_is_enabled() and not music_is_paused()) else "Music Off"
                draw_button(rect, mlabel, assets["button_font"])
            elif kind == "music_prev":
                draw_button(rect, "<<", assets["button_font"])
            elif kind == "music_next":
                draw_button(rect, ">>", assets["button_font"])
            elif kind == "equip":
                icon = assets["cosmetic_icons"].get(payload)
                if icon:
                    draw_icon_button_rect(rect, icon)

        # Hand indicator while clicked
        if cat["clicked"] and assets["hand_image"]:
            screen.blit(assets["hand_image"], (cat["rect"].centerx - 80, cat["rect"].centery - 190))

        pygame.display.flip()
        clock.tick(60)
