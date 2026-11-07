"""The kit models, built from the parts in unsc_lib. Blender space: front at -y, z up, metres.

Each builder returns the texture size of its kit. EFAK's five kits go into addons/kits, the five
pouches of Enhanced Utility Pouches into addons/eup (ADDON below).
"""
import math

from unsc_lib import (box, bolt, cyl, decal, frame, hinge, lbox, lcyl, plate, prism, rect, rivets, rrect, screw,
                      toggle_latch, vents)

F = (0, -1, 0)   # front normal
B = (0, 1, 0)
UP = (0, 0, 1)
DOWN = (0, 0, -1)
R = (1, 0, 0)
L_ = (-1, 0, 0)


def _on_face(x0, z0, x1, z1):
    """Centre and rotation of a plate lying on the chamfer from (x0, z0) to (x1, z1) in the x/z plane."""
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    nx, nz = (z1 - z0), -(x1 - x0)
    ln = math.hypot(nx, nz)
    nx, nz = nx / ln, nz / ln
    if nz < 0:
        nx, nz = -nx, -nz
    return (cx, cz), math.degrees(math.atan2(nx, nz)), math.hypot(x1 - x0, z1 - z0)


def feet(xs, ys, z=0.0, size=0.022, look="rubber"):
    """Rubber feet under a case."""
    for x in xs:
        for y in ys:
            lbox(frame((x, y, z + 0.0005), DOWN, (0, 1, 0)), (size, size, 0.003), (0, 0, 0), look, cut=0.004,
                 bevel=0.0008)


def molle_back(W, D, H, y0, look="dark_poly"):
    """MOLLE back plate with two straps and snaps, on the back face at y0."""
    box((W * 0.78, 0.01, H * 0.9), (0, y0 + 0.005, H * 0.49), look, cut=0.012, axis="y", bevel=0.002, segs=2)
    for sx in (-W * 0.21, W * 0.21):
        box((0.026, 0.005, H * 0.95), (sx, y0 + 0.012, H * 0.49), "webbing", bevel=0.0012, segs=1)
        box((0.03, 0.007, 0.014), (sx, y0 + 0.016, 0.012), "black_metal", cut=0.003, axis="y", bevel=0.001,
            segs=1)
        cyl(0.0045, 0.003, (sx, y0 + 0.0205, 0.012), "steel", axis="y", n=16)
    for sz in (H * 0.2, H * 0.8):
        screw((W * 0.33, y0 + 0.01, sz), B)
        screw((-W * 0.33, y0 + 0.01, sz), B)


def carry_handle(cx, cy, z, length, look="rubber"):
    """Folding top handle: two pivot mounts, a steel bar and a rubber grip, lying flat."""
    for sx in (-1, 1):
        lbox(frame((cx + sx * length / 2, cy, z), UP, B), (0.02, 0.026, 0.012), (0, 0, 0), "black_metal",
             cut=0.004, bevel=0.0015)
        bolt((cx + sx * (length / 2 + 0.011), cy, z + 0.006), (sx, 0, 0), 0.003)
    cyl(0.0042, length + 0.012, (cx, cy, z + 0.008), "steel", axis="x", n=12)
    cyl(0.0085, length * 0.72, (cx, cy, z + 0.008), look, axis="x", n=16, bevel=0.002, segs=2)


def side_handle(x, sx, z, look="black_metal"):
    """Fixed side handle: two mounts with bolts and a bar."""
    for sy in (-1, 1):
        box((0.022, 0.016, 0.03), (x + sx * 0.011, sy * 0.045, z), look, bevel=0.002, segs=2)
        bolt((x + sx * 0.022, sy * 0.045, z - 0.007), (sx, 0, 0), 0.0028)
    box((0.012, 0.106, 0.012), (x + sx * 0.024, 0, z + 0.004), look, bevel=0.003, segs=2)


def unsc_case(W, D, H, body, lid_h=0.048, base_h=0.026, cap=0.034, latches=2, handles=True):
    """A UNSC case in the style of Halo Infinite's: a black polymer frame (skid, end caps and lid cap)
    around a painted body, draw latches on the front, hinge at the back, recessed grips in the end
    caps. Returns the places the decals of the kit go."""
    zb, zl = base_h, H - lid_h
    inner = W - 2 * cap
    # skid, its lower edges cut
    box((W + 0.006, D + 0.012, base_h), (0, 0, base_h / 2), "frame_black", cut=0.008, cuts=(1, 1, 0, 0),
        axis="x", bevel=0.003, segs=2)
    # body between the end caps
    box((inner + 0.004, D, zl - zb + 0.004), (0, 0, (zb + zl) / 2), body, bevel=0.003, segs=2)
    # raised front and back panels with cut lower corners
    for sy in (-1, 1):
        box((inner * 0.84, 0.005, (zl - zb) * 0.74), (0, sy * (D / 2 + 0.0025), zb + (zl - zb) * 0.46), body,
            cut=0.02, cuts=(1, 1, 0, 0), axis="y", bevel=0.002, segs=2)
    # end caps, proud of the body all round
    for sx in (-1, 1):
        x = sx * (W / 2 - cap / 2)
        box((cap, D + 0.012, zl - zb + 0.006), (x, 0, (zb + zl) / 2), "frame_black", cut=0.006, axis="x",
            bevel=0.004, segs=3)
        if handles:
            # recessed grip: a dark pocket with a bar across it
            gw = min(0.11, D * 0.6)
            gz = zb + (zl - zb) * 0.62
            Fh = frame((sx * W / 2, 0, gz), (sx, 0, 0), UP)
            lbox(Fh, (gw, 0.034, 0.002), (0, 0, 0), "rubber", cut=0.006, bevel=0.0008)
            lbox(Fh, (gw - 0.01, 0.012, 0.007), (0, 0.004, 0.0015), "frame_black", cut=0.003, bevel=0.002, segs=2)
            for sy in (-1, 1):
                screw((sx * W / 2 + sx * 0.002, sy * (gw / 2 + 0.008), gz), (sx, 0, 0), 0.0022)
        # small yellow marker in the lower front corner of each cap
        lbox(frame((x, -D / 2 - 0.006, zb + 0.014), F, UP), (0.012, 0.012, 0.0008), (0, 0, 0), "hazard_yellow",
             bevel=0.0003)
    # seal under the lid
    box((W - 0.004, D + 0.004, 0.005), (0, 0, zl + 0.001), "rubber", bevel=0.001, segs=1)
    # lid cap over the whole length, with two ribs
    box((W + 0.006, D + 0.016, lid_h), (0, 0, H - lid_h / 2 + 0.002), "frame_black", bevel=0.008, segs=3,
        taper=0.003)
    top = H + 0.002
    for sy in (-1, 1):
        lbox(frame((0, sy * (D / 2 - 0.018), top - 0.0005), UP, B), (W * 0.62, 0.008, 0.003), (0, 0, 0),
             "frame_black", cut=0.003, bevel=0.0012)
    # latches over the seam, hinge at the back
    xs = [0.0] if latches == 1 else [sx * inner * 0.3 for sx in (-1, 1)]
    for x in xs:
        toggle_latch((x, -D / 2 - 0.0055, zl + 0.004), F, w=0.034, h=0.054, look="frame_black")
    hinge((-inner * 0.4, D / 2 + 0.008, zl + 0.004), (inner * 0.4, D / 2 + 0.008, zl + 0.004), r=0.005,
          knuckles=7, look="frame_black")
    feet((-W / 2 + 0.05, W / 2 - 0.05), (-D / 2 + 0.04, D / 2 - 0.04), size=0.03)
    return dict(front=-D / 2 - 0.005, back=D / 2 + 0.005, top=top, zb=zb, zl=zl, inner=inner,
                mid=zb + (zl - zb) * 0.46)


# ===================================================================================================
# EFAK
# ===================================================================================================
def ifak():
    """IFAK: an angular polymer case for one casualty, belt or MOLLE mounted, red pull tab."""
    W, D, H = 0.17, 0.06, 0.13
    cut = 0.022
    box((W, D, H), (0, 0, H / 2), "olive", cut=cut, cuts=(0.5, 0.5, 1, 1), axis="y", bevel=0.004, segs=3)
    # moulded parting line round the body
    for sy in (-1, 1):
        box((W - 0.03, 0.002, 0.003), (0, sy * (D / 2 + 0.0006), 0.006), "olive", bevel=0.0006, segs=1)
    # front lid, a little smaller, so the seam shows all round
    lf = -D / 2 - 0.0075
    box((0.152, 0.008, 0.114), (0, -D / 2 - 0.0035, 0.066), "olive_dark", cut=0.018, cuts=(0.5, 0.5, 1, 1),
        axis="y", bevel=0.0025, segs=2)
    # raised label field on the lid
    box((0.128, 0.003, 0.066), (0, -D / 2 - 0.009, 0.07), "olive_dark", cut=0.006, axis="y", bevel=0.001, segs=1)
    decal("ifak_label", (0, -D / 2 - 0.0105, 0.07), F, UP, 0.122, depth=0.004)
    # hinge along the foot of the lid
    hinge((-0.055, lf + 0.001, 0.008), (0.055, lf + 0.001, 0.008), r=0.0032, knuckles=5)
    # finger notch to open the lid, top middle
    box((0.03, 0.003, 0.008), (0, lf - 0.0015, 0.112), "olive_dark", cut=0.003, axis="y", bevel=0.0012, segs=1)
    # pull tab on top, and its loop
    box((0.05, 0.018, 0.012), (0, -0.012, H + 0.004), "red", cut=0.004, axis="y", bevel=0.002, segs=2)
    box((0.03, 0.006, 0.02), (0, -0.024, H + 0.012), "red", cut=0.006, cuts=(0, 0, 1, 1), axis="y",
        bevel=0.0015, segs=2)
    bolt((0, -0.012, H + 0.01), UP, 0.003)
    # grip ribs on both sides
    for sx in (-1, 1):
        for k in range(3):
            box((0.006, 0.044, 0.007), (sx * (W / 2 + 0.001), 0, 0.03 + k * 0.022), "olive_dark", bevel=0.0015,
                segs=2)
    decal("cross_tag", (W / 2 + 0.001, 0, 0.104), R, UP, 0.026, depth=0.004)
    plate((-W / 2, 0, 0.104), L_, UP, 0.04, 0.022, "black_metal", "serial_white")
    decal("qa_red", (W / 2 + 0.004, -0.012, 0.012), R, UP, 0.016, depth=0.006)
    # guards on the cut top corners
    for sx in (-1, 1):
        (cx, cz), ang, ln = _on_face(sx * (W / 2 - cut), H, sx * W / 2, H - cut)
        prism(rect(ln * 0.8, D + 0.004), 0.004, "dark_poly", (cx, 0, cz), (0, ang, 0), bevel=0.0012, segs=1)
    decal("egb_white", (0.045, 0.012, H), UP, B, 0.02, depth=0.004)
    molle_back(W, D, H, D / 2)
    return 2048


def afak():
    """AFAK: the flat field medkit - octagonal hard case, light lid with the medical mark, red
    reflectors, rubber grips front and back."""
    W, D = 0.36, 0.27
    C = 0.06
    base_h, lid_z, lid_h = 0.034, 0.039, 0.040
    top = lid_z + lid_h
    prism(rect(W, D, C), base_h, "shell_dark", bevel=0.003, segs=2)
    prism(rect(W - 0.008, D - 0.008, C - 0.002), 0.008, "rubber", (0, 0, base_h - 0.002), bevel=0.001, segs=1)
    prism(rect(W, D, C), lid_h, "shell_grey", (0, 0, lid_z), bevel=0.003, segs=2, taper=0.012)
    # centre plate with the mark, screwed down
    box((0.135, 0.135, 0.008), (0, 0, top + 0.003), "shell_white", cut=0.01, bevel=0.002, segs=2, taper=0.003)
    decal("med_h", (0, 0, top + 0.007), UP, B, 0.118, depth=0.003)
    for sx in (-1, 1):
        for sy in (-1, 1):
            screw((sx * 0.056, sy * 0.056, top + 0.007), UP, 0.0024)
    # wings left and right of it, each with a vent
    wing = [(0.078, -0.072), (0.138, -0.046), (0.138, 0.046), (0.078, 0.072)]
    prism(wing, 0.004, "shell_white", (0, 0, top - 0.001), bevel=0.0012, segs=1)
    prism([(-x, y) for x, y in reversed(wing)], 0.004, "shell_white", (0, 0, top - 0.001), bevel=0.0012, segs=1)
    for sx in (-1, 1):
        vents((sx * 0.108, 0, top + 0.003), UP, (1, 0, 0), 5, 0.058, 0.0075, look="dark_poly")
    # reflectors on top, on the diagonals around the plate
    for sx in (-1, 1):
        for sy in (-1, 1):
            ang = math.degrees(math.atan2(sy * 0.085, sx * 0.1)) + 90
            prism(rect(0.032, 0.016, 0.006, (1, 1, 0, 0)), 0.003, "red_reflector",
                  (sx * 0.1, sy * 0.086, top - 0.001), (0, 0, ang), bevel=0.0008, segs=1)
    # reflectors on the cut corners of the base
    for sx in (-1, 1):
        for sy in (-1, 1):
            nx, ny = sx / math.sqrt(2), sy / math.sqrt(2)
            cx, cy = sx * (W / 2 - C / 2), sy * (D / 2 - C / 2)
            a = math.degrees(math.atan2(nx, -ny))
            prism(rect(0.04, 0.016, 0.004), 0.003, "red_reflector", (cx, cy, base_h / 2), (90, 0, a),
                  bevel=0.0008, segs=1)
    # status lens
    cyl(0.006, 0.003, (0.105, -0.085, top + 0.0005), "black_metal", n=20)
    cyl(0.0038, 0.003, (0.105, -0.085, top + 0.0015), "green_lens", n=20)
    # rubber grips front and back, ribbed, bolted at the ends
    for sy in (-1, 1):
        y = sy * (D / 2 + 0.004)
        box((0.2, 0.026, 0.05), (0, y, 0.04), "rubber", bevel=0.006, segs=3)
        for k in range(6):
            box((0.186, 0.004, 0.003), (0, y + sy * 0.0135, 0.0235 + k * 0.0066), "rubber", bevel=0.0008, segs=1)
        for sx in (-1, 1):
            bolt((sx * 0.092, y + sy * 0.0155, 0.04), (0, sy, 0), 0.003)
    # latches on both grips
    for sy in (-1, 1):
        box((0.034, 0.01, 0.032), (0, sy * (D / 2 + 0.0215), 0.04), "steel", cut=0.005, axis="y", bevel=0.0015,
            segs=2)
        box((0.018, 0.004, 0.006), (0, sy * (D / 2 + 0.0275), 0.048), "black_metal", bevel=0.0008, segs=1)
    # labels
    decal("afak_label", (0, -0.095, top), UP, B, 0.12, depth=0.003)
    decal("serial_white", (0, 0.098, top), UP, (0, -1, 0), 0.08, depth=0.003)
    decal("qa_red", (-0.11, -D / 2, 0.017), F, UP, 0.02, depth=0.004)
    feet((-0.12, 0.12), (-0.08, 0.08))
    return 2048


def mfak():
    """MFAK: a khaki UNSC medical case in Halo Infinite's style - black frame, EGB on the front."""
    W, D, H = 0.46, 0.25, 0.25
    c = unsc_case(W, D, H, "unsc_khaki")
    decal("egb_white", (0, c["front"], c["mid"]), F, UP, 0.07, depth=0.004)
    decal("med_sticker", (0.1, c["front"], c["zb"] + 0.045), F, UP, 0.07, depth=0.004)
    decal("warning_red", (-0.1, c["front"], c["zb"] + 0.045), F, UP, 0.07, depth=0.004)
    decal("mfak_white", (0.0, -0.01, c["top"]), UP, B, 0.2, depth=0.006)
    decal("sticker_orange", (-0.16, 0.06, c["top"]), UP, B, 0.06, depth=0.006)
    decal("wordmark_white", (0.15, -D / 2 - 0.008, c["zl"] + 0.026), F, UP, 0.07, depth=0.006)
    for sx in (-1, 1):
        decal("lift_white", (sx * W / 2, 0, c["zb"] + (c["zl"] - c["zb"]) * 0.9), (sx, 0, 0), UP, 0.06,
              depth=0.006)
    decal("side_up_white", (-W / 2, 0, c["zb"] + 0.03), L_, UP, 0.07, depth=0.006)
    decal("code_grey", (W / 2, 0, c["zb"] + 0.03), R, UP, 0.06, depth=0.006)
    decal("serial_white", (-0.1, c["back"], c["mid"]), B, UP, 0.09, depth=0.004)
    decal("qa_red", (0.12, c["back"], c["mid"]), B, UP, 0.03, depth=0.004)
    return 4096


def mfakplus():
    """MFAK+: a taller olive UNSC medical case, the same family as the MFAK."""
    W, D, H = 0.44, 0.24, 0.36
    c = unsc_case(W, D, H, "unsc_olive", lid_h=0.05)
    decal("egb_white", (0, c["front"], c["mid"] + 0.02), F, UP, 0.1, depth=0.004)
    decal("med_sticker", (0.1, c["front"], c["zb"] + 0.055), F, UP, 0.075, depth=0.004)
    decal("warning_red", (-0.1, c["front"], c["zb"] + 0.055), F, UP, 0.07, depth=0.004)
    decal("mfakplus_white", (0.0, -0.01, c["top"]), UP, B, 0.22, depth=0.006)
    decal("sticker_orange", (-0.15, 0.06, c["top"]), UP, B, 0.06, depth=0.006)
    decal("wordmark_white", (0.14, -D / 2 - 0.008, c["zl"] + 0.027), F, UP, 0.07, depth=0.006)
    for sx in (-1, 1):
        decal("lift_white", (sx * W / 2, 0, c["zb"] + (c["zl"] - c["zb"]) * 0.82), (sx, 0, 0), UP, 0.06,
              depth=0.006)
    decal("side_up_white", (-W / 2, 0, c["zb"] + 0.04), L_, UP, 0.07, depth=0.006)
    decal("code_grey", (W / 2, 0, c["zb"] + 0.04), R, UP, 0.06, depth=0.006)
    decal("serial_white", (-0.1, c["back"], c["mid"]), B, UP, 0.09, depth=0.004)
    decal("qa_red", (0.12, c["back"], c["mid"]), B, UP, 0.03, depth=0.004)
    return 4096


def narcbox():
    """Narc case: a moulded green hard case like the launcher ammo cases - corner bumpers, grey
    latches, padlock hasp, yellow stencil."""
    W, D = 0.30, 0.17
    r = 0.022
    prism(rrect(W, D, r, 4), 0.044, "poly_green", bevel=0.005, segs=2)
    prism(rrect(W + 0.006, D + 0.006, r + 0.003, 4), 0.006, "poly_green", (0, 0, 0.041), bevel=0.0015, segs=1)
    prism(rrect(W, D, r, 4), 0.044, "poly_green", (0, 0, 0.046), bevel=0.01, segs=3)
    top = 0.09
    # moulded grip grooves along the long sides of the base
    for sy in (-1, 1):
        for k in range(3):
            box((0.16, 0.002, 0.003), (0, sy * (D / 2 + 0.0004), 0.01 + k * 0.007), "poly_green", bevel=0.0006,
                segs=1)
    # corner bumpers, top and bottom
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = (sx * (W / 2 - r), sy * (D / 2 - r))
            cyl(0.026, 0.05, (c[0], c[1], 0.068), "poly_green", n=16, bevel=0.012, segs=3)
            cyl(0.026, 0.044, (c[0], c[1], 0.022), "poly_green", n=16, bevel=0.01, segs=2)
    # stencil field
    prism(rrect(0.232, 0.116, 0.01, 3), 0.002, "poly_green", (0, 0, top - 0.0005), bevel=0.0008, segs=1)
    decal("narc_yellow", (0, 0, top + 0.0015), UP, B, 0.222, depth=0.003)
    # latches over the seam on the front
    fy = -D / 2
    for sx in (-0.085, 0.085):
        box((0.05, 0.014, 0.05), (sx, fy - 0.004, 0.046), "latch_grey", cut=0.006, axis="y", bevel=0.003, segs=2)
        for dz in (-0.009, 0.0, 0.009):
            box((0.034, 0.004, 0.0035), (sx, fy - 0.012, 0.046 + dz), "latch_grey", bevel=0.0008, segs=1)
        box((0.056, 0.01, 0.012), (sx, fy - 0.002, 0.075), "latch_grey", bevel=0.003, segs=2)
        cyl(0.003, 0.058, (sx, fy - 0.008, 0.075), "steel", axis="x", n=10)
    # padlock hasp in the middle
    Fh = frame((0, fy - 0.0025, 0.046), F, UP)
    lbox(Fh, (0.026, 0.03, 0.003), (0, 0, 0), "steel", cut=0.003, bevel=0.0006)
    for sx in (-1, 1):
        lbox(Fh, (0.004, 0.012, 0.012), (sx * 0.007, -0.004, 0.003), "steel", bevel=0.0008)
    lcyl(Fh, 0.0022, 0.02, (0, -0.004, 0.013), "steel", n=10, axis="x")
    screw((-0.009, fy - 0.0055, 0.056), F, 0.002, "steel")
    screw((0.009, fy - 0.0055, 0.056), F, 0.002, "steel")
    # hinges on the back
    for sx in (-0.08, 0.08):
        hinge((sx - 0.03, D / 2 + 0.002, 0.046), (sx + 0.03, D / 2 + 0.002, 0.046), r=0.006, knuckles=3,
              look="poly_green")
    # pressure relief valve on the left
    Fv = frame((-W / 2, 0, 0.022), L_, UP)
    lcyl(Fv, 0.011, 0.003, look="dark_poly", n=24, bevel=0.0008)
    lcyl(Fv, 0.007, 0.006, (0, 0, 0.002), "dark_poly", n=20, bevel=0.0015, segs=2)
    decal("hazard", (W / 2, 0, 0.022), R, UP, 0.07, depth=0.004)
    feet((-0.1, 0.1), (-0.05, 0.05), size=0.018)
    return 2048


# ===================================================================================================
# Enhanced Utility Pouches
# ===================================================================================================
def utility_pouch():
    """Utility pouch: a webbing pouch with a moulded lid. Two straps run over the lid and down the
    flap to side-release buckles on the body; the label sits on the flap between them."""
    W, D, H = 0.15, 0.06, 0.118
    box((W, D, H - 0.01), (0, 0, (H - 0.01) / 2), "webbing", bevel=0.01, segs=3)
    # binding tape round the opening
    box((W + 0.003, D + 0.003, 0.006), (0, 0, H - 0.012), "webbing", bevel=0.002, segs=1)
    # moulded lid and its front flap
    box((W + 0.004, D + 0.006, 0.012), (0, 0, H - 0.002), "olive_dark", cut=0.008, bevel=0.003, segs=2)
    flap_y = -D / 2 - 0.004
    box((W - 0.016, 0.006, 0.05), (0, flap_y, H - 0.03), "olive_dark", cut=0.012, cuts=(1, 1, 0, 0),
        axis="y", bevel=0.002, segs=2)
    decal("util_label", (0, flap_y - 0.003, H - 0.026), F, UP, 0.062, depth=0.003)
    for sx in (-1, 1):
        x = sx * 0.047
        # strap: over the lid, down the flap, ending in the male half of the buckle below the flap
        box((0.02, 0.064, 0.0025), (x, -0.004, H + 0.0055), "webbing", bevel=0.0008, segs=1)
        box((0.02, 0.003, 0.058), (x, flap_y - 0.0045, H - 0.026), "webbing", bevel=0.0008, segs=1)
        Fb = frame((x, -D / 2 - 0.002, H - 0.066), F, UP)
        lbox(Fb, (0.024, 0.016, 0.006), (0, 0.006, 0.002), "dark_poly", cut=0.004, cuts=(0, 0, 1, 1),
             bevel=0.0012)
        for k in (-1, 1):
            lbox(Fb, (0.004, 0.01, 0.002), (k * 0.007, 0.006, 0.008), "dark_poly", bevel=0.0004)
        # female half on a short strap sewn to the body
        lbox(Fb, (0.026, 0.016, 0.006), (0, -0.01, 0.0), "dark_poly", cut=0.004, cuts=(1, 1, 0, 0), bevel=0.0012)
        box((0.02, 0.003, 0.03), (x, -D / 2 - 0.0005, H - 0.098), "webbing", bevel=0.0008, segs=1)
    # side compression straps
    for sx in (-1, 1):
        box((0.004, D * 0.8, 0.014), (sx * (W / 2 + 0.002), 0, 0.05), "webbing", bevel=0.001, segs=1)
    decal("marines_yellow", (W / 2 + 0.004, 0, 0.082), R, UP, 0.03, depth=0.006)
    decal("qa_red", (-W / 2 - 0.004, 0.0, 0.085), L_, UP, 0.02, depth=0.006)
    molle_back(W, D, H - 0.01, D / 2)
    return 2048


def ammo_pouch():
    """Double magazine pouch: two moulded cells side by side, each closed by its own lid with a
    tongue, snap and pull tab - the magazines are inside, as they would be."""
    W, D, H = 0.1, 0.056, 0.14
    for sx in (-1, 1):
        x = sx * 0.025
        box((0.048, D, H - 0.012), (x, 0, (H - 0.012) / 2), "olive", cut=0.008, cuts=(0.6, 0.6, 0, 0), axis="y",
            bevel=0.004, segs=3)
        # rib down the outer side of each cell
        box((0.004, D * 0.7, 0.07), (sx * (W / 2 + 0.0005), 0, 0.055), "olive_dark", bevel=0.001, segs=1)
        # lid and its tongue down the front
        box((0.05, D + 0.006, 0.012), (x, 0, H - 0.006), "olive_dark", cut=0.004, bevel=0.003, segs=2)
        box((0.032, 0.005, 0.034), (x, -D / 2 - 0.003, H - 0.024), "olive_dark", cut=0.008, cuts=(1, 1, 0, 0),
            axis="y", bevel=0.0015, segs=2)
        Fs = frame((x, -D / 2 - 0.0055, H - 0.03), F, UP)
        lcyl(Fs, 0.0045, 0.002, look="steel", n=16, bevel=0.0006)
        lcyl(Fs, 0.0025, 0.003, look="steel", n=12, bevel=0.0008)
        # pull tab hanging from the tongue
        box((0.014, 0.003, 0.018), (x, -D / 2 - 0.0045, H - 0.047), "webbing", cut=0.004, cuts=(1, 1, 0, 0),
            axis="y", bevel=0.0006, segs=1)
        decal("ammo_cell", (x, -D / 2, 0.055), F, UP, 0.036, depth=0.004)
    decal("marines_yellow", (W / 2 + 0.0025, 0, 0.105), R, UP, 0.026, depth=0.006)
    decal("qa_red", (-W / 2, 0, 0.105), L_, UP, 0.018, depth=0.006)
    # drain grommets in the floor
    for sx in (-1, 1):
        lcyl(frame((sx * 0.025, 0, 0.0005), DOWN, B), 0.004, 0.0015, look="steel", n=14, bevel=0.0004)
    molle_back(W, D, H, D / 2)
    return 2048


def ammo_bag():
    """Ammunition case: an olive UNSC case with a folding top handle, Marine Corps insignia and the
    ammunition stencil."""
    W, D, H = 0.36, 0.18, 0.2
    c = unsc_case(W, D, H, "unsc_olive", lid_h=0.042, cap=0.03)
    carry_handle(0, 0, c["top"], 0.13, look="rubber")
    decal("marines_white", (-0.07, c["front"], c["mid"] + 0.006), F, UP, 0.06, depth=0.004)
    decal("ammo_crate_label", (0.05, c["front"], c["mid"] + 0.006), F, UP, 0.14, depth=0.004)
    decal("wordmark_white", (0.12, -D / 2 - 0.008, c["zl"] + 0.022), F, UP, 0.06, depth=0.006)
    decal("sticker_orange", (-0.12, 0.05, c["top"]), UP, B, 0.05, depth=0.006)
    decal("ammo_crate_label", (0, c["back"], c["mid"]), B, UP, 0.18, depth=0.004)
    decal("code_grey", (W / 2, 0, c["zb"] + 0.028), R, UP, 0.05, depth=0.006)
    decal("side_up_white", (-W / 2, 0, c["zb"] + 0.028), L_, UP, 0.06, depth=0.006)
    return 4096


def engineer_bag():
    """Engineer's tool case: a grey UNSC case with hazard stripes on the lid and the engineering
    stencil."""
    W, D, H = 0.42, 0.21, 0.21
    c = unsc_case(W, D, H, "unsc_grey", lid_h=0.046)
    carry_handle(0, 0, c["top"], 0.15, look="rubber")
    decal("eng_label", (0, c["front"], c["mid"] + 0.004), F, UP, 0.19, depth=0.004)
    decal("hazard", (0, -D / 2 - 0.008, c["zl"] + 0.024), F, UP, 0.11, depth=0.006)
    decal("wordmark_white", (0.14, -D / 2 - 0.008, c["zl"] + 0.024), F, UP, 0.06, depth=0.006)
    decal("egb_white", (-0.11, c["front"], c["zb"] + 0.042), F, UP, 0.026, depth=0.004)
    decal("sticker_orange", (-0.14, 0.055, c["top"]), UP, B, 0.06, depth=0.006)
    plate((0.0, c["back"], c["mid"]), B, UP, 0.08, 0.036, "black_metal", "serial_white")
    for sx in (-1, 1):
        decal("lift_white", (sx * W / 2, 0, c["zb"] + (c["zl"] - c["zb"]) * 0.9), (sx, 0, 0), UP, 0.055,
              depth=0.006)
    decal("code_grey", (W / 2, 0, c["zb"] + 0.03), R, UP, 0.055, depth=0.006)
    return 4096


def cbrn_bag():
    """CBRN container: a white UNSC case with a yellow band, a seal pressure gauge and a purge valve."""
    W, D, H = 0.4, 0.23, 0.24
    c = unsc_case(W, D, H, "hazmat_white", lid_h=0.05)
    inner = c["inner"]
    # yellow band round the body
    box((inner * 0.98, D + 0.012, 0.018), (0, 0, c["zb"] + 0.022), "hazard_yellow", bevel=0.002, segs=1)
    carry_handle(0, 0, c["top"], 0.15, look="rubber")
    fy = c["front"]
    # seal gauge
    gz = c["mid"] + 0.01
    Fg = frame((0.1, fy, gz), F, UP)
    lcyl(Fg, 0.03, 0.006, look="black_metal", n=36, bevel=0.0015, segs=2)
    lcyl(Fg, 0.024, 0.0075, look="dial", n=36, bevel=0.0004)
    decal("gauge_face", (0.1, fy - 0.0075, gz), F, UP, 0.047, depth=0.002)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        screw((0.1 + 0.027 * math.cos(a), fy - 0.006, gz + 0.027 * math.sin(a)), F, 0.0016, "steel")
    decal("cbrn_label", (-0.05, fy, gz), F, UP, 0.17, depth=0.004)
    decal("wordmark_white", (0.13, -D / 2 - 0.008, c["zl"] + 0.026), F, UP, 0.065, depth=0.006)
    # purge valve with a red knob on the right end cap, above the grip
    Fv = frame((W / 2 + 0.001, 0.0, c["zl"] - 0.022), R, UP)
    lcyl(Fv, 0.013, 0.005, look="steel", n=6, bevel=0.0008)
    lcyl(Fv, 0.006, 0.01, (0, 0, 0.004), "steel", n=16)
    lcyl(Fv, 0.01, 0.008, (0, 0, 0.012), "red", n=12, bevel=0.002, segs=2)
    decal("cbrn_label", (0.0, c["back"], c["mid"]), B, UP, 0.12, depth=0.004)
    decal("sticker_orange", (-0.13, 0.06, c["top"]), UP, B, 0.06, depth=0.006)
    decal("side_up_white", (-W / 2, 0, c["zb"] + 0.034), L_, UP, 0.06, depth=0.006)
    return 4096


BUILDERS = {"ifak": ifak, "afak": afak, "mfak": mfak, "mfakplus": mfakplus, "narcbox": narcbox,
            "utility_pouch": utility_pouch, "ammo_pouch": ammo_pouch, "ammo_bag": ammo_bag,
            "engineer_bag": engineer_bag, "cbrn_bag": cbrn_bag}

ADDON = {k: "kits" for k in ("ifak", "afak", "mfak", "mfakplus", "narcbox")}
ADDON.update({k: "eup" for k in ("utility_pouch", "ammo_pouch", "ammo_bag", "engineer_bag", "cbrn_bag")})
