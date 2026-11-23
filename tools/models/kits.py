"""The kit models, built from the parts in unsc_lib. Blender space: front at -y, z up, metres.

Each builder returns the texture size of its kit. EFAK's five kits go into addons/kits, the five
pouches of Enhanced Utility Pouches into addons/eup (ADDON below), and with them the two cases this
mod adds itself: special ammunition, explosives and ordnance.
"""
import math

from unsc_lib import (box, bolt, cluster, eggcrate, loft, clustered, cyl, decal, frame, hinge, inset, lbox, lcyl, lid, lid_axis,
                      plate, prism, rect, rivets, rrect, screw, bail_latch, vents, SHADOW)
from mathutils import Vector

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
        box((W + 0.006 - 0.02, D + 0.016 - 0.02, 0.006), (0, 0, top - 0.013), "foam", bevel=0.0015, segs=1)
        eggcrate(frame((0, 0, top - 0.016), DOWN, B), W - 0.02, D - 0.01, depth=0.014, pitch=0.046)
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
        box((0.13, 0.002, 0.09), (0, -D / 2 - 0.0025, 0.066), "foam", cut=0.01, axis="y", bevel=0.0006, segs=1)
        eggcrate(frame((0, -D / 2 - 0.0015, 0.066), B, UP), 0.118, 0.078, depth=0.005, pitch=0.026)
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
    return 4096


# The AFAK: the Halo health pack, built here with our own parts and texture to its measures (taken
# in game): an octagon 40 x 50 cm at its waist with 20 cm wide ends, standing straight from 5 to 15 cm,
# drawing in steeply to a 20 x 24 cm floor and to a 25 x 27 cm top. It opens at the middle of the
# waist. C is the cut at the waist as one 45-degree figure, for the contents' tray.
AF = dict(W=0.40, L=0.50, C=0.12, bot=0.05, seam=0.10, waist=0.15, H=0.2)


def oct8(w, l, cx, cy, d=0.0):
    """An octagon w x l, its ends cut in by cx across and cy along, moved in by d."""
    pts = [(-w / 2 + cx, -l / 2), (w / 2 - cx, -l / 2), (w / 2, -l / 2 + cy), (w / 2, l / 2 - cy),
           (w / 2 - cx, l / 2), (-w / 2 + cx, l / 2), (-w / 2, l / 2 - cy), (-w / 2, -l / 2 + cy)]
    return inset(pts, d) if d else pts


def af_outline(d=0.0):
    """The pack's outline at the waist, moved in by d."""
    return oct8(0.40, 0.50, 0.10, 0.15, d)


def afak():
    """AFAK: the white pack, opening at its waist - the lower half a tray with the contents in cut
    foam, the upper half the lid, hinged at the back and lined with egg-crate foam. The red H on a
    framed plate on the top, a grip recess in the top bevel at each end, red reflectors on the four
    corner bevels, ribbed rubber grips in frames on the long sides."""
    W, L = AF["W"], AF["L"]
    zb, zs, zw, top = AF["bot"], AF["seam"], AF["waist"], AF["H"]
    out = af_outline()
    floor = oct8(0.20, 0.24, 0.04, 0.05)
    # the lower half: the bottom bevel and the waist up to the seam (a wall round the tray)
    loft(floor, out, 0.0, zb, "halo_white", bevel=0.005, segs=3)
    prism(out, zs - zb, "halo_white", (0, 0, zb), bevel=0.003, segs=2, hollow=0.012)
    prism(inset(out, 0.002), 0.004, "rubber", (0, 0, zs - 0.001), bevel=0.001, segs=1, hollow=0.008)
    hy = L / 2 + 0.004
    lid_axis((-0.08, hy, zs + 0.002), (0.08, hy, zs + 0.002))
    with lid():
        prism(out, zw - zs - 0.002, "halo_white", (0, 0, zs + 0.002), bevel=0.003, segs=2, hollow=0.012)
        # a narrow chamfer up to the shoulder, the raised block on it, its ends sloping down
        zsh, zbl = 0.162, 0.172
        shoulder = oct8(0.342, 0.411, 0.085, 0.12)
        loft(out, shoulder, zw, zsh, "halo_white", bevel=0.003, segs=2)
        loft(oct8(0.258, 0.411, 0.012, 0.012), oct8(0.258, 0.411, 0.012, 0.012), zsh - 0.001, zbl, "halo_white",
             bevel=0.003, segs=2)
        loft(oct8(0.258, 0.411, 0.012, 0.012), oct8(0.258, 0.268, 0.012, 0.012), zbl, top, "halo_white",
             bevel=0.004, segs=2)
        # the lining under the lid
        prism(inset(out, 0.012), 0.004, "foam", (0, 0, zw - 0.004), bevel=0.001, segs=1)
        eggcrate(frame((0, 0, zw - 0.004), DOWN, B), W - 0.05, L - 0.06, depth=0.012, pitch=0.044,
                 inside=lambda x, y: abs(x) < W / 2 - 0.03 and abs(y) < L / 2 - 0.03
                 and abs(x) / 0.1 + abs(y) / 0.15 < 2.6)
        # the framed plate with the H on the block
        box((0.13, 0.13, 0.004), (0, 0, top + 0.001), "halo_white", cut=0.006, bevel=0.0015, segs=2, taper=0.002)
        box((0.136, 0.136, 0.002), (0, 0, top), "red", cut=0.007, bevel=0.0006, segs=1, hollow=0.003)
        # a grip recess in each sloping end of the block: a grey pocket, a tab over its upper edge
        slope = math.atan2(top - zbl, (0.411 - 0.268) / 2)
        for sy in (-1, 1):
            n = (0, sy * math.sin(slope), math.cos(slope))
            c = (0, sy * (0.268 + 0.411) / 4, (zbl + top) / 2)
            Fr = frame(c, n, (0, -sy, 0))
            lbox(Fr, (0.16, 0.08, 0.004), (0, 0, -0.003), "dark_poly", cut=0.014, bevel=0.0012)
            lbox(Fr, (0.05, 0.014, 0.006), (0, 0.03, -0.001), "halo_white", cut=0.004, bevel=0.0015)
        # ribbed rubber grips on the shoulder beside the block
        for sx in (-1, 1):
            Fs = frame((sx * 0.15, 0, zsh), UP, B)
            lbox(Fs, (0.05, 0.21, 0.003), (0, 0, -0.002), "dark_poly", bevel=0.0006)
            for k in range(19):
                lbox(Fs, (0.044, 0.006, 0.004), (0, -0.099 + k * 0.011, -0.001), "rubber", bevel=0.0009)
        # red reflectors on the four corner chamfers
        for sx in (-1, 1):
            for sy in (-1, 1):
                Fq = frame((sx * 0.147, sy * 0.178, (zw + zsh) / 2 + 0.001), (sx * 0.55, sy * 0.4, 1), UP)
                lbox(Fq, (0.065, 0.026, 0.003), (0, 0, -0.0012), "red_reflector", cut=0.008, cuts=(1, 1, 0, 0),
                     bevel=0.0008)
    decal("med_h", (0, 0, top + 0.003), UP, B, 0.1, depth=0.003)
    # ribbed rubber grips in frames on the long sides, across the seam (each half has its part)
    for sx in (-1, 1):
        for z0, z1, in_lid in ((zs + 0.006, zw - 0.006, True),):
            def grip(sx=sx, z0=z0, z1=z1):
                Fg = frame((sx * (W / 2 + 0.0005), 0, (z0 + z1) / 2), (sx, 0, 0), UP)
                lbox(Fg, (0.19, z1 - z0, 0.003), (0, 0, 0), "shell_grey", bevel=0.0008)
                lbox(Fg, (0.17, z1 - z0 - 0.008, 0.002), (0, 0, 0.003), "rubber", bevel=0.0006)
                for k in range(16):
                    lbox(Fg, (0.0045, z1 - z0 - 0.012, 0.003), (-0.075 + k * 0.01, 0, 0.004), "rubber",
                         bevel=0.0006)
            if in_lid:
                with lid():
                    grip()
            else:
                grip()
    # a small hinge at the back, on the end between its cut corners
    hinge((-0.08, hy, zs + 0.002), (0.08, hy, zs + 0.002), r=0.004, knuckles=7, look="shell_grey")
    decal("serial_white", (0.0, -L / 2, (zb + zs) / 2), F, UP, 0.05, depth=0.006)
    return 4096


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
        prism(inset(outline, 0.008), 0.004, "foam", (0, 0, 0.072), bevel=0.0012, segs=1)
        eggcrate(frame((0, 0, 0.072), DOWN, B), W - 0.03, D - 0.03, depth=0.009, pitch=0.038,
                 inside=lambda x, y: abs(x) < 0.097 or abs(y) < 0.024)
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
    return 4096


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
        box((W - 0.012, D - 0.006, 0.002), (0, 0, H - 0.002), "foam", cut=0.004, bevel=0.0006, segs=1)
        eggcrate(frame((0, 0, H - 0.003), DOWN, B), W - 0.022, D - 0.014, depth=0.004, pitch=0.022)
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


# The ammo pouch: width, depth, height, the cells' centres and width - two MA5 magazines a cell.
AP = dict(W=0.25, D=0.082, H=0.19, cx=0.0625, cw=0.123)


def ammo_pouch():
    """Double magazine pouch for the MA5: two moulded cells side by side, two magazines in each,
    every cell closed by its own lined lid with a tongue, snap and pull tab. Built for magazines at
    their full size (OPTRE's MA5 magazine is 16.4 cm long and 10.8 cm deep)."""
    W, D, H = AP["W"], AP["D"], AP["H"]
    cx, cw = AP["cx"], AP["cw"]
    for sx in (-1, 1):
        x = sx * cx
        box((cw, D, H - 0.06), (x, 0, (H - 0.06) / 2), "olive", cut=0.012, cuts=(0.6, 0.6, 0, 0), axis="y",
            bevel=0.005, segs=3)
        box((cw, D, 0.048), (x, 0, H - 0.016 - 0.024), "olive", bevel=0.004, segs=2, hollow=0.005)
        # rib down the outer side of each cell
        box((0.005, D * 0.7, 0.05), (sx * (W / 2 + 0.0005), 0, 0.05), "olive_dark", bevel=0.0012, segs=1)
        # lid (a shallow lined shell) and its tongue down the front
        with lid(), cluster():
            box((cw + 0.002, D + 0.008, 0.005), (x, 0, H - 0.0025), "olive_dark", cut=0.006, bevel=0.002, segs=2)
            box((cw + 0.002, D + 0.008, 0.012), (x, 0, H - 0.011), "olive_dark", cut=0.006, bevel=0.0015, segs=1,
                hollow=0.0045)
            box((cw - 0.012, D - 0.006, 0.002), (x, 0, H - 0.006), "foam", bevel=0.0005, segs=1)
            eggcrate(frame((x, 0, H - 0.007), DOWN, B), cw - 0.018, D - 0.016, depth=0.005, pitch=0.024)
            box((0.06, 0.006, 0.05), (x, -D / 2 - 0.004, H - 0.032), "olive_dark", cut=0.012,
                cuts=(1, 1, 0, 0), axis="y", bevel=0.002, segs=2)
            Fs = frame((x, -D / 2 - 0.007, H - 0.04), F, UP)
            lcyl(Fs, 0.006, 0.0025, look="steel", n=16, bevel=0.0007)
            lcyl(Fs, 0.0034, 0.0035, look="steel", n=12, bevel=0.0009)
            # pull tab hanging from the tongue
            box((0.02, 0.003, 0.026), (x, -D / 2 - 0.0055, H - 0.064), "webbing", cut=0.006, cuts=(1, 1, 0, 0),
                axis="y", bevel=0.0007, segs=1)
    lid_axis((-W / 2, D / 2 + 0.004, H - 0.016), (W / 2, D / 2 + 0.004, H - 0.016))
    for sx in (-1, 1):
        decal("ammo_cell", (sx * cx, -D / 2, 0.065), F, UP, 0.05, depth=0.003)
    decal("marines_yellow", (W / 2 - 0.001, 0, 0.1), R, UP, 0.028, depth=0.003)
    decal("qa_red", (-W / 2 + 0.001, 0, 0.1), L_, UP, 0.022, depth=0.003)
    # drain grommets in the floor
    for sx in (-1, 1):
        lcyl(frame((sx * cx, 0, 0.0005), DOWN, B), 0.005, 0.0015, look="steel", n=14, bevel=0.0004)
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
# Two cases of this mod's own (kits it registers itself, addons/eup)
# ===================================================================================================
def special_ammo():
    """Special ammunition case: the ammunition case again under its own stencil - what the marksmen
    draw."""
    W, D, H = 0.36, 0.18, 0.2
    c = unsc_case(W, D, H, "unsc_olive", lid_h=0.042, cap=0.03)
    with lid():
        carry_handle(0, 0, c["top"], 0.13, look="rubber")
    decal("marines_white", (-0.085, c["front"], c["mid"] + 0.006), F, UP, 0.05, depth=0.004)
    decal("spec_ammo_label", (0.035, c["front"], c["mid"] + 0.006), F, UP, 0.15, depth=0.004)
    decal("wordmark_white", (c["lid_x"] - 0.034, c["lid_front"], c["lid_z"]), F, UP, 0.05, depth=0.003)
    decal("sticker_orange", (-0.12, 0.05, c["top"]), UP, B, 0.05, depth=0.006)
    decal("spec_ammo_label", (0, c["back"], c["mid"] + 0.004), B, UP, 0.17, depth=0.004)
    decal("code_grey", (W / 2, 0, c["zb"] + 0.028), R, UP, 0.05, depth=0.006)
    decal("side_up_white", (-W / 2, 0, c["zb"] + 0.028), L_, UP, 0.06, depth=0.006)
    return 4096


# The ordnance case: width, depth, height, the seam's height, wall and floor thickness. About two
# thirds of a real rocket case - a two-hand load with a grip on each end and one on the front.
ORD = dict(W=0.78, D=0.27, H=0.17, seam=0.088, wall=0.012, floor=0.03)
BUMP = dict(bx=0.095, by=0.07, proud=0.008, r=0.016)


def _bumper_outline(sx, sy, proud, inner):
    """Outline of a corner bumper round the corner (sx, sy) of the ordnance case: bx along the long
    face, by along the end, standing `proud` of both, its outer corner rounded. inner=True: an angle
    only as deep as the wall (2 mm into it), so the open tub shows none of it; False: the whole
    corner field, for the caps on top and underneath."""
    import math as _mm
    cx, cy = ORD["W"] / 2, ORD["D"] / 2
    bx, by, r = BUMP["bx"], BUMP["by"], BUMP["r"] + (proud - BUMP["proud"])
    pts = [(cx - bx, cy + proud)]
    for k in range(7):
        a = _mm.radians(90 - 15 * k)
        pts.append((cx + proud - r + r * _mm.cos(a), cy + proud - r + r * _mm.sin(a)))
    pts.append((cx + proud, cy - by))
    if inner:
        pts += [(cx - 0.002, cy - by), (cx - 0.002, cy - 0.002), (cx - bx, cy - 0.002)]
    else:
        pts.append((cx - bx, cy - by))
    pts = [(sx * x, sy * y) for x, y in pts]
    if sx * sy < 0:
        pts.reverse()
    return pts


def _bumper(sx, sy, z0, z1, cap_z, look="bumper_tan"):
    """One corner bumper: the angle round the corner from z0 to z1 and its cap at cap_z (the foot
    under a lower bumper, the cap on an upper one). The cap overhangs the angle by a lip and the
    angle runs into it, so the two read as one moulding without a seam between them."""
    p = BUMP["proud"]
    prism(_bumper_outline(sx, sy, p, True), z1 - z0, look, (0, 0, z0), bevel=0.0035, segs=3)
    prism(_bumper_outline(sx, sy, p + 0.0015, False), 0.008, look, (0, 0, cap_z), bevel=0.003, segs=3)


@clustered
def chest_handle(center, normal, length):
    """A folding chest handle on a face, hanging down flat against it: a steel back plate held by
    four screws, two pivot lugs at its top, a bail hinged in them and a rubber grip on the bail's
    bar. Lies too close to the face to cast a shadow of its own."""
    if SHADOW[0]:
        return
    Fh = frame(center, normal, UP)
    pw, ph = length + 0.036, 0.046
    lbox(Fh, (pw, ph, 0.002), (0, 0, 0), "black_metal", cut=0.005, bevel=0.0008)
    for sx in (-1, 1):
        for sy in (-1, 1):
            at = Fh @ Vector((sx * (pw / 2 - 0.007), sy * (ph / 2 - 0.007), 0.002))
            screw(tuple(at), normal, 0.002, "steel")
        lbox(Fh, (0.012, 0.014, 0.011), (sx * length / 2, 0.012, 0.002), "black_metal", cut=0.003, bevel=0.0012)
        lbox(Fh, (0.005, 0.032, 0.005), (sx * length / 2, -0.002, 0.008), "steel", bevel=0.0012)
    lcyl(Fh, 0.0032, length, (0, -0.016, 0.0105), "steel", n=10, axis="x")
    lcyl(Fh, 0.0075, length - 0.014, (0, -0.016, 0.0105), "rubber", n=14, bevel=0.002, segs=2, axis="x")


def ordnance_crate():
    """Explosives and ordnance case, after the UNSC's rocket case: a long, flat shell of red-brown
    polymer split at half height, tan rubber bumpers moulded round its eight corners, two draw
    latches and a folding handle on the front, a folding handle on each end, the stencil across the
    lid."""
    W, D, H, zl, wall, floor = (ORD[k] for k in ("W", "D", "H", "seam", "wall", "floor"))
    body = "ord_brown"
    bx, by, p = BUMP["bx"], BUMP["by"], BUMP["proud"]
    # the tub: a floor set in from the wall, the wall round the well, a gasket on its rim
    box((W - 0.014, D - 0.014, floor - 0.004), (0, 0, 0.004 + (floor - 0.004) / 2), body, cut=0.006,
        cuts=(1, 1, 0, 0), axis="x", bevel=0.003, segs=2)
    box((W, D, zl - 0.012), (0, 0, (0.012 + zl) / 2), body, bevel=0.004, segs=3, hollow=wall)
    box((W - 0.004, D - 0.004, 0.004), (0, 0, zl + 0.0005), "rubber", bevel=0.001, segs=1, hollow=0.006)
    # a rib round the tub under the seam, two skids, the rail the hinge sits on
    box((W + 0.004, D + 0.004, 0.01), (0, 0, zl - 0.014), body, bevel=0.002, segs=2, hollow=0.014)
    for sx in (-1, 1):
        box((0.04, D * 0.8, 0.005), (sx * W * 0.2, 0, 0.0025), "frame_black", bevel=0.0015, segs=1)
    box((W * 0.62, 0.008, 0.012), (0, D / 2 + 0.004, zl - 0.007), body, bevel=0.002, segs=2)
    for sx in (-1, 1):
        for sy in (-1, 1):
            _bumper(sx, sy, 0.004, zl - 0.001, 0.0)
    top = H
    lb = zl + 0.002
    with lid():
        # the lid: a skirt and a top plate with cut upper edges, a raised field for the stencil,
        # lined with egg-crate foam
        box((W, D, top - 0.012 - lb), (0, 0, (lb + top - 0.012) / 2), body, bevel=0.004, segs=3, hollow=wall)
        box((W, D, 0.012), (0, 0, top - 0.006), body, cut=0.006, cuts=(0, 0, 1, 1), axis="x", bevel=0.003, segs=2)
        box((W - 2 * bx - 0.03, D - 0.06, 0.002), (0, 0, top + 0.001), body, cut=0.012, bevel=0.0012, segs=1)
        box((W + 0.004, D + 0.004, 0.01), (0, 0, lb + 0.014), body, bevel=0.002, segs=2, hollow=0.014)
        box((W * 0.62, 0.008, 0.012), (0, D / 2 + 0.004, lb + 0.007), body, bevel=0.002, segs=2)
        box((W - 2 * wall - 0.002, D - 2 * wall - 0.002, 0.004), (0, 0, top - 0.014), "foam", bevel=0.0015, segs=1)
        eggcrate(frame((0, 0, top - 0.016), DOWN, B), W - 2 * wall - 0.006, D - 2 * wall - 0.006, depth=0.014,
                 pitch=0.046)
        for sx in (-1, 1):
            for sy in (-1, 1):
                _bumper(sx, sy, lb + 0.001, top - 0.002, top - 0.002)
    # the hinge on its rails, clear of the bumpers, so the lid swings past them
    hy = D / 2 + 0.011
    lid_axis((-W / 2, hy, zl + 0.001), (W / 2, hy, zl + 0.001))
    for x in (-W * 0.2, W * 0.2):
        bail_latch((x, -D / 2, lb), F, UP, w=0.04, below=0.022, body_off=0.0, lid_off=0.0, look="black_metal")
    hinge((-W * 0.3, hy, zl + 0.001), (W * 0.3, hy, zl + 0.001), r=0.0045, knuckles=11, look="black_metal")
    # grips: one on the front between the latches, one on each end between the bumpers
    zg = 0.041
    chest_handle((0, -D / 2, zg), F, 0.14)
    for sx in (-1, 1):
        chest_handle((sx * W / 2, 0, zg), (sx, 0, 0), D - 2 * by - 0.046)
    # the stencil across the lid, reading from the front; small marks on the lid's faces
    zm = lb + 0.019 + (top - 0.012 - lb - 0.019) * 0.5
    decal("ord_label", (0, 0, top + 0.002), UP, B, 0.5, depth=0.005)
    decal("ord_front", (-0.215, -D / 2, zm), F, UP, 0.12, depth=0.004)
    decal("unsc_white", (0.215, -D / 2, zm), F, UP, 0.09, depth=0.004)
    decal("ord_front", (0, D / 2, zm), B, UP, 0.11, depth=0.004)
    decal("code_grey", (W / 2, 0, zm), R, UP, 0.045, depth=0.004)
    decal("side_up_white", (-W / 2, 0, zm), L_, UP, 0.05, depth=0.004)
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


# The contents and the cut foam they lie in: interiors.py.
from interiors import (fill_ifak, fill_afak, fill_mfak, fill_mfakplus, fill_narcbox, fill_utility_pouch,  # noqa: E402
                       fill_ammo_pouch, fill_ammo_bag, fill_engineer_bag, fill_cbrn_bag, fill_special_ammo,
                       fill_ordnance_crate)


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
    "mfak": _filled(mfak, fill_mfak),
    "mfakplus": _filled(mfakplus, fill_mfakplus),
    "narcbox": _filled(narcbox, fill_narcbox),
    "utility_pouch": _filled(utility_pouch, fill_utility_pouch),
    "ammo_pouch": _filled(ammo_pouch, fill_ammo_pouch),
    "ammo_bag": _filled(ammo_bag, fill_ammo_bag),
    "engineer_bag": _filled(engineer_bag, fill_engineer_bag),
    "cbrn_bag": _filled(cbrn_bag, fill_cbrn_bag),
    "special_ammo": _filled(special_ammo, fill_special_ammo),
    "ordnance_crate": _filled(ordnance_crate, fill_ordnance_crate),
}


# Kits that lie differently in the game than they are built (degrees about x, y, z): the IFAK lies
# on its back, the label up, the way a belt case is put down - turned round so the holder shows it
# with the label reading towards the front.
EXPORT_ROT = {"ifak": (-90, 0, 180)}

# Kits built smaller than they are, set to their real size on export (build_kit.py): what is packed
# inside comes from other mods and is then the size it is there - the ammunition box's MA5 and BR
# magazines (built at half size), the rocket case's M41 tube and Lykoi rocket (built at 60 %), the
# special ammunition box's SRS99 magazines and 14.5 mm packets (half size), the engineer's tools and
# the utility pouch's flashlight and chemlights at the size of real ones.
KIT_SCALE = {"ammo_bag": 2.0, "special_ammo": 2.0, "ordnance_crate": 1 / 0.6, "engineer_bag": 1.4,
             "utility_pouch": 1.5}

# What each kit weighs as a world object (kg), packed.
KIT_MASS = {"ifak": 1.5, "afak": 6.0, "mfak": 12.0, "mfakplus": 15.0, "narcbox": 8.0, "utility_pouch": 1.0,
            "ammo_pouch": 2.5, "ammo_bag": 25.0, "engineer_bag": 18.0, "cbrn_bag": 14.0, "special_ammo": 20.0,
            "ordnance_crate": 30.0}

ADDON = {k: "kits" for k in ("ifak", "afak", "mfak", "mfakplus", "narcbox")}
ADDON.update({k: "eup" for k in ("utility_pouch", "ammo_pouch", "ammo_bag", "engineer_bag", "cbrn_bag", "special_ammo",
                                 "ordnance_crate")})
