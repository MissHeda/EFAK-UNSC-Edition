"""What is packed inside the kits: cut foam trays with a pocket round every piece, and the pieces
themselves - more of them, and the flat ones held under elastic on the lid lining, the way a real
case is packed. Replaces the fill_* functions of kits.py (which import these).

A tray is two layers: a base slab the pieces stand on, and a pocket layer on top of it, built from
foam blocks that tile the tray round the pockets. A piece sunk into its pocket reads as cut foam
without any boolean work. Pockets are rectangles in the kit's x/y; `clip` trims the layer to a tray
that is not a rectangle (the AFAK's octagon, the Narc box's rounded corners).
"""
from unsc_lib import (box, cyl, prism, rect, rrect, circle, inset, contents, lid, cluster, clustered, frame, lbox,
                      lcyl, decal, imported, imported_size)


MARGIN = 0.004      # foam left round each piece (the cut is a touch bigger than the piece)


def pocket_foam(x0, y0, x1, y1, z, h, pockets, look="foam", clip=None, margin=MARGIN, wall=False):
    """The pocket layer: foam from z up by h over the rectangle x0..x1 / y0..y1, cut round every
    pocket (x, y, w, d) in `pockets`. clip(ya, yb) -> (xa, xb) narrows a band of the layer between
    ya and yb (both edges given, the narrowest wins).
    wall=True stands the layer against a wall facing -y instead: x stays, the rectangle's second
    axis is the height (z), and `z` is the wall's y - the foam comes out of it towards -y by h."""
    def block(dx, dy, cx, cy):
        if wall:
            box((dx, h, dy), (cx, z - h / 2, cy), look, bevel=0.001, segs=1)
        else:
            box((dx, dy, h), (cx, cy, z + h / 2), look, bevel=0.0012, segs=1)

    rects = []
    for (x, y, w, d) in pockets:
        # a piece must lie inside its tray, and inside what is left of the tray where it is trimmed
        lim0, lim1 = x0, x1
        if clip is not None:
            ca = clip(y - d / 2, y + d / 2)
            lim0, lim1 = max(lim0, ca[0]), min(lim1, ca[1])
        if x - w / 2 < lim0 - 0.0005 or x + w / 2 > lim1 + 0.0005 or y - d / 2 < y0 - 0.0005 or y + d / 2 > y1 + 0.0005:
            raise SystemExit("POCKET outside its tray: (%.3f, %.3f) %.3f x %.3f, tray x %.3f..%.3f y %.3f..%.3f"
                             % (x, y, w, d, lim0, lim1, y0, y1))
        rects.append((x - w / 2 - margin, y - d / 2 - margin, x + w / 2 + margin, y + d / 2 + margin))
    # and no two pieces in each other's cut
    for i, (ax, ay, aw, ad) in enumerate(pockets):
        for (bx, by, bw, bd) in pockets[i + 1:]:
            if abs(ax - bx) < (aw + bw) / 2 - 0.0005 and abs(ay - by) < (ad + bd) / 2 - 0.0005:
                raise SystemExit("POCKETS overlap: (%.3f, %.3f) %.3f x %.3f and (%.3f, %.3f) %.3f x %.3f"
                                 % (ax, ay, aw, ad, bx, by, bw, bd))
    ys = sorted({y0, y1} | {r[1] for r in rects} | {r[3] for r in rects})
    ys = [y for y in ys if y0 <= y <= y1]
    with cluster():
        for ya, yb in zip(ys, ys[1:]):
            if yb - ya < 0.0015:
                continue
            xa, xb = x0, x1
            if clip is not None:
                ca = clip(ya, yb)
                xa, xb = max(xa, ca[0]), min(xb, ca[1])
            ym = (ya + yb) / 2
            holes = sorted((max(r[0], xa), min(r[2], xb)) for r in rects if r[1] < ym < r[3])
            x = xa
            for hx0, hx1 in holes:
                if hx0 - x > 0.0015:
                    block(hx0 - x, yb - ya, (x + hx0) / 2, ym)
                x = max(x, hx1)
            if xb - x > 0.0015:
                block(xb - x, yb - ya, (x + xb) / 2, ym)


def octagon_clip(W, D, C, ins):
    """clip() for an octagonal tray of W x D with corners cut by C, the layer `ins` inside the edge."""
    Wh, Dh = W / 2 - ins, D / 2 - ins

    def clip(ya, yb):
        y = max(abs(ya), abs(yb))
        x = Wh - max(0.0, C - ins - (D / 2 - ins - y))
        return (-x, x)
    return clip


def round_clip(W, D, r, ins):
    """clip() for a tray with corners rounded by r, the layer `ins` inside the edge."""
    import math
    Wh, Dh = W / 2 - ins, D / 2 - ins
    rr = r - ins

    def clip(ya, yb):
        y = max(abs(ya), abs(yb))
        if rr <= 0 or y <= Dh - rr:
            return (-Wh, Wh)
        dy = y - (Dh - rr)
        x = Wh - rr + math.sqrt(max(0.0, rr * rr - dy * dy))
        return (-x, x)
    return clip


def print_on(image, center, normal, up, width, look=None, depth=0.004):
    """A label printed on a packed piece. Never checked: the check casts its rays through the shut
    lid, which sits right over the tray."""
    decal(image, center, normal, up, width, depth=depth, looks=[look] if look else None, check=False)


# --- pieces ----------------------------------------------------------------------------------------
# What comes from other mods (imports/README.md): the model, how it is turned to lie flat, its scale.
#   biofoam   OPTRE's canister, 36 cm long there - packed here at a third, as a field-size canister
#   medigel   UNSC Infirmary's tube, as it is
#   injector  UNSC Infirmary's auto-injector, 20 cm there - at 55 %
#   ammo pack OPTRE's sealed M118 7.62x51 pack
#   magazine  OPTRE's MA5 series magazine and BR magazine
_REAL = {
    "biofoam": ("optre/biofoam.p3d", (-90, 0, 0), 0.36, 900),
    "medigel": ("unsci/medigel_tube.p3d", (-90, 0, 0), 1.0, 700, -90),
    "injector": ("unsci/injector.p3d", (0, 0, 0), 0.55, 700, -90),
    "ammo_pack": ("optre/ma5ammo.p3d", (-90, 0, 0), 0.36, 500),
    "ma5_mag": ("optre/ma5_mag.p3d", (0, 0, 0), 0.5, 500),
    "br_mag": ("optre/br_mag.p3d", (90, 0, 0), 0.5, 500),
}


def _turn(name, axis, stand=False):
    """The rotation for a piece lying along x or y (its long side), or standing on end."""
    file, rot, scale, faces = _REAL[name][:4]
    # which way to turn a piece onto the other axis: the way its print then reads from the front
    quarter = _REAL[name][4] if len(_REAL[name]) > 4 else 90
    w, d, h = imported_size(file, rot, scale, faces)
    long_y = d >= w
    rz = 0 if (axis == "y") == long_y else quarter
    return file, (rot[0], rot[1], rot[2] + rz), scale, faces


def real(name, c, axis="y", **kw):
    """Puts one of the imported pieces at c (its footprint centred there, standing on c's z), its
    long side along `axis`."""
    file, rot, scale, faces = _turn(name, axis)
    imported(file, c, rot=rot, scale=scale, max_faces=faces, **kw)


def real_pocket(name, c, axis="y"):
    """The pocket real() needs."""
    file, rot, scale, faces = _turn(name, axis)
    w, d, h = imported_size(file, rot, scale, faces)
    return (c[0], c[1], w, d)


def real_height(name):
    file, rot, scale, faces = _REAL[name][:4]
    return imported_size(file, rot, scale, faces)[2]


def biofoam(c, axis="x", **kw):
    real("biofoam", c, axis, spec=0.3, gloss=0.5)


def biofoam_pocket(c, axis="x", **kw):
    return real_pocket("biofoam", c, axis)


def medigel_tube(c, axis="y"):
    real("medigel", c, axis, spec=0.3, gloss=0.6)


def medigel_pocket(c, axis="y"):
    return real_pocket("medigel", c, axis)


_DRUG = {"red": "unsci_injector_epinephrine_co", "orange": "unsci_injector_morphine_co",
         "blue": "unsci_injector_stimulant_co"}


def injector(c, axis="y", cap="red", upright=False, **kw):
    """UNSC auto-injector; `cap` picks the drug band (red epinephrine, orange morphine, blue stimulant).
    upright: standing on its long edge, flat face to the front (the IFAK's wall)."""
    file, rot, scale, faces = _REAL["injector"][:4]
    tex = {"unsci_injector_stimulant_co": _DRUG.get(cap, _DRUG["blue"])}
    if upright:
        imported(file, c, rot=(90, -90, 0), scale=scale * 0.5, max_faces=faces, spec=0.25, gloss=0.45, textures=tex)
    else:
        real("injector", c, axis, spec=0.25, gloss=0.45, textures=tex)


def injector_pocket(c, axis="y", **kw):
    return real_pocket("injector", c, axis)


def ammo_pack(c, axis="y"):
    real("ammo_pack", c, axis, spec=0.2, gloss=0.5)


def ammo_pack_pocket(c, axis="y"):
    return real_pocket("ammo_pack", c, axis)


def d_(axis):
    return (1, 0, 0) if axis == "x" else (0, 1, 0)


@clustered
def dressing(c, w=0.06, d=0.04, h=0.012, look="pack_olive", flat=True):
    """A sealed dressing pack with a tear strip."""
    x, y, z = c
    image = "lbl_dressing" if look == "pack_olive" else "lbl_gauze"
    if flat:
        # the pillow, its flat crimped seal all round, the tear strip, the print on top
        box((w, d, h), (x, y, z + h / 2), look, bevel=0.0012, segs=1)
        box((w + 0.005, d + 0.005, 0.0012), (x, y, z + h * 0.45), look, bevel=0.0004, segs=1)
        box((w * 0.9, 0.003, 0.0012), (x, y + d * 0.36, z + h + 0.0004), "red", bevel=0.0003, segs=1)
        box((0.004, 0.0035, 0.0014), (x - w / 2 - 0.001, y + d * 0.36, z + h * 0.45), "red", bevel=0.0003, segs=1)
        print_on(image, (x, y - d * 0.08, z + h), (0, 0, 1), (0, 1, 0), w * 0.78, look=look)
    else:   # standing against a wall that faces -y (the IFAK's front)
        box((w, h, d), (x, y - h / 2, z), look, bevel=0.0015, segs=1)
        box((w + 0.005, 0.0012, d + 0.005), (x, y - h * 0.45, z), look, bevel=0.0004, segs=1)
        box((w * 0.9, 0.0012, 0.003), (x, y - h - 0.0004, z + d * 0.36), "red", bevel=0.0003, segs=1)
        # the IFAK lies on its back with the latch towards the user: like the label on its lid, the
        # print reads from that side, its top towards the hinge (-z here)
        print_on(image, (x, y - h, z - d * 0.06), (0, -1, 0), (0, 0, -1), w * 0.92, look=look)


@clustered
def tourniquet(c, flat=True):
    """Folded tourniquet: black strap bundle with its windlass and buckle."""
    x, y, z = c
    if flat:
        box((0.07, 0.026, 0.012), (x, y, z + 0.006), "rubber", bevel=0.002, segs=2)
        box((0.008, 0.032, 0.015), (x - 0.018, y, z + 0.0075), "red", bevel=0.002, segs=1)
        box((0.012, 0.022, 0.014), (x + 0.026, y, z + 0.007), "steel", bevel=0.002, segs=1)
        # the windlass rod along the bundle, and the white time tag
        cyl(0.003, 0.055, (x + 0.002, y - 0.009, z + 0.0135), "dark_poly", axis="x", n=10, bevel=0.0006)
        box((0.02, 0.009, 0.0008), (x + 0.004, y + 0.006, z + 0.0124), "pack_white", bevel=0.0002, segs=1)
        print_on("lbl_tq_tag", (x + 0.004, y + 0.006, z + 0.0128), (0, 0, 1), (0, 1, 0), 0.018, look="pack_white")
    else:
        box((0.026, 0.006, 0.06), (x, y - 0.003, z), "rubber", bevel=0.0012, segs=1)
        box((0.03, 0.0065, 0.008), (x, y - 0.00325, z - 0.015), "red", bevel=0.001, segs=1)
        cyl(0.003, 0.05, (x - 0.009, y - 0.0075, z + 0.002), "dark_poly", n=10, bevel=0.0006)
        box((0.012, 0.0008, 0.018), (x + 0.006, y - 0.0065, z + 0.012), "pack_white", bevel=0.0002, segs=1)


@clustered
def suture_kit(c):
    x, y, z = c
    box((0.05, 0.036, 0.01), (x, y, z + 0.005), "pack_white", bevel=0.0012, segs=1)
    box((0.055, 0.041, 0.0012), (x, y, z + 0.0045), "pack_white", bevel=0.0004, segs=1)
    box((0.012, 0.03, 0.0012), (x - 0.016, y, z + 0.0104), "red", bevel=0.0003, segs=1)
    print_on("lbl_suture", (x + 0.007, y, z + 0.01), (0, 0, 1), (0, 1, 0), 0.032, look="pack_white")


@clustered
def vial(c, r=0.0065, h=0.03, axis="x"):
    """A drug vial lying in its cut, cap at +axis - never standing, where it would snap."""
    x, y, z = c
    d = d_(axis)
    cyl(r, h, (x, y, z + r), "glass_amber", axis=axis, n=14, bevel=0.0012)
    cyl(r + 0.0003, h * 0.5, (x - d[0] * h * 0.08, y - d[1] * h * 0.08, z + r), "pack_white", axis=axis, n=14,
        bevel=0.0002)
    cyl(r * 0.6, 0.004, (x + d[0] * (h / 2 + 0.002), y + d[1] * (h / 2 + 0.002), z + r), "glass_amber", axis=axis,
        n=12, bevel=0.0006)
    cyl(r * 0.8, 0.005, (x + d[0] * (h / 2 + 0.0065), y + d[1] * (h / 2 + 0.0065), z + r), "steel", axis=axis, n=12,
        bevel=0.001)
    print_on("lbl_morphine", (x - d[0] * h * 0.08, y - d[1] * h * 0.08, z + 2 * r), (0, 0, 1),
             (0, 1, 0) if axis == "x" else (-1, 0, 0), h * 0.42, look="pack_white", depth=r * 0.6)


def vial_pocket(c, r=0.0065, h=0.03, axis="x"):
    x, y, z = c
    d = d_(axis)
    ln = h + 0.011
    return (x + d[0] * 0.0045, y + d[1] * 0.0045, ln if axis == "x" else 2 * r, 2 * r if axis == "x" else ln)


@clustered
def pill_box(c):
    x, y, z = c
    box((0.04, 0.026, 0.012), (x, y, z + 0.006), "pack_white", bevel=0.002, segs=1)
    # the lid seam round the box and the print on top
    box((0.0405, 0.0265, 0.0008), (x, y, z + 0.0085), "dark_poly", bevel=0.0002, segs=1)
    print_on("lbl_pills", (x, y, z + 0.012), (0, 0, 1), (0, 1, 0), 0.036, look="pack_white")


@clustered
def shears(c):
    """Trauma shears: two offset blades, orange handles."""
    x, y, z = c
    box((0.075, 0.009, 0.0025), (x - 0.03, y + 0.002, z + 0.00125), "steel", bevel=0.0006, segs=1)
    box((0.075, 0.009, 0.0025), (x - 0.03, y - 0.004, z + 0.00375), "steel", bevel=0.0006, segs=1)
    cyl(0.003, 0.006, (x + 0.006, y - 0.001, z + 0.003), "black_metal", n=10, bevel=0.0006)
    for sy, ang in ((1, 0), (-1, 0)):
        box((0.05, 0.012, 0.008), (x + 0.035, y + sy * 0.009, z + 0.004), "orange", cut=0.004,
            bevel=0.0012, segs=1)


@clustered
def saline_bag(c, w=0.08, d=0.05):
    """A soft saline pouch, its port at one end."""
    x, y, z = c
    box((w, d, 0.014), (x, y, z + 0.007), "pack_white", bevel=0.002, segs=2)
    box((w + 0.005, d + 0.005, 0.0012), (x, y, z + 0.007), "pack_white", bevel=0.0004, segs=1)
    cyl(0.004, 0.012, (x + w / 2 + 0.004, y - d * 0.2, z + 0.007), "glass", axis="x", n=12, bevel=0.001)
    cyl(0.0045, 0.004, (x + w / 2 + 0.0095, y - d * 0.2, z + 0.007), "red", axis="x", n=12, bevel=0.0008)
    print_on("lbl_saline", (x - 0.004, y + 0.003, z + 0.014), (0, 0, 1), (0, 1, 0), w * 0.7, look="pack_white")


@clustered
def glove_pack(c, w=0.05, d=0.07):
    x, y, z = c
    box((w, d, 0.006), (x, y, z + 0.003), "pack_white", bevel=0.002, segs=1)
    box((w + 0.004, d + 0.004, 0.001), (x, y, z + 0.0025), "pack_white", bevel=0.0003, segs=1)
    print_on("lbl_gloves", (x, y, z + 0.006), (0, 0, 1), (0, 1, 0), w * 0.8, look="pack_white")


@clustered
def gauze_roll(c, r=0.014, length=0.07, axis="x"):
    x, y, z = c
    cyl(r, length, (x, y, z + r), "pack_white", axis=axis, n=16, bevel=0.002, segs=2)
    cyl(r + 0.0004, 0.006, (x, y, z + r), "red", axis=axis, n=16, bevel=0.0004)
    print_on("lbl_gauze", (x + 0.012, y, z + 2 * r), (0, 0, 1), (0, 1, 0), length * 0.5, look="pack_white",
             depth=r * 0.6)


@clustered
def splint(c, length=0.1):
    """A rolled moldable splint, orange, in its band."""
    x, y, z = c
    cyl(0.022, length, (x, y, z + 0.022), "orange", axis="x", n=18, bevel=0.0012, segs=1)
    cyl(0.0225, 0.014, (x, y, z + 0.022), "rubber", axis="x", n=18, bevel=0.0006)
    print_on("lbl_splint", (x + 0.025, y, z + 0.044), (0, 0, 1), (0, 1, 0), 0.044, look="orange", depth=0.012)


@clustered
def chest_seal(c):
    x, y, z = c
    box((0.06, 0.044, 0.004), (x, y, z + 0.002), "pack_olive", bevel=0.0015, segs=1)
    print_on("lbl_chest_seal", (x, y, z + 0.004), (0, 0, 1), (0, 1, 0), 0.05, look="pack_olive")


@clustered
def blanket(c):
    """A folded emergency blanket pack."""
    x, y, z = c
    box((0.045, 0.045, 0.018), (x, y, z + 0.009), "orange", bevel=0.0015, segs=1)
    box((0.045, 0.008, 0.019), (x, y + 0.012, z + 0.0095), "steel", bevel=0.0005, segs=1)
    print_on("lbl_blanket", (x, y - 0.008, z + 0.018), (0, 0, 1), (0, 1, 0), 0.038, look="orange")


@clustered
def chemlight(c, look="green_lens", length=0.1):
    x, y, z = c
    cyl(0.0045, length, (x, y, z + 0.0045), look, axis="x", n=12, bevel=0.0008)
    cyl(0.005, 0.01, (x - length / 2 + 0.005, y, z + 0.0045), "dark_poly", axis="x", n=12, bevel=0.0008)


@clustered
def multitool(c, length=0.09):
    """A folded multitool: two steel handles side by side, the pivot bolts at one end."""
    x, y, z = c
    for sy in (-1, 1):
        box((length, 0.009, 0.012), (x, y + sy * 0.0052, z + 0.006), "black_metal", cut=0.002, bevel=0.001, segs=1)
    box((length * 0.7, 0.0015, 0.0125), (x - length * 0.1, y, z + 0.00625), "steel", bevel=0.0004, segs=1)
    for sy in (-1, 1):
        cyl(0.0028, 0.0014, (x + length / 2 - 0.006, y + sy * 0.0052, z + 0.0125), "steel", n=10, bevel=0.0004)


@clustered
def notebook(c):
    x, y, z = c
    box((0.07, 0.1, 0.008), (x, y, z + 0.004), "olive_green", bevel=0.0012, segs=1)
    box((0.004, 0.1, 0.009), (x - 0.033, y, z + 0.0045), "black_metal", bevel=0.0006, segs=1)


@clustered
def mag_top(c, h=0.012, w=0.026, d=0.044):
    """The top of an MA5 magazine standing in its slot."""
    x, y, z = c
    box((w, d, h), (x, y, z + h / 2), "dark_poly", cut=0.003, bevel=0.0012, segs=1)
    for sx in (-1, 1):
        box((0.0035, d - 0.012, 0.004), (x + sx * (w / 2 - 0.004), y + 0.002, z + h + 0.002), "black_metal",
            bevel=0.0006, segs=1)
    rz = z + h + 0.0032
    cyl(0.0036, 0.026, (x, y + 0.004, rz), "brass", axis="y", n=12, bevel=0.0008)
    cyl(0.0024, 0.009, (x, y - 0.0135, rz), "steel", axis="y", n=10, bevel=0.0016, segs=2)


@clustered
def mag_flat(c, length=0.132, depth=0.062, thick=0.024):
    """A full MA5 magazine lying flat: body along y (feed end at +y), floor plate, feed lips, the
    top round between them."""
    x, y, z = c
    box((depth, length, thick), (x, y, z + thick / 2), "dark_poly", cut=0.004, bevel=0.0015, segs=1)
    for sx in (-1, 1):
        box((0.005, length * 0.72, 0.0016), (x + sx * depth * 0.22, y - 0.006, z + thick + 0.0008), "dark_poly",
            bevel=0.0005, segs=1)
    box((depth + 0.004, 0.009, thick + 0.003), (x, y - length / 2 - 0.0035, z + thick / 2 + 0.0005),
        "black_metal", cut=0.002, bevel=0.0012, segs=1)
    yl = y + length / 2
    for sz in (-1, 1):
        box((depth - 0.016, 0.006, 0.0035), (x + 0.004, yl + 0.003, z + thick / 2 + sz * 0.0085), "black_metal",
            bevel=0.0006, segs=1)
    cyl(0.0038, 0.03, (x + 0.007, yl + 0.0045, z + thick / 2), "brass", axis="x", n=12, bevel=0.0008)
    cyl(0.0026, 0.011, (x - 0.0135, yl + 0.0045, z + thick / 2), "steel", axis="x", n=10, bevel=0.0018, segs=2)
    print_on("lbl_mag", (x, y - 0.03, z + thick), (0, 0, 1), (0, 1, 0), 0.03, look="dark_poly")


@clustered
def ammo_box(c):
    """A sealed carton of loose rounds."""
    x, y, z = c
    box((0.06, 0.1, 0.03), (x, y, z + 0.015), "pack_olive", bevel=0.002, segs=1)
    box((0.06, 0.012, 0.031), (x, y + 0.03, z + 0.0155), "hazard_yellow", bevel=0.0006, segs=1)
    box((0.061, 0.101, 0.0008), (x, y, z + 0.021), "dark_poly", bevel=0.0002, segs=1)
    print_on("lbl_carton", (x, y - 0.015, z + 0.03), (0, 0, 1), (0, 1, 0), 0.05, look="pack_olive")


@clustered
def wrench(c, length=0.12):
    """Combination wrench: an I-beam shank, an open jaw (two prongs) at one end and a ring at the
    other, the size stamped in the web."""
    x, y, z = c
    box((length - 0.03, 0.011, 0.005), (x, y, z + 0.0025), "steel", bevel=0.0012, segs=1)
    box((length - 0.05, 0.004, 0.0062), (x, y, z + 0.0031), "black_metal", bevel=0.0004, segs=1)
    # open jaw
    jx = x - length / 2 + 0.006
    box((0.012, 0.026, 0.006), (jx + 0.008, y, z + 0.003), "steel", cut=0.004, bevel=0.0012, segs=1)
    for sy in (-1, 1):
        box((0.016, 0.008, 0.006), (jx - 0.004, y + sy * 0.009, z + 0.003), "steel", cut=0.002, bevel=0.001,
            segs=1)
    # ring end
    rx = x + length / 2 - 0.012
    prism(circle(0.013, 14), 0.007, "steel", (rx, y, z), bevel=0.001, segs=1, hollow=0.005)
    print_on("lbl_wrench", (x, y, z + 0.0062), (0, 0, 1), (0, 1, 0), 0.03, look="black_metal", depth=0.002)


@clustered
def screwdriver(c, look="orange"):
    """Screwdriver: a fluted handle with a black end cap and grip rings, a steel ferrule, the shaft and
    its flattened tip."""
    x, y, z = c
    hz = z + 0.008
    cyl(0.008, 0.046, (x - 0.03, y, hz), look, axis="x", n=6, bevel=0.0015, segs=1)
    cyl(0.0084, 0.006, (x - 0.055, y, hz), "black_metal", axis="x", n=12, bevel=0.0012)
    for k in (-0.04, -0.03, -0.02):
        cyl(0.0083, 0.002, (x + k, y, hz), "black_metal", axis="x", n=12, bevel=0.0003)
    cyl(0.0048, 0.008, (x - 0.004, y, hz), "steel", axis="x", n=10, bevel=0.0008)
    cyl(0.0022, 0.056, (x + 0.028, y, hz), "steel", axis="x", n=8, bevel=0.0004)
    box((0.008, 0.0054, 0.0012), (x + 0.058, y, hz), "steel", bevel=0.0003, segs=1)


@clustered
def pliers(c):
    """Combination pliers: two tapered jaws, the pivot bolt, dipped red grips."""
    x, y, z = c
    for sy in (-1, 1):
        box((0.036, 0.0065, 0.008), (x - 0.036, y + sy * 0.0036, z + 0.004), "steel", cut=0.002,
            cuts=(1, 0, 0, 1) if sy > 0 else (0, 1, 1, 0), bevel=0.0008, segs=1)
        box((0.016, 0.009, 0.008), (x - 0.012, y + sy * 0.004, z + 0.004), "steel", bevel=0.001, segs=1)
        box((0.062, 0.0085, 0.0085), (x + 0.03, y + sy * 0.0095, z + 0.00425), "red", cut=0.003, bevel=0.002,
            segs=2)
        box((0.008, 0.0095, 0.0092), (x + 0.004, y + sy * 0.0095, z + 0.0046), "black_metal", bevel=0.001, segs=1)
    cyl(0.0042, 0.0092, (x - 0.012, y, z + 0.0046), "black_metal", n=10, bevel=0.0006)
    cyl(0.002, 0.0096, (x - 0.012, y, z + 0.0048), "steel", n=8, bevel=0.0003)


@clustered
def tape_roll(c):
    x, y, z = c
    cyl(0.03, 0.025, (x, y, z + 0.0125), "rubber", n=22, bevel=0.002, segs=2)
    cyl(0.016, 0.026, (x, y, z + 0.013), "pack_olive", n=16, bevel=0.0008)
    print_on("lbl_tape", (x, y - 0.03, z + 0.0125), (0, -1, 0), (0, 0, 1), 0.04, look="rubber", depth=0.012)


@clustered
def initiator(c):
    """A firing device: a yellow box, its red button under a flip guard, an arming key, the cable
    socket on the end and its print."""
    x, y, z = c
    box((0.06, 0.04, 0.028), (x, y, z + 0.014), "hazard_yellow", cut=0.004, bevel=0.002, segs=2)
    box((0.062, 0.042, 0.004), (x, y, z + 0.006), "rubber", cut=0.004, bevel=0.001, segs=1)
    cyl(0.008, 0.004, (x + 0.014, y + 0.006, z + 0.03), "red", n=14, bevel=0.0008)
    cyl(0.0105, 0.002, (x + 0.014, y + 0.006, z + 0.029), "black_metal", n=14, bevel=0.0005)
    # flip guard standing open behind the button
    box((0.024, 0.002, 0.014), (x + 0.014, y + 0.0185, z + 0.035), "glass", bevel=0.0005, segs=1)
    # arming key in its lock
    cyl(0.005, 0.003, (x - 0.014, y + 0.006, z + 0.0295), "steel", n=12, bevel=0.0006)
    box((0.003, 0.012, 0.01), (x - 0.014, y + 0.006, z + 0.036), "steel", bevel=0.0008, segs=1)
    # cable socket on the end
    cyl(0.005, 0.006, (x - 0.032, y, z + 0.016), "black_metal", axis="x", n=12, bevel=0.0008)
    print_on("lbl_initiator", (x, y - 0.011, z + 0.028), (0, 0, 1), (0, 1, 0), 0.036, look="hazard_yellow")


@clustered
def multimeter(c):
    """A field multimeter in its rubber holster: display, range dial with a pointer, three probe
    sockets, two buttons, the print round the dial."""
    x, y, z = c
    box((0.06, 0.09, 0.02), (x, y, z + 0.01), "hazard_yellow", bevel=0.003, segs=2)
    # holster corners
    for sx in (-1, 1):
        for sy in (-1, 1):
            box((0.012, 0.016, 0.022), (x + sx * 0.0255, y + sy * 0.038, z + 0.011), "rubber", bevel=0.003, segs=2)
    # display with its bezel
    box((0.048, 0.03, 0.0015), (x, y + 0.025, z + 0.0203), "black_metal", bevel=0.0005, segs=1)
    box((0.042, 0.024, 0.0012), (x, y + 0.025, z + 0.0212), "glass", bevel=0.0004, segs=1)
    print_on("lbl_meter_display", (x, y + 0.025, z + 0.0218), (0, 0, 1), (0, 1, 0), 0.036, look="glass", depth=0.002)
    # dial and pointer
    cyl(0.013, 0.005, (x, y - 0.012, z + 0.0225), "dark_poly", n=18, bevel=0.0012)
    box((0.003, 0.02, 0.003), (x, y - 0.012, z + 0.0262), "dark_poly", bevel=0.0008, segs=1)
    box((0.0012, 0.006, 0.0006), (x, y - 0.004, z + 0.028), "pack_white", bevel=0.0002, segs=1)
    print_on("lbl_meter_dial", (x, y - 0.012, z + 0.02), (0, 0, 1), (0, 1, 0), 0.05, look="hazard_yellow",
             depth=0.002)
    # sockets and buttons
    for k, lk in ((-1, "dark_poly"), (0, "red"), (1, "dark_poly")):
        cyl(0.0032, 0.003, (x + k * 0.016, y - 0.036, z + 0.0212), lk, n=10, bevel=0.0006)
        cyl(0.0016, 0.0032, (x + k * 0.016, y - 0.036, z + 0.0214), "black_metal", n=8, bevel=0.0003)
    for k in (-1, 1):
        box((0.008, 0.005, 0.002), (x + k * 0.018, y + 0.005, z + 0.021), "dark_poly", bevel=0.0006, segs=1)


@clustered
def demo_block(c):
    """A demolition charge: olive block, yellow tape, a detonator well."""
    x, y, z = c
    box((0.09, 0.05, 0.024), (x, y, z + 0.012), "olive", bevel=0.0012, segs=1)
    # the wrapper's seam, and a second band at the other end
    box((0.0906, 0.0506, 0.0008), (x, y, z + 0.012), "olive_dark", bevel=0.0002, segs=1)
    box((0.006, 0.052, 0.025), (x - 0.038, y, z + 0.0125), "black_metal", bevel=0.0008, segs=1)
    box((0.012, 0.052, 0.025), (x + 0.025, y, z + 0.0125), "hazard_yellow", bevel=0.001, segs=1)
    cyl(0.006, 0.004, (x - 0.025, y, z + 0.025), "black_metal", n=12, bevel=0.0008)
    print_on("lbl_demo", (x - 0.003, y, z + 0.024), (0, 0, 1), (0, 1, 0), 0.04, look="olive")


@clustered
def cable_coil(c, r=0.03):
    x, y, z = c
    cyl(r, 0.012, (x, y, z + 0.006), "rubber", n=20, bevel=0.0016, segs=1)
    cyl(r * 0.45, 0.0125, (x, y, z + 0.0063), "foam", n=14, bevel=0.0008)


@clustered
def gas_mask(c):
    """Gas mask lying face up: rubber body, visor, a filter on its cheek."""
    x, y, z = c
    prism(rrect(0.1, 0.075, 0.03, 4), 0.026, "rubber", (x, y, z), bevel=0.005, segs=2)
    prism(rrect(0.07, 0.04, 0.016, 3), 0.004, "glass", (x, y + 0.008, z + 0.025), bevel=0.0015, segs=1)
    cyl(0.018, 0.022, (x + 0.062, y - 0.01, z + 0.018), "olive_dark", axis="x", n=18, bevel=0.0012, segs=1)
    cyl(0.011, 0.006, (x, y - 0.03, z + 0.028), "rubber", n=16, bevel=0.0015)
    for sx in (-1, 1):
        box((0.03, 0.012, 0.003), (x + sx * 0.045, y + 0.025, z + 0.0015), "webbing", bevel=0.0006, segs=1)


@clustered
def filter_can(c):
    x, y, z = c
    cyl(0.019, 0.024, (x, y, z + 0.012), "olive_dark", n=18, bevel=0.0012, segs=1)
    cyl(0.008, 0.0045, (x, y, z + 0.0265), "black_metal", n=12, bevel=0.0008)
    cyl(0.0195, 0.003, (x, y, z + 0.004), "black_metal", n=18, bevel=0.0004)
    print_on("lbl_filter", (x, y - 0.019, z + 0.013), (0, -1, 0), (0, 0, 1), 0.03, look="olive_dark", depth=0.009)


@clustered
def decon_kit(c):
    """A decontamination kit: a flat yellow-banded olive pack with a sponge mitt."""
    x, y, z = c
    box((0.09, 0.07, 0.02), (x, y, z + 0.01), "pack_olive", bevel=0.0012, segs=1)
    box((0.09, 0.014, 0.021), (x, y + 0.012, z + 0.0105), "hazard_yellow", bevel=0.0006, segs=1)
    print_on("lbl_decon", (x, y - 0.014, z + 0.02), (0, 0, 1), (0, 1, 0), 0.07, look="pack_olive")


@clustered
def detector_paper(c):
    x, y, z = c
    box((0.05, 0.08, 0.006), (x, y, z + 0.003), "pack_white", bevel=0.0012, segs=1)
    print_on("lbl_detector", (x, y, z + 0.006), (0, 0, 1), (0, 1, 0), 0.044, look="pack_white")


@clustered
def field_generator(c):
    """The AFAK's sterile field generator: a white puck with a red ring and a status lens."""
    x, y, z = c
    cyl(0.034, 0.016, (x, y, z + 0.008), "shell_white", n=28, bevel=0.0012, segs=1)
    cyl(0.0345, 0.004, (x, y, z + 0.008), "red", n=28, bevel=0.0008)
    cyl(0.009, 0.003, (x, y, z + 0.0165), "black_metal", n=16, bevel=0.0006)
    cyl(0.006, 0.003, (x, y, z + 0.0175), "green_lens", n=16, bevel=0.0006)


@clustered
def flashlight(c, length=0.09):
    x, y, z = c
    cyl(0.0065, length, (x, y, z), "black_metal", axis="x", n=14, bevel=0.0012)
    cyl(0.0085, 0.02, (x + length / 2 - 0.01, y, z), "black_metal", axis="x", n=14, bevel=0.0015)
    cyl(0.0072, 0.002, (x + length / 2 + 0.0005, y, z), "glass", axis="x", n=14, bevel=0.0004)


# --- the fills ---------------------------------------------------------------------------------------
def case_tray(W, D, H, lid_h, cap, pockets, h=0.016, clip=None):
    """The foam tray of a UNSC case: base slab a little under the rim, pocket layer on it. Returns the
    z of the base slab's top, where the pieces stand."""
    inner = W - 2 * cap
    tw, td = inner + 0.004 - 0.017, D - 0.017
    base_top = H - lid_h - 0.008
    box((tw, td, 0.004), (0, 0, base_top - 0.002), "foam", bevel=0.0015, segs=2)
    pocket_foam(-tw / 2, -td / 2, tw / 2, td / 2, base_top, h, pockets, clip=clip)
    return base_top


def fill_mfak(more=False):
    """MFAK (and MFAK+ with more=True): the big medical case. Two biofoam canisters along the front
    left, medigel and saline on the right, injectors in a row, shears, gauze, tourniquet, dressings,
    vials lying in their cuts, gloves."""
    W, D, H, lid_h, cap = (0.44, 0.24, 0.36, 0.05, 0.034) if more else (0.46, 0.25, 0.25, 0.048, 0.034)
    with contents():
        pockets = []
        items = []

        def put(fn, pocket):
            items.append(fn)
            pockets.append(pocket)

        for y in (-0.082, -0.026):
            put(lambda zf, y=y: biofoam((-0.105, y, zf), axis="x"), biofoam_pocket((-0.105, y, 0), axis="x"))
        put(lambda zf: medigel_tube((0.105, -0.035, zf), axis="x"), medigel_pocket((0.105, -0.035, 0), axis="x"))
        put(lambda zf: saline_bag((0.096, -0.084, zf), 0.08, 0.044), (0.1, -0.084, 0.096, 0.05))
        for k, x in enumerate((0.0, 0.026, 0.052)):
            put(lambda zf, x=x, k=k: injector((x, 0.042, zf), axis="y", cap="red" if k < 2 else "orange"),
                injector_pocket((x, 0.042, 0), axis="y"))
        put(lambda zf: shears((-0.105, 0.019, zf)), (-0.105, 0.019, 0.14, 0.03))
        put(lambda zf: gauze_roll((-0.13, 0.06, zf)), (-0.13, 0.06, 0.07, 0.028))
        put(lambda zf: tourniquet((-0.052, 0.053, zf)), (-0.052, 0.053, 0.078, 0.034))
        put(lambda zf: dressing((-0.132, 0.094, zf), 0.045, 0.026, 0.012), (-0.132, 0.094, 0.05, 0.031))
        put(lambda zf: suture_kit((-0.066, 0.0925, zf)), (-0.066, 0.0925, 0.055, 0.036))
        put(lambda zf: pill_box((0.11, 0.095, zf)), (0.11, 0.095, 0.04, 0.026))
        for y in (0.01, 0.032, 0.054):
            put(lambda zf, y=y: vial((0.105, y, zf)), vial_pocket((0.105, y, 0)))
        put(lambda zf: glove_pack((0.155, 0.03, zf), 0.036, 0.056), (0.155, 0.03, 0.04, 0.06))
        if more:
            put(lambda zf: blanket((0.153, 0.086, zf - 0.004), ), (0.153, 0.086, 0.045, 0.045))
        zf = case_tray(W, D, H, lid_h, cap, pockets, h=0.016)
        for it in items:
            it(zf)


def fill_mfakplus():
    fill_mfak(more=True)


def fill_ifak():
    """IFAK: a cut foam insert on the compartment's back wall - two labelled field dressings, a
    tourniquet and two auto-injectors, each in its own cut. (The case lies on its back in the game,
    so the wall is the floor of an open box.)"""
    with contents():
        box((0.14, 0.004, 0.09), (0, -0.0115, 0.06), "foam", bevel=0.0012, segs=1)
        wall = -0.0135
        # pockets as (x, height, width, tall); the insert is 0.132 wide and reaches from z 0.012 to 0.108
        pockets = [(-0.042, 0.074, 0.04, 0.056), (0.002, 0.074, 0.04, 0.056),     # dressings
                   (0.045, 0.072, 0.032, 0.062),                                   # tourniquet
                   (-0.031, 0.026, 0.06, 0.014), (0.033, 0.026, 0.06, 0.014)]      # auto-injectors
        pocket_foam(-0.066, 0.012, 0.066, 0.108, wall, 0.007, pockets, margin=0.0015, wall=True)
        for x in (-0.042, 0.002):
            dressing((x, wall, 0.074), 0.034, 0.05, 0.01, flat=False)
        tourniquet((0.045, wall, 0.072), flat=False)
        for k, x in enumerate((-0.031, 0.033)):
            injector((x, wall - 0.0045, 0.02), cap="red" if k == 0 else "orange", upright=True)


def fill_afak():
    """AFAK: the sterile field generator in the middle of an octagonal tray, a biofoam canister along
    each side, medigel and injectors behind, dressings and a chest seal across the front."""
    W, D, C = 0.36, 0.27, 0.06
    with contents():
        prism(inset(rect(W, D, C), 0.0085), 0.004, "foam", (0, 0, 0.02), bevel=0.0012, segs=1)
        zf = 0.024
        pockets = [(0, 0, 0.07, 0.07)]
        for sx in (-1, 1):
            pockets.append(biofoam_pocket((sx * 0.115, -0.01, 0), axis="y"))
        pockets.append(medigel_pocket((-0.05, 0.095, 0), axis="x"))
        for x in (0.045, 0.07):
            pockets.append(injector_pocket((x, 0.085, 0), axis="x") if False else injector_pocket((x, 0.065, 0), axis="y"))
        for x in (-0.04, 0.04):
            pockets.append((x, -0.056, 0.05, 0.03))
        pockets.append((0.0, -0.1, 0.06, 0.044))
        pocket_foam(-W / 2 + 0.012, -D / 2 + 0.012, W / 2 - 0.012, D / 2 - 0.012, zf, 0.012, pockets,
                    clip=octagon_clip(W, D, C, 0.024))
        field_generator((0, 0, zf))
        for sx in (-1, 1):
            biofoam((sx * 0.115, -0.01, zf), axis="y")
        medigel_tube((-0.05, 0.095, zf), axis="x")
        for k, x in enumerate((0.045, 0.07)):
            injector((x, 0.065, zf), axis="y", cap="red" if k == 0 else "orange")
        for x in (-0.04, 0.04):
            dressing((x, -0.056, zf), 0.05, 0.03, 0.01)
        chest_seal((0.0, -0.1, zf))


def fill_narcbox():
    """Narc box: auto-injectors in a row, eight vials lying each in its own cut, pill boxes, a
    tamper tag."""
    W, D = 0.30, 0.17
    with contents():
        prism(inset(rrect(W, D, 0.022, 4), 0.0075), 0.004, "foam", (0, 0, 0.03), bevel=0.0012, segs=1)
        zf = 0.034
        pockets = []
        inj = [-0.085 + k * 0.026 for k in range(4)]
        for x in inj:
            pockets.append(injector_pocket((x, -0.008, 0), axis="y"))
        vials = [(x, y) for x in (0.03, 0.07) for y in (-0.052, -0.034, -0.016, 0.002)]
        for x, y in vials:
            pockets.append(vial_pocket((x, y, 0), h=0.026))
        for x in (0.03, 0.074):
            pockets.append((x, 0.04, 0.04, 0.026))
        pockets.append((-0.045, 0.062, 0.1, 0.012))
        # the corner bumpers (r 0.024 at x 0.124, y 0.05) reach into the tray
        def clip(ya, yb):
            y = max(abs(ya), abs(yb))
            x = 0.097 if y > 0.024 else W / 2 - 0.015
            return (-x, x)
        pocket_foam(-W / 2 + 0.015, -D / 2 + 0.015, W / 2 - 0.015, D / 2 - 0.015, zf, 0.012, pockets, clip=clip)
        for k, x in enumerate(inj):
            injector((x, -0.008, zf), axis="y", cap="orange" if k < 2 else "red")
        for x, y in vials:
            vial((x, y, zf), h=0.026)
        for x in (0.03, 0.074):
            pill_box((x, 0.04, zf))
        with cluster():
            box((0.1, 0.012, 0.004), (-0.045, 0.062, zf + 0.002), "hazard_yellow", bevel=0.0008, segs=1)


def fill_utility_pouch():
    """Utility pouch: what a Marine keeps to hand - a flashlight, a multitool, two chemlights and a
    hank of cord, each in its cut in the insert, all inside the pouch's walls."""
    W, D, H = 0.15, 0.06, 0.118
    with contents():
        box((W - 0.012, D - 0.012, 0.003), (0, 0, H - 0.03), "foam", bevel=0.0006, segs=1)
        z = H - 0.0285
        # the insert is 0.138 x 0.048; every piece and its cut stay inside it
        pockets = [(-0.018, -0.012, 0.092, 0.018),    # flashlight, head to the right
                   (0.047, -0.012, 0.034, 0.02),      # multitool
                   (-0.015, 0.006, 0.1, 0.0095),      # chemlight
                   (-0.015, 0.0175, 0.1, 0.0095),     # chemlight
                   (0.052, 0.012, 0.024, 0.024)]      # cord
        pocket_foam(-W / 2 + 0.006, -D / 2 + 0.006, W / 2 - 0.006, D / 2 - 0.006, z, 0.01, pockets, margin=0.0012)
        flashlight((-0.022, -0.012, z + 0.0085), length=0.08)
        multitool((0.047, -0.012, z), length=0.034)
        chemlight((-0.015, 0.006, z), "green_lens", 0.1)
        chemlight((-0.015, 0.0175, z), "orange", 0.1)
        cable_coil((0.052, 0.012, z), r=0.012)


def fill_ammo_pouch():
    """Ammo pouch: three MA5 magazines standing in each cell, feed end up."""
    D, H = 0.056, 0.14
    file, rot, scale, faces = _REAL["ma5_mag"][:4]
    with contents():
        for sx in (-1, 1):
            for y in (-0.013, 0.0, 0.013):
                imported(file, (sx * 0.025, y, H - 0.047 - 0.028), rot=(90, 0, 0), scale=0.34, max_faces=faces,
                         spec=0.25, gloss=0.4)


def fill_ammo_bag():
    """Ammo crate, packed the way the UNSC Marines draw it: MA5 magazines standing on edge in slots
    on the left, BR magazines behind them, sealed M118 7.62x51 packs on the right."""
    W, D, H, lid_h, cap = 0.36, 0.18, 0.2, 0.042, 0.03
    file, rot, scale, faces = _REAL["ma5_mag"][:4]
    with contents():
        pockets = []
        mags = [-0.125 + k * 0.026 for k in range(6)]
        mw, md, mh = imported_size(file, (0, 90, 0), scale, faces)
        for x in mags:
            pockets.append((x, -0.03, mw, md))
        br = [(-0.095, 0.052), (-0.03, 0.052)]
        for x, y in br:
            pockets.append(real_pocket("br_mag", (x, y, 0), axis="x"))
        packs = [0.055, 0.1]
        for x in packs:
            pockets.append(ammo_pack_pocket((x, 0.0, 0), axis="y"))
        zf = case_tray(W, D, H, lid_h, cap, pockets, h=0.018)
        for x in mags:
            imported(file, (x, -0.03, zf - 0.026), rot=(0, 90, 0), scale=scale, max_faces=faces, spec=0.25, gloss=0.4)
        for x, y in br:
            real("br_mag", (x, y, zf), axis="x", spec=0.25, gloss=0.4)
        for x in packs:
            ammo_pack((x, 0.0, zf), axis="y")


def fill_engineer_bag():
    """Engineer case: tools in cut foam, charges, the firing device, det cord, tape - nothing in
    another piece's cut."""
    W, D, H, lid_h, cap = 0.42, 0.21, 0.21, 0.046, 0.034
    with contents():
        pockets = [(-0.09, -0.07, 0.15, 0.032),        # wrench
                   (-0.1, -0.04, 0.12, 0.018),         # screwdriver
                   (-0.1, -0.018, 0.12, 0.018),        # screwdriver
                   (-0.095, 0.006, 0.125, 0.03),       # pliers
                   (0.125, -0.035, 0.06, 0.09),        # multimeter
                   (-0.11, 0.055, 0.09, 0.05),         # charge
                   (-0.01, 0.055, 0.09, 0.05),         # charge
                   (0.125, 0.052, 0.062, 0.062),       # tape
                   (0.041, -0.062, 0.07, 0.04),        # firing device with its cable socket
                   (0.05, -0.01, 0.03, 0.03)]          # det cord
        zf = case_tray(W, D, H, lid_h, cap, pockets, h=0.014)
        wrench((-0.09, -0.07, zf))
        screwdriver((-0.1, -0.04, zf), "orange")
        screwdriver((-0.1, -0.018, zf), "red")
        pliers((-0.0925, 0.006, zf))
        multimeter((0.125, -0.035, zf))
        for x in (-0.11, -0.01):
            demo_block((x, 0.055, zf))
        tape_roll((0.125, 0.052, zf))
        initiator((0.045, -0.062, zf))
        cable_coil((0.05, -0.01, zf), r=0.014)


def fill_cbrn_bag():
    """CBRN case: the mask in its own cut, filters, auto-injectors, decon kit, detector paper - all
    inside the tray (0.319 x 0.213)."""
    W, D, H, lid_h, cap = 0.4, 0.23, 0.24, 0.05, 0.034
    with contents():
        pockets = [(-0.068, 0.045, 0.176, 0.08)]                       # mask with its filter
        for x in (0.035, 0.08, 0.125):
            pockets.append((x, -0.065, 0.038, 0.038))                  # filters
        for y in (0.02, 0.05, 0.08):
            pockets.append(injector_pocket((0.09, y, 0), axis="x"))    # auto-injectors
        pockets.append((-0.105, -0.06, 0.09, 0.07))                    # decon kit
        pockets.append((-0.022, -0.058, 0.05, 0.08))                   # detector paper
        zf = case_tray(W, D, H, lid_h, cap, pockets, h=0.016)
        gas_mask((-0.085, 0.045, zf))
        for x in (0.035, 0.08, 0.125):
            filter_can((x, -0.065, zf))
        for y in (0.02, 0.05, 0.08):
            injector((0.09, y, zf), axis="x", cap="orange")
        decon_kit((-0.105, -0.06, zf))
        detector_paper((-0.022, -0.058, zf))
