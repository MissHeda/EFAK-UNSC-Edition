"""The kit models, built from the parts in unsc_lib. Blender space: front at -y, z up, metres.

Each builder returns the texture size of its kit. EFAK's five kits go into addons/kits, the five
pouches of Enhanced Utility Pouches into addons/eup (ADDON below).
"""
import math

from unsc_lib import (box, bolt, cluster, clustered, cyl, decal, frame, hinge, inset, lbox, lcyl, lid, lid_axis,
                      plate, prism, rect, rivets, rrect, screw, bail_latch, vents)

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


@clustered
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


@clustered
def carry_handle(cx, cy, z, length, look="rubber"):
    """Folding top handle: two pivot mounts, a steel bar and a rubber grip, lying flat."""
    for sx in (-1, 1):
        lbox(frame((cx + sx * length / 2, cy, z), UP, B), (0.02, 0.026, 0.012), (0, 0, 0), "black_metal",
             cut=0.004, bevel=0.0015)
        bolt((cx + sx * (length / 2 + 0.011), cy, z + 0.006), (sx, 0, 0), 0.003)
    cyl(0.0042, length + 0.012, (cx, cy, z + 0.008), "steel", axis="x", n=12)
    cyl(0.0085, length * 0.72, (cx, cy, z + 0.008), look, axis="x", n=16, bevel=0.002, segs=2)


@clustered
def side_handle(x, sx, z, look="black_metal"):
    """Fixed side handle: two mounts with bolts and a bar."""
    for sy in (-1, 1):
        box((0.022, 0.016, 0.03), (x + sx * 0.011, sy * 0.045, z), look, bevel=0.002, segs=2)
        bolt((x + sx * 0.022, sy * 0.045, z - 0.007), (sx, 0, 0), 0.0028)
    box((0.012, 0.106, 0.012), (x + sx * 0.024, 0, z + 0.004), look, bevel=0.003, segs=2)


def unsc_case(W, D, H, body, lid_h=0.048, base_h=0.026, cap=0.034, latches=2, handles=True):
    """A UNSC case in the style of Halo Infinite's: a black polymer frame (skid, end caps and lid cap)
    around a painted body, draw latches on the front, hinge at the back, recessed grips in the end
    caps. The body is a tub with a gasket on its rim, the lid a shell lined with egg-crate foam, so an
    open case is a case and not a block. Returns the places the decals of the kit go."""
    zb, zl = base_h, H - lid_h
    inner = W - 2 * cap
    well = min(0.05, (zl - zb) * 0.45)
    # skid, its lower edges cut
    box((W + 0.006, D + 0.012, base_h), (0, 0, base_h / 2), "frame_black", cut=0.008, cuts=(1, 1, 0, 0),
        axis="x", bevel=0.003, segs=2)
    # body between the end caps: solid below the well, a wall round the well above
    box((inner + 0.004, D, zl - well - zb + 0.004), (0, 0, (zb + zl - well) / 2), body, bevel=0.003, segs=2)
    box((inner + 0.004, D, well), (0, 0, zl - well / 2), body, bevel=0.003, segs=2, hollow=0.008)
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
    # gasket on the rim of the tub
    box((inner + 0.002, D - 0.002, 0.004), (0, 0, zl + 0.0005), "rubber", bevel=0.001, segs=1, hollow=0.006)
    # the lid: a top plate on a skirt, lined with egg-crate foam, ribs on top
    top = H + 0.002
    lb = zl + 0.002
    with lid():
        box((W + 0.006, D + 0.016, 0.01), (0, 0, top - 0.005), "frame_black", bevel=0.006, segs=3)
        box((W + 0.006, D + 0.016, lid_h - 0.006), (0, 0, lb + (lid_h - 0.006) / 2), "frame_black", bevel=0.004,
            segs=2, hollow=0.008)
        box((W + 0.006 - 0.02, D + 0.016 - 0.02, 0.006), (0, 0, top - 0.013), "foam_egg", bevel=0.0015, segs=1)
        for sy in (-1, 1):
            lbox(frame((0, sy * (D / 2 - 0.018), top - 0.0005), UP, B), (W * 0.62, 0.008, 0.003), (0, 0, 0),
                 "frame_black", cut=0.003, bevel=0.0012)
    lid_axis((-W / 2, D / 2 + 0.008, zl + 0.004), (W / 2, D / 2 + 0.008, zl + 0.004))
    # draw latches over the seam (bracket on the body, keeper on the lid's skirt), hinge at the back
    xs = [0.0] if latches == 1 else [sx * inner * 0.3 for sx in (-1, 1)]
    for x in xs:
        bail_latch((x, -D / 2, lb), F, UP, w=0.034, below=0.018, body_off=0.0, lid_off=0.008,
                   look="frame_black")
    hinge((-inner * 0.4, D / 2 + 0.008, zl + 0.004), (inner * 0.4, D / 2 + 0.008, zl + 0.004), r=0.005,
          knuckles=7, look="frame_black")
    feet((-W / 2 + 0.05, W / 2 - 0.05), (-D / 2 + 0.04, D / 2 - 0.04), size=0.03)
    grip_top = zb + (zl - zb) * 0.62 + 0.017
    keeper = (inner * 0.3 + 0.0136) if latches == 2 else 0.0136
    return dict(front=-D / 2 - 0.005, back=D / 2 + 0.005, top=top, zb=zb, zl=zl, inner=inner,
                mid=zb + (zl - zb) * 0.46, lid_front=-D / 2 - 0.008, lid_z=H - lid_h / 2 - 0.002,
                lift_z=(grip_top + zl - 0.004) / 2, keeper=keeper, lid_x=W / 2 + 0.003 - 0.008)


def case_foam(W, D, H, lid_h, cap):
    """The foam insert in a UNSC case's tub, a little under the rim. Returns the height of its top."""
    inner = W - 2 * cap
    return foam((inner + 0.004 - 0.017, D - 0.017, 0.004), (0, 0, H - lid_h - 0.010))


# ===================================================================================================
# EFAK
# ===================================================================================================
def ifak():
    """IFAK: an angular polymer case for one casualty, belt or MOLLE mounted, red pull tab. The front
    lid closes over a real compartment."""
    W, D, H = 0.17, 0.06, 0.13
    cut = 0.022
    # solid back half, and the walls of the compartment in front of it
    box((W, 0.042, H), (0, 0.009, H / 2), "olive", cut=cut, cuts=(0.5, 0.5, 1, 1), axis="y", bevel=0.004, segs=3)
    box((W, 0.02, H), (0, -0.02, H / 2), "olive", cut=cut, cuts=(0.5, 0.5, 1, 1), axis="y", bevel=0.003, segs=2,
        hollow=0.006)
    # moulded parting line round the body
    for sy in (-1, 1):
        box((W - 0.03, 0.002, 0.003), (0, sy * (D / 2 + 0.0006), 0.006), "olive", bevel=0.0006, segs=1)
    # front lid: a plate on a short skirt, lined, a little smaller so the seam shows
    lf = -D / 2 - 0.0075
    with lid():
        box((0.152, 0.004, 0.114), (0, -D / 2 - 0.0055, 0.066), "olive_dark", cut=0.018, cuts=(0.5, 0.5, 1, 1),
            axis="y", bevel=0.0018, segs=2)
        box((0.152, 0.004, 0.114), (0, -D / 2 - 0.0016, 0.066), "olive_dark", cut=0.018, cuts=(0.5, 0.5, 1, 1),
            axis="y", bevel=0.0012, segs=1, hollow=0.005)
        box((0.13, 0.002, 0.09), (0, -D / 2 - 0.0025, 0.066), "foam_egg", cut=0.01, axis="y", bevel=0.0006, segs=1)
        # raised label field on the lid
        box((0.128, 0.003, 0.066), (0, -D / 2 - 0.009, 0.07), "olive_dark", cut=0.006, axis="y", bevel=0.001,
            segs=1)
    lid_axis((-0.07, lf + 0.001, 0.008), (0.07, lf + 0.001, 0.008))
    # the label reads from the latch side (the case lies on its back, latch towards the user)
    decal("ifak_label", (0, -D / 2 - 0.0105, 0.07), F, DOWN, 0.1, depth=0.003)
    # hinge along the foot of the lid, so it opens on the side of the red pull tab
    hinge((-0.055, lf + 0.001, 0.008), (0.055, lf + 0.001, 0.008), r=0.0032, knuckles=5)
    # the latch on the top end: a bracket on the body, a lever with the red pull tab and a wire bail
    # reaching over the edge onto a keeper on the lid's face. Opening, the lever swings out and hangs
    # down the end of the case (it lies on its back), clear of the compartment, then the lid goes.
    bail_latch((0, -D / 2, H), UP, F, w=0.03, below=0.016, body_off=0.0,
               keeper=(0.0075, 0.0135, -0.013, 0.007), look="black_metal", tab="red")
    # grip ribs on both sides
    for sx in (-1, 1):
        for k in range(2):
            box((0.006, 0.044, 0.007), (sx * (W / 2 + 0.001), 0, 0.03 + k * 0.022), "olive_dark", bevel=0.0015,
                segs=2)
    # side markings upright as the case lies (on its back: the front F points up)
    decal("cross_tag", (W / 2, 0.01, 0.08), R, F, 0.018, depth=0.003)
    plate((-W / 2, 0, 0.08), L_, F, 0.04, 0.022, "black_metal", "serial_white")
    # guards on the cut top corners
    for sx in (-1, 1):
        (cx, cz), ang, ln = _on_face(sx * (W / 2 - cut), H, sx * W / 2, H - cut)
        prism(rect(ln * 0.8, D + 0.004), 0.004, "dark_poly", (cx, 0, cz), (0, ang, 0), bevel=0.0012, segs=1)
    decal("egb_white", (0.044, 0.01, H), UP, F, 0.012, depth=0.003)
    molle_back(W, D, H, D / 2)
    return 2048


def afak():
    """AFAK: the flat field medkit - octagonal hard case, light lid with the medical mark, red
    reflectors, rubber grips front and back. A tray with a gasket below, a lined shell above."""
    W, D = 0.36, 0.27
    C = 0.06
    base_h, lid_z, lid_h = 0.034, 0.039, 0.040
    top = lid_z + lid_h
    outline = rect(W, D, C)
    prism(outline, 0.012, "shell_dark", bevel=0.003, segs=2)
    prism(outline, base_h - 0.01, "shell_dark", (0, 0, 0.01), bevel=0.003, segs=2, hollow=0.008)
    prism(rect(W - 0.004, D - 0.004, C - 0.001), 0.006, "rubber", (0, 0, base_h - 0.002), bevel=0.001, segs=1,
          hollow=0.006)
    # the lid turns about the hinge's pin
    lid_axis((-0.09, D / 2 + 0.004, lid_z), (0.09, D / 2 + 0.004, lid_z))
    with lid():
        prism(outline, lid_h - 0.014, "shell_grey", (0, 0, lid_z), bevel=0.003, segs=2, hollow=0.008)
        prism(outline, 0.016, "shell_grey", (0, 0, top - 0.016), bevel=0.003, segs=2, taper=0.012)
        prism(inset(outline, 0.009), 0.005, "foam_egg", (0, 0, top - 0.021), bevel=0.0015, segs=1)
        # centre plate with the mark, screwed down
        box((0.135, 0.135, 0.008), (0, 0, top + 0.003), "shell_white", cut=0.01, bevel=0.002, segs=2, taper=0.003)
        for sx in (-1, 1):
            for sy in (-1, 1):
                screw((sx * 0.056, sy * 0.056, top + 0.007), UP, 0.0024)
        # wings left and right of it, each with a vent
        wing = [(0.078, -0.072), (0.138, -0.046), (0.138, 0.046), (0.078, 0.072)]
        prism(wing, 0.004, "shell_white", (0, 0, top - 0.001), bevel=0.0012, segs=1)
        prism([(-x, y) for x, y in reversed(wing)], 0.004, "shell_white", (0, 0, top - 0.001), bevel=0.0012,
              segs=1)
        for sx in (-1, 1):
            vents((sx * 0.108, 0, top + 0.003), UP, (1, 0, 0), 5, 0.058, 0.0075, look="dark_poly")
        # reflectors on top, on the diagonals around the plate
        for sx in (-1, 1):
            for sy in (-1, 1):
                ang = math.degrees(math.atan2(sy * 0.085, sx * 0.1)) + 90
                prism(rect(0.032, 0.016, 0.006, (1, 1, 0, 0)), 0.003, "red_reflector",
                      (sx * 0.1, sy * 0.086, top - 0.001), (0, 0, ang), bevel=0.0008, segs=1)
        # status lens of the sterile field generator, front right, clear of the reflector
        with cluster():
            cyl(0.006, 0.003, (0.072, -0.108, top + 0.0005), "black_metal", n=20)
            cyl(0.0038, 0.003, (0.072, -0.108, top + 0.0015), "green_lens", n=20)
    decal("med_h", (0, 0, top + 0.007), UP, B, 0.1, depth=0.003)
    # reflectors on the cut corners of the base - they stay with the base
    for sx in (-1, 1):
        for sy in (-1, 1):
            nx, ny = sx / math.sqrt(2), sy / math.sqrt(2)
            cx, cy = sx * (W / 2 - C / 2), sy * (D / 2 - C / 2)
            a = math.degrees(math.atan2(nx, -ny))
            prism(rect(0.04, 0.016, 0.004), 0.003, "red_reflector", (cx, cy, base_h / 2), (90, 0, a),
                  bevel=0.0008, segs=1)
    # rubber grips on the base, front and back, ribbed, bolted at the ends
    for sy in (-1, 1):
        y = sy * (D / 2 + 0.004)
        box((0.2, 0.026, 0.028), (0, y, 0.02), "rubber", bevel=0.006, segs=3)
        for k in range(4):
            box((0.186, 0.004, 0.003), (0, y + sy * 0.0135, 0.01 + k * 0.0066), "rubber", bevel=0.0008, segs=1)
        for sx in (-1, 1):
            bolt((sx * 0.092, y + sy * 0.0155, 0.02), (0, sy, 0), 0.003)
    # the latch: bracket on the front grip, the bail reaching back over the seam onto a keeper on the
    # lid; opening, it swings out and hangs down in front of the grip
    bail_latch((0, -D / 2, lid_z), F, UP, w=0.034, below=0.012, body_off=0.0195, lid_off=0.0,
               keeper=(0.004, 0.011, 0.0, 0.016), look="steel")
    # the hinge along the back
    hinge((-0.09, D / 2 + 0.004, lid_z), (0.09, D / 2 + 0.004, lid_z), r=0.0045, knuckles=7, look="shell_dark")
    # labels
    decal("afak_label", (0, -0.095, top), UP, B, 0.12, depth=0.003)
    decal("serial_white", (0, 0.098, top), UP, B, 0.08, depth=0.003)
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
    decal("wordmark_white", (c["lid_x"] - 0.04, c["lid_front"], c["lid_z"]), F, UP, 0.06, depth=0.003)
    for sx in (-1, 1):
        decal("lift_white", (sx * W / 2, 0, c["lift_z"]), (sx, 0, 0), UP, 0.06, depth=0.004)
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
    decal("wordmark_white", (c["lid_x"] - 0.04, c["lid_front"], c["lid_z"]), F, UP, 0.06, depth=0.003)
    for sx in (-1, 1):
        decal("lift_white", (sx * W / 2, 0, c["lift_z"]), (sx, 0, 0), UP, 0.06, depth=0.004)
    decal("side_up_white", (-W / 2, 0, c["zb"] + 0.04), L_, UP, 0.07, depth=0.006)
    decal("code_grey", (W / 2, 0, c["zb"] + 0.04), R, UP, 0.06, depth=0.006)
    decal("serial_white", (-0.1, c["back"], c["mid"]), B, UP, 0.09, depth=0.004)
    decal("qa_red", (0.12, c["back"], c["mid"]), B, UP, 0.03, depth=0.004)
    return 4096


def narcbox():
    """Narc case: a moulded green hard case like the launcher ammo cases - corner bumpers, grey
    latches, padlock hasp, yellow stencil. Lower shell a tray, upper shell a lined lid."""
    W, D = 0.30, 0.17
    r = 0.022
    outline = rrect(W, D, r, 4)
    prism(outline, 0.01, "poly_green", bevel=0.005, segs=2)
    prism(outline, 0.034, "poly_green", (0, 0, 0.01), bevel=0.004, segs=2, hollow=0.007)
    prism(rrect(W + 0.006, D + 0.006, r + 0.003, 4), 0.006, "poly_green", (0, 0, 0.041), bevel=0.0015, segs=1,
          hollow=0.01)
    with lid():
        prism(outline, 0.03, "poly_green", (0, 0, 0.046), bevel=0.004, segs=2, hollow=0.007)
        prism(outline, 0.014, "poly_green", (0, 0, 0.076), bevel=0.01, segs=3)
        prism(inset(outline, 0.008), 0.004, "foam_egg", (0, 0, 0.072), bevel=0.0012, segs=1)
    lid_axis((-W / 2 + r, D / 2 + 0.002, 0.046), (W / 2 - r, D / 2 + 0.002, 0.046))
    top = 0.09
    # moulded grip grooves along the long sides of the base
    for sy in (-1, 1):
        for k in range(3):
            box((0.16, 0.002, 0.003), (0, sy * (D / 2 + 0.0004), 0.01 + k * 0.007), "poly_green", bevel=0.0006,
                segs=1)
    # corner bumpers, top and bottom, set out so they stay outside the shells' inner walls
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = (sx * (W / 2 - r + 0.008), sy * (D / 2 - r + 0.008))
            with lid():
                cyl(0.024, 0.044, (c[0], c[1], 0.071), "poly_green", n=16, bevel=0.011, segs=3)
            cyl(0.024, 0.044, (c[0], c[1], 0.022), "poly_green", n=16, bevel=0.009, segs=2)
    # stencil field
    with lid():
        prism(rrect(0.232, 0.116, 0.01, 3), 0.002, "poly_green", (0, 0, top - 0.0005), bevel=0.0008, segs=1)
    decal("narc_yellow", (0, 0, top + 0.0015), UP, B, 0.2, depth=0.003)
    # draw latches over the seam on the front
    fy = -D / 2
    for sx in (-0.078, 0.078):
        bail_latch((sx, fy, 0.046), F, UP, w=0.04, below=0.016, body_off=0.0, lid_off=0.0, look="latch_grey")
    # padlock hasp in the middle: the hasp hangs from the lid over the staple on the body
    with cluster():
        Fh = frame((0, fy, 0.046), F, UP)
        with lid():
            # a spacer screwed to the lid, the plate on it clear of the base's rim
            lbox(Fh, (0.026, 0.012, 0.0035), (0, 0.012, 0), "steel", bevel=0.0006)
            lbox(Fh, (0.026, 0.03, 0.003), (0, 0.004, 0.0035), "steel", cut=0.003, bevel=0.0006)
            screw((-0.009, fy - 0.0065, 0.058), F, 0.002, "steel")
            screw((0.009, fy - 0.0065, 0.058), F, 0.002, "steel")
        Fs = frame((0, fy, 0.046), F, UP)
        for sx in (-1, 1):
            lbox(Fs, (0.004, 0.01, 0.019), (sx * 0.007, -0.006, 0), "steel", bevel=0.0008)
        lcyl(Fs, 0.0022, 0.02, (0, -0.006, 0.0165), "steel", n=10, axis="x")
    # hinges on the back
    for sx in (-0.072, 0.072):
        hinge((sx - 0.026, D / 2 + 0.002, 0.046), (sx + 0.026, D / 2 + 0.002, 0.046), r=0.006, knuckles=3,
              look="poly_green")
    # pressure relief valve on the left
    with cluster():
        Fv = frame((-W / 2, 0, 0.022), L_, UP)
        lcyl(Fv, 0.011, 0.003, look="dark_poly", n=24, bevel=0.0008)
        lcyl(Fv, 0.007, 0.006, (0, 0, 0.002), "dark_poly", n=20, bevel=0.0015, segs=2)
    decal("hazard", (W / 2, 0, 0.027), R, UP, 0.07, depth=0.004)
    feet((-0.075, 0.075), (-0.042, 0.042), size=0.018)
    return 2048


# ===================================================================================================
# Enhanced Utility Pouches
# ===================================================================================================
def utility_pouch():
    """Utility pouch: a webbing pouch with a moulded lid. Two straps run over the lid and down the
    flap to side-release buckles on the body; the label sits on the flap between them. The pouch is
    open under the lid."""
    W, D, H = 0.15, 0.06, 0.118
    box((W, D, H - 0.04), (0, 0, (H - 0.04) / 2), "webbing", bevel=0.01, segs=3)
    box((W, D, 0.032), (0, 0, H - 0.026), "webbing", bevel=0.004, segs=2, hollow=0.005)
    # binding tape round the opening
    box((W + 0.003, D + 0.003, 0.006), (0, 0, H - 0.012), "webbing", bevel=0.002, segs=1, hollow=0.0065)
    # moulded lid (a shallow lined shell) and its front flap
    flap_y = -D / 2 - 0.004
    lid_axis((-W / 2, D / 2 + 0.003, H - 0.008), (W / 2, D / 2 + 0.003, H - 0.008))
    with lid():
        box((W + 0.004, D + 0.006, 0.005), (0, 0, H + 0.0015), "olive_dark", cut=0.008, bevel=0.002, segs=2)
        box((W + 0.004, D + 0.006, 0.008), (0, 0, H - 0.005), "olive_dark", cut=0.008, bevel=0.0015, segs=1,
            hollow=0.004)
        box((W - 0.012, D - 0.006, 0.002), (0, 0, H - 0.002), "foam_egg", cut=0.004, bevel=0.0006, segs=1)
        box((W - 0.016, 0.006, 0.05), (0, flap_y, H - 0.03), "olive_dark", cut=0.012, cuts=(1, 1, 0, 0),
            axis="y", bevel=0.002, segs=2)
    decal("util_label", (0, flap_y - 0.003, H - 0.026), F, UP, 0.062, depth=0.003)
    for sx in (-1, 1):
        cl = cluster()
        cl.__enter__()
        x = sx * 0.047
        # strap: over the lid, down the flap, ending in the male half of the buckle below the flap
        Fb = frame((x, -D / 2 - 0.002, H - 0.066), F, UP)
        with lid():
            box((0.02, 0.064, 0.0025), (x, -0.004, H + 0.0055), "webbing", bevel=0.0008, segs=1)
            box((0.02, 0.003, 0.058), (x, flap_y - 0.0045, H - 0.026), "webbing", bevel=0.0008, segs=1)
            lbox(Fb, (0.024, 0.016, 0.006), (0, 0.006, 0.002), "dark_poly", cut=0.004, cuts=(0, 0, 1, 1),
                 bevel=0.0012)
            for k in (-1, 1):
                lbox(Fb, (0.004, 0.01, 0.002), (k * 0.007, 0.006, 0.008), "dark_poly", bevel=0.0004)
        # female half on a short strap sewn to the body
        lbox(Fb, (0.026, 0.016, 0.006), (0, -0.01, 0.0), "dark_poly", cut=0.004, cuts=(1, 1, 0, 0), bevel=0.0012)
        box((0.02, 0.003, 0.03), (x, -D / 2 - 0.0005, H - 0.098), "webbing", bevel=0.0008, segs=1)
        cl.__exit__()
    # side compression straps
    for sx in (-1, 1):
        box((0.004, D * 0.8, 0.014), (sx * (W / 2 + 0.002), 0, 0.06), "webbing", bevel=0.001, segs=1)
    decal("marines_yellow", (W / 2, 0, 0.032), R, UP, 0.02, depth=0.003)
    decal("qa_red", (-W / 2, 0.0, 0.032), L_, UP, 0.016, depth=0.003)
    molle_back(W, D, H - 0.01, D / 2)
    return 2048


def ammo_pouch():
    """Double magazine pouch: two moulded cells side by side, each open at the top and closed by its
    own lined lid with a tongue, snap and pull tab - the magazines stand inside."""
    W, D, H = 0.1, 0.056, 0.14
    for sx in (-1, 1):
        x = sx * 0.025
        box((0.048, D, H - 0.047), (x, 0, (H - 0.047) / 2), "olive", cut=0.008, cuts=(0.6, 0.6, 0, 0), axis="y",
            bevel=0.004, segs=3)
        box((0.048, D, 0.037), (x, 0, H - 0.012 - 0.0175), "olive", bevel=0.003, segs=2, hollow=0.004)
        # rib down the outer side of each cell
        box((0.004, D * 0.7, 0.035), (sx * (W / 2 + 0.0005), 0, 0.0375), "olive_dark", bevel=0.001, segs=1)
        # lid (a shallow lined shell) and its tongue down the front
        with lid(), cluster():
            box((0.05, D + 0.006, 0.004), (x, 0, H - 0.002), "olive_dark", cut=0.004, bevel=0.0015, segs=2)
            box((0.05, D + 0.006, 0.009), (x, 0, H - 0.0085), "olive_dark", cut=0.004, bevel=0.0012, segs=1,
                hollow=0.0035)
            box((0.04, D - 0.004, 0.002), (x, 0, H - 0.005), "foam_egg", bevel=0.0005, segs=1)
            box((0.032, 0.005, 0.034), (x, -D / 2 - 0.003, H - 0.024), "olive_dark", cut=0.008,
                cuts=(1, 1, 0, 0), axis="y", bevel=0.0015, segs=2)
            Fs = frame((x, -D / 2 - 0.0055, H - 0.03), F, UP)
            lcyl(Fs, 0.0045, 0.002, look="steel", n=16, bevel=0.0006)
            lcyl(Fs, 0.0025, 0.003, look="steel", n=12, bevel=0.0008)
            # pull tab hanging from the tongue
            box((0.014, 0.003, 0.018), (x, -D / 2 - 0.0045, H - 0.047), "webbing", cut=0.004, cuts=(1, 1, 0, 0),
                axis="y", bevel=0.0006, segs=1)
    lid_axis((-W / 2, D / 2 + 0.003, H - 0.012), (W / 2, D / 2 + 0.003, H - 0.012))
    for sx in (-1, 1):
        x = sx * 0.025
        decal("ammo_cell", (x, -D / 2, 0.055), F, UP, 0.03, depth=0.003)
    decal("marines_yellow", (W / 2 - 0.001, 0, 0.075), R, UP, 0.02, depth=0.003)
    decal("qa_red", (-W / 2 + 0.001, 0, 0.075), L_, UP, 0.016, depth=0.003)
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
    with lid():
        carry_handle(0, 0, c["top"], 0.13, look="rubber")
    decal("marines_white", (-0.07, c["front"], c["mid"] + 0.006), F, UP, 0.06, depth=0.004)
    decal("ammo_crate_label", (0.05, c["front"], c["mid"] + 0.006), F, UP, 0.14, depth=0.004)
    decal("wordmark_white", (c["lid_x"] - 0.034, c["lid_front"], c["lid_z"]), F, UP, 0.05, depth=0.003)
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
    with lid():
        carry_handle(0, 0, c["top"], 0.15, look="rubber")
    decal("eng_label", (0, c["front"], c["mid"] + 0.004), F, UP, 0.19, depth=0.004)
    decal("hazard", (0, c["lid_front"], c["lid_z"]), F, UP, 0.08, depth=0.003)
    decal("wordmark_white", (c["lid_x"] - 0.034, c["lid_front"], c["lid_z"]), F, UP, 0.05, depth=0.003)
    decal("egb_white", (-0.11, c["front"], c["zb"] + 0.042), F, UP, 0.026, depth=0.004)
    decal("sticker_orange", (-0.14, 0.055, c["top"]), UP, B, 0.06, depth=0.006)
    plate((0.0, c["back"], c["mid"]), B, UP, 0.08, 0.036, "black_metal", "serial_white")
    for sx in (-1, 1):
        decal("lift_white", (sx * W / 2, 0, c["lift_z"]), (sx, 0, 0), UP, 0.055, depth=0.004)
    decal("code_grey", (W / 2, 0, c["zb"] + 0.03), R, UP, 0.055, depth=0.006)
    return 4096


def cbrn_bag():
    """CBRN container: a white UNSC case with a yellow band, a seal pressure gauge and a purge valve."""
    W, D, H = 0.4, 0.23, 0.24
    c = unsc_case(W, D, H, "hazmat_white", lid_h=0.05)
    inner = c["inner"]
    # yellow band round the body
    box((inner * 0.98, D + 0.012, 0.018), (0, 0, c["zb"] + 0.022), "hazard_yellow", bevel=0.002, segs=1)
    with lid():
        carry_handle(0, 0, c["top"], 0.15, look="rubber")
    fy = c["front"]
    # seal gauge
    gz = c["mid"] + 0.01
    gauge = cluster()
    gauge.__enter__()
    Fg = frame((0.1, fy, gz), F, UP)
    lcyl(Fg, 0.03, 0.006, look="black_metal", n=36, bevel=0.0015, segs=2)
    lcyl(Fg, 0.024, 0.0075, look="dial", n=36, bevel=0.0004)
    decal("gauge_face", (0.1, fy - 0.0075, gz), F, UP, 0.047, depth=0.002, check=False)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        screw((0.1 + 0.027 * math.cos(a), fy - 0.006, gz + 0.027 * math.sin(a)), F, 0.0016, "steel")
    gauge.__exit__()
    decal("cbrn_label", (-0.045, fy, gz), F, UP, 0.16, depth=0.004)
    decal("wordmark_white", (c["lid_x"] - 0.034, c["lid_front"], c["lid_z"]), F, UP, 0.05, depth=0.003)
    # purge valve with a red knob on the right end cap, above the grip
    with cluster():
        Fv = frame((W / 2 + 0.001, 0.0, c["zl"] - 0.022), R, UP)
        lcyl(Fv, 0.013, 0.005, look="steel", n=6, bevel=0.0008)
        lcyl(Fv, 0.006, 0.01, (0, 0, 0.004), "steel", n=16)
        lcyl(Fv, 0.01, 0.008, (0, 0, 0.012), "red", n=12, bevel=0.002, segs=2)
    decal("cbrn_label", (0.0, c["back"], c["mid"]), B, UP, 0.12, depth=0.004)
    decal("sticker_orange", (-0.13, 0.06, c["top"]), UP, B, 0.06, depth=0.006)
    decal("side_up_white", (-W / 2, 0, c["zb"] + 0.034), L_, UP, 0.06, depth=0.006)
    return 4096


# ===================================================================================================
# What is packed inside - seen when a lid opens (efku_lids). Every piece sits under the closed lid, so
# the lid hides it; it casts no shadow and leaves the far LODs.
# ===================================================================================================
from unsc_lib import contents  # noqa: E402


def foam(size, center, profile=None):
    """A foam insert: the dark bed the contents sit in."""
    sx, sy, sz = size
    if profile is not None:
        prism(profile, sz, "foam", (center[0], center[1], center[2] - sz / 2), bevel=0.0015, segs=2)
    else:
        box(size, center, "foam", bevel=0.0015, segs=2)
    return center[2] + sz / 2


@clustered
def biofoam(c, axis="x", length=0.07, r=0.012):
    """Biofoam canister lying in the foam: white body, red band, grey cap, red nozzle."""
    x, y, z = c
    d = (1, 0, 0) if axis == "x" else (0, 1, 0)
    cyl(r, length, (x, y, z), "biofoam", axis=axis, n=18, bevel=0.002, segs=2)
    off = length * 0.22
    cyl(r + 0.0006, 0.008, (x - d[0] * off, y - d[1] * off, z), "red", axis=axis, n=18, bevel=0.0006)
    end = length / 2 + 0.006
    cyl(r * 0.7, 0.012, (x + d[0] * end, y + d[1] * end, z), "dark_poly", axis=axis, n=14, bevel=0.0015)
    tip = length / 2 + 0.014
    cyl(r * 0.25, 0.008, (x + d[0] * tip, y + d[1] * tip, z), "red", axis=axis, n=10, bevel=0.0005)


@clustered
def injector(c, axis="y", length=0.1, r=0.0055, cap="red"):
    """Auto-injector: olive body, a window band, a coloured safety cap."""
    x, y, z = c
    d = (1, 0, 0) if axis == "x" else (0, 1, 0)
    cyl(r, length, (x, y, z), "injector", axis=axis, n=14, bevel=0.0012)
    cyl(r + 0.0004, length * 0.12, (x + d[0] * length * 0.15, y + d[1] * length * 0.15, z), "glass", axis=axis,
        n=14, bevel=0.0004)
    e = length / 2 + 0.009
    cyl(r + 0.0006, 0.018, (x + d[0] * e, y + d[1] * e, z), cap, axis=axis, n=14, bevel=0.0015, segs=2)


@clustered
def dressing(c, w=0.06, d=0.04, h=0.012, look="pack_olive", flat=True):
    """A sealed dressing pack with a tear strip."""
    x, y, z = c
    if flat:
        box((w, d, h), (x, y, z + h / 2), look, bevel=0.003, segs=2)
        box((w * 0.9, 0.004, 0.0012), (x, y + d * 0.32, z + h + 0.0004), "red", bevel=0.0003, segs=1)
    else:   # standing against a wall that faces -y (the IFAK's front)
        box((w, h, d), (x, y - h / 2, z), look, bevel=0.0015, segs=1)
        box((w * 0.9, 0.0012, 0.004), (x, y - h - 0.0004, z + d * 0.32), "red", bevel=0.0003, segs=1)


@clustered
def tourniquet(c, flat=True):
    """Folded tourniquet: black strap bundle with its windlass and buckle."""
    x, y, z = c
    if flat:
        box((0.07, 0.026, 0.012), (x, y, z + 0.006), "rubber", bevel=0.005, segs=2)
        box((0.008, 0.032, 0.015), (x - 0.018, y, z + 0.0075), "red", bevel=0.002, segs=1)
        box((0.012, 0.022, 0.014), (x + 0.026, y, z + 0.007), "steel", bevel=0.002, segs=1)
    else:
        box((0.026, 0.006, 0.06), (x, y - 0.003, z), "rubber", bevel=0.0025, segs=2)
        box((0.03, 0.0065, 0.008), (x, y - 0.00325, z - 0.015), "red", bevel=0.001, segs=1)


@clustered
def suture_kit(c):
    x, y, z = c
    box((0.05, 0.036, 0.01), (x, y, z + 0.005), "pack_white", bevel=0.003, segs=2)
    box((0.012, 0.03, 0.0012), (x - 0.016, y, z + 0.0104), "red", bevel=0.0003, segs=1)


@clustered
def vial(c, r=0.0065, h=0.03):
    x, y, z = c
    cyl(r, h, (x, y, z + h / 2), "glass_amber", n=14, bevel=0.0012)
    cyl(r + 0.0004, 0.006, (x, y, z + h + 0.003), "steel", n=14, bevel=0.0012)


@clustered
def pill_box(c):
    x, y, z = c
    box((0.04, 0.026, 0.012), (x, y, z + 0.006), "pack_white", bevel=0.002, segs=1)
    box((0.04, 0.008, 0.0012), (x, y - 0.006, z + 0.0124), "red", bevel=0.0003, segs=1)


@clustered
def mag_top(c, h=0.012, w=0.026, d=0.044):
    """The top of an MA5 magazine standing in its slot: the body, long side front to back (d), the two
    feed lips along it, and the top round lying between them, bullet forward (-y), all within the
    body's length - the way a loaded magazine looks from above."""
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
    """A full MA5 magazine lying flat in foam: the body along y (feed end at +y), its front-to-back
    depth along x, ribs on the face, the floor plate, feed lips and the top round lying front to back
    (bullet towards -x) inside the lips."""
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


@clustered
def filter_can(c):
    x, y, z = c
    cyl(0.019, 0.024, (x, y, z + 0.012), "olive_dark", n=18, bevel=0.003, segs=2)
    cyl(0.008, 0.0045, (x, y, z + 0.0265), "black_metal", n=12, bevel=0.0008)


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


def fill_medical_case(W, D, H, lid_h, cap, more=False):
    with contents():
        zf = case_foam(W, D, H, lid_h, cap)
        for k, y in enumerate((-0.08, -0.048, -0.016)):
            biofoam((-0.09, y, zf + 0.007))
        for k in range(6):
            injector((0.03 + k * 0.018, -0.005, zf + 0.0035), cap="red" if k % 2 == 0 else "orange")
        for x in (-0.11, -0.04):
            dressing((x, 0.06, zf), 0.06, 0.04, 0.012)
        tourniquet((0.1, 0.085, zf))
        suture_kit((-0.01, -0.09, zf))
        for x in (0.07, 0.13):
            dressing((x, -0.092, zf), 0.05, 0.03, 0.01, look="pack_white")
        pill_box((0.03, 0.088, zf))
        if more:
            dressing((0.155, 0.04, zf), 0.03, 0.05, 0.01, look="pack_white")


def fill_ifak():
    with contents():
        # on the back wall of the compartment behind the front lid
        box((0.14, 0.004, 0.09), (0, -0.0115, 0.06), "foam", bevel=0.0012, segs=1)
        wall = -0.0135
        for x in (-0.045, -0.005):
            dressing((x, wall, 0.07), 0.034, 0.05, 0.012, flat=False)
        injector((0.012, wall - 0.005, 0.03), axis="x", length=0.06, r=0.0045, cap="red")
        tourniquet((0.045, wall, 0.075), flat=False)


def fill_afak():
    W, D, C = 0.36, 0.27, 0.06
    with contents():
        prism(inset(rect(W, D, C), 0.0085), 0.004, "foam", (0, 0, 0.02), bevel=0.0012, segs=1)
        zf = 0.024
        field_generator((0, 0, zf))
        for x in (-0.13, -0.095, 0.095, 0.13):
            biofoam((x, 0.0, zf + 0.006), axis="y", length=0.06, r=0.011)
        for x in (-0.04, 0.04):
            dressing((x, -0.07, zf), 0.05, 0.03, 0.01)
        for y in (0.062, 0.084):
            injector((0.0, y, zf + 0.0035), axis="x", length=0.1, cap="red")


def fill_narcbox():
    W, D = 0.30, 0.17
    with contents():
        prism(inset(rrect(W, D, 0.022, 4), 0.0075), 0.004, "foam", (0, 0, 0.03), bevel=0.0012, segs=1)
        zf = 0.034
        for k in range(6):
            injector((-0.09 + k * 0.018, -0.004, zf + 0.0035), length=0.1, cap="red" if k < 3 else "orange")
        for x, y in ((0.04, -0.035), (0.07, -0.035), (0.04, -0.005), (0.07, -0.005)):
            vial((x, y, zf), h=0.026)
        for x in (0.035, 0.08):
            pill_box((x, 0.045, zf))


def fill_utility_pouch():
    W, D, H = 0.15, 0.06, 0.118
    with contents():
        box((W - 0.012, D - 0.012, 0.003), (0, 0, H - 0.03), "foam", bevel=0.0006, segs=1)
        z = H - 0.0285
        flashlight((-0.03, -0.006, z + 0.0065))
        box((0.05, 0.018, 0.007), (0.042, -0.008, z + 0.0035), "steel", cut=0.004, bevel=0.0015, segs=1)
        cyl(0.0055, 0.04, (0.042, 0.013, z + 0.0055), "olive_dark", axis="x", n=12, bevel=0.002, segs=1)


def fill_ammo_pouch():
    D, H = 0.056, 0.14
    with contents():
        for sx in (-1, 1):
            mag_top((sx * 0.025, 0.002, H - 0.047), h=0.025)


def fill_ammo_bag():
    W, D, H, lid_h, cap = 0.36, 0.18, 0.2, 0.042, 0.03
    with contents():
        zf = case_foam(W, D, H, lid_h, cap)
        # four full magazines lying flat, sunk halfway into their foam cut-outs
        for k in range(4):
            mag_flat((-0.108 + k * 0.072, -0.004, zf - 0.016))


def fill_engineer_bag():
    W, D, H, lid_h, cap = 0.42, 0.21, 0.21, 0.046, 0.034
    with contents():
        zf = case_foam(W, D, H, lid_h, cap)
        wrench((-0.09, -0.065, zf))
        screwdriver((-0.085, -0.035, zf), "orange")
        screwdriver((-0.085, -0.01, zf), "red")
        multimeter((0.12, -0.035, zf))
        for x in (-0.1, 0.0):
            demo_block((x, 0.05, zf))
        cable_coil((0.12, 0.05, zf))


def fill_cbrn_bag():
    W, D, H, lid_h, cap = 0.4, 0.23, 0.24, 0.05, 0.034
    with contents():
        zf = case_foam(W, D, H, lid_h, cap)
        gas_mask((-0.085, 0.005, zf))
        for x in (0.035, 0.08, 0.125):
            filter_can((x, -0.06, zf))
        for y in (0.03, 0.055, 0.08):
            injector((0.08, y, zf + 0.0035), axis="x", length=0.1, cap="red")
        for x in (-0.11, -0.055):
            dressing((x, -0.08, zf), 0.045, 0.032, 0.01, look="pack_white")


def _filled(builder, fill):
    def build():
        size = builder()
        fill()
        return size
    build.__name__ = builder.__name__
    return build


BUILDERS = {
    "ifak": _filled(ifak, fill_ifak),
    "afak": _filled(afak, fill_afak),
    "mfak": _filled(mfak, lambda: fill_medical_case(0.46, 0.25, 0.25, 0.048, 0.034)),
    "mfakplus": _filled(mfakplus, lambda: fill_medical_case(0.44, 0.24, 0.36, 0.05, 0.034, more=True)),
    "narcbox": _filled(narcbox, fill_narcbox),
    "utility_pouch": _filled(utility_pouch, fill_utility_pouch),
    "ammo_pouch": _filled(ammo_pouch, fill_ammo_pouch),
    "ammo_bag": _filled(ammo_bag, fill_ammo_bag),
    "engineer_bag": _filled(engineer_bag, fill_engineer_bag),
    "cbrn_bag": _filled(cbrn_bag, fill_cbrn_bag),
}


# Kits that lie differently in the game than they are built (degrees about x, y, z): the IFAK lies
# on its back, the label up, the way a belt case is put down - turned round so the holder shows it
# with the label reading towards the front.
EXPORT_ROT = {"ifak": (-90, 0, 180)}

ADDON = {k: "kits" for k in ("ifak", "afak", "mfak", "mfakplus", "narcbox")}
ADDON.update({k: "eup" for k in ("utility_pouch", "ammo_pouch", "ammo_bag", "engineer_bag", "cbrn_bag")})
