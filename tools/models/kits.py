"""The five kit models, built from the parts in unsc_lib. Blender space: front at -y, z up, metres.

Each builder returns the texture size of its kit. Sizes follow EFAK's own kits closely enough that
the inventory feels the same: a pouch-sized IFAK, a flat AFAK, two cases for the medic bags and a
small hard case for the narcotics.
"""
import math

from unsc_lib import box, cyl, decal, prism, rect, rrect

F = (0, -1, 0)   # front normal
B = (0, 1, 0)
UP = (0, 0, 1)
R = (1, 0, 0)


def _on_face(x0, z0, x1, z1):
    """Centre and rotation of a plate lying on the chamfer from (x0, z0) to (x1, z1) in the x/z plane."""
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    nx, nz = (z1 - z0), -(x1 - x0)
    ln = math.hypot(nx, nz)
    nx, nz = nx / ln, nz / ln
    if nz < 0:
        nx, nz = -nx, -nz
    return (cx, cz), math.degrees(math.atan2(nx, nz)), math.hypot(x1 - x0, z1 - z0)


# ---------------------------------------------------------------------------------------------------
def ifak():
    """M7 IFAK: an angular polymer case for one casualty, belt or MOLLE mounted, red pull tab."""
    W, D, H = 0.17, 0.06, 0.13
    cut = 0.022
    box((W, D, H), (0, 0, H / 2), "olive", cut=cut, cuts=(0.5, 0.5, 1, 1), axis="y", bevel=0.004, segs=3)
    # front lid, a little smaller, so the seam shows all round
    box((0.152, 0.008, 0.114), (0, -D / 2 - 0.0035, 0.066), "olive_dark", cut=0.018, cuts=(0.5, 0.5, 1, 1),
        axis="y", bevel=0.0025, segs=2)
    # raised label field on the lid
    box((0.128, 0.003, 0.066), (0, -D / 2 - 0.009, 0.07), "olive_dark", cut=0.006, axis="y", bevel=0.001, segs=1)
    lid_front = -D / 2 - 0.0105
    decal("ifak_label", (0, lid_front, 0.07), F, UP, 0.122, depth=0.004)
    # status lens and its bezel, upper right of the lid
    cyl(0.0065, 0.003, (0.056, -D / 2 - 0.0085, 0.114), "black_metal", axis="y", n=20)
    cyl(0.0042, 0.003, (0.056, -D / 2 - 0.0095, 0.114), "green_lens", axis="y", n=20)
    # pull tab on top, and its loop
    box((0.05, 0.018, 0.012), (0, -0.012, H + 0.004), "red", cut=0.004, axis="y", bevel=0.002, segs=2)
    box((0.03, 0.006, 0.02), (0, -0.024, H + 0.012), "red", cut=0.006, cuts=(0, 0, 1, 1), axis="y",
        bevel=0.0015, segs=2)
    # grip ribs on both sides
    for sx in (-1, 1):
        for k in range(3):
            box((0.006, 0.044, 0.007), (sx * (W / 2 + 0.001), 0, 0.03 + k * 0.022), "olive_dark", bevel=0.0015,
                segs=2)
    decal("cross_tag", (W / 2 + 0.001, 0, 0.104), R, UP, 0.026, depth=0.004)
    # guards on the cut top corners
    for sx in (-1, 1):
        (cx, cz), ang, ln = _on_face(sx * (W / 2 - cut), H, sx * W / 2, H - cut)
        prism(rect(ln * 0.8, D + 0.004), 0.004, "dark_poly", (cx, 0, cz), (0, ang, 0), bevel=0.0012, segs=1)
    # back: MOLLE plate, two straps with snaps
    box((0.13, 0.01, 0.116), (0, D / 2 + 0.005, 0.064), "dark_poly", cut=0.012, axis="y", bevel=0.002, segs=2)
    for sx in (-0.036, 0.036):
        box((0.026, 0.005, 0.122), (sx, D / 2 + 0.012, 0.064), "dark_poly", bevel=0.0012, segs=1)
        box((0.03, 0.007, 0.014), (sx, D / 2 + 0.016, 0.012), "black_metal", cut=0.003, axis="y", bevel=0.001,
            segs=1)
        cyl(0.0045, 0.003, (sx, D / 2 + 0.0205, 0.012), "steel", axis="y", n=16)
    return 2048


# ---------------------------------------------------------------------------------------------------
def afak():
    """M9 AFAK: the flat field medkit - octagonal hard case, light lid with the medical mark, red
    reflectors, rubber grips front and back."""
    W, D = 0.36, 0.27
    C = 0.06
    base_h, lid_z, lid_h = 0.034, 0.039, 0.040
    top = lid_z + lid_h
    prism(rect(W, D, C), base_h, "shell_dark", bevel=0.003, segs=2)
    prism(rect(W - 0.008, D - 0.008, C - 0.002), 0.008, "black_metal", (0, 0, base_h - 0.002), bevel=0.001,
          segs=1)
    prism(rect(W, D, C), lid_h, "shell_grey", (0, 0, lid_z), bevel=0.003, segs=2, taper=0.012)
    # centre plate with the mark
    box((0.135, 0.135, 0.008), (0, 0, top + 0.003), "shell_white", cut=0.01, bevel=0.002, segs=2, taper=0.003)
    decal("med_h", (0, 0, top + 0.007), UP, B, 0.124, depth=0.003)
    # wings left and right of it
    wing = [(0.078, -0.072), (0.138, -0.046), (0.138, 0.046), (0.078, 0.072)]
    prism(wing, 0.004, "shell_white", (0, 0, top - 0.001), bevel=0.0012, segs=1)
    prism([(-x, y) for x, y in reversed(wing)], 0.004, "shell_white", (0, 0, top - 0.001), bevel=0.0012, segs=1)
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
    # rubber grips front and back, ribbed
    for sy in (-1, 1):
        y = sy * (D / 2 + 0.004)
        box((0.2, 0.026, 0.05), (0, y, 0.04), "rubber", bevel=0.006, segs=3)
        for k in range(6):
            box((0.186, 0.004, 0.003), (0, y + sy * 0.0135, 0.0235 + k * 0.0066), "rubber", bevel=0.0008, segs=1)
    # latch on the front grip
    box((0.034, 0.01, 0.032), (0, -D / 2 - 0.0215, 0.04), "steel", cut=0.005, axis="y", bevel=0.0015, segs=2)
    box((0.018, 0.004, 0.006), (0, -D / 2 - 0.0275, 0.048), "black_metal", bevel=0.0008, segs=1)
    # labels
    decal("afak_label", (0, -0.095, top), UP, B, 0.12, depth=0.003)
    decal("serial_white", (0, 0.098, top), UP, (0, -1, 0), 0.08, depth=0.003)
    return 2048


# ---------------------------------------------------------------------------------------------------
def mfak():
    """MFAK: a UNSC supply crate - tan olive body on a black skid, corner posts, padded lid."""
    W, D = 0.44, 0.24
    z0, z1 = 0.03, 0.21
    box((W + 0.012, D + 0.012, z0), (0, 0, z0 / 2), "dark_poly", bevel=0.003, segs=2)
    box((W, D, z1 - z0), (0, 0, (z0 + z1) / 2), "olive_tan", bevel=0.003, segs=2)
    # corner posts, their outer edge cut
    cuts = {(1, -1): (0, 1, 0, 0), (-1, -1): (1, 0, 0, 0), (1, 1): (0, 0, 1, 0), (-1, 1): (0, 0, 0, 1)}
    for (sx, sy), c in cuts.items():
        prism(rect(0.04, 0.04, 0.014, c), 0.204, "olive_tan_dark", (sx * (W / 2 - 0.01), sy * (D / 2 - 0.01), 0.008),
              bevel=0.0025, segs=2)
    # front: framed panel with angled lower corners, top rib, latch
    fy = -D / 2
    box((0.34, 0.006, 0.15), (0, fy - 0.003, 0.125), "olive_tan", cut=0.03, cuts=(1, 1, 0, 0), axis="y",
        bevel=0.002, segs=2)
    box((0.30, 0.004, 0.118), (0, fy - 0.006 - 0.002, 0.118), "olive_tan", cut=0.026, cuts=(1, 1, 0, 0), axis="y",
        bevel=0.0015, segs=2)
    panel = fy - 0.010
    box((0.36, 0.012, 0.014), (0, fy - 0.004, 0.199), "olive_tan_dark", bevel=0.002, segs=2)
    box((0.06, 0.016, 0.028), (0, fy - 0.008, 0.204), "dark_poly", cut=0.009, cuts=(1, 1, 0, 0), axis="y",
        bevel=0.002, segs=2)
    box((0.03, 0.004, 0.008), (0, fy - 0.0175, 0.2), "black_metal", bevel=0.0008, segs=1)
    decal("unsc_white", (0.07, panel, 0.096), F, UP, 0.16, depth=0.004)
    decal("warning_red", (-0.1, panel, 0.088), F, UP, 0.075, depth=0.004)
    decal("data_panel", (0.118, panel, 0.155), F, UP, 0.05, depth=0.004)
    # red ring marker on the front left post
    cyl(0.009, 0.002, (-(W / 2 - 0.01), fy - 0.011, 0.17), "red", axis="y", n=24)
    cyl(0.0055, 0.0024, (-(W / 2 - 0.01), fy - 0.0112, 0.17), "olive_tan_dark", axis="y", n=20)
    # sides: panels and handles
    for sx in (-1, 1):
        box((0.008, 0.16, 0.13), (sx * (W / 2 + 0.002), 0, 0.12), "olive_tan", cut=0.02, axis="x", bevel=0.002,
            segs=2)
        for sy in (-1, 1):
            box((0.022, 0.016, 0.03), (sx * (W / 2 + 0.014), sy * 0.045, 0.16), "black_metal", bevel=0.002, segs=2)
        box((0.012, 0.106, 0.012), (sx * (W / 2 + 0.026), 0, 0.16), "black_metal", bevel=0.003, segs=2)
    # back
    decal("serial_white", (0, D / 2, 0.12), B, UP, 0.1, depth=0.004)
    # lid: padded, overhanging, and the seam under it
    box((W + 0.004, D + 0.004, 0.004), (0, 0, z1 + 0.001), "black_metal", bevel=0.001, segs=1)
    box((W + 0.034, D + 0.034, 0.04), (0, 0, z1 + 0.022), "olive_tan", bevel=0.009, segs=3, taper=0.004)
    lid_top = z1 + 0.042
    decal("mfak_white", (0.035, 0.0, lid_top), UP, B, 0.22, depth=0.004)
    decal("emblem_yellow", (-0.17, -0.085, lid_top), UP, B, 0.06, depth=0.004)
    return 2048


# ---------------------------------------------------------------------------------------------------
def mfakplus():
    """MFAK+: a tall UNSC locker tin - green, framed front, grey feet, black fold handles."""
    W, D, H = 0.42, 0.19, 0.33
    box((W, D, H), (0, 0, H / 2), "olive_green", bevel=0.004, segs=3)
    fy = -D / 2
    # feet on the four bottom corners, front and back
    for sx in (-1, 1):
        for sy in (-1, 1):
            box((0.05, 0.006, 0.04), (sx * (W / 2 - 0.03), sy * (D / 2 + 0.002), 0.022), "shell_dark",
                cut=0.012, cuts=(0, 0, 1, 1) if sx > 0 else (0, 0, 1, 1), axis="y", bevel=0.0015, segs=1)
    # front: corner strips, framed panel, top bracket with a handle bump
    for sx in (-1, 1):
        box((0.026, 0.006, 0.27), (sx * (W / 2 - 0.022), fy - 0.002, 0.18), "olive_green", cut=0.008,
            axis="y", bevel=0.002, segs=2)
    box((0.30, 0.005, 0.25), (0, fy - 0.0025, 0.16), "olive_green", cut=0.04, cuts=(1, 1, 0, 0), axis="y",
        bevel=0.002, segs=2)
    panel = fy - 0.005
    box((0.18, 0.006, 0.03), (0, fy - 0.006, 0.272), "olive_green", cut=0.012, cuts=(1, 1, 0, 0), axis="y",
        bevel=0.0015, segs=2)
    box((0.06, 0.008, 0.014), (0, fy - 0.01, 0.282), "olive_green", cut=0.004, axis="y", bevel=0.0015, segs=2)
    decal("unsc_white", (0.0, panel, 0.12), F, UP, 0.22, depth=0.004)
    decal("warning_red", (-0.085, panel, 0.215), F, UP, 0.07, depth=0.004)
    decal("data_panel", (0.09, panel, 0.215), F, UP, 0.055, depth=0.004)
    cyl(0.008, 0.002, (-(W / 2 - 0.022), fy - 0.006, 0.29), "red", axis="y", n=24)
    cyl(0.005, 0.0024, (-(W / 2 - 0.022), fy - 0.0062, 0.29), "olive_green", axis="y", n=20)
    # sides: panels and fold handles
    for sx in (-1, 1):
        box((0.006, 0.14, 0.24), (sx * (W / 2 + 0.002), 0, 0.165), "olive_green", cut=0.02, axis="x", bevel=0.002,
            segs=2)
        box((0.008, 0.044, 0.04), (sx * (W / 2 + 0.008), 0, 0.29), "black_metal", bevel=0.002, segs=2)
        for sy in (-1, 1):
            box((0.026, 0.008, 0.008), (sx * (W / 2 + 0.022), sy * 0.022, 0.29), "black_metal", bevel=0.002,
                segs=1)
        box((0.008, 0.06, 0.012), (sx * (W / 2 + 0.034), 0, 0.29), "black_metal", bevel=0.003, segs=2)
    # back: hinge and serial
    cyl(0.006, W - 0.06, (0, D / 2 + 0.002, H + 0.002), "shell_dark", axis="x", n=16)
    decal("serial_white", (0, D / 2, 0.2), B, UP, 0.1, depth=0.004)
    # lid
    box((W + 0.008, D + 0.008, 0.026), (0, 0, H + 0.013), "olive_green", bevel=0.006, segs=3)
    lid_top = H + 0.026
    decal("mfakplus_white", (0.0, 0.0, lid_top), UP, B, 0.25, depth=0.004)
    decal("emblem_yellow", (-0.16, -0.055, lid_top), UP, B, 0.05, depth=0.004)
    return 2048


# ---------------------------------------------------------------------------------------------------
def narcbox():
    """Narc case: a moulded green hard case like the launcher ammo cases - corner bumpers, grey
    latches, yellow stencil."""
    W, D = 0.30, 0.17
    r = 0.022
    prism(rrect(W, D, r, 4), 0.044, "poly_green", bevel=0.005, segs=2)
    prism(rrect(W + 0.006, D + 0.006, r + 0.003, 4), 0.006, "poly_green", (0, 0, 0.041), bevel=0.0015, segs=1)
    prism(rrect(W, D, r, 4), 0.044, "poly_green", (0, 0, 0.046), bevel=0.01, segs=3)
    top = 0.09
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
    # hinges on the back
    for sx in (-0.08, 0.08):
        cyl(0.006, 0.06, (sx, D / 2 + 0.002, 0.046), "poly_green", axis="x", n=16)
    decal("hazard", (W / 2, 0, 0.022), R, UP, 0.07, depth=0.004)
    return 2048


BUILDERS = {"ifak": ifak, "afak": afak, "mfak": mfak, "mfakplus": mfakplus, "narcbox": narcbox}
