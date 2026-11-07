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


# ===================================================================================================
# EFAK
# ===================================================================================================
def ifak():
    """M7 IFAK: an angular polymer case for one casualty, belt or MOLLE mounted, red pull tab."""
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
    for sx in (-1, 1):
        screw((sx * 0.066, lf, 0.017), F)
        screw((sx * 0.058, lf, 0.112), F)
    # hinge along the foot of the lid
    hinge((-0.055, lf + 0.001, 0.008), (0.055, lf + 0.001, 0.008), r=0.0032, knuckles=5)
    # status lens and its bezel, top middle of the lid
    cyl(0.0065, 0.003, (0, lf - 0.0015, 0.112), "black_metal", axis="y", n=20)
    cyl(0.0042, 0.003, (0, lf - 0.0025, 0.112), "green_lens", axis="y", n=20)
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
    molle_back(W, D, H, D / 2)
    feet((-0.06, 0.06), (0,), size=0.018)
    return 2048


def afak():
    """M9 AFAK: the flat field medkit - octagonal hard case, light lid with the medical mark, red
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
    """MFAK: a UNSC supply crate - tan olive body on a black skid, riveted corner posts, padded lid,
    toggle latches."""
    W, D = 0.44, 0.24
    z0, z1 = 0.03, 0.21
    box((W + 0.012, D + 0.012, z0), (0, 0, z0 / 2), "dark_poly", bevel=0.003, segs=2)
    box((W, D, z1 - z0), (0, 0, (z0 + z1) / 2), "olive_tan", bevel=0.003, segs=2)
    # corner posts, their outer edge cut, riveted
    cuts = {(1, -1): (0, 1, 0, 0), (-1, -1): (1, 0, 0, 0), (1, 1): (0, 0, 1, 0), (-1, 1): (0, 0, 0, 1)}
    for (sx, sy), c in cuts.items():
        px, py = sx * (W / 2 - 0.01), sy * (D / 2 - 0.01)
        prism(rect(0.04, 0.04, 0.014, c), 0.204, "olive_tan_dark", (px, py, 0.008), bevel=0.0025, segs=2)
        rivets((px - sx * 0.006, py + sy * 0.02, 0.05), (px - sx * 0.006, py + sy * 0.02, 0.13), (0, sy, 0), 3)
        rivets((px + sx * 0.02, py - sy * 0.006, 0.05), (px + sx * 0.02, py - sy * 0.006, 0.19), (sx, 0, 0), 4)
    # front: framed panel with angled lower corners, top rib
    fy = -D / 2
    box((0.34, 0.006, 0.15), (0, fy - 0.003, 0.125), "olive_tan", cut=0.03, cuts=(1, 1, 0, 0), axis="y",
        bevel=0.002, segs=2)
    box((0.30, 0.004, 0.118), (0, fy - 0.008, 0.118), "olive_tan", cut=0.026, cuts=(1, 1, 0, 0), axis="y",
        bevel=0.0015, segs=2)
    panel = fy - 0.010
    box((0.36, 0.012, 0.014), (0, fy - 0.004, 0.199), "olive_tan_dark", bevel=0.002, segs=2)
    for sx in (-1, 1):
        toggle_latch((sx * 0.12, fy - 0.010, 0.208), F)
    box((0.06, 0.006, 0.012), (0, fy - 0.0125, 0.199), "dark_poly", cut=0.004, axis="y", bevel=0.0012, segs=1)
    decal("unsc_white", (0.07, panel, 0.096), F, UP, 0.16, depth=0.004)
    decal("warning_red", (-0.1, panel, 0.088), F, UP, 0.075, depth=0.004)
    decal("data_panel", (0.118, panel, 0.155), F, UP, 0.05, depth=0.004)
    # red ring marker on the front left post
    cyl(0.009, 0.002, (-(W / 2 - 0.01), fy - 0.011, 0.17), "red", axis="y", n=24)
    cyl(0.0055, 0.0024, (-(W / 2 - 0.01), fy - 0.0112, 0.17), "olive_tan_dark", axis="y", n=20)
    # sides: panels, handles, a plate and a stencil
    for sx in (-1, 1):
        box((0.008, 0.16, 0.13), (sx * (W / 2 + 0.002), 0, 0.12), "olive_tan", cut=0.02, axis="x", bevel=0.002,
            segs=2)
        side_handle(sx * (W / 2 + 0.003), sx, 0.16)
    plate((W / 2 + 0.006, 0, 0.09), R, UP, 0.07, 0.035, "black_metal", "serial_white")
    decal("side_up_white", (-W / 2 - 0.006, 0, 0.095), L_, UP, 0.11, depth=0.004)
    # back
    decal("lift_white", (0, D / 2, 0.15), B, UP, 0.09, depth=0.004)
    decal("qa_red", (0.15, D / 2, 0.06), B, UP, 0.03, depth=0.004)
    decal("serial_white", (-0.1, D / 2, 0.08), B, UP, 0.09, depth=0.004)
    hinge((-0.17, D / 2 + 0.004, z1 + 0.003), (0.17, D / 2 + 0.004, z1 + 0.003), r=0.005, knuckles=7)
    # lid: padded, a little overhanging, and the seam under it; stacking pads on top
    box((W + 0.004, D + 0.004, 0.004), (0, 0, z1 + 0.001), "rubber", bevel=0.001, segs=1)
    box((W + 0.012, D + 0.012, 0.04), (0, 0, z1 + 0.022), "lid_pad", bevel=0.009, segs=3, taper=0.004)
    lid_top = z1 + 0.042
    decal("mfak_white", (0.035, 0.0, lid_top), UP, B, 0.22, depth=0.004)
    decal("emblem_yellow", (-0.17, -0.085, lid_top), UP, B, 0.06, depth=0.004)
    for sx in (-1, 1):
        for sy in (-1, 1):
            lbox(frame((sx * 0.19, sy * 0.095, lid_top - 0.001), UP, B), (0.03, 0.03, 0.004), (0, 0, 0), "rubber",
                 cut=0.006, bevel=0.001)
    feet((-0.19, 0.19), (-0.1, 0.1), z=0.0, size=0.03)
    return 4096


def mfakplus():
    """MFAK+: a tall UNSC locker tin - green, framed front, grey feet, black fold handles."""
    W, D, H = 0.42, 0.19, 0.33
    box((W, D, H), (0, 0, H / 2), "olive_green", bevel=0.004, segs=3)
    fy = -D / 2
    # feet on the four bottom corners, front and back
    for sx in (-1, 1):
        for sy in (-1, 1):
            box((0.05, 0.006, 0.04), (sx * (W / 2 - 0.03), sy * (D / 2 + 0.002), 0.022), "shell_dark",
                cut=0.012, cuts=(0, 0, 1, 1), axis="y", bevel=0.0015, segs=1)
            screw((sx * (W / 2 - 0.03), sy * (D / 2 + 0.005), 0.018), (0, sy, 0), 0.0025)
    # front: riveted corner strips, framed panel, top bracket with a handle bump, latches
    for sx in (-1, 1):
        box((0.026, 0.006, 0.27), (sx * (W / 2 - 0.022), fy - 0.002, 0.18), "olive_green", cut=0.008,
            axis="y", bevel=0.002, segs=2)
        rivets((sx * (W / 2 - 0.022), fy - 0.005, 0.06), (sx * (W / 2 - 0.022), fy - 0.005, 0.26), F, 6)
    box((0.30, 0.005, 0.25), (0, fy - 0.0025, 0.16), "olive_green", cut=0.04, cuts=(1, 1, 0, 0), axis="y",
        bevel=0.002, segs=2)
    panel = fy - 0.005
    box((0.18, 0.006, 0.03), (0, fy - 0.006, 0.272), "olive_green", cut=0.012, cuts=(1, 1, 0, 0), axis="y",
        bevel=0.0015, segs=2)
    box((0.06, 0.008, 0.014), (0, fy - 0.01, 0.282), "olive_green", cut=0.004, axis="y", bevel=0.0015, segs=2)
    for sx in (-1, 1):
        toggle_latch((sx * 0.125, fy - 0.0005, 0.33), F)
    decal("unsc_white", (0.0, panel, 0.12), F, UP, 0.22, depth=0.004)
    decal("warning_red", (-0.085, panel, 0.215), F, UP, 0.07, depth=0.004)
    decal("data_panel", (0.09, panel, 0.215), F, UP, 0.055, depth=0.004)
    cyl(0.008, 0.002, (-(W / 2 - 0.022), fy - 0.006, 0.29), "red", axis="y", n=24)
    cyl(0.005, 0.0024, (-(W / 2 - 0.022), fy - 0.0062, 0.29), "olive_green", axis="y", n=20)
    # sides: panels, a vent, fold handles
    for sx in (-1, 1):
        box((0.006, 0.14, 0.24), (sx * (W / 2 + 0.002), 0, 0.165), "olive_green", cut=0.02, axis="x", bevel=0.002,
            segs=2)
        box((0.008, 0.044, 0.04), (sx * (W / 2 + 0.008), 0, 0.29), "black_metal", bevel=0.002, segs=2)
        for sy in (-1, 1):
            box((0.026, 0.008, 0.008), (sx * (W / 2 + 0.022), sy * 0.022, 0.29), "black_metal", bevel=0.002,
                segs=1)
            bolt((sx * (W / 2 + 0.012), sy * 0.015, 0.302), (sx, 0, 0), 0.0024)
        box((0.008, 0.06, 0.012), (sx * (W / 2 + 0.034), 0, 0.29), "black_metal", bevel=0.003, segs=2)
    vents((-W / 2 - 0.005, 0, 0.13), L_, UP, 7, 0.09, 0.0095, look="olive_green")
    decal("side_up_white", (W / 2 + 0.005, 0, 0.13), R, UP, 0.1, depth=0.004)
    # back: hinge, plate and stencils
    hinge((-W / 2 + 0.03, D / 2 + 0.003, H + 0.002), (W / 2 - 0.03, D / 2 + 0.003, H + 0.002), r=0.0055, knuckles=9)
    plate((0.1, D / 2, 0.22), B, UP, 0.075, 0.036, "black_metal", "serial_white")
    decal("lift_white", (-0.08, D / 2, 0.22), B, UP, 0.09, depth=0.004)
    decal("qa_red", (0.15, D / 2, 0.07), B, UP, 0.03, depth=0.004)
    # lid with two stacking ribs
    box((W + 0.008, D + 0.008, 0.026), (0, 0, H + 0.013), "olive_green", bevel=0.006, segs=3)
    lid_top = H + 0.026
    for sx in (-1, 1):
        lbox(frame((sx * 0.175, 0, lid_top - 0.0005), UP, B), (0.014, 0.16, 0.004), (0, 0, 0), "olive_green",
             cut=0.004, bevel=0.0012)
    decal("mfakplus_white", (0.0, 0.0, lid_top), UP, B, 0.25, depth=0.004)
    decal("emblem_yellow", (-0.13, -0.065, lid_top), UP, B, 0.05, depth=0.004)
    decal("nostep_yellow", (0.06, 0.07, lid_top), UP, B, 0.1, depth=0.004)
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
    """M12 utility pouch: a webbing pouch with a moulded lid, two straps with buckles, MOLLE back."""
    W, D, H = 0.15, 0.06, 0.118
    box((W, D, H - 0.01), (0, 0, (H - 0.01) / 2), "webbing", bevel=0.01, segs=3)
    # binding tape round the opening
    box((W + 0.003, D + 0.003, 0.006), (0, 0, H - 0.012), "webbing", bevel=0.002, segs=1)
    # moulded lid and its front flap
    box((W + 0.004, D + 0.006, 0.012), (0, 0, H - 0.002), "olive_dark", cut=0.008, bevel=0.003, segs=2)
    box((W - 0.016, 0.006, 0.05), (0, -D / 2 - 0.004, H - 0.03), "olive_dark", cut=0.012, cuts=(1, 1, 0, 0),
        axis="y", bevel=0.002, segs=2)
    decal("util_label", (0, -D / 2 - 0.007, H - 0.028), F, UP, 0.1, depth=0.004)
    for sx in (-1, 1):
        screw((sx * 0.06, -D / 2 - 0.007, H - 0.012), F, 0.0022)
    # straps from the flap down the front, with side-release buckles
    for sx in (-1, 1):
        x = sx * 0.042
        box((0.022, 0.004, 0.064), (x, -D / 2 - 0.001, 0.034), "webbing", bevel=0.001, segs=1)
        Fb = frame((x, -D / 2 - 0.003, 0.046), F, UP)
        lbox(Fb, (0.026, 0.018, 0.006), (0, -0.006, 0), "dark_poly", cut=0.004, cuts=(1, 1, 0, 0), bevel=0.0012)
        lbox(Fb, (0.024, 0.012, 0.007), (0, 0.009, 0), "dark_poly", cut=0.004, cuts=(0, 0, 1, 1), bevel=0.0012)
        for k in (-1, 1):
            lbox(Fb, (0.004, 0.01, 0.002), (k * 0.008, -0.006, 0.006), "dark_poly", bevel=0.0004)
    # side compression straps and grommets
    for sx in (-1, 1):
        box((0.004, D * 0.8, 0.014), (sx * (W / 2 + 0.002), 0, 0.05), "webbing", bevel=0.001, segs=1)
        lcyl(frame((sx * 0.045, 0, 0.0005), DOWN, B), 0.0045, 0.002, look="steel", n=16, bevel=0.0006)
    decal("qa_red", (W / 2 + 0.004, 0.0, 0.085), R, UP, 0.02, depth=0.006)
    molle_back(W, D, H - 0.01, D / 2)
    return 2048


def ammo_pouch():
    """Double magazine pouch: a moulded open-top shell, two magazines with rounds showing, bungee
    retention and pull tabs."""
    W, D, H = 0.095, 0.06, 0.12
    box((W, D, H), (0, 0, H / 2), "olive", cut=0.012, cuts=(0.5, 0.5, 1, 1), axis="y", bevel=0.004, segs=3)
    # rim of the opening
    box((W + 0.004, D + 0.004, 0.008), (0, 0, H - 0.004), "olive_dark", cut=0.006, bevel=0.002, segs=2)
    for sx in (-1, 1):
        x = sx * 0.022
        # magazine body above the shell: slightly curved look with ribs
        box((0.036, 0.024, 0.05), (x, -0.003, H + 0.022), "dark_poly", cut=0.004, axis="y", bevel=0.002, segs=2)
        for k in range(2):
            box((0.03, 0.002, 0.003), (x, -0.003 - 0.0125, H + 0.012 + k * 0.012), "dark_poly", bevel=0.0005,
                segs=1)
        box((0.03, 0.014, 0.004), (x, -0.003, H + 0.048), "black_metal", bevel=0.0008, segs=1)
        # two rounds in the feed lips: brass case, steel tip
        for k, (dx, dz) in enumerate(((-0.0045, 0.0545), (0.0045, 0.0525))):
            cyl(0.0042, 0.016, (x + dx, 0.0, H + dz), "brass", axis="y", n=14, bevel=0.0008)
            cyl(0.0028, 0.007, (x + dx, -0.0115, H + dz), "steel", axis="y", n=12, bevel=0.0012, segs=2)
        # bungee loop over the mag and a pull tab
        box((0.04, 0.004, 0.008), (x, -0.0175, H + 0.03), "webbing", bevel=0.0012, segs=1)
        box((0.014, 0.004, 0.022), (x, -0.0195, H + 0.022), "olive_dark", cut=0.004, cuts=(1, 1, 0, 0), axis="y",
            bevel=0.001, segs=1)
    decal("ammo_label", (0, -D / 2, 0.062), F, UP, 0.078, depth=0.004)
    for sx in (-1, 1):
        screw((sx * 0.04, -D / 2, 0.012), F, 0.002)
        for k in range(3):
            box((0.005, 0.044, 0.006), (sx * (W / 2 + 0.001), 0, 0.03 + k * 0.022), "olive_dark", bevel=0.0012,
                segs=1)
    decal("qa_red", (W / 2 + 0.004, 0, 0.098), R, UP, 0.018, depth=0.006)
    molle_back(W, D, H, D / 2)
    return 2048


def ammo_bag():
    """Ammunition crate: a steel can with ribs, a sealed lid, folding carry handle, toggle latches,
    yellow HE band."""
    W, D, H = 0.34, 0.17, 0.17
    box((W, D, H), (0, 0, H / 2), "olive_green", bevel=0.004, segs=3)
    # reinforcing ribs all round
    for z in (0.03, 0.14):
        for sy in (-1, 1):
            box((W - 0.01, 0.006, 0.012), (0, sy * (D / 2 + 0.002), z), "olive_green", bevel=0.002, segs=2)
        for sx in (-1, 1):
            box((0.006, D - 0.01, 0.012), (sx * (W / 2 + 0.002), 0, z), "olive_green", bevel=0.002, segs=2)
    # gasket and lid
    box((W + 0.004, D + 0.004, 0.004), (0, 0, H + 0.001), "rubber", bevel=0.001, segs=1)
    box((W + 0.008, D + 0.008, 0.03), (0, 0, H + 0.016), "olive_green", bevel=0.005, segs=3)
    lid_top = H + 0.031
    carry_handle(0, 0, lid_top, 0.13)
    for sx in (-1, 1):
        toggle_latch((sx * 0.1, -D / 2 - 0.0005, H + 0.002), F, w=0.03, h=0.046)
        side_handle(sx * W / 2 + sx * 0.003, sx, 0.09)
    hinge((-0.14, D / 2 + 0.004, H + 0.002), (0.14, D / 2 + 0.004, H + 0.002), r=0.005, knuckles=7)
    decal("ammo_crate_label", (0, -D / 2 - 0.0, 0.085), F, UP, 0.24, depth=0.004)
    decal("yellow_band", (0, -D / 2 - 0.004, H + 0.016), F, UP, 0.3, 0.02, depth=0.004)
    decal("yellow_band", (0, D / 2 + 0.004, H + 0.016), B, UP, 0.3, 0.02, depth=0.004)
    decal("ammo_crate_label", (0, D / 2, 0.085), B, UP, 0.24, depth=0.004)
    decal("unsc_white", (0.0, 0.0, lid_top), UP, B, 0.1, depth=0.004)
    plate((0.0, D / 2 + 0.002, 0.03), B, UP, 0.06, 0.008, "black_metal")
    decal("qa_red", (-0.13, -D / 2, 0.03), F, UP, 0.022, depth=0.006)
    feet((-0.14, 0.14), (-0.06, 0.06), size=0.024)
    return 4096


def engineer_bag():
    """Engineer's tool case: an olive polymer case with orange corner bumpers, top handle, side vents,
    hazard stripes on the lid."""
    W, D, H = 0.40, 0.2, 0.16
    box((W, D, H), (0, 0, H / 2), "olive_dark", cut=0.02, bevel=0.005, segs=3)
    box((W + 0.004, D + 0.004, 0.004), (0, 0, H + 0.001), "rubber", cut=0.021, bevel=0.001, segs=1)
    box((W + 0.004, D + 0.004, 0.04), (0, 0, H + 0.022), "olive_dark", cut=0.021, bevel=0.008, segs=3, taper=0.006)
    lid_top = H + 0.042
    # orange bumpers on the cut corners, body and lid
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * (W / 2 - 0.01), sy * (D / 2 - 0.01)
            n = (sx / math.sqrt(2), sy / math.sqrt(2), 0)
            for z, h in ((0.075, 0.13), (H + 0.02, 0.03)):
                Fc = frame((cx + n[0] * 0.0005, cy + n[1] * 0.0005, z), n, UP)
                lbox(Fc, (0.034, h, 0.006), (0, 0, 0), "orange", cut=0.006, bevel=0.0018, segs=2)
                screw((cx + n[0] * 0.0065, cy + n[1] * 0.0065, z + h * 0.32), n, 0.002)
    carry_handle(0, 0, lid_top, 0.16)
    # front: label, latches, hazard stripes on the lid
    fy = -D / 2
    for sx in (-1, 1):
        toggle_latch((sx * 0.12, fy - 0.0005, H + 0.002), F)
    decal("eng_label", (0, fy, 0.08), F, UP, 0.2, depth=0.004)
    decal("hazard", (0, fy - 0.002, H + 0.02), F, UP, 0.12, depth=0.006)
    # sides: vents and a plate
    for sx in (-1, 1):
        vents((sx * W / 2, 0, 0.085), (sx, 0, 0), UP, 7, 0.1, 0.0095, look="dark_poly")
    plate((0.0, D / 2, 0.09), B, UP, 0.08, 0.036, "black_metal", "serial_white")
    decal("lift_white", (0.12, D / 2, 0.1), B, UP, 0.08, depth=0.004)
    decal("qa_red", (-0.13, D / 2, 0.04), B, UP, 0.026, depth=0.004)
    hinge((-0.15, D / 2 + 0.004, H + 0.002), (0.15, D / 2 + 0.004, H + 0.002), r=0.005, knuckles=7)
    decal("emblem_yellow", (0.13, -0.05, lid_top - 0.006), UP, B, 0.05, depth=0.008)
    feet((-0.15, 0.15), (-0.06, 0.06), size=0.026)
    return 4096


def cbrn_bag():
    """CBRN container: a white sealed case with yellow bands, a seal pressure gauge, purge valve,
    rubber gasket and toggle latches."""
    W, D, H = 0.38, 0.22, 0.2
    box((W, D, H), (0, 0, H / 2), "hazmat_white", bevel=0.01, segs=3)
    for z in (0.04, 0.165):
        box((W + 0.004, D + 0.004, 0.02), (0, 0, z), "hazard_yellow", bevel=0.003, segs=2)
    box((W + 0.006, D + 0.006, 0.008), (0, 0, H + 0.002), "rubber", bevel=0.002, segs=1)
    box((W + 0.004, D + 0.004, 0.045), (0, 0, H + 0.0275), "hazmat_white", bevel=0.012, segs=3, taper=0.004)
    lid_top = H + 0.05
    carry_handle(0, 0, lid_top, 0.15)
    fy = -D / 2
    # seal gauge
    Fg = frame((0.12, fy, 0.105), F, UP)
    lcyl(Fg, 0.03, 0.006, look="black_metal", n=36, bevel=0.0015, segs=2)
    lcyl(Fg, 0.024, 0.0075, look="dial", n=36, bevel=0.0004)
    decal("gauge_face", (0.12, fy - 0.0075, 0.105), F, UP, 0.047, depth=0.002)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        screw((0.12 + 0.027 * math.cos(a), fy - 0.006, 0.105 + 0.027 * math.sin(a)), F, 0.0016, "steel")
    decal("cbrn_label", (-0.06, fy, 0.1), F, UP, 0.2, depth=0.004)
    for sx in (-1, 1):
        toggle_latch((sx * 0.12, fy - 0.003, H + 0.004), F)
        side_handle(sx * W / 2 + sx * 0.002, sx, 0.12)
    # purge valve with red knob on the right side
    Fv = frame((W / 2 + 0.001, 0.06, 0.1), R, UP)
    lcyl(Fv, 0.014, 0.006, look="steel", n=6, bevel=0.0008)
    lcyl(Fv, 0.006, 0.012, (0, 0, 0.004), "steel", n=16)
    lcyl(Fv, 0.011, 0.008, (0, 0, 0.014), "red", n=12, bevel=0.002, segs=2)
    # back
    hinge((-0.15, D / 2 + 0.005, H + 0.004), (0.15, D / 2 + 0.005, H + 0.004), r=0.0055, knuckles=7)
    plate((0.0, D / 2, 0.1), B, UP, 0.08, 0.036, "steel", None)
    decal("cbrn_label", (0.0, D / 2, 0.1), B, UP, 0.07, depth=0.006)
    decal("side_up_white", (-W / 2, -0.03, 0.1), L_, UP, 0.1, depth=0.004, looks=["hazmat_white"])
    decal("qa_red", (0.14, D / 2, 0.11), B, UP, 0.026, depth=0.004)
    decal("cbrn_label", (0.0, 0.0, lid_top), UP, B, 0.16, depth=0.004)
    feet((-0.15, 0.15), (-0.07, 0.07), size=0.026)
    return 4096


BUILDERS = {"ifak": ifak, "afak": afak, "mfak": mfak, "mfakplus": mfakplus, "narcbox": narcbox,
            "utility_pouch": utility_pouch, "ammo_pouch": ammo_pouch, "ammo_bag": ammo_bag,
            "engineer_bag": engineer_bag, "cbrn_bag": cbrn_bag}

ADDON = {k: "kits" for k in ("ifak", "afak", "mfak", "mfakplus", "narcbox")}
ADDON.update({k: "eup" for k in ("utility_pouch", "ammo_pouch", "ammo_bag", "engineer_bag", "cbrn_bag")})
