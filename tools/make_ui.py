#!/usr/bin/env python3
"""Draws the UNSC look of the kit window and converts it to PAA.

    python tools/make_ui.py

- addons/gui/ui/gloss_pouch_ca.paa, gloss_contents_ca.paa: the glass over EFAK's two windows -
  HUD frame corners, a rim, faint scan lines and a hex field. Drawn at each window's true shape
  (sizes from EFAK's addons/gui/defines.hpp, as EFAK's own generate_ui_textures.py does) and squeezed
  into the texture; the game stretches it back.
- addons/kits/ui/<kit>_bg_ca.paa: the artwork behind a kit's contents list - the kit's own render,
  faded into the glass as a cyan hologram, with its designation.
- logo.paa for mod.cpp.

The kit renders come from tools/models/build_kit.py (tools/models/out/<kit>/<kit>_icon.png).
"""
import math
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, ".."))
IMAGE_TO_PAA = r"D:\Steam\steamapps\common\Arma 3 Tools\ImageToPAA\ImageToPAA.exe"
CYAN = (92, 209, 245)

KITS = {
    "ifak": ("IFAK", "INDIVIDUAL FIRST AID KIT"),
    "afak": ("AFAK", "TRAUMA KIT"),
    "mfak": ("MFAK", "MULTI-CASUALTY MEDICAL SUPPLY"),
    "mfakplus": ("MFAK+", "FIELD MEDIC RESUPPLY"),
    "narcbox": ("NARC", "CONTROLLED SUBSTANCES"),
    "utility_pouch": ("UTIL", "UTILITY POUCH"),
    "ammo_pouch": ("AMMO", "DOUBLE MAGAZINE POUCH"),
    "ammo_bag": ("AMMO", "AMMUNITION CRATE  600 RDS"),
    "engineer_bag": ("ENG", "COMBAT ENGINEER TOOL SET"),
    "cbrn_bag": ("CBRN", "DECON & PROTECTION KIT"),
}
EUP = ("utility_pouch", "ammo_pouch", "ammo_bag", "engineer_bag", "cbrn_bag")


def font(size, weight="Bold"):
    f = ImageFont.truetype("bahnschrift.ttf", size)
    try:
        f.set_variation_by_name(weight + " Condensed")
    except (OSError, ValueError):
        f.set_variation_by_name(weight)
    return f


def hexfield(w, h, cell, alpha_img):
    """Hex grid lines, faded by alpha_img (L)."""
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    r = cell
    dx = r * math.sqrt(3)
    y = 0
    row = 0
    while y < h + r:
        x = (dx / 2 if row % 2 else 0)
        while x < w + dx:
            pts = [(x + r * math.cos(math.radians(60 * k + 30)), y + r * math.sin(math.radians(60 * k + 30)))
                   for k in range(6)]
            d.polygon(pts, outline=255, width=max(1, int(r * 0.06)))
            x += dx
        y += r * 1.5
        row += 1
    return ImageChops.multiply(im, alpha_img)


def gloss(tex_w, tex_h, width, height, radius, screen_h, label):
    scale = 4096 / max(width, height)
    w, h = round(width * scale), round(height * scale)
    px = h / screen_h          # one screen pixel at 1080p, in drawing pixels
    r = radius * scale
    a = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(a)

    # rim
    shape = Image.new("L", (w, h), 0)
    ImageDraw.Draw(shape).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    inner = Image.new("L", (w, h), 0)
    e = 1.2 * px
    ImageDraw.Draw(inner).rounded_rectangle([e, e, w - 1 - e, h - 1 - e], radius=max(r - e, 0), fill=255)
    ring = ImageChops.subtract(shape, inner).point(lambda v: v * 0.22)
    a = ImageChops.add(a, ring)
    d = ImageDraw.Draw(a)

    # HUD corner brackets, with a cut corner
    m = 7 * px
    L = min(w, h) * 0.07
    t = 2.2 * px
    c = L * 0.28
    for sx, sy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        x0 = m if sx == 0 else w - m
        y0 = m if sy == 0 else h - m
        dx = 1 if sx == 0 else -1
        dy = 1 if sy == 0 else -1
        pts = [(x0, y0 + dy * L), (x0, y0 + dy * c), (x0 + dx * c, y0), (x0 + dx * L, y0)]
        d.line(pts, fill=150, width=round(t), joint="curve")
        # small tick past the bracket
        d.line([(x0 + dx * (L + 4 * px), y0), (x0 + dx * (L + 10 * px), y0)], fill=90, width=round(t))

    # tick marks along the top, centred
    for k in range(-12, 13):
        x = w / 2 + k * 9 * px
        ln = (6 if k % 4 == 0 else 3) * px
        d.line([(x, m), (x, m + ln)], fill=60 if k % 4 else 95, width=max(1, round(px)))

    # scan lines over the glass
    scan = Image.new("L", (1, h), 0)
    step = max(2, round(3 * px))
    for y in range(0, h, step):
        scan.putpixel((0, y), 7)
    scan = ImageChops.multiply(scan.resize((w, h), Image.NEAREST), inner)
    a = ImageChops.add(a, scan)

    # sheen along the top, like EFAK's glass, a touch cooler
    sheen = Image.new("L", (1, h))
    sh = min(h * 0.4, 6.5 * scale)
    for y in range(h):
        sheen.putpixel((0, y), round(255 * 0.04 * max(0.0, 1 - y / sh) ** 1.6))
    a = ImageChops.add(a, ImageChops.multiply(sheen.resize((w, h), Image.NEAREST), inner))

    # hex field fading in from the lower right
    # distance from the lower right corner, as a fade: full there, gone by 60% of the diagonal
    small = Image.new("L", (64, 64))
    for yy in range(64):
        for xx in range(64):
            dist = math.hypot(63 - xx, 63 - yy) / (63 * math.sqrt(2) * 0.6)
            small.putpixel((xx, yy), round(255 * max(0.0, 1 - dist) ** 1.5))
    grad = small.resize((w, h), Image.BICUBIC)
    hexes = hexfield(w, h, 14 * px, grad.point(lambda v: v * 0.10))
    a = ImageChops.add(a, ImageChops.multiply(hexes, inner))

    # designation, bottom left
    d = ImageDraw.Draw(a)
    d.text((m + 14 * px, h - m - 5 * px), label, font=font(round(11 * px), "SemiBold"), fill=70, anchor="ls")

    rgb = Image.new("RGB", (w, h), CYAN)
    im = Image.merge("RGBA", (*rgb.split(), a))
    return im.resize((tex_w, tex_h), Image.LANCZOS)


def kit_background(kit):
    """The kit's render as a faint cyan hologram behind its contents list (LIST_W x LIST_H, about
    17.5 x 18 rows)."""
    w = h = 1024
    src = os.path.join(HERE, "models", "out", kit, kit + "_icon.png")
    a = Image.new("L", (w, h), 0)
    if os.path.isfile(src):
        icon = Image.open(src).convert("RGBA").resize((760, 760), Image.LANCZOS)
        lum = ImageOps.autocontrast(icon.convert("L"))
        alpha = ImageChops.multiply(lum, icon.getchannel("A")).point(lambda v: v * 0.11)
        # scan lines through the hologram
        lines = Image.new("L", (1, 760), 255)
        for y in range(0, 760, 4):
            lines.putpixel((0, y), 120)
        alpha = ImageChops.multiply(alpha, lines.resize((760, 760), Image.NEAREST))
        a.paste(alpha, (132, 150))
        # a soft outline glow
        edge = icon.getchannel("A").filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(2))
        a = ImageChops.add(a, Image.new("L", (w, h), 0))
        glow = Image.new("L", (w, h), 0)
        glow.paste(edge.point(lambda v: v * 0.25), (132, 150))
        a = ImageChops.add(a, glow)
    d = ImageDraw.Draw(a)
    name, sub = KITS[kit]
    d.text((w - 40, h - 70), name, font=font(84, "Bold"), fill=34, anchor="rs")
    d.text((w - 40, h - 36), sub, font=font(26, "SemiBold"), fill=30, anchor="rs")
    d.line([(w - 420, h - 120), (w - 40, h - 120)], fill=26, width=2)
    rgb = Image.new("RGB", (w, h), CYAN)
    return Image.merge("RGBA", (*rgb.split(), a))


def logo():
    s = 512
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    oct_ = [(s * x, s * y) for x, y in ((0.3, 0.04), (0.7, 0.04), (0.96, 0.3), (0.96, 0.7), (0.7, 0.96),
                                        (0.3, 0.96), (0.04, 0.7), (0.04, 0.3))]
    d.polygon(oct_, fill=(58, 64, 42, 255), outline=(222, 196, 64, 255), width=10)
    d.rectangle([s * 0.41, s * 0.2, s * 0.59, s * 0.62], fill=(236, 236, 228, 255))
    d.rectangle([s * 0.23, s * 0.32, s * 0.77, s * 0.5], fill=(236, 236, 228, 255))
    d.text((s / 2, s * 0.82), "UNSC", font=font(104, "Bold"), fill=(222, 196, 64, 255), anchor="mm")
    return im


def to_paa(im, paa):
    tmp = os.path.join(tempfile.mkdtemp(), os.path.splitext(os.path.basename(paa))[0] + ".png")
    im.save(tmp)
    os.makedirs(os.path.dirname(paa), exist_ok=True)
    subprocess.run([IMAGE_TO_PAA, tmp, paa], check=True, capture_output=True)
    shutil.copyfile(tmp, os.path.join(HERE, "models", "out", os.path.basename(tmp)))
    print("wrote", os.path.relpath(paa, REPO))


def main():
    os.makedirs(os.path.join(HERE, "models", "out"), exist_ok=True)
    ui = os.path.join(REPO, "addons", "gui", "ui")
    to_paa(gloss(1024, 1024, 1.1 * 37 / 0.95, 36, 0.6, 36 * 0.95 * 1080 / 37, "UNSC // MED CORPS  FIELD INVENTORY"),
           os.path.join(ui, "gloss_pouch_ca.paa"))
    to_paa(gloss(512, 1024, 14.9, 23.05, 0.6, 23.05 * 1080 / 40, "UNSC // CONTENTS"),
           os.path.join(ui, "gloss_contents_ca.paa"))
    for kit in KITS:
        addon = "eup" if kit in EUP else "kits"
        to_paa(kit_background(kit), os.path.join(REPO, "addons", addon, "ui", kit + "_bg_ca.paa"))
    to_paa(logo(), os.path.join(REPO, "logo_ca.paa"))
    os.replace(os.path.join(REPO, "logo_ca.paa"), os.path.join(REPO, "logo.paa"))


if __name__ == "__main__":
    main()
