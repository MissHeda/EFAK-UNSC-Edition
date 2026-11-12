"""Draws the decals the kit models carry: stencils, logos, labels. RGBA PNGs into out/decals/.

Run with a Python that has Pillow:  python tools/models/make_decals.py
build_kit.py (Blender) projects them onto the models while baking, so they end up in each kit's
texture. Everything is drawn at 2x and scaled down for clean edges.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "decals")
os.makedirs(OUT, exist_ok=True)
SS = 2

WHITE = (236, 236, 228, 255)
YELLOW = (222, 196, 64, 255)
RED = (196, 38, 34, 255)
DARK = (26, 28, 26, 255)
BLACK = (18, 18, 18, 255)


def font(size, weight="Bold", condensed=True):
    """Bahnschrift: a DIN-like military face that ships with Windows."""
    f = ImageFont.truetype("bahnschrift.ttf", size * SS)
    name = weight + (" Condensed" if condensed else "")
    try:
        f.set_variation_by_name(name)
    except (OSError, ValueError):
        f.set_variation_by_name(weight)
    return f


def canvas(w, h):
    return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))


def text(d, xy, s, f, fill, anchor="la", spacing=0):
    x, y = xy
    if spacing:
        for ch in s:
            d.text((x * SS, y * SS), ch, font=f, fill=fill, anchor=anchor)
            x += d.textlength(ch, font=f) / SS + spacing
        return
    d.text((x * SS, y * SS), s, font=f, fill=fill, anchor=anchor)


def rect(d, box, fill=None, outline=None, width=1):
    d.rectangle([c * SS for c in box], fill=fill, outline=outline, width=width * SS)


def poly(d, pts, fill):
    d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill)


def barcode(d, x, y, w, h, fill, seed=3):
    import random
    rnd = random.Random(seed)
    cx = x
    while cx < x + w:
        bw = rnd.choice((1, 1, 2, 3))
        if rnd.random() > 0.35:
            rect(d, (cx, y, cx + bw - 0.01, y + h), fill=fill)
        cx += bw + rnd.choice((1, 1, 2))


def stencil_wear(im, amount=0.35, seed=1):
    """Paint wear: knock holes into the alpha with blurred noise, like sprayed stencils that aged."""
    a = im.getchannel("A")
    n = ImageOps.autocontrast(Image.effect_noise(im.size, 90).filter(ImageFilter.GaussianBlur(2.2 * SS)))
    cut = n.point(lambda v: 0 if v > 255 * (1 - amount * 0.55) else 255)
    a = Image.composite(a, Image.new("L", im.size, 0), cut)
    im.putalpha(a)
    return im


def save(im, name, wear=0.0):
    w, h = im.size
    if wear:
        im = stencil_wear(im, wear)
    im = im.resize((w // SS, h // SS), Image.LANCZOS)
    im.save(os.path.join(OUT, name + ".png"))
    print("decal", name, im.size)


def unsc_mark(d, x, y, h, fill):
    """The service mark: a slanted bar block and the letters, all in one colour."""
    f = font(h, "Bold", condensed=False)
    # slanted bars
    sk = h * 0.42
    poly(d, [(x, y + h * 0.18), (x + h * 0.18, y + h * 0.18), (x + h * 0.18 + sk * 0.6, y + h * 0.86),
             (x + sk * 0.6, y + h * 0.86)], fill)
    bx = x + h * 0.32
    poly(d, [(bx, y + h * 0.18), (bx + h * 1.7, y + h * 0.18), (bx + h * 1.7, y + h * 0.86),
             (bx + sk * 0.6, y + h * 0.86)], fill)
    text(d, (bx + h * 1.85, y + h * 0.5), "UNSC", f, fill, anchor="lm")


# --- UNSC service mark, white, for crates ------------------------------------------------------
im = canvas(560, 120)
d = ImageDraw.Draw(im)
unsc_mark(d, 6, 10, 100, WHITE)
save(im, "unsc_white", wear=0.30)

# --- Medical mark: white square, red frame, red H (the field medkit's mark) ----------------------
im = canvas(256, 256)
d = ImageDraw.Draw(im)
rect(d, (6, 6, 250, 250), fill=(232, 230, 224, 255))
rect(d, (14, 14, 242, 242), outline=RED, width=7)
# H made of three bars, slightly condensed
rect(d, (68, 52, 104, 204), fill=RED)
rect(d, (152, 52, 188, 204), fill=RED)
rect(d, (104, 112, 152, 144), fill=RED)
save(im, "med_h", wear=0.12)

# --- Small red medical cross tag, for soft goods ------------------------------------------------
im = canvas(128, 128)
d = ImageDraw.Draw(im)
rect(d, (4, 4, 124, 124), fill=(228, 226, 218, 255))
rect(d, (46, 18, 82, 110), fill=RED)
rect(d, (18, 46, 110, 82), fill=RED)
save(im, "cross_tag", wear=0.1)

# --- IFAK label: yellow stencil block -----------------------------------------------------------
im = canvas(512, 256)
d = ImageDraw.Draw(im)
rect(d, (8, 8, 504, 248), outline=YELLOW, width=5)
text(d, (26, 20), "IFAK", font(96, "Bold"), YELLOW)
text(d, (210, 34), "INDIVIDUAL", font(30, "SemiBold"), YELLOW)
text(d, (210, 70), "FIRST AID KIT", font(30, "SemiBold"), YELLOW)
rect(d, (26, 134, 486, 138), fill=YELLOW)
text(d, (26, 150), "BIOFOAM  //  POLYPSEUDOMORPHINE  //  DRESSINGS", font(22, "SemiBold"), YELLOW)
text(d, (26, 184), "UNSC MED CORPS   LOT 2552.0117", font(20, "Regular"), YELLOW)
barcode(d, 330, 206, 156, 30, YELLOW, seed=11)
save(im, "ifak_label", wear=0.35)

# --- AFAK side label: dark print on the light case ----------------------------------------------
im = canvas(512, 128)
d = ImageDraw.Draw(im)
rect(d, (4, 4, 508, 124), fill=(206, 204, 196, 255))
rect(d, (4, 4, 88, 124), fill=RED)
text(d, (46, 64), "+", font(92, "Bold", condensed=False), (240, 236, 228, 255), anchor="mm")
text(d, (102, 14), "AFAK  TRAUMA KIT", font(40, "Bold"), DARK)
text(d, (102, 64), "STERILE FIELD GEN. / BIOFOAM INJ. x4", font(22, "SemiBold"), DARK)
text(d, (102, 92), "HANDLE WITH CARE   LOT 2557.0442", font(20, "Regular"), DARK)
barcode(d, 420, 12, 82, 40, DARK, seed=5)
save(im, "afak_label", wear=0.15)

# --- Warning strip, red/white, small text ------------------------------------------------------
im = canvas(320, 96)
d = ImageDraw.Draw(im)
text(d, (8, 6), "WARNING", font(30, "Bold"), RED)
text(d, (8, 42), "PRESSURISED BIOFOAM CANISTERS", font(15, "SemiBold"), RED)
text(d, (8, 62), "DO NOT EXPOSE TO OPEN FLAME", font(15, "SemiBold"), RED)
save(im, "warning_red", wear=0.25)

# --- Yellow data panel (line art, as on UNSC crates) --------------------------------------------
im = canvas(256, 200)
d = ImageDraw.Draw(im)
rect(d, (6, 6, 250, 194), outline=YELLOW, width=3)
rect(d, (6, 6, 250, 40), outline=YELLOW, width=3)
text(d, (16, 12), "UNSC MED CORPS", font(20, "SemiBold"), YELLOW)
for k in range(6):
    rect(d, (18, 56 + k * 20, 18 + [150, 120, 170, 90, 140, 110][k], 64 + k * 20), fill=YELLOW)
rect(d, (196, 52, 238, 94), outline=YELLOW, width=3)
rect(d, (206, 62, 228, 84), fill=YELLOW)
barcode(d, 160, 156, 80, 28, YELLOW, seed=9)
save(im, "data_panel", wear=0.4)

# --- Unit emblem: winged chevron, our own -----------------------------------------------------
im = canvas(256, 128)
d = ImageDraw.Draw(im)
c = 128
poly(d, [(c, 24), (c + 22, 70), (c, 104), (c - 22, 70)], YELLOW)
for s in (1, -1):
    for k in range(4):
        y0 = 40 + k * 14
        poly(d, [(c + s * 28, y0), (c + s * (120 - k * 18), y0 - 8 + k * 2), (c + s * (112 - k * 18), y0 + 6 + k * 2),
                 (c + s * 30, y0 + 12)], YELLOW)
save(im, "emblem_yellow", wear=0.3)

# --- MFAK lid stencil ---------------------------------------------------------------------------
im = canvas(512, 160)
d = ImageDraw.Draw(im)
text(d, (10, 2), "MFAK", font(104, "Bold"), WHITE)
text(d, (232, 22), "MULTI-CASUALTY", font(34, "SemiBold"), WHITE)
text(d, (232, 62), "MEDICAL SUPPLY", font(34, "SemiBold"), WHITE)
rect(d, (10, 122, 500, 128), fill=WHITE)
text(d, (232, 134), "MASS 6.2 KG", font(18, "Regular"), WHITE)
save(im, "mfak_white", wear=0.35)

# --- MFAK+ stencil ------------------------------------------------------------------------------
im = canvas(512, 160)
d = ImageDraw.Draw(im)
text(d, (10, 2), "MFAK+", font(104, "Bold"), WHITE)
text(d, (290, 22), "FIELD MEDIC", font(34, "SemiBold"), WHITE)
text(d, (290, 62), "RESUPPLY", font(34, "SemiBold"), WHITE)
rect(d, (10, 122, 500, 128), fill=WHITE)
text(d, (290, 134), "MASS 9.8 KG", font(18, "Regular"), WHITE)
save(im, "mfakplus_white", wear=0.35)

# --- Narc case lid: SPNKr-style yellow stencil ------------------------------------------------
im = canvas(640, 300)
d = ImageDraw.Draw(im)
rect(d, (8, 8, 400, 140), outline=YELLOW, width=6)
text(d, (26, 16), "NARC", font(118, "Bold", condensed=False), YELLOW)
text(d, (420, 20), "CONTROLLED", font(34, "Bold"), YELLOW)
text(d, (420, 58), "SUBSTANCES", font(34, "Bold"), YELLOW)
for k in range(9):
    rect(d, (420 + k * 22, 102, 432 + k * 22, 136), fill=YELLOW)
text(d, (16, 160), "POLYPSEUDOMORPHINE AUTO-INJECTOR (x6)", font(27, "SemiBold"), YELLOW)
text(d, (16, 196), "EPINEPHRINE 1MG/ML  //  ADENOSINE 6MG", font(27, "SemiBold"), YELLOW)
text(d, (16, 232), "COUNT: 2 (x6)", font(27, "SemiBold"), YELLOW)
text(d, (16, 264), "LOT 50017.231", font(25, "SemiBold"), YELLOW)
rect(d, (300, 240, 440, 286), outline=YELLOW, width=3)
text(d, (370, 263), "MED CORPS", font(18, "Bold"), YELLOW, anchor="mm")
save(im, "narc_yellow", wear=0.3)

# --- Hazard chevrons for latches/edges ----------------------------------------------------------
im = canvas(256, 64)
d = ImageDraw.Draw(im)
rect(d, (0, 0, 256, 64), fill=(212, 182, 52, 255))
for k in range(-2, 12):
    poly(d, [(k * 32, 64), (k * 32 + 16, 64), (k * 32 + 48, 0), (k * 32 + 32, 0)], BLACK)
save(im, "hazard", wear=0.2)

# --- Small serial plate text ------------------------------------------------------------------
im = canvas(256, 64)
d = ImageDraw.Draw(im)
text(d, (6, 4), "UNSC PROPERTY", font(24, "Bold"), WHITE)
text(d, (6, 34), "SN 0442-117-B   REV 3", font(18, "SemiBold"), WHITE)
save(im, "serial_white", wear=0.25)


# ================================================================================================
# Small stencils used all over
# ================================================================================================
def arrow_up(d, x, y, s, fill):
    poly(d, [(x, y), (x + s * 0.5, y + s * 0.5), (x + s * 0.2, y + s * 0.5), (x + s * 0.2, y + s),
             (x - s * 0.2, y + s), (x - s * 0.2, y + s * 0.5), (x - s * 0.5, y + s * 0.5)], fill)


im = canvas(256, 96)
d = ImageDraw.Draw(im)
arrow_up(d, 40, 10, 76, WHITE)
arrow_up(d, 216, 10, 76, WHITE)
text(d, (128, 30), "THIS SIDE", font(26, "Bold"), WHITE, anchor="mm")
text(d, (128, 64), "UP", font(30, "Bold"), WHITE, anchor="mm")
save(im, "side_up_white", wear=0.35)

im = canvas(192, 64)
d = ImageDraw.Draw(im)
rect(d, (4, 4, 188, 60), outline=WHITE, width=3)
text(d, (96, 32), "LIFT HERE", font(28, "Bold"), WHITE, anchor="mm")
save(im, "lift_white", wear=0.35)

im = canvas(128, 128)
d = ImageDraw.Draw(im)
d.ellipse([8 * SS, 8 * SS, 120 * SS, 120 * SS], outline=RED, width=5 * SS)
text(d, (64, 48), "QA", font(34, "Bold"), RED, anchor="mm")
text(d, (64, 84), "2552-07", font(18, "SemiBold"), RED, anchor="mm")
save(im, "qa_red", wear=0.45)

im = canvas(256, 48)
d = ImageDraw.Draw(im)
text(d, (4, 24), "NO STEP  //  KEEP DRY", font(26, "SemiBold"), YELLOW, anchor="lm")
save(im, "nostep_yellow", wear=0.35)

# ================================================================================================
# EUP
# ================================================================================================
im = canvas(384, 160)
d = ImageDraw.Draw(im)
text(d, (8, 0), "UTIL", font(110, "Bold"), YELLOW)
text(d, (200, 24), "UTILITY POUCH", font(30, "SemiBold"), YELLOW)
text(d, (200, 60), "GENERAL PURPOSE", font(30, "SemiBold"), YELLOW)
rect(d, (8, 124, 376, 128), fill=YELLOW)
text(d, (8, 134), "UNSC MARINE CORPS  //  LOT 2552.0042", font(20, "Regular"), YELLOW)
save(im, "util_label", wear=0.35)

im = canvas(320, 256)
d = ImageDraw.Draw(im)
text(d, (160, 46), "AMMO", font(96, "Bold"), YELLOW, anchor="mm")
rect(d, (20, 98, 300, 104), fill=YELLOW)
text(d, (160, 132), "7.62x51mm  M118 FMJ-AP", font(26, "SemiBold"), YELLOW, anchor="mm")
text(d, (160, 170), "2 MAG  //  60 RDS EACH", font(26, "SemiBold"), YELLOW, anchor="mm")
text(d, (160, 214), "LOT MA5-2551-0310", font(22, "Regular"), YELLOW, anchor="mm")
save(im, "ammo_label", wear=0.35)

im = canvas(640, 240)
d = ImageDraw.Draw(im)
text(d, (12, 0), "AMMUNITION", font(110, "Bold"), YELLOW)
rect(d, (12, 128, 628, 134), fill=YELLOW)
text(d, (12, 146), "CTG 7.62x51mm M118 FMJ-AP   600 RDS (10x60)", font(28, "SemiBold"), YELLOW)
text(d, (12, 186), "MA5 MAGAZINES  //  LOT 2552-114  //  GROSS WT 14.8 KG", font(24, "Regular"), YELLOW)
save(im, "ammo_crate_label", wear=0.35)

im = canvas(512, 48)
d = ImageDraw.Draw(im)
rect(d, (0, 0, 512, 48), fill=(206, 168, 44, 255))
save(im, "yellow_band", wear=0.25)


def gear(d, cx, cy, r, fill, teeth=8):
    pts = []
    for k in range(teeth * 2):
        a = math.pi * k / teeth
        rr = r if k % 2 == 0 else r * 0.78
        for da in (-0.18, 0.18):
            pts.append((cx + rr * math.cos(a + da * math.pi / teeth * 2), cy + rr * math.sin(a + da * math.pi / teeth * 2)))
    poly(d, pts, fill)
    d.ellipse([(cx - r * 0.38) * SS, (cy - r * 0.38) * SS, (cx + r * 0.38) * SS, (cy + r * 0.38) * SS],
              fill=(0, 0, 0, 0))


import math  # noqa: E402

im = canvas(512, 200)
d = ImageDraw.Draw(im)
gear(d, 90, 96, 76, YELLOW)
text(d, (190, 10), "ENGINEERING", font(62, "Bold"), YELLOW)
text(d, (190, 84), "FIELD REPAIR & DEMOLITION", font(28, "SemiBold"), YELLOW)
text(d, (190, 122), "COMBAT ENGINEER TOOL SET  //  UNSC", font(22, "Regular"), YELLOW)
barcode(d, 190, 156, 200, 30, YELLOW, seed=21)
save(im, "eng_label", wear=0.35)


def trefoil(d, cx, cy, r, fill):
    for k in range(3):
        a0 = -90 + 120 * k - 30
        d.pieslice([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], a0, a0 + 60, fill=fill)
    d.ellipse([(cx - r * 0.3) * SS, (cy - r * 0.3) * SS, (cx + r * 0.3) * SS, (cy + r * 0.3) * SS],
              fill=(0, 0, 0, 0))
    d.ellipse([(cx - r * 0.18) * SS, (cy - r * 0.18) * SS, (cx + r * 0.18) * SS, (cy + r * 0.18) * SS], fill=fill)


im = canvas(512, 200)
d = ImageDraw.Draw(im)
poly(d, [(100, 8), (190, 188), (10, 188)], (206, 168, 44, 255))
trefoil(d, 100, 126, 50, BLACK)
text(d, (210, 14), "CBRN", font(96, "Bold"), DARK)
text(d, (210, 112), "DECON & PROTECTION KIT", font(28, "SemiBold"), DARK)
text(d, (210, 150), "SEALED  //  INSPECT GASKET BEFORE USE", font(20, "Regular"), DARK)
save(im, "cbrn_label", wear=0.25)

# gauge face: white dial, ticks, green/red bands, needle
im = canvas(256, 256)
d = ImageDraw.Draw(im)
c = 128
d.ellipse([4 * SS, 4 * SS, 252 * SS, 252 * SS], fill=(232, 230, 220, 255))
for a0, a1, col in ((135, 315, (60, 150, 70, 255)), (315, 405, (200, 40, 34, 255))):
    d.arc([22 * SS, 22 * SS, 234 * SS, 234 * SS], a0, a1, fill=col, width=12 * SS)
for k in range(11):
    a = math.radians(135 + 27 * k)
    r0, r1 = (88, 106) if k % 2 == 0 else (96, 106)
    d.line([((c + r0 * math.cos(a)) * SS, (c + r0 * math.sin(a)) * SS),
            ((c + r1 * math.cos(a)) * SS, (c + r1 * math.sin(a)) * SS)], fill=BLACK, width=4 * SS)
a = math.radians(135 + 27 * 6.5)
d.line([(c * SS, c * SS), ((c + 84 * math.cos(a)) * SS, (c + 84 * math.sin(a)) * SS)], fill=RED, width=5 * SS)
d.ellipse([(c - 10) * SS, (c - 10) * SS, (c + 10) * SS, (c + 10) * SS], fill=BLACK)
text(d, (c, 184), "SEAL kPa", font(22, "SemiBold"), BLACK, anchor="mm")
save(im, "gauge_face")


# ================================================================================================
# The real UNSC marks (tools/models/logos, from Halopedia; Halo (c) Microsoft, used under the Game
# Content Usage Rules). The SVGs are rendered to masks by svg_to_png.py in Blender first.
# ================================================================================================
LOGOS = os.path.join(HERE, "logos")


def mask_decal(src, name, color, height, wear=0.25, pad=0.04):
    """Colour a logo mask (white or black on transparent: its alpha is the shape)."""
    m = Image.open(os.path.join(LOGOS, src)).convert("RGBA").getchannel("A")
    bb = m.getbbox()
    m = m.crop(bb)
    w = round(m.width * height / m.height)
    m = m.resize((w * SS, height * SS), Image.LANCZOS)
    p = round(height * pad) * SS
    im = Image.new("RGBA", (w * SS + 2 * p, height * SS + 2 * p), (0, 0, 0, 0))
    col = Image.new("RGBA", m.size, color)
    col.putalpha(m)
    im.alpha_composite(col, (p, p))
    save(im, name, wear=wear)


if os.path.isfile(os.path.join(LOGOS, "Merch_UNSC_Logo_White.png")):
    mask_decal("Merch_UNSC_Logo_White.png", "egb_white", WHITE, 512)
    mask_decal("Merch_UNSC_Logo_White.png", "egb_yellow", YELLOW, 512)
    mask_decal("Merch_UNSC_Logo_White.png", "egb_dark", DARK, 512, wear=0.15)
    mask_decal("UNSC_MC_Logo.png", "marines_white", WHITE, 512)
    mask_decal("UNSC_MC_Logo.png", "marines_yellow", YELLOW, 512)
    mask_decal("H4_UNSC_logo.png", "wordmark_white", WHITE, 160)
    mask_decal("H4_UNSC_logo.png", "wordmark_dark", DARK, 160, wear=0.15)
    mask_decal("H4_UNSC_logo.png", "wordmark_yellow", YELLOW, 160)

# Orange inventory sticker, as on the lids of UNSC cases
im = canvas(256, 96)
d = ImageDraw.Draw(im)
rect(d, (2, 2, 254, 94), fill=(226, 118, 34, 255))
rect(d, (8, 8, 120, 88), fill=(240, 238, 230, 255))
barcode(d, 14, 14, 100, 52, BLACK, seed=33)
text(d, (64, 80), "2552-0117", font(12, "SemiBold"), BLACK, anchor="mm")
text(d, (188, 30), "UNSC", font(34, "Bold", condensed=False), (40, 30, 20, 255), anchor="mm")
text(d, (188, 66), "PROPERTY", font(22, "SemiBold"), (40, 30, 20, 255), anchor="mm")
save(im, "sticker_orange", wear=0.2)

# Medical sticker: white, red cross, text
im = canvas(256, 96)
d = ImageDraw.Draw(im)
rect(d, (2, 2, 254, 94), fill=(236, 234, 226, 255))
rect(d, (2, 2, 96, 94), fill=RED)
rect(d, (38, 18, 60, 78), fill=(240, 238, 230, 255))
rect(d, (19, 37, 79, 59), fill=(240, 238, 230, 255))
text(d, (176, 32), "MEDICAL", font(34, "Bold"), RED, anchor="mm")
text(d, (176, 68), "MED CORPS", font(22, "SemiBold"), DARK, anchor="mm")
save(im, "med_sticker", wear=0.2)

# Ammo cell label for the magazine pouch
im = canvas(160, 128)
d = ImageDraw.Draw(im)
# what the cell holds: three MA5 magazines of M118 7.62x51 full metal jacket armour piercing
text(d, (80, 30), "7.62x51", font(42, "Bold"), YELLOW, anchor="mm")
rect(d, (14, 58, 146, 62), fill=YELLOW)
text(d, (80, 80), "M118 FMJ-AP", font(20, "SemiBold"), YELLOW, anchor="mm")
text(d, (80, 106), "MA5 MAG x3", font(20, "SemiBold"), YELLOW, anchor="mm")
save(im, "ammo_cell", wear=0.3)

# Grey stencil code, as on the ends of UNSC cases
im = canvas(256, 64)
d = ImageDraw.Draw(im)
text(d, (128, 32), "F-21HB", font(52, "Bold"), (150, 150, 146, 255), anchor="mm")
save(im, "code_grey", wear=0.35)


# ================================================================================================
# Labels on what is packed inside the kits (interiors.py). Small prints, read up close with the
# lid open; most are white or olive pack labels with a cross or band and a lot number.
# ================================================================================================
OLIVE_INK = (40, 42, 30, 255)
PACK_CREAM = (238, 236, 226, 255)


def pack_label(name, w, h, title, lines, ink=OLIVE_INK, band=RED, cross=True, bg=None, wear=0.08):
    """A printed pack face: a coloured band down the left with a cross, the title and small lines."""
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    if bg:
        rect(d, (0, 0, w, h), fill=bg)
    bw = int(h * 0.42)
    rect(d, (0, 0, bw, h), fill=band)
    if cross:
        cw = bw * 0.5
        cx, cy = bw / 2, h / 2
        rect(d, (cx - cw / 6, cy - cw / 2, cx + cw / 6, cy + cw / 2), fill=PACK_CREAM)
        rect(d, (cx - cw / 2, cy - cw / 6, cx + cw / 2, cy + cw / 6), fill=PACK_CREAM)
    x = bw + h * 0.12
    room = w - x - h * 0.1
    fs = max(10, int(h * 0.3))
    while fs > 10 and d.textlength(title, font=font(fs, "Bold")) / SS > room:
        fs -= 1
    text(d, (x, h * 0.06), title, font(fs, "Bold"), ink)
    ls = max(7, int(h * 0.15))
    y = h * 0.06 + fs * 1.2
    for ln in lines:
        text(d, (x, y), ln, font(ls, "SemiBold"), ink)
        y += ls * 1.3
    rect(d, (x, min(h - h * 0.08, y + h * 0.04), w - h * 0.1, min(h - h * 0.06, y + h * 0.06)), fill=ink)
    save(im, name, wear=wear)


pack_label("lbl_dressing", 220, 96, "FIELD DRESSING", ["STERILE · 10 x 18 cm", "UNSC MED CORPS", "LOT 2552-0117"],
           ink=PACK_CREAM)
pack_label("lbl_gauze", 220, 96, "HEMOSTATIC GAUZE", ["Z-FOLD · 7.5 cm x 3.7 m", "UNSC MED CORPS", "LOT 2552-0211"])
pack_label("lbl_chest_seal", 200, 96, "CHEST SEAL", ["VENTED · 2 PER PACK", "UNSC MED CORPS"])
pack_label("lbl_gloves", 180, 96, "NITRILE GLOVES", ["SIZE L · 2 PAIR", "EXAM GRADE"], band=(60, 110, 170, 255),
           cross=False)
pack_label("lbl_suture", 200, 96, "SUTURE KIT", ["3-0 NYLON · 1 NEEDLE", "STERILE"])
pack_label("lbl_pills", 180, 96, "ANALGESIC", ["TABLETS 500 mg · 20", "UNSC MED CORPS"])
pack_label("lbl_saline", 220, 110, "SALINE 0.9 %", ["500 ml · IV · SINGLE USE", "UNSC MED CORPS", "LOT 2552-0088"],
           band=(60, 110, 170, 255), cross=False)
pack_label("lbl_blanket", 200, 96, "SURVIVAL BLANKET", ["FOIL · 210 x 160 cm", "UNSC MED CORPS"], ink=BLACK,
           band=(50, 50, 48, 255), cross=False)
pack_label("lbl_decon", 220, 96, "DECON KIT", ["SKIN · 3 SPONGE PACKS", "UNSC CBRN DEFENSE"], ink=PACK_CREAM,
           band=YELLOW, cross=False)
pack_label("lbl_detector", 180, 96, "DETECTOR PAPER", ["CHEMICAL AGENT · 25 SHEETS", "UNSC CBRN DEFENSE"],
           band=YELLOW, cross=False)
pack_label("lbl_carton", 220, 110, "7.62 x 51 mm", ["M118 FMJ-AP · 200 RDS", "UNSC ARMORY", "LOT 2552-0404"],
           ink=PACK_CREAM, band=YELLOW, cross=False)
pack_label("lbl_demo", 220, 96, "C-12", ["SHAPED CHARGE · 1.2 kg", "DANGER · HIGH EXPLOSIVE"], ink=PACK_CREAM,
           band=YELLOW, cross=False)

# Bands round cylinders: a strip of print that wraps the front of a canister, vial or injector
def band_label(name, w, h, title, sub, bg=PACK_CREAM, ink=OLIVE_INK, stripe=RED):
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    rect(d, (0, 0, w, h), fill=bg)
    rect(d, (0, 0, w, int(h * 0.14)), fill=stripe)
    text(d, (w / 2, h * 0.46), title, font(int(h * 0.36), "Bold"), ink, anchor="mm")
    if sub:
        text(d, (w / 2, h * 0.8), sub, font(int(h * 0.2), "SemiBold"), ink, anchor="mm")
    save(im, name, wear=0.06)


band_label("lbl_biofoam", 220, 100, "BIOFOAM", "UNSC MED CORPS · 1 USE")
band_label("lbl_morphine", 160, 72, "MORPHINE", "10 mg/ml")
band_label("lbl_epi", 160, 72, "EPINEPHRINE", "1 mg/ml", stripe=(60, 110, 170, 255))
band_label("lbl_atropine", 180, 64, "ATROPINE", "2 mg AUTO-INJ", stripe=YELLOW)
band_label("lbl_filter", 200, 80, "NBC FILTER", "C-SERIES · 24 h", bg=(70, 74, 56, 255), ink=PACK_CREAM,
           stripe=YELLOW)
band_label("lbl_splint", 220, 80, "MOLDABLE SPLINT", "36 in · ROLLED", bg=(226, 118, 34, 255), ink=BLACK,
           stripe=BLACK)
band_label("lbl_tape", 200, 80, "RIGGER TAPE", "50 mm · 10 m", bg=(50, 50, 48, 255), ink=PACK_CREAM,
           stripe=(226, 118, 34, 255))

# Tourniquet time tag and the firing device's face
im = canvas(160, 64)
d = ImageDraw.Draw(im)
rect(d, (0, 0, 160, 64), fill=PACK_CREAM)
text(d, (8, 6), "TIME:", font(26, "Bold"), BLACK)
rect(d, (74, 44, 150, 47), fill=BLACK)
text(d, (8, 40), "TQ", font(16, "SemiBold"), RED)
save(im, "lbl_tq_tag", wear=0.05)

im = canvas(200, 120)
d = ImageDraw.Draw(im)
text(d, (100, 24), "FIRING DEVICE", font(26, "Bold"), BLACK, anchor="mm")
text(d, (100, 54), "M-ARM / FIRE", font(18, "SemiBold"), BLACK, anchor="mm")
rect(d, (20, 78, 180, 82), fill=BLACK)
text(d, (100, 100), "DANGER", font(22, "Bold"), RED, anchor="mm")
save(im, "lbl_initiator", wear=0.1)

im = canvas(200, 90)
d = ImageDraw.Draw(im)
rect(d, (0, 0, 200, 90), fill=(236, 234, 226, 255))
text(d, (100, 26), "MA5 60 RD", font(30, "Bold"), BLACK, anchor="mm")
text(d, (100, 60), "7.62 x 51 M118", font(20, "SemiBold"), BLACK, anchor="mm")
save(im, "lbl_mag", wear=0.2)


# ================================================================================================
# Halo pieces: the biofoam canister's data label, the medigel tube, the UNSC injector, the ammo pack
# ================================================================================================
im = canvas(260, 120)
d = ImageDraw.Draw(im)
rect(d, (0, 0, 260, 120), fill=PACK_CREAM)
rect(d, (0, 0, 260, 4), fill=BLACK)
rect(d, (0, 116, 260, 120), fill=BLACK)
text(d, (10, 8), "CANISTER, MEDICAL", font(22, "Bold"), BLACK)
text(d, (10, 34), "BIOFOAM", font(34, "Bold"), BLACK)
text(d, (10, 72), "POLYMER WOUND FILLER · 1 USE", font(13, "SemiBold"), BLACK)
text(d, (10, 88), "UNSC MED CORPS · LOT 2552-0117", font(13, "SemiBold"), BLACK)
barcode(d, 190, 10, 60, 40, BLACK, seed=21)
# a small cross in a box, bottom right
rect(d, (206, 64, 250, 108), fill=RED)
rect(d, (223, 70, 233, 102), fill=PACK_CREAM)
rect(d, (212, 81, 244, 91), fill=PACK_CREAM)
save(im, "lbl_biofoam", wear=0.12)

im = canvas(200, 110)
d = ImageDraw.Draw(im)
rect(d, (0, 0, 200, 110), fill=(236, 240, 244, 255))
rect(d, (0, 0, 200, 30), fill=(40, 104, 176, 255))
text(d, (100, 15), "UNSC MED CORPS", font(16, "Bold"), (236, 240, 244, 255), anchor="mm")
text(d, (100, 56), "MEDIGEL", font(34, "Bold"), (40, 104, 176, 255), anchor="mm")
text(d, (100, 86), "WOUND & BURN DRESSING · 40 ml", font(12, "SemiBold"), (40, 60, 90, 255), anchor="mm")
save(im, "lbl_medigel", wear=0.05)

im = canvas(200, 90)
d = ImageDraw.Draw(im)
text(d, (100, 26), "UNSC", font(40, "Bold", condensed=False), PACK_CREAM, anchor="mm")
text(d, (100, 66), "AUTO-INJECTOR · 1 DOSE", font(16, "SemiBold"), PACK_CREAM, anchor="mm")
save(im, "lbl_injector", wear=0.15)

AMBER = (230, 150, 40, 255)
im = canvas(200, 160)
d = ImageDraw.Draw(im)
text(d, (100, 30), "M118", font(40, "Bold"), AMBER, anchor="mm")
text(d, (100, 72), "7.62x51mm", font(34, "Bold"), AMBER, anchor="mm")
text(d, (100, 112), "FMJ-AP", font(34, "Bold"), AMBER, anchor="mm")
text(d, (100, 144), "##", font(22, "Bold"), AMBER, anchor="mm")
save(im, "lbl_ammo_top", wear=0.1)

im = canvas(200, 170)
d = ImageDraw.Draw(im)
text(d, (100, 24), "200 ROUNDS", font(26, "Bold"), BLACK, anchor="mm")
rect(d, (30, 44, 170, 47), fill=BLACK)
text(d, (100, 86), "PULL TAB", font(40, "Bold"), AMBER, anchor="mm")
poly(d, [(80, 120), (120, 120), (100, 150)], AMBER)
save(im, "lbl_ammo_body", wear=0.1)


# Engineer's tools
im = canvas(160, 40)
dd = ImageDraw.Draw(im)
text(dd, (80, 20), "19 mm  CR-V", font(24, "Bold"), (190, 190, 186, 255), anchor="mm")
save(im, "lbl_wrench", wear=0.15)

im = canvas(200, 110)
dd = ImageDraw.Draw(im)
GREEN = (120, 220, 150, 255)
text(dd, (104, 50), "12.60", font(64, "Bold", condensed=False), GREEN, anchor="mm")
text(dd, (176, 24), "V", font(26, "Bold"), GREEN, anchor="mm")
text(dd, (22, 92), "DC", font(18, "SemiBold"), GREEN, anchor="mm")
text(dd, (150, 92), "AUTO", font(18, "SemiBold"), GREEN, anchor="mm")
save(im, "lbl_meter_display")

im = canvas(240, 240)
dd = ImageDraw.Draw(im)
import math as _m
labels = ["OFF", "V~", "V=", "mV", "Ohm", "A", "mA", "uA"]
for k, lab in enumerate(labels):
    ang = _m.radians(90 - k * 360 / len(labels))
    cx, cy = 120 + 96 * _m.cos(ang), 120 - 96 * _m.sin(ang)
    text(dd, (cx, cy), lab, font(20, "Bold"), BLACK, anchor="mm")
    x0, y0 = 120 + 70 * _m.cos(ang), 120 - 70 * _m.sin(ang)
    x1, y1 = 120 + 80 * _m.cos(ang), 120 - 80 * _m.sin(ang)
    dd.line([(x0 * SS, y0 * SS), (x1 * SS, y1 * SS)], fill=BLACK, width=3 * SS)
save(im, "lbl_meter_dial", wear=0.08)
