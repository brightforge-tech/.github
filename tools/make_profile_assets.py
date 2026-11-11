"""BrightForge org-profile assets: banner (1280x400), square avatar, logos.

Usage: python tools/make_profile_assets.py <path to brightforge logo png>
Needs Sora + Manrope variable TTFs (SIL OFL) in $FONTS_DIR.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "profile", "assets")
FONTS = os.environ["FONTS_DIR"]
SORA = os.path.join(FONTS, "Sora%5Bwght%5D.ttf")
MANROPE = os.path.join(FONTS, "Manrope%5Bwght%5D.ttf")

TEAL = (53, 178, 190)
ORANGE_LIFT = (224, 122, 69)
SLATE = (15, 19, 22)
SLATE2 = (26, 33, 38)
CREAM = (242, 239, 233)
GREY = (174, 183, 188)
MUTED = (110, 122, 128)

os.makedirs(OUT, exist_ok=True)
logo = Image.open(SRC).convert("RGBA")
logo = logo.crop(logo.getbbox())


def dark_variant(im):
    out = im.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a and max(r, g, b) < 70:
                px[x, y] = (*CREAM, a)
    return out


def fit_w(im, w):
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def font(path, size, weight):
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


# ---- logos ----
light = fit_w(logo, 720)
dark = dark_variant(light)
light.save(os.path.join(OUT, "brightforge-logo.png"), optimize=True)
dark.save(os.path.join(OUT, "brightforge-logo-dark.png"), optimize=True)

# ---- avatar: the round mark on white, square ----
# The mark is the left part of the lockup: a circle as tall as the image.
mark = logo.crop((0, 0, logo.height, logo.height))
mark = mark.crop(mark.getbbox())
A = 1024
avatar = Image.new("RGBA", (A, A), (255, 255, 255, 255))
m = mark.resize((round(A * 0.8), round(A * 0.8 * mark.height / mark.width)), Image.LANCZOS)
avatar.paste(m, ((A - m.width) // 2, (A - m.height) // 2), m)
avatar.convert("RGB").save(os.path.join(OUT, "brightforge-avatar.png"), optimize=True)

# ---- banner ----
W, H, S = 1280, 400, 2
img = Image.new("RGB", (W * S, H * S), SLATE)
d = ImageDraw.Draw(img)
for y in range(H * S):
    t = y / (H * S)
    d.line([(0, y), (W * S, y)], fill=tuple(round(SLATE[i] + (SLATE2[i] - SLATE[i]) * t) for i in range(3)))

glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse([60 * S, 40 * S, 420 * S, 360 * S], fill=(*TEAL, 55))
glow = glow.filter(ImageFilter.GaussianBlur(80 * S))
img.paste(glow, (0, 0), glow)

lock = fit_w(dark_variant(logo), 470 * S)
img.paste(lock, (70 * S, (H * S - lock.height) // 2), lock)

d = ImageDraw.Draw(img)
x0 = 640 * S
d.text((x0, 92 * S), "SHAPING INNOVATION · FORGING THE FUTURE", font=font(SORA, 14 * S, 600), fill=TEAL)
d.text((x0, 122 * S), "Technology built side by side\nwith the people who run it.",
       font=font(SORA, 34 * S, 700), fill=CREAM, spacing=8 * S)
d.text((x0, 228 * S), "Custom software  ·  Consulting  ·  BrightForge Labs",
       font=font(MANROPE, 20 * S, 600), fill=ORANGE_LIFT)
d.text((x0, 270 * S), "Business systems, automation and AI for organisations\nthat need them to work.",
       font=font(MANROPE, 17 * S, 500), fill=GREY, spacing=6 * S)
img = img.resize((W, H), Image.LANCZOS)
ImageDraw.Draw(img).text((640, 352), "brightforgett.com", font=font(MANROPE, 15, 600), fill=MUTED)
img.save(os.path.join(OUT, "brightforge-banner.png"), optimize=True)
print("ok", sorted(os.listdir(OUT)))
