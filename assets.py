import os
import pygame

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))


def _path(*parts):
    return os.path.join(ASSETS_DIR, *parts)


def _load_image(p, size=None):
    try:
        img = pygame.image.load(p).convert_alpha()
        return pygame.transform.smoothscale(img, size) if size else img
    except Exception:
        s = pygame.Surface((1, 1), pygame.SRCALPHA)
        return s


def _load_sound(p, vol=0.3):
    try:
        s = pygame.mixer.Sound(p)
        s.set_volume(vol)
        return s
    except Exception:
        return None


def load_assets(W, H):
    assets = {}
    assets["icon"] = _load_image(_path("images", "pawn.jpg"))
    assets["background"] = _load_image(_path("images", "background.png"), (W, H))
    assets["cat_idle"] = _load_image(_path("images", "cat_idle.png"), (300, 300))
    assets["cat_happy"] = _load_image(_path("images", "cat_happy.png"), (300, 300))
    assets["cat_blink"] = _load_image(_path("images", "cat_blink.png"), (300, 300))
    assets["hand_image"] = _load_image(_path("images", "hand.png"), (250, 250))

    # cosmetics
    src = {
        "witch_hat": "hat",
        "collar": "collar",
        "bow": "bow",
        "bowtie": "bowtie",
        "cape": "cape",
        "minihat": "minihat",
        "littlebow": "littlebow",
    }
    assets["cosmetic_images"] = {}
    for k, shopk in src.items():
        img = _load_image(_path("images", f"{k}.png"), (300, 300))
        if img:
            assets["cosmetic_images"][shopk] = img

    # cosmetic icons and offsets
    assets["cosmetic_icons"] = {
        k: pygame.transform.smoothscale(v, (40, 40)) for k, v in assets["cosmetic_images"].items()
    }
    assets["cosmetic_offsets"] = {
        "hat": (-165, -260),
        "collar": (-150, -150),
        "bow": (-160, -250),
        "bowtie": (-150, -150),
        "cape": (-150, -150),
        "minihat": (-150, -260),
        "littlebow": (-150, -260),
    }

    # decor
    sizes = {
        "cat food": (200, 200),
        "can": (200, 200),
        "butterfly": (300, 300),
        "ball": (150, 150),
        "box": (300, 300),
        "yarn": (200, 200),
        "toy mouse": (300, 300),
        "catnip": (200, 200),
    }
    assets["decor_images"] = {}
    for n, sz in sizes.items():
        assets["decor_images"][n] = _load_image(_path("images", f"{n.replace(' ', '_')}.png"), sz)

    # fonts
    assets["fancy_font"] = pygame.font.Font("freesansbold.ttf", 25)
    assets["button_font"] = pygame.font.Font("freesansbold.ttf", 16)

    # sounds
    assets["buy_sound"] = _load_sound(_path("music", "sound effect", "sound-effect-twinklesparkle.mp3"))
    assets["pickup_sound"] = _load_sound(_path("music", "sound effect", "pickup.mp3"))
    return assets