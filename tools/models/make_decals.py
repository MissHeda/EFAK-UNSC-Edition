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
text(d, (210, 34), "M7 INDIVIDUAL", font(30, "SemiBold"), YELLOW)
text(d, (210, 70), "FIRST AID KIT", font(30, "SemiBold"), YELLOW)
rect(d, (26, 134, 486, 138), fill=YELLOW)
text(d, (26, 150), "BIOFOAM  //  POLYPSEUDOMORPHINE  //  DRESSINGS", font(22, "SemiBold"), YELLOW)
text(d, (26, 184), "LOT 2552.0117   NSN 6545-01-NEW-1138", font(20, "Regular"), YELLOW)
barcode(d, 330, 206, 156, 30, YELLOW, seed=11)
save(im, "ifak_label", wear=0.35)

# --- AFAK side label: dark print on the light case ----------------------------------------------
im = canvas(512, 128)
d = ImageDraw.Draw(im)
rect(d, (4, 4, 508, 124), fill=(206, 204, 196, 255))
rect(d, (4, 4, 88, 124), fill=RED)
text(d, (46, 64), "+", font(92, "Bold", condensed=False), (240, 236, 228, 255), anchor="mm")
text(d, (102, 14), "AFAK  M9 TRAUMA", font(40, "Bold"), DARK)
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
text(d, (16, 12), "MED-CORPS  M3", font(20, "SemiBold"), YELLOW)
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
text(d, (16, 160), "M41 POLYPSEUDOMORPHINE AUTO-INJECTOR (x6)", font(27, "SemiBold"), YELLOW)
text(d, (16, 196), "EPINEPHRINE 1MG/ML  //  ADENOSINE 6MG", font(27, "SemiBold"), YELLOW)
text(d, (16, 232), "COUNT: 2 (x6)", font(27, "SemiBold"), YELLOW)
text(d, (16, 264), "LOT 50017.231", font(25, "SemiBold"), YELLOW)
rect(d, (300, 240, 440, 286), outline=YELLOW, width=3)
text(d, (370, 263), "MED-CORPS", font(18, "Bold"), YELLOW, anchor="mm")
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
text(d, (200, 24), "M12 UTILITY", font(30, "SemiBold"), YELLOW)
text(d, (200, 60), "GENERAL PURPOSE", font(30, "SemiBold"), YELLOW)
rect(d, (8, 124, 376, 128), fill=YELLOW)
text(d, (8, 134), "NSN 8465-01-UTL-0042", font(20, "Regular"), YELLOW)
save(im, "util_label", wear=0.35)

im = canvas(320, 256)
d = ImageDraw.Draw(im)
text(d, (160, 46), "AMMO", font(96, "Bold"), YELLOW, anchor="mm")
rect(d, (20, 98, 300, 104), fill=YELLOW)
text(d, (160, 132), "7.62x51mm  M118 SAP-HE", font(26, "SemiBold"), YELLOW, anchor="mm")
text(d, (160, 170), "2 MAG  //  60 RDS EACH", font(26, "SemiBold"), YELLOW, anchor="mm")
text(d, (160, 214), "LOT MA5-2551-0310", font(22, "Regular"), YELLOW, anchor="mm")
save(im, "ammo_label", wear=0.35)

im = canvas(640, 240)
d = ImageDraw.Draw(im)
text(d, (12, 0), "AMMUNITION", font(110, "Bold"), YELLOW)
rect(d, (12, 128, 628, 134), fill=YELLOW)
text(d, (12, 146), "CTG 7.62x51mm M118 SAP-HE   600 RDS (2x300)", font(28, "SemiBold"), YELLOW)
text(d, (12, 186), "LINKED  //  LOT UNSC-2552-114  //  GROSS WT 14.8 KG", font(24, "Regular"), YELLOW)
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
text(d, (190, 122), "TOOL SET M88  //  CORPS OF ENGINEERS", font(22, "Regular"), YELLOW)
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
