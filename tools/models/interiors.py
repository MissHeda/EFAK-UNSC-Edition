"""What is packed inside the kits: cut foam trays with a pocket round every piece, and the pieces
themselves - more of them, and the flat ones held under elastic on the lid lining, the way a real
case is packed. Replaces the fill_* functions of kits.py (which import these).

A tray is two layers: a base slab the pieces stand on, and a pocket layer on top of it, built from
foam blocks that tile the tray round the pockets. A piece sunk into its pocket reads as cut foam
without any boolean work. Pockets are rectangles in the kit's x/y; `clip` trims the layer to a tray
that is not a rectangle (the AFAK's octagon, the Narc box's rounded corners).
"""
from unsc_lib import box, cyl, prism, rect, rrect, circle, inset, contents, lid, cluster, clustered, frame, lbox, lcyl, decal


MARGIN = 0.004      # foam left round each piece (the cut is a touch bigger than the piece)


def pocket_foam(x0, y0, x1, y1, z, h, pockets, look="foam", clip=None, margin=MARGIN):
    """The pocket layer: foam from z up by h over the rectangle x0..x1 / y0..y1, cut round every
    pocket (x, y, w, d) in `pockets`. clip(ya, yb) -> (xa, xb) narrows a band of the layer between
    ya and yb (both edges given, the narrowest wins)."""
    rects = []
    for (x, y, w, d) in pockets:
        rects.append((x - w / 2 - margin, y - d / 2 - margin, x + w / 2 + margin, y + d / 2 + margin))
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
                    box((hx0 - x, yb - ya, h), ((x + hx0) / 2, ym, z + h / 2), look, bevel=0.0012, segs=1)
                x = max(x, hx1)
            if xb - x > 0.0015:
                box((xb - x, yb - ya, h), ((x + xb) / 2, ym, z + h / 2), look, bevel=0.0012, segs=1)


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
def _dims(a, g, s3, along_a, along_g, along_s):
    """Box size in world axes from sizes along three axis-aligned unit vectors."""
    return tuple(along_a * abs(a[i]) + along_g * abs(g[i]) + along_s * abs(s3[i]) for i in range(3))


def _add(*vs):
    return tuple(sum(v[i] for v in vs) for i in range(3))


def _mul(v, k):
    return (v[0] * k, v[1] * k, v[2] * k)


@clustered
def biofoam(c, axis="x", length=0.11, r=0.018, grip=None):
    """The biofoam canister as Halo shows it: a dark olive steel cylinder, knurled rings, a conical
    nozzle with a red safety cap at +axis, a carry grip with a trigger, a white data label. `grip`
    is the way the grip points (a unit vector across the axis); it lies flat to the side when the
    canister is packed under a lid. The label faces up."""
    x, y, z = c
    a = d_(axis)
    if grip is None:
        grip = (0, 0, 1)
    g = grip
    s3 = (a[1] * g[2] - a[2] * g[1], a[2] * g[0] - a[0] * g[2], a[0] * g[1] - a[1] * g[0])
    rot = (0, 90, 0) if axis == "x" else (-90, 0, 0)
    cyl(r, length, (x, y, z), "canister", axis=axis, n=24, bevel=0.003, segs=3)
    for k in (-0.46, 0.46):
        cyl(r + 0.0012, 0.006, _add((x, y, z), _mul(a, length * k)), "black_metal", axis=axis, n=24, bevel=0.0008)
    nz = length / 2
    cyl(r * 0.8, 0.012, _add((x, y, z), _mul(a, nz + 0.006)), "steel", axis=axis, n=20, bevel=0.0015)
    prism(circle(r * 0.62, 20), 0.04, "canister", _add((x, y, z), _mul(a, nz + 0.012)), rot, bevel=0.0012, segs=1,
          taper=r * 0.42)
    cyl(r * 0.24, 0.01, _add((x, y, z), _mul(a, nz + 0.055)), "red", axis=axis, n=12, bevel=0.0015, segs=2)
    # the grip: two posts off the body, a rubber bar across them, the trigger lever at the front post
    base = _add((x, y, z), _mul(g, r))
    for k in (-0.36, -0.1):
        box(_dims(a, g, s3, 0.009, 0.007, 0.012), _add(base, _mul(a, length * k), _mul(g, 0.0035)), "black_metal",
            bevel=0.0015, segs=1)
    box(_dims(a, g, s3, length * 0.34, 0.007, 0.014), _add(base, _mul(a, -length * 0.23), _mul(g, 0.0105)), "rubber",
        bevel=0.0025, segs=2)
    box(_dims(a, g, s3, 0.016, 0.009, 0.005), _add(base, _mul(a, length * 0.06), _mul(g, 0.0045)), "red",
        bevel=0.0012, segs=1)
    # label: on top when the grip lies to the side, else on the side away from the grip
    n = (0, 0, 1) if abs(g[2]) < 0.5 else s3
    up = (n[1] * a[2] - n[2] * a[1], n[2] * a[0] - n[0] * a[2], n[0] * a[1] - n[1] * a[0])
    print_on("lbl_biofoam", _add((x, y, z), _mul(n, r * 0.98), _mul(a, -0.004)), n, up, length * 0.5,
             look="canister", depth=r * 0.5)


def biofoam_pocket(c, axis="x", length=0.11, r=0.018, grip=None):
    """The pocket biofoam() needs: body, nozzle, and the grip to its side."""
    x, y, z = c
    a = d_(axis)
    if grip is None:
        grip = (0, 0, 1)
    along = length + 0.065
    cx, cy = x + a[0] * (0.0325 + 0.002), y + a[1] * (0.0325 + 0.002)
    across = 2 * r + 0.004
    side = abs(grip[0]) + abs(grip[1])     # grip lying flat: the pocket grows that way by its height
    if side:
        across += 0.016
        cx += grip[0] * 0.008
        cy += grip[1] * 0.008
    return (cx, cy, along if axis == "x" else across, across if axis == "x" else along)


def d_(axis):
    return (1, 0, 0) if axis == "x" else (0, 1, 0)


@clustered
def medigel_tube(c, axis="y"):
    """A medigel tube: a flattened blue tube, round at the cap, crimped flat at the far end, a grey
    screw cap. Lies flat, the cap at +axis."""
    x, y, z = c
    d = d_(axis)
    L, W_, T = 0.1, 0.032, 0.018
    # the tube: a tapered box, thick at the cap end, flat at the crimp
    for k in range(5):
        f = k / 4
        t = T * (1 - 0.8 * f) + 0.003
        w = W_ * (1 - 0.1 * f)
        seg = L / 5
        at = -L / 2 + seg * (k + 0.5)
        box((seg + 0.001, w, t) if axis == "x" else (w, seg + 0.001, t),
            (x - d[0] * at, y - d[1] * at, z + t / 2), "medigel", bevel=min(0.003, t * 0.45), segs=2)
    # crimped seal at the far end
    box((0.004, W_ + 0.002, 0.0016) if axis == "x" else (W_ + 0.002, 0.004, 0.0016),
        (x - d[0] * (L / 2 + 0.001), y - d[1] * (L / 2 + 0.001), z + 0.0016), "steel", bevel=0.0004, segs=1)
    # neck and ribbed cap
    cyl(0.006, 0.006, (x + d[0] * (L / 2 + 0.003), y + d[1] * (L / 2 + 0.003), z + T / 2), "steel", axis=axis,
        n=12, bevel=0.0008)
    cyl(0.0085, 0.014, (x + d[0] * (L / 2 + 0.013), y + d[1] * (L / 2 + 0.013), z + T / 2), "steel", axis=axis,
        n=14, bevel=0.0015, segs=2)
    print_on("lbl_medigel", (x - d[0] * 0.012, y - d[1] * 0.012, z + T * 0.8), (0, 0, 1),
             (d[0], d[1], 0), L * 0.6, look="medigel", depth=0.012)


def medigel_pocket(c, axis="y"):
    x, y, z = c
    d = d_(axis)
    return (x + d[0] * 0.01, y + d[1] * 0.01, 0.125 if axis == "x" else 0.036, 0.036 if axis == "x" else 0.125)


@clustered
def injector(c, axis="y", length=0.12, r=0.0055, cap="red", upright=False):
    """A UNSC auto-injector: a flat dark olive pen with rounded edges, a dose window, a white square
    cap at the needle end, the drug named on a band whose colour tells the drug. `cap` is kept for
    the callers: red = epinephrine, orange = atropine."""
    x, y, z = c
    d = d_(axis)
    w, t = 0.024, 0.016
    if upright:
        # standing on its long edge against a wall at -y (the IFAK): flat face to the front
        box((length, t, w), (x, y, z), "injector", cut=0.004, bevel=0.004, segs=3)
        box((0.022, t + 0.001, w + 0.001), (x + length / 2 - 0.01, y, z), "pack_white", cut=0.003, bevel=0.002,
            segs=2)
        box((0.02, 0.0012, 0.009), (x - 0.01, y - t / 2 - 0.0005, z), "glass", bevel=0.0003, segs=1)
        box((0.01, t + 0.0012, w + 0.0012), (x + 0.012, y, z), cap, bevel=0.001, segs=1)
        print_on("lbl_injector", (x - 0.034, y - t / 2, z), (0, -1, 0), (0, 0, 1), 0.04, look="injector")
        return
    box((length, w, t) if axis == "x" else (w, length, t), (x, y, z + t / 2), "injector", cut=0.004,
        bevel=0.004, segs=3)
    # white cap at the needle end, the window and the UNSC mark on top
    box((0.022, w + 0.001, t + 0.001) if axis == "x" else (w + 0.001, 0.022, t + 0.001),
        (x + d[0] * (length / 2 - 0.01), y + d[1] * (length / 2 - 0.01), z + t / 2), "pack_white", cut=0.003,
        bevel=0.002, segs=2)
    box((0.02, 0.009, 0.0012) if axis == "x" else (0.009, 0.02, 0.0012),
        (x - d[0] * 0.01, y - d[1] * 0.01, z + t + 0.0005), "glass", bevel=0.0003, segs=1)
    band = cap
    box((0.01, w + 0.0012, t + 0.0012) if axis == "x" else (w + 0.0012, 0.01, t + 0.0012),
        (x + d[0] * 0.012, y + d[1] * 0.012, z + t / 2), band, bevel=0.001, segs=1)
    print_on("lbl_injector", (x - d[0] * 0.034, y - d[1] * 0.034, z + t), (0, 0, 1), (d[0], d[1], 0), 0.04,
             look="injector")


def injector_pocket(c, axis="y", length=0.12, r=0.0055):
    x, y, z = c
    return (x, y, length + 0.002 if axis == "x" else 0.026, 0.026 if axis == "x" else length + 0.002)


@clustered
def ammo_pack(c, w=0.066, length=0.14, t=0.03, axis="y", standing=False):
    """A sealed ammo pack like the UNSC ones in Halo: a foil pouch, the top third dark red with two
    hanging slots and the round's name, the body grey-olive with the count and a pull tab. Lies flat
    with the red end at +axis, or stands on its bottom edge (red end up) when `standing`."""
    x, y, z = c
    if standing:
        # body and red top standing in a pouch cell, slots cut into the top, the tab on the face
        body = length * 0.64
        box((w, t, body), (x, y, z + body / 2), "pack_grey", bevel=0.004, segs=3)
        box((w, t * 0.9, length - body), (x, y, z + body + (length - body) / 2), "pack_red", bevel=0.004,
            segs=3)
        for sx in (-1, 1):
            box((0.012, t, 0.006), (x + sx * w * 0.25, y, z + length - 0.012), "dark_poly", bevel=0.0006, segs=1)
        print_on("lbl_ammo_top", (x, y - t * 0.45, z + body + (length - body) * 0.45), (0, -1, 0), (0, 0, 1),
                 w * 0.8, look="pack_red", depth=0.006)
        print_on("lbl_ammo_body", (x, y - t / 2, z + body * 0.5), (0, -1, 0), (0, 0, 1), w * 0.8,
                 look="pack_grey", depth=0.006)
        return
    d = d_(axis)
    body = length * 0.64
    top = length - body
    # the pillow of the pouch: body, then the red top, both on a flat crimped seal
    box((w, body, t) if axis == "x" else (w, body, t) if axis == "y" else None,
        (x - d[0] * top / 2, y - d[1] * top / 2, z + t / 2), "pack_grey", bevel=0.005, segs=3) if axis == "y" else \
        box((body, w, t), (x - d[0] * top / 2, y - d[1] * top / 2, z + t / 2), "pack_grey", bevel=0.005, segs=3)
    if axis == "y":
        box((w, top, t * 0.85), (x, y + d[1] * body / 2, z + t * 0.425), "pack_red", bevel=0.005, segs=3)
        box((w + 0.006, length + 0.006, 0.0012), (x, y, z + 0.0012), "pack_grey", bevel=0.0004, segs=1)
        for sx in (-1, 1):
            box((0.012, 0.006, t * 0.85 + 0.001), (x + sx * w * 0.25, y + length / 2 - 0.012, z + t * 0.425),
                "dark_poly", bevel=0.0006, segs=1)
        print_on("lbl_ammo_top", (x, y + body / 2 + top * 0.42, z + t * 0.85), (0, 0, 1), (0, 1, 0), w * 0.8,
                 look="pack_red")
        print_on("lbl_ammo_body", (x, y - top / 2, z + t), (0, 0, 1), (0, 1, 0), w * 0.8, look="pack_grey")
    else:
        box((top, w, t * 0.85), (x + body / 2, y, z + t * 0.425), "pack_red", bevel=0.005, segs=3)
        box((length + 0.006, w + 0.006, 0.0012), (x, y, z + 0.0012), "pack_grey", bevel=0.0004, segs=1)
        for sy in (-1, 1):
            box((0.006, 0.012, t * 0.85 + 0.001), (x + length / 2 - 0.012, y + sy * w * 0.25, z + t * 0.425),
                "dark_poly", bevel=0.0006, segs=1)
        print_on("lbl_ammo_top", (x + body / 2 + top * 0.42, y, z + t * 0.85), (0, 0, 1), (1, 0, 0), w * 0.8,
                 look="pack_red")
        print_on("lbl_ammo_body", (x - top / 2, y, z + t), (0, 0, 1), (1, 0, 0), w * 0.8, look="pack_grey")


def ammo_pack_pocket(c, w=0.066, length=0.14, axis="y"):
    x, y, z = c
    return (x, y, w + 0.004 if axis == "y" else length + 0.004, length + 0.004 if axis == "y" else w + 0.004)


@clustered
def dressing(c, w=0.06, d=0.04, h=0.012, look="pack_olive", flat=True):
    """A sealed dressing pack with a tear strip."""
    x, y, z = c
    image = "lbl_dressing" if look == "pack_olive" else "lbl_gauze"
    if flat:
        # the pillow, its flat crimped seal all round, the tear strip, the print on top
        box((w, d, h), (x, y, z + h / 2), look, bevel=0.003, segs=2)
        box((w + 0.005, d + 0.005, 0.0012), (x, y, z + h * 0.45), look, bevel=0.0004, segs=1)
        box((w * 0.9, 0.003, 0.0012), (x, y + d * 0.36, z + h + 0.0004), "red", bevel=0.0003, segs=1)
        box((0.004, 0.0035, 0.0014), (x - w / 2 - 0.001, y + d * 0.36, z + h * 0.45), "red", bevel=0.0003, segs=1)
        print_on(image, (x, y - d * 0.08, z + h), (0, 0, 1), (0, 1, 0), w * 0.78, look=look)
    else:   # standing against a wall that faces -y (the IFAK's front)
        box((w, h, d), (x, y - h / 2, z), look, bevel=0.0015, segs=1)
        box((w + 0.005, 0.0012, d + 0.005), (x, y - h * 0.45, z), look, bevel=0.0004, segs=1)
        box((w * 0.9, 0.0012, 0.003), (x, y - h - 0.0004, z + d * 0.36), "red", bevel=0.0003, segs=1)
        print_on(image, (x, y - h, z - d * 0.08), (0, -1, 0), (0, 0, 1), w * 0.78, look=look)


@clustered
def tourniquet(c, flat=True):
    """Folded tourniquet: black strap bundle with its windlass and buckle."""
    x, y, z = c
    if flat:
        box((0.07, 0.026, 0.012), (x, y, z + 0.006), "rubber", bevel=0.005, segs=2)
        box((0.008, 0.032, 0.015), (x - 0.018, y, z + 0.0075), "red", bevel=0.002, segs=1)
        box((0.012, 0.022, 0.014), (x + 0.026, y, z + 0.007), "steel", bevel=0.002, segs=1)
        # the windlass rod along the bundle, and the white time tag
        cyl(0.003, 0.055, (x + 0.002, y - 0.009, z + 0.0135), "dark_poly", axis="x", n=10, bevel=0.0006)
        box((0.02, 0.009, 0.0008), (x + 0.004, y + 0.006, z + 0.0124), "pack_white", bevel=0.0002, segs=1)
        print_on("lbl_tq_tag", (x + 0.004, y + 0.006, z + 0.0128), (0, 0, 1), (0, 1, 0), 0.018, look="pack_white")
    else:
        box((0.026, 0.006, 0.06), (x, y - 0.003, z), "rubber", bevel=0.0025, segs=2)
        box((0.03, 0.0065, 0.008), (x, y - 0.00325, z - 0.015), "red", bevel=0.001, segs=1)
        cyl(0.003, 0.05, (x - 0.009, y - 0.0075, z + 0.002), "dark_poly", n=10, bevel=0.0006)
        box((0.012, 0.0008, 0.018), (x + 0.006, y - 0.0065, z + 0.012), "pack_white", bevel=0.0002, segs=1)


@clustered
def suture_kit(c):
    x, y, z = c
    box((0.05, 0.036, 0.01), (x, y, z + 0.005), "pack_white", bevel=0.003, segs=2)
    box((0.055, 0.041, 0.0012), (x, y, z + 0.0045), "pack_white", bevel=0.0004, segs=1)
    box((0.012, 0.03, 0.0012), (x - 0.016, y, z + 0.0104), "red", bevel=0.0003, segs=1)
    print_on("lbl_suture", (x + 0.007, y, z + 0.01), (0, 0, 1), (0, 1, 0), 0.032, look="pack_white")


@clustered
def vial(c, r=0.0065, h=0.03):
    x, y, z = c
    cyl(r, h, (x, y, z + h / 2), "glass_amber", n=14, bevel=0.0012)
    cyl(r + 0.0003, h * 0.45, (x, y, z + h * 0.42), "pack_white", n=14, bevel=0.0002)
    cyl(r + 0.0004, 0.006, (x, y, z + h + 0.003), "steel", n=14, bevel=0.0012)
    cyl(r - 0.0012, 0.0025, (x, y, z + h + 0.0072), "red", n=12, bevel=0.0005)
    print_on("lbl_morphine", (x, y - r, z + h * 0.42), (0, -1, 0), (0, 0, 1), r * 1.6, look="pack_white",
             depth=r * 0.6)


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
            bevel=0.0025, segs=2)


@clustered
def saline_bag(c, w=0.08, d=0.05):
    """A soft saline pouch, its port at one end."""
    x, y, z = c
    box((w, d, 0.014), (x, y, z + 0.007), "pack_white", bevel=0.005, segs=3)
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
    cyl(0.022, length, (x, y, z + 0.022), "orange", axis="x", n=18, bevel=0.003, segs=2)
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
    box((0.07, 0.045, 0.018), (x, y, z + 0.009), "orange", bevel=0.003, segs=2)
    box((0.07, 0.01, 0.019), (x, y, z + 0.0095), "steel", bevel=0.0006, segs=1)
    print_on("lbl_blanket", (x - 0.012, y - 0.012, z + 0.018), (0, 0, 1), (0, 1, 0), 0.04, look="orange")


@clustered
def chemlight(c, look="green_lens", length=0.1):
    x, y, z = c
    cyl(0.0045, length, (x, y, z + 0.0045), look, axis="x", n=12, bevel=0.0008)
    cyl(0.005, 0.01, (x - length / 2 + 0.005, y, z + 0.0045), "dark_poly", axis="x", n=12, bevel=0.0008)


@clustered
def multitool(c):
    x, y, z = c
    box((0.09, 0.02, 0.012), (x, y, z + 0.006), "black_metal", cut=0.003, bevel=0.0015, segs=1)
    box((0.09, 0.004, 0.0124), (x, y, z + 0.0062), "steel", bevel=0.0006, segs=1)


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
    x, y, z = c
    box((length, 0.014, 0.006), (x, y, z + 0.003), "steel", bevel=0.0015, segs=1)
    box((0.026, 0.03, 0.007), (x - length / 2, y, z + 0.0035), "steel", cut=0.006, bevel=0.0015, segs=1)
    box((0.024, 0.026, 0.007), (x + length / 2, y, z + 0.0035), "steel", bevel=0.0015, segs=1)


@clustered
def screwdriver(c, look="orange"):
    x, y, z = c
    cyl(0.008, 0.05, (x - 0.03, y, z + 0.008), look, axis="x", n=8, bevel=0.002, segs=1)
    cyl(0.0022, 0.06, (x + 0.025, y, z + 0.008), "steel", axis="x", n=8, bevel=0.0004)


@clustered
def pliers(c):
    x, y, z = c
    box((0.05, 0.016, 0.008), (x - 0.03, y, z + 0.004), "steel", cut=0.004, bevel=0.0012, segs=1)
    cyl(0.004, 0.009, (x - 0.003, y, z + 0.0045), "black_metal", n=10, bevel=0.0006)
    for sy in (-1, 1):
        box((0.06, 0.011, 0.009), (x + 0.03, y + sy * 0.009, z + 0.0045), "red", cut=0.003, bevel=0.0025,
            segs=2)


@clustered
def tape_roll(c):
    x, y, z = c
    cyl(0.03, 0.025, (x, y, z + 0.0125), "rubber", n=22, bevel=0.002, segs=2)
    cyl(0.016, 0.026, (x, y, z + 0.013), "pack_olive", n=16, bevel=0.0008)
    print_on("lbl_tape", (x, y - 0.03, z + 0.0125), (0, -1, 0), (0, 0, 1), 0.04, look="rubber", depth=0.012)


@clustered
def initiator(c):
    """A firing device: a yellow box with a safety bail and a red button."""
    x, y, z = c
    box((0.06, 0.04, 0.028), (x, y, z + 0.014), "hazard_yellow", cut=0.004, bevel=0.003, segs=2)
    cyl(0.009, 0.004, (x + 0.012, y, z + 0.03), "red", n=14, bevel=0.0008)
    box((0.02, 0.006, 0.012), (x - 0.014, y, z + 0.034), "steel", bevel=0.0012, segs=1)
    print_on("lbl_initiator", (x, y - 0.013, z + 0.028), (0, 0, 1), (0, 1, 0), 0.034, look="hazard_yellow")


@clustered
def multimeter(c):
    x, y, z = c
    box((0.06, 0.09, 0.02), (x, y, z + 0.01), "hazard_yellow", bevel=0.004, segs=2)
    box((0.044, 0.026, 0.002), (x, y + 0.025, z + 0.0205), "glass", bevel=0.0005, segs=1)
    cyl(0.012, 0.004, (x, y - 0.012, z + 0.021), "dark_poly", n=16, bevel=0.0008)
    for k in (-1, 1):
        cyl(0.003, 0.004, (x + k * 0.018, y - 0.035, z + 0.021), "red" if k > 0 else "dark_poly", n=10,
            bevel=0.0006)


@clustered
def demo_block(c):
    """A demolition charge: olive block, yellow tape, a detonator well."""
    x, y, z = c
    box((0.09, 0.05, 0.024), (x, y, z + 0.012), "olive", bevel=0.003, segs=2)
    box((0.012, 0.052, 0.025), (x + 0.025, y, z + 0.0125), "hazard_yellow", bevel=0.001, segs=1)
    cyl(0.006, 0.004, (x - 0.025, y, z + 0.025), "black_metal", n=12, bevel=0.0008)
    print_on("lbl_demo", (x - 0.003, y, z + 0.024), (0, 0, 1), (0, 1, 0), 0.04, look="olive")


@clustered
def cable_coil(c, r=0.03):
    x, y, z = c
    cyl(r, 0.012, (x, y, z + 0.006), "rubber", n=20, bevel=0.004, segs=2)
    cyl(r * 0.45, 0.0125, (x, y, z + 0.0063), "foam", n=14, bevel=0.0008)


@clustered
def gas_mask(c):
    """Gas mask lying face up: rubber body, visor, a filter on its cheek."""
    x, y, z = c
    prism(rrect(0.1, 0.075, 0.03, 4), 0.026, "rubber", (x, y, z), bevel=0.008, segs=2)
    prism(rrect(0.07, 0.04, 0.016, 3), 0.004, "glass", (x, y + 0.008, z + 0.025), bevel=0.0015, segs=1)
    cyl(0.018, 0.022, (x + 0.062, y - 0.01, z + 0.018), "olive_dark", axis="x", n=18, bevel=0.003, segs=2)
    cyl(0.011, 0.006, (x, y - 0.03, z + 0.028), "rubber", n=16, bevel=0.0015)
    for sx in (-1, 1):
        box((0.03, 0.012, 0.003), (x + sx * 0.045, y + 0.025, z + 0.0015), "webbing", bevel=0.0006, segs=1)


@clustered
def filter_can(c):
    x, y, z = c
    cyl(0.019, 0.024, (x, y, z + 0.012), "olive_dark", n=18, bevel=0.003, segs=2)
    cyl(0.008, 0.0045, (x, y, z + 0.0265), "black_metal", n=12, bevel=0.0008)
    cyl(0.0195, 0.003, (x, y, z + 0.004), "black_metal", n=18, bevel=0.0004)
    print_on("lbl_filter", (x, y - 0.019, z + 0.013), (0, -1, 0), (0, 0, 1), 0.03, look="olive_dark", depth=0.009)


@clustered
def decon_kit(c):
    """A decontamination kit: a flat yellow-banded olive pack with a sponge mitt."""
    x, y, z = c
    box((0.09, 0.07, 0.02), (x, y, z + 0.01), "pack_olive", bevel=0.003, segs=2)
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
    cyl(0.034, 0.016, (x, y, z + 0.008), "shell_white", n=28, bevel=0.003, segs=2)
    cyl(0.0345, 0.004, (x, y, z + 0.008), "red", n=28, bevel=0.0008)
    cyl(0.009, 0.003, (x, y, z + 0.0165), "black_metal", n=16, bevel=0.0006)
    cyl(0.006, 0.003, (x, y, z + 0.0175), "green_lens", n=16, bevel=0.0006)


@clustered
def flashlight(c, length=0.09):
    x, y, z = c
    cyl(0.0065, length, (x, y, z), "black_metal", axis="x", n=14, bevel=0.0012)
    cyl(0.0085, 0.02, (x + length / 2 - 0.01, y, z), "black_metal", axis="x", n=14, bevel=0.0015)
    cyl(0.0072, 0.002, (x + length / 2 + 0.0005, y, z), "glass", axis="x", n=14, bevel=0.0004)


# --- lid linings -------------------------------------------------------------------------------------
def lid_straps(W, D, z_lining, flats, card=None):
    # no flats: no straps either, only the card
    """Elastic straps on a lid's lining (its underside, at z_lining, facing down while shut) holding
    flat packs: each flat is (x, y, w, d, thickness, look). Two webbing bands run across the lid
    over them. card: (x, y, w) for a laminated instruction card. All in the lid group."""
    with lid():
        with cluster():
            for (x, y, w, d, t, look) in flats:
                box((w, d, t), (x, y, z_lining - t / 2), look, bevel=0.002, segs=1)
                box((w + 0.005, d + 0.005, 0.0012), (x, y, z_lining - t * 0.5), look, bevel=0.0004, segs=1)
                box((w * 0.8, 0.003, 0.0012), (x, y + d * 0.3, z_lining - t - 0.0005), "red", bevel=0.0003,
                    segs=1)
                # read with the lid standing open: the hinge side (+y) is then at the bottom
                print_on("lbl_dressing" if look == "pack_olive" else "lbl_gauze", (x, y + d * 0.1, z_lining - t),
                         (0, 0, -1), (0, -1, 0), w * 0.75, look=look)
            tmax = max([f[4] for f in flats] + [0.006])
            for sx in ((-1, 1) if flats else ()):
                x = sx * W * 0.3
                box((0.022, D - 0.05, 0.0025), (x, 0, z_lining - tmax - 0.0015), "webbing", bevel=0.0006, segs=1)
                for sy in (-1, 1):
                    box((0.022, 0.012, tmax + 0.003), (x, sy * (D / 2 - 0.028), z_lining - (tmax + 0.003) / 2),
                        "webbing", bevel=0.0006, segs=1)
            if card is not None:
                # a laminated card riveted to the lining; its print is not checked, the check casts
                # its rays through the shut case and hits the tray
                cx, cy, cw = card
                ch = cw * 0.62
                Fc = frame((cx, cy, z_lining - 0.0005), (0, 0, -1), (0, 1, 0))
                lbox(Fc, (cw, ch, 0.0012), (0, 0, 0), "pack_white", cut=cw * 0.05, bevel=0.0004)
                for sx in (-1, 1):
                    for sy in (-1, 1):
                        lcyl(Fc, 0.0014, 0.0008, (sx * (cw / 2 - 0.004), sy * (ch / 2 - 0.004), 0.0012), "steel",
                             n=8, bevel=0.0005)
                decal("data_panel", (cx, cy, z_lining - 0.0017), (0, 0, -1), (0, -1, 0), cw * 0.7, depth=0.0015,
                      check=False)


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
    """MFAK (and MFAK+ with more=True): the big medical case. Two biofoam canisters along the left,
    medigel and saline on the right, injectors in a row, shears, gauze, tourniquet, dressings, vials
    and gloves each in their cut, flat packs under the lid's straps."""
    W, D, H, lid_h, cap = (0.44, 0.24, 0.36, 0.05, 0.034) if more else (0.46, 0.25, 0.25, 0.048, 0.034)
    with contents():
        pockets = []
        items = []
        for y, gy in ((-0.088, -1), (-0.038, 1)):
            items.append(lambda zf, y=y, gy=gy: biofoam((-0.105, y, zf + 0.012), axis="x", grip=(0, gy, 0)))
            pockets.append(biofoam_pocket((-0.105, y, 0), axis="x", grip=(0, gy, 0)))
        items.append(lambda zf: medigel_tube((0.1, -0.035, zf), axis="x"))
        pockets.append(medigel_pocket((0.1, -0.035, 0), axis="x"))
        items.append(lambda zf: saline_bag((0.096, -0.085, zf), 0.08, 0.044))
        pockets.append((0.1, -0.085, 0.096, 0.044))
        for k, y in enumerate((-0.005, 0.023, 0.051)):
            items.append(lambda zf, y=y, k=k: injector((0.055, y, zf), axis="x", length=0.1,
                                                       cap="red" if k < 2 else "orange"))
            pockets.append(injector_pocket((0.055, y, 0), axis="x", length=0.1))
        items.append(lambda zf: shears((-0.08, 0.03, zf)))
        pockets.append((-0.08, 0.03, 0.14, 0.03))
        items.append(lambda zf: gauze_roll((-0.1, 0.07, zf)))
        pockets.append((-0.1, 0.07, 0.07, 0.028))
        items.append(lambda zf: tourniquet((-0.025, 0.07, zf)))
        pockets.append((-0.025, 0.07, 0.078, 0.034))
        items.append(lambda zf: dressing((0.045, 0.095, zf), 0.05, 0.036, 0.012))
        pockets.append((0.045, 0.095, 0.05, 0.036))
        items.append(lambda zf: suture_kit((0.1, 0.095, zf)))
        pockets.append((0.1, 0.095, 0.05, 0.036))
        items.append(lambda zf: pill_box((0.15, 0.095, zf)))
        pockets.append((0.15, 0.095, 0.04, 0.026))
        for y in (0.0, 0.025):
            items.append(lambda zf, y=y: vial((0.165, y, zf)))
            pockets.append((0.165, y, 0.0135, 0.0135))
        items.append(lambda zf: glove_pack((-0.16, 0.095, zf), 0.04, 0.03))
        pockets.append((-0.16, 0.095, 0.04, 0.03))
        if more:
            items.append(lambda zf: blanket((0.145, 0.065, zf)))
            pockets.append((0.145, 0.065, 0.07, 0.045))
        zf = case_tray(W, D, H, lid_h, cap, pockets, h=0.016)
        for it in items:
            it(zf)
    lid_straps(W, D, H + 0.002 - 0.016, [
        (-W * 0.3, 0.05, 0.07, 0.07, 0.004, "pack_olive"),
        (W * 0.3, 0.05, 0.06, 0.04, 0.006, "pack_white"),
    ], card=(0.0, -0.05, 0.1))


def fill_mfakplus():
    fill_mfak(more=True)


def fill_ifak():
    """IFAK: the compartment behind the front lid - dressings, an injector and a tourniquet standing
    against the back wall, held by two elastic bands, gloves tucked behind."""
    with contents():
        box((0.14, 0.004, 0.09), (0, -0.0115, 0.06), "foam", bevel=0.0012, segs=1)
        wall = -0.0135
        for x in (-0.045, -0.005):
            dressing((x, wall, 0.07), 0.034, 0.05, 0.012, flat=False)
        # the injector lies along the bottom of the compartment, flat side to the wall
        injector((0.012, wall - 0.0085, 0.027), axis="x", length=0.07, cap="red", upright=True)
        tourniquet((0.045, wall, 0.075), flat=False)
        with cluster():
            for z in (0.052, 0.088):
                box((0.136, 0.0015, 0.012), (0, wall - 0.0145, z), "webbing", bevel=0.0004, segs=1)


def fill_afak():
    """AFAK: the sterile field generator in the middle of an octagonal tray, a biofoam canister along
    each side, medigel and injectors behind, dressings and a chest seal across the front."""
    W, D, C = 0.36, 0.27, 0.06
    with contents():
        prism(inset(rect(W, D, C), 0.0085), 0.004, "foam", (0, 0, 0.02), bevel=0.0012, segs=1)
        zf = 0.024
        pockets = [(0, 0, 0.07, 0.07)]
        for sx in (-1, 1):
            pockets.append(biofoam_pocket((sx * 0.115, -0.03, 0), axis="y", length=0.09, r=0.016, grip=(sx, 0, 0)))
        pockets.append(medigel_pocket((-0.055, 0.095, 0), axis="x"))
        for x in (0.048, 0.076):
            pockets.append(injector_pocket((x, 0.06, 0), axis="y", length=0.1))
        for x in (-0.04, 0.04):
            pockets.append((x, -0.056, 0.05, 0.03))
        pockets.append((0.0, -0.1, 0.06, 0.044))
        pocket_foam(-W / 2 + 0.012, -D / 2 + 0.012, W / 2 - 0.012, D / 2 - 0.012, zf, 0.012, pockets,
                    clip=octagon_clip(W, D, C, 0.024))
        field_generator((0, 0, zf))
        for sx in (-1, 1):
            biofoam((sx * 0.115, -0.03, zf + 0.012), axis="y", length=0.09, r=0.016, grip=(sx, 0, 0))
        medigel_tube((-0.055, 0.095, zf), axis="x")
        for k, x in enumerate((0.048, 0.076)):
            injector((x, 0.06, zf), axis="y", length=0.1, cap="red" if k == 0 else "orange")
        for x in (-0.04, 0.04):
            dressing((x, -0.056, zf), 0.05, 0.03, 0.01)
        chest_seal((0.0, -0.1, zf))


def fill_narcbox():
    """Narc box: injectors in a row, vials each in its own cell, pill boxes, a tamper tag."""
    W, D = 0.30, 0.17
    with contents():
        prism(inset(rrect(W, D, 0.022, 4), 0.0075), 0.004, "foam", (0, 0, 0.03), bevel=0.0012, segs=1)
        zf = 0.034
        pockets = []
        for k in range(4):
            pockets.append(injector_pocket((-0.1 + k * 0.03, -0.004, 0), length=0.1))
        vials = [(0.04 + i * 0.022, -0.04 + j * 0.022) for i in range(4) for j in range(2)]
        for x, y in vials:
            pockets.append((x, y, 0.0135, 0.0135))
        for x in (0.045, 0.09):
            pockets.append((x, 0.045, 0.04, 0.026))
        pockets.append((-0.09, 0.062, 0.12, 0.012))
        # the corner bumpers (r 0.024 at x 0.124, y 0.05) reach into the tray
        def clip(ya, yb):
            y = max(abs(ya), abs(yb))
            x = 0.097 if y > 0.024 else W / 2 - 0.015
            return (-x, x)
        pocket_foam(-W / 2 + 0.015, -D / 2 + 0.015, W / 2 - 0.015, D / 2 - 0.015, zf, 0.012, pockets, clip=clip)
        for k in range(4):
            injector((-0.1 + k * 0.03, -0.004, zf), length=0.1, cap="red" if k < 2 else "orange")
        for x, y in vials:
            vial((x, y, zf), h=0.026)
        for x in (0.045, 0.09):
            pill_box((x, 0.045, zf))
        with cluster():
            box((0.12, 0.012, 0.004), (-0.09, 0.062, zf + 0.002), "hazard_yellow", bevel=0.0008, segs=1)


def fill_utility_pouch():
    """Utility pouch: a cut insert with a flashlight, a multitool, two chemlights and a notebook."""
    W, D, H = 0.15, 0.06, 0.118
    with contents():
        box((W - 0.012, D - 0.012, 0.003), (0, 0, H - 0.03), "foam", bevel=0.0006, segs=1)
        z = H - 0.0285
        pockets = [(-0.03, -0.012, 0.1, 0.017), (0.045, -0.012, 0.04, 0.02), (-0.025, 0.014, 0.1, 0.01),
                   (0.045, 0.014, 0.04, 0.01)]
        pocket_foam(-W / 2 + 0.006, -D / 2 + 0.006, W / 2 - 0.006, D / 2 - 0.006, z, 0.01, pockets, margin=0.0015)
        flashlight((-0.03, -0.012, z + 0.0065))
        multitool((0.045, -0.012, z))
        chemlight((-0.025, 0.014, z), "green_lens", 0.1)
        chemlight((0.045, 0.014, z), "hazard_yellow", 0.04)


def fill_ammo_pouch():
    """Ammo pouch: an ammo pack standing in each cell, its red top showing above the rim."""
    D, H = 0.056, 0.14
    with contents():
        for sx in (-1, 1):
            ammo_pack((sx * 0.025, 0.0, H - 0.047 - 0.075), w=0.042, length=0.115, t=0.03, standing=True)


def fill_ammo_bag():
    """Ammo crate: eight sealed ammo packs in two rows, each in its cut, the lot card under the lid."""
    W, D, H, lid_h, cap = 0.36, 0.18, 0.2, 0.042, 0.03
    with contents():
        spots = [(x, y) for y in (-0.04, 0.04) for x in (-0.105, -0.035, 0.035, 0.105)]
        pockets = [ammo_pack_pocket((x, y, 0), w=0.062, length=0.072, axis="x") for x, y in spots]
        zf = case_tray(W, D, H, lid_h, cap, pockets, h=0.018)
        for x, y in spots:
            ammo_pack((x, y, zf - 0.006), w=0.062, length=0.072, t=0.028, axis="x")
    lid_straps(W, D, H + 0.002 - 0.016, [], card=(0.0, 0.0, 0.1))


def fill_engineer_bag():
    """Engineer case: tools in cut foam, charges, the initiator, det cord, tape."""
    W, D, H, lid_h, cap = 0.42, 0.21, 0.21, 0.046, 0.034
    with contents():
        pockets = [(-0.09, -0.07, 0.15, 0.032), (-0.085, -0.04, 0.12, 0.018), (-0.085, -0.018, 0.12, 0.018),
                   (-0.03, 0.0, 0.12, 0.02), (0.12, -0.04, 0.06, 0.09),
                   (-0.11, 0.05, 0.09, 0.05), (-0.01, 0.05, 0.09, 0.05), (0.12, 0.05, 0.06, 0.06),
                   (0.065, -0.07, 0.06, 0.04), (0.14, -0.075, 0.06, 0.028)]
        zf = case_tray(W, D, H, lid_h, cap, pockets, h=0.014)
        wrench((-0.09, -0.07, zf))
        screwdriver((-0.085, -0.04, zf), "orange")
        screwdriver((-0.085, -0.018, zf), "red")
        pliers((-0.03, 0.0, zf))
        multimeter((0.12, -0.04, zf))
        for x in (-0.11, -0.01):
            demo_block((x, 0.05, zf))
        tape_roll((0.12, 0.05, zf))
        initiator((0.065, -0.07, zf))
        cable_coil((0.14, -0.075, zf), r=0.014)
    lid_straps(W, D, H + 0.002 - 0.016, [
        (-W * 0.3, -0.04, 0.08, 0.05, 0.006, "pack_olive"),
        (W * 0.3, -0.04, 0.06, 0.06, 0.004, "pack_white"),
    ], card=(0.0, 0.05, 0.09))


def fill_cbrn_bag():
    """CBRN case: the mask in its own cut, filters, auto-injectors, decon kit, detector paper."""
    W, D, H, lid_h, cap = 0.4, 0.23, 0.24, 0.05, 0.034
    with contents():
        pockets = [(-0.085, 0.0, 0.11, 0.08), (-0.02, -0.0, 0.0, 0.0)]
        pockets = [(-0.075, 0.0, 0.17, 0.08)]
        for x in (0.035, 0.08, 0.125):
            pockets.append((x, -0.065, 0.038, 0.038))
        for y in (0.025, 0.055, 0.085):
            pockets.append(injector_pocket((0.08, y, 0), axis="x", length=0.1))
        pockets.append((-0.1, -0.085, 0.09, 0.07))
        pockets.append((-0.01, -0.085, 0.05, 0.08))
        pockets.append((-0.1, 0.085, 0.045, 0.032))
        zf = case_tray(W, D, H, lid_h, cap, pockets, h=0.016)
        gas_mask((-0.085, 0.005, zf))
        for x in (0.035, 0.08, 0.125):
            filter_can((x, -0.065, zf))
        for y in (0.025, 0.055, 0.085):
            injector((0.08, y, zf), axis="x", length=0.1, cap="orange")
        decon_kit((-0.1, -0.085, zf))
        detector_paper((-0.01, -0.085, zf))
        dressing((-0.1, 0.085, zf), 0.045, 0.032, 0.01, look="pack_white")
    lid_straps(W, D, H + 0.002 - 0.016, [
        (-W * 0.3, -0.04, 0.07, 0.07, 0.004, "pack_white"),
        (W * 0.3, -0.04, 0.06, 0.04, 0.006, "pack_olive"),
    ], card=(0.0, 0.055, 0.1))
