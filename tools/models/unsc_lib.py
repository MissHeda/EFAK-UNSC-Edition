"""Blender side of the kit pipeline: hard-surface parts, baking, LODs, the MLOD writer, icons.

Runs inside Blender (5.x). kits.py describes each model with the helpers here; build_kit.py runs
one kit from start to end:

    blender -b -P tools/models/build_kit.py -- ifak

Conventions
- Modelled in Blender space: x width, y depth with the FRONT at -y, z up from the ground at 0.
- Written for the game as x -> x, y -> -y, z -> z: a mirror, because the game reads p3d files
  left-handed. That keeps text the right way round in game (EFAK's narc box learned this the hard
  way) and puts the front at +y, as EFAK's own kits have it.
- Each part has a "look" (LOOKS), a material that is only used for baking: the bake turns colour,
  grime, edge wear and decals into one texture per kit (_co), plus _nohq (rounded edges, surface
  grain) and _smdi (specular, gloss).
"""
import bmesh
import bpy
import math
import os
import struct
import subprocess

from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "out")
DECALS = os.path.join(OUT, "decals")
IMAGE_TO_PAA = r"D:\Steam\steamapps\common\Arma 3 Tools\ImageToPAA\ImageToPAA.exe"


def srgb(r, g, b):
    """0-255 sRGB -> linear, which is what shader colours are."""
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(r), lin(g), lin(b), 1.0)


# --- Looks ---------------------------------------------------------------------------------------
# color: base; wear_color: what chipped edges show at their core (bare metal, raw plastic);
# primer: the layer between paint and core, if the look is paint over metal; wear: how much edges
# chip (0-1); grime: dirt in cavities (0-1); streaks: run-down dirt on walls (0-1); mottle:
# low-frequency colour variation; pattern + grain: surface relief in the normal map (paint = orange
# peel, stipple = cast polymer, brushed = brushed metal along x, rubber = pebbled, weave = webbing,
# smooth); spec/gloss: for _smdi (0-1); wear_gloss: gloss where worn; bevel: rounded-edge radius in
# the normal map (m).
def look(color, wear_color=None, wear=0.4, grime=0.5, mottle=0.03, grain=0.15, spec=0.12, gloss=0.3,
         wear_gloss=0.5, bevel=0.0025, primer=None, pattern="paint", streaks=0.5, rust=0.0):
    return dict(color=color, wear_color=wear_color or color, wear=wear, grime=grime, mottle=mottle,
                grain=grain, spec=spec, gloss=gloss, wear_gloss=wear_gloss, bevel=bevel, primer=primer, rust=rust,
                pattern=pattern, streaks=streaks)


STEEL = srgb(150, 152, 154)
WEAR_BOOST = 1.6
PRIMER = srgb(118, 112, 96)

LOOKS = {
    # UNSC olive drab: paint over metal (chips show primer, then steel) or moulded polymer
    "olive": look(srgb(92, 97, 64), srgb(140, 138, 116), wear=0.45, grime=0.55, spec=0.1, gloss=0.28,
                  pattern="stipple", grain=0.25),
    "olive_dark": look(srgb(66, 70, 46), srgb(120, 120, 98), wear=0.45, grime=0.55, spec=0.1, gloss=0.26,
                       pattern="stipple", grain=0.25),
    "olive_green": look(srgb(62, 78, 42), STEEL, wear=0.45, grime=0.5, spec=0.22, gloss=0.44, primer=PRIMER,
                        wear_gloss=0.65, rust=0.6),
    "olive_tan": look(srgb(86, 78, 52), STEEL, wear=0.5, grime=0.6, spec=0.2, gloss=0.42, primer=PRIMER,
                      wear_gloss=0.65, rust=0.6),
    "olive_tan_dark": look(srgb(80, 74, 50), STEEL, wear=0.55, grime=0.6, spec=0.1, gloss=0.25, primer=PRIMER),
    "poly_green": look(srgb(92, 112, 56), srgb(130, 146, 100), wear=0.25, grime=0.4, spec=0.16, gloss=0.38,
                       mottle=0.03, grain=0.2, pattern="stipple"),
    "lid_pad": look(srgb(102, 94, 64), srgb(130, 122, 92), wear=0.25, grime=0.55, spec=0.05, gloss=0.15,
                    pattern="weave", grain=0.35, streaks=0.3),
    # health pack: light grey shell, darker lower half
    "shell_white": look(srgb(192, 195, 193), srgb(120, 122, 124), wear=0.35, grime=0.45, spec=0.22, gloss=0.45,
                        mottle=0.03, pattern="stipple", grain=0.12),
    "shell_grey": look(srgb(150, 153, 154), srgb(200, 202, 204), wear=0.4, grime=0.5, spec=0.2, gloss=0.42,
                       mottle=0.04, pattern="stipple", grain=0.12),
    "shell_dark": look(srgb(60, 63, 66), STEEL, wear=0.45, grime=0.5, spec=0.24, gloss=0.46, primer=srgb(96, 98, 98),
                       wear_gloss=0.65, rust=0.4),
    # Halo Infinite UNSC cases: black polymer frame, painted body panels
    "frame_black": look(srgb(36, 37, 38), srgb(92, 94, 94), wear=0.4, grime=0.45, spec=0.14, gloss=0.38,
                        pattern="stipple", grain=0.25),
    "unsc_olive": look(srgb(60, 66, 46), STEEL, wear=0.5, grime=0.55, spec=0.24, gloss=0.46, primer=PRIMER,
                       wear_gloss=0.68, rust=0.7),
    "unsc_khaki": look(srgb(98, 90, 64), STEEL, wear=0.5, grime=0.55, spec=0.24, gloss=0.46, primer=PRIMER,
                       wear_gloss=0.68, rust=0.7),
    "unsc_grey": look(srgb(76, 78, 78), STEEL, wear=0.5, grime=0.55, spec=0.26, gloss=0.48, primer=PRIMER,
                      wear_gloss=0.68, rust=0.7),
    # what is packed inside the cases
    "foam": look(srgb(44, 46, 48), srgb(60, 62, 64), wear=0.1, grime=0.5, spec=0.03, gloss=0.08, pattern="stipple",
                 grain=0.6, streaks=0.0, bevel=0.002),
    "biofoam": look(srgb(214, 214, 206), srgb(160, 160, 152), wear=0.25, grime=0.35, spec=0.3, gloss=0.55,
                    pattern="smooth", bevel=0.0015),
    "injector": look(srgb(96, 102, 74), srgb(140, 140, 120), wear=0.2, grime=0.3, spec=0.25, gloss=0.45,
                     pattern="smooth", bevel=0.001),
    "pack_olive": look(srgb(112, 106, 80), srgb(140, 132, 104), wear=0.15, grime=0.4, spec=0.12, gloss=0.35,
                       pattern="paint", grain=0.3, bevel=0.003),
    "pack_white": look(srgb(222, 220, 212), srgb(180, 178, 170), wear=0.15, grime=0.35, spec=0.15, gloss=0.4,
                       pattern="paint", grain=0.25, bevel=0.003),
    "foam_egg": look(srgb(44, 46, 48), srgb(60, 62, 64), wear=0.05, grime=0.45, spec=0.03, gloss=0.08,
                     pattern="eggcrate", grain=1.2, streaks=0.0, bevel=0.002),
    "glass_amber": look(srgb(150, 86, 30), srgb(180, 120, 60), wear=0.05, grime=0.2, spec=0.85, gloss=0.92,
                        pattern="smooth", grain=0.0, bevel=0.001),
    # EUP colours
    "hazard_yellow": look(srgb(180, 144, 34), STEEL, wear=0.55, grime=0.55, spec=0.24, gloss=0.46, primer=PRIMER,
                          wear_gloss=0.65, rust=0.6),
    "hazmat_white": look(srgb(172, 172, 162), STEEL, wear=0.4, grime=0.7, spec=0.26, gloss=0.5, primer=PRIMER,
                         wear_gloss=0.65, rust=0.5,
                         pattern="stipple", grain=0.12),
    "orange": look(srgb(196, 92, 30), srgb(220, 160, 120), wear=0.3, grime=0.4, spec=0.25, gloss=0.5,
                   pattern="stipple", grain=0.1),
    "webbing": look(srgb(70, 72, 50), srgb(96, 96, 74), wear=0.1, grime=0.45, spec=0.03, gloss=0.08,
                    pattern="weave", grain=0.6, bevel=0.0015, streaks=0.2),
    "brass": look(srgb(176, 136, 66), srgb(220, 190, 120), wear=0.3, grime=0.35, spec=0.6, gloss=0.6,
                  wear_gloss=0.75, pattern="smooth", bevel=0.0008),
    "glass": look(srgb(30, 38, 40), srgb(60, 70, 72), wear=0.05, grime=0.2, spec=0.9, gloss=0.95,
                  pattern="smooth", grain=0.0, bevel=0.0006),
    "dial": look(srgb(220, 218, 206), srgb(220, 218, 206), wear=0.0, grime=0.3, spec=0.5, gloss=0.8,
                 pattern="smooth", grain=0.0, bevel=0.0005),
    # small parts
    "dark_poly": look(srgb(40, 42, 40), srgb(90, 92, 88), wear=0.3, grime=0.3, spec=0.08, gloss=0.25,
                      pattern="stipple", grain=0.2),
    "rubber": look(srgb(30, 31, 31), srgb(52, 52, 50), wear=0.15, grime=0.3, spec=0.04, gloss=0.12,
                   grain=0.5, bevel=0.0015, pattern="rubber"),
    "latch_grey": look(srgb(146, 149, 148), srgb(196, 198, 196), wear=0.2, grime=0.4, spec=0.18, gloss=0.4,
                       mottle=0.02, grain=0.1, pattern="stipple"),
    "steel": look(srgb(96, 98, 100), srgb(180, 182, 184), wear=0.6, grime=0.4, spec=0.5, gloss=0.55, rust=0.45,
                  wear_gloss=0.75, grain=0.25, bevel=0.0012, pattern="brushed"),
    "black_metal": look(srgb(28, 29, 30), STEEL, wear=0.55, grime=0.25, spec=0.35, gloss=0.5, rust=0.5,
                        wear_gloss=0.7, grain=0.08, bevel=0.0012),
    "red": look(srgb(176, 30, 26), srgb(210, 120, 110), wear=0.2, grime=0.3, spec=0.4, gloss=0.65,
                mottle=0.02, grain=0.05, pattern="stipple"),
    "red_reflector": look(srgb(206, 36, 30), srgb(230, 120, 110), wear=0.1, grime=0.2, spec=0.7, gloss=0.85,
                          mottle=0.01, grain=0.0, bevel=0.001, pattern="smooth"),
    "green_lens": look(srgb(90, 230, 120), srgb(150, 255, 170), wear=0.0, grime=0.1, spec=0.8, gloss=0.9,
                       mottle=0.0, grain=0.0, bevel=0.0008, pattern="smooth"),
}


# --- Scene ---------------------------------------------------------------------------------------
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for kind in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = kind
                prefs.get_devices()
                if any(d.type == kind for d in prefs.devices):
                    for d in prefs.devices:
                        d.use = d.type == kind
                    scene.cycles.device = "GPU"
                    break
            except TypeError:
                continue
    except KeyError:
        pass
    scene.unit_settings.scale_length = 1.0
    import random
    random.seed(7)
    return scene


PARTS = []          # every object made, joined at the end
PROJECTORS = []     # decals: dicts made by decal()
GROUP = [""]        # the group new parts go into, see lid() and contents()
CLUSTER = [None]    # parts made inside one helper share a cluster and may overlap, see check_overlaps()
_CLUSTER_NEXT = [0]


class cluster:
    """with cluster(): ... - the parts made inside belong together (a bolt and its washer, a lens and
    its bezel) and may overlap each other."""

    def __enter__(self):
        if CLUSTER[-1] is None:
            _CLUSTER_NEXT[0] += 1
            CLUSTER.append(_CLUSTER_NEXT[0])
        else:
            CLUSTER.append(CLUSTER[-1])

    def __exit__(self, *a):
        CLUSTER.pop()


def clustered(fn):
    """Decorator: everything a helper makes is one cluster."""
    import functools

    @functools.wraps(fn)
    def wrap(*a, **k):
        with cluster():
            return fn(*a, **k)
    return wrap
SHADOW = [False]    # True while building the shadow LOD: sharp parts, no small ones, no decals
LID_AXIS = []       # two points of the lid's hinge, see lid_axis()
LATCHES = []        # two points of each latch's pivot, see latch()


def group_id(name):
    """The number a part's 'lid' attribute carries: 0 body (and contents), 1 lid, 1 + k the k-th latch."""
    if name == "lid":
        return 1
    if name.startswith("latch"):
        return 1 + int(name[5:])
    return 0


def group_names():
    """{group number: named selection} of the moving parts made so far."""
    names = {1: "lid"} if LID_AXIS else {}
    for k in range(1, len(LATCHES) + 1):
        names[1 + k] = "latch%d" % k
    return names


class lid:
    """with lid(): ... - every part made inside belongs to the lid, which the game can swing open
    about the axis given by lid_axis()."""

    def __enter__(self):
        GROUP.append("lid")

    def __exit__(self, *a):
        GROUP.pop()


class latch:
    """with latch(p0, p1): ... - the swinging part of a latch (its lever and bail), which the game turns
    about the pivot p0-p1 (Blender space) before the lid opens, so it hangs down out of the lid's way.
    The k-th latch made becomes the selection 'latch<k>' with the memory points 'latch<k>_axis'."""

    def __init__(self, p0, p1):
        LATCHES.append((tuple(p0), tuple(p1)))
        self.name = "latch%d" % len(LATCHES)

    def __enter__(self):
        GROUP.append(self.name)

    def __exit__(self, *a):
        GROUP.pop()


class contents:
    """with contents(): ... - what is packed inside: hidden in the closed lid, seen when it opens. Casts
    no shadow (it is inside) and drops out of the far LODs with the other small parts."""

    def __enter__(self):
        GROUP.append("contents")

    def __exit__(self, *a):
        GROUP.pop()


def lid_axis(p0, p1):
    """The lid's hinge line, from p0 to p1 (Blender space). The game turns the lid about it."""
    LID_AXIS[:] = [tuple(p0), tuple(p1)]


def _finish(bm, name, mat, matrix):
    import random
    bm.normal_update()
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    # one random number per part, so no two parts have quite the same shade
    attr = me.attributes.new("part_rand", "FLOAT", "POINT")
    r = random.random()
    attr.data.foreach_set("value", [r] * len(me.vertices))
    # which moving part a point belongs to (see group_id), so the p3d writer can put the lid and each
    # latch in its own selection
    lid_attr = me.attributes.new("lid", "FLOAT", "POINT")
    lid_attr.data.foreach_set("value", [float(group_id(GROUP[-1]))] * len(me.vertices))
    # which part a point belongs to, so the shadow LOD keeps every part a closed volume of its own
    comp = me.attributes.new("comp", "INT", "POINT")
    comp.data.foreach_set("value", [len(PARTS)] * len(me.vertices))
    # what is packed inside, so the far LODs can leave it out
    inner = me.attributes.new("inner", "INT", "POINT")
    inner.data.foreach_set("value", [int(GROUP[-1] == "contents")] * len(me.vertices))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world = matrix
    ob["look"] = mat
    if CLUSTER[-1] is None:
        _CLUSTER_NEXT[0] += 1
        ob["cluster"] = _CLUSTER_NEXT[0]
    else:
        ob["cluster"] = CLUSTER[-1]
    PARTS.append(ob)
    return ob


def _matrix(loc=(0, 0, 0), rot=(0, 0, 0)):
    return Matrix.Translation(Vector(loc)) @ Matrix.LocRotScale(None, _euler(rot), None)


def _euler(rot):
    from mathutils import Euler
    return Euler(tuple(math.radians(a) for a in rot), "XYZ")


def _bevel(bm, width, segs, edges=None):
    if width <= 0:
        return
    bmesh.ops.bevel(bm, geom=list(edges if edges is not None else bm.edges), offset=width, offset_type="OFFSET",
                    segments=segs, profile=0.5, affect="EDGES", clamp_overlap=True)


def inset(profile, d):
    """A convex outline (counter-clockwise) moved inwards by d: each edge shifted along its inner
    normal, corners where neighbouring shifted edges meet."""
    n = len(profile)
    lines = []
    for i in range(n):
        x0, y0 = profile[i]
        x1, y1 = profile[(i + 1) % n]
        ex, ey = x1 - x0, y1 - y0
        ln = math.hypot(ex, ey) or 1.0
        nx, ny = -ey / ln, ex / ln          # left normal = inwards for a counter-clockwise outline
        lines.append(((x0 + nx * d, y0 + ny * d), (ex, ey)))
    out = []
    for i in range(n):
        (p0, d0), (p1, d1) = lines[i - 1], lines[i]
        den = d0[0] * d1[1] - d0[1] * d1[0]
        if abs(den) < 1e-12:
            out.append(p1)
            continue
        t = ((p1[0] - p0[0]) * d1[1] - (p1[1] - p0[1]) * d1[0]) / den
        out.append((p0[0] + d0[0] * t, p0[1] + d0[1] * t))
    return out


def prism(profile, depth, look="olive", loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.002, segs=2, name="part",
          taper=0.0, matrix=None, hollow=0.0):
    """A 2D outline (local x, y; counter-clockwise) extruded along local z from 0 to depth, edges
    bevelled. taper shrinks the top outline by that much (a draft/chamfered top)."""
    if SHADOW[0] and GROUP[-1] == "contents":
        return None
    if SHADOW[0]:
        # The shadow LOD wants few, closed, sharp volumes: leave out what is too small to cast a
        # shadow that matters, thin out round outlines, drop the bevels.
        xs = [p[0] for p in profile]
        ys = [p[1] for p in profile]
        dims = (max(xs) - min(xs), max(ys) - min(ys), depth)
        if min(dims) < 0.005 or max(dims) < 0.02:
            return None
        if len(profile) > 12:
            profile = profile[::-(-len(profile) // 12)]
        bevel = 0
    if hollow > 0.0:
        # a wall of thickness `hollow` round the outline, open at both ends of the extrusion: a closed
        # ring solid (outer walls, inner walls, the two rims)
        bm = bmesh.new()
        inner = inset(profile, hollow)
        n = len(profile)
        ob_ = [bm.verts.new((x, y, 0.0)) for x, y in profile]
        ot = [bm.verts.new((x, y, depth)) for x, y in profile]
        ib = [bm.verts.new((x, y, 0.0)) for x, y in inner]
        it = [bm.verts.new((x, y, depth)) for x, y in inner]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((ob_[i], ob_[j], ot[j], ot[i]))
            bm.faces.new((it[i], it[j], ib[j], ib[i]))
            bm.faces.new((ot[i], ot[j], it[j], it[i]))
            bm.faces.new((ib[i], ib[j], ob_[j], ob_[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        _bevel(bm, min(bevel, hollow * 0.3), segs)
        ob = _finish(bm, name, look, matrix if matrix is not None else _matrix(loc, rot))
        ob["hollow"] = 1   # its box says nothing about what is inside it: the overlap check leaves it out
        return ob
    bm = bmesh.new()
    n = len(profile)
    cx = sum(p[0] for p in profile) / n
    cy = sum(p[1] for p in profile) / n
    bot = [bm.verts.new((x, y, 0.0)) for x, y in profile]
    top = []
    for x, y in profile:
        if taper:
            dx, dy = x - cx, y - cy
            ln = math.hypot(dx, dy) or 1.0
            k = max(0.0, (ln - taper) / ln)
            x, y = cx + dx * k, cy + dy * k
        top.append(bm.verts.new((x, y, depth)))
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    _bevel(bm, bevel, segs)
    return _finish(bm, name, look, matrix if matrix is not None else _matrix(loc, rot))


def rect(w, h, cut=0.0, cuts=(1, 1, 1, 1)):
    """Rectangle outline centred on 0, corners cut at 45 degrees by `cut` (order: bl, br, tr, tl)."""
    x, y = w / 2, h / 2
    c = [cut * k for k in cuts]
    pts = []
    for (px, py, cc, a, b) in ((-x, -y, c[0], (0, 1), (1, 0)), (x, -y, c[1], (-1, 0), (0, 1)),
                               (x, y, c[2], (0, -1), (-1, 0)), (-x, y, c[3], (1, 0), (0, -1))):
        if cc > 0:
            pts.append((px + a[0] * cc, py + a[1] * cc))
            pts.append((px + b[0] * cc, py + b[1] * cc))
        else:
            pts.append((px, py))
    return pts


def rrect(w, h, r, n=4):
    """Rounded rectangle outline, n segments per corner."""
    x, y = w / 2 - r, h / 2 - r
    pts = []
    for (cx, cy, a0) in ((x, -y, -90), (x, y, 0), (-x, y, 90), (-x, -y, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def circle(r, n=20):
    return [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def box(size, center, look="olive", cut=0.0, cuts=(1, 1, 1, 1), bevel=0.002, segs=2, name="box", axis="z",
        taper=0.0, hollow=0.0):
    """Box of size (sx, sy, sz) centred at center. The outline (with optional cut corners) lies across
    `axis` and is extruded along it: axis z cuts the corners seen from above, y seen from the front,
    x seen from the side."""
    sx, sy, sz = size
    cx, cy, cz = center
    if axis == "z":
        return prism(rect(sx, sy, cut, cuts), sz, look, (cx, cy, cz - sz / 2), (0, 0, 0), bevel, segs, name,
                     taper, hollow=hollow)
    if axis == "y":
        # outline in x/z, extruded towards -y (the front): rotate local z onto -y
        return prism(rect(sx, sz, cut, cuts), sy, look, (cx, cy + sy / 2, cz), (90, 0, 0), bevel, segs, name,
                     taper, hollow=hollow)
    # axis x: outline in y/z, extruded along +x
    return prism(rect(sy, sz, cut, cuts), sx, look, (cx - sx / 2, cy, cz), (90, 0, 90), bevel, segs, name,
                 taper, hollow=hollow)


def cyl(r, length, center, look="steel", axis="z", n=20, bevel=0.001, segs=1, name="cyl"):
    cx, cy, cz = center
    rot = {"z": (0, 0, 0), "y": (90, 0, 0), "x": (0, 90, 0)}[axis]
    off = {"z": (0, 0, -length / 2), "y": (0, length / 2, 0), "x": (-length / 2, 0, 0)}[axis]
    return prism(circle(r, n), length, look, (cx + off[0], cy + off[1], cz + off[2]), rot, bevel, segs, name)


# --- Details, placed on a surface -------------------------------------------------------------------
def frame(center, normal, up=(0, 0, 1)):
    """A placement on a surface: local z along normal (out of the surface), local y towards up."""
    z = Vector(normal).normalized()
    u = Vector(up)
    if abs(u.normalized().dot(z)) > 0.99:
        u = Vector((0, 1, 0)) if abs(z.y) < 0.9 else Vector((1, 0, 0))
    y = (u - z * u.dot(z)).normalized()
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = Vector(center)
    return m


def lbox(F, size, at=(0, 0, 0), look="steel", cut=0.0, cuts=(1, 1, 1, 1), bevel=0.001, segs=1, taper=0.0):
    """Box in a frame: size (along x, along y, height out of the surface), `at` is the centre of its
    foot (z = 0 sits on the surface)."""
    sx, sy, sz = size
    m = F @ Matrix.Translation(Vector(at))
    return prism(rect(sx, sy, cut, cuts), sz, look, bevel=bevel, segs=segs, taper=taper, matrix=m)


def lcyl(F, r, h, at=(0, 0, 0), look="steel", n=16, bevel=0.0006, segs=1, axis="z"):
    """Cylinder in a frame. axis z stands out of the surface (foot at `at`); x lies along the surface,
    centred on `at`."""
    m = F @ Matrix.Translation(Vector(at))
    if axis == "x":
        m = m @ Matrix.Rotation(math.radians(90), 4, "Y") @ Matrix.Translation((0, 0, -h / 2))
    return prism(circle(r, n), h, look, bevel=bevel, segs=segs, matrix=m)


@clustered
def bolt(center, normal, r=0.0035, look="steel", up=(0, 0, 1)):
    """Hex-head bolt on a washer."""
    F = frame(center, normal, up)
    lcyl(F, r * 1.45, r * 0.28, look=look, n=16, bevel=r * 0.08)
    prism(circle(r, 6), r * 0.75, look, bevel=r * 0.12, segs=1,
          matrix=F @ Matrix.Translation((0, 0, r * 0.26)))


@clustered
def screw(center, normal, r=0.0028, look="black_metal", up=(0, 0, 1)):
    """Flush pan-head screw with a slot."""
    F = frame(center, normal, up)
    lcyl(F, r, r * 0.45, look=look, n=14, bevel=r * 0.3, segs=2)
    lbox(F, (r * 1.5, r * 0.28, r * 0.14), (0, 0, r * 0.42), look, bevel=0)


def rivet(center, normal, r=0.0022, look="steel"):
    F = frame(center, normal)
    lcyl(F, r, r * 0.6, look=look, n=10, bevel=r * 0.5, segs=2)


def rivets(p0, p1, normal, n, r=0.0022, look="steel"):
    for k in range(n):
        t = k / (n - 1) if n > 1 else 0.5
        rivet(tuple(a + (b - a) * t for a, b in zip(p0, p1)), normal, r, look)


@clustered
def rod(p0, p1, r, look="steel", n=8):
    """A straight round rod from p0 to p1 (a wire, a bail)."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    q = d.normalized().to_track_quat("Z", "Y")
    m = Matrix.Translation(a) @ q.to_matrix().to_4x4()
    return prism(circle(r, n), d.length, look, bevel=0, segs=1, matrix=m)


def bail_latch(center, normal, up=(0, 0, 1), w=0.03, below=0.016, body_off=0.0, lid_off=0.0, keeper=None,
               look="black_metal", tab=None):
    """A draw latch over a lid's seam, built the way it works. center is on the seam, in the plane the
    latch is measured from (local z = 0, out along normal); up points from the body to the lid.

    On the body, `below` under the seam: a bracket with two lugs and the pin. On the pin: the lever,
    and from its top a wire bail whose cross bar hooks over the keeper on the lid (keeper: its box
    (y0, y1, z0, z1) in the latch's frame, default a block on the lid's face at lid_off). Body face
    at body_off, lid face at lid_off. tab: look of a pull tab on the lever's top.

    The lever and bail are a latch() of their own: the game swings them out about the pin and lets
    them hang down before the lid opens (model.cfg), so nothing stands over the opening and the lid
    is free to go up. Returns the pin's two ends."""
    F = frame(center, normal, up)
    out = max(body_off, lid_off) + 0.008
    yp = -below
    top = -0.003
    ky0, ky1, kz0, kz1 = keeper or (0.004, 0.011, lid_off, lid_off + 0.009)
    yc, zc = ky1 + 0.0014, kz1 - 0.0022
    kw = w * 0.5
    xw = kw / 2 + 0.003

    def at(x, y, z):
        return F @ Vector((x, y, z))

    with cluster():
        # bracket: a plate screwed to the body, two lugs holding the pin
        lbox(F, (w, 0.014, 0.003), (0, yp - 0.0035, body_off), look, cut=0.002, bevel=0.0008)
        for sx in (-1, 1):
            lbox(F, (0.0045, 0.009, out - body_off + 0.0035), (sx * (w / 2 - 0.00225), yp, body_off), look,
                 bevel=0.0008)
            screw(at(sx * w * 0.24, yp - 0.0075, body_off + 0.003), normal, r=0.0016, up=up)
        lcyl(F, 0.0015, w + 0.002, (0, yp, out), "steel", n=10, axis="x")
        p0, p1 = at(-w / 2, yp, out), at(w / 2, yp, out)
        with latch(p0, p1):
            # the lever on the pin, up to just under the seam
            lcyl(F, 0.003, w - 0.0105, (0, yp, out), look, n=12, axis="x", bevel=0.0005)
            lbox(F, (w - 0.0105, top - yp, 0.003), (0, (yp + top) / 2, out - 0.0015), look, cut=0.002,
                 bevel=0.0008)
            if tab:
                lbox(F, (w * 0.62, 0.005, 0.0065), (0, top - 0.0025, out + 0.0012), tab, cut=0.0015,
                     bevel=0.0008)
            # the bail: two wires from the lever's top to the cross bar over the keeper
            for sx in (-1, 1):
                rod(at(sx * xw, top - 0.002, out), at(sx * xw, yc, zc), 0.0011)
            lcyl(F, 0.0014, 2 * xw + 0.0022, (0, yc, zc), "steel", n=10, axis="x")
        with lid():
            # the keeper on the lid, the bail's cross bar pulled down on its top
            lbox(F, (kw, ky1 - ky0, kz1 - kz0), (0, (ky0 + ky1) / 2, kz0), look, cut=0.0015, bevel=0.0008)
    return p0, p1


@clustered
def vents(center, normal, up, n, w, gap, fin=0.004, depth=0.003, look="dark_poly"):
    """A row of n louvre fins, w long, stacked along up with `gap` between, in a frame."""
    F = frame(center, normal, up)
    hgt = n * gap
    lbox(F, (w + 0.008, hgt + 0.006, 0.0015), (0, 0, 0), look, bevel=0.0006)
    for k in range(n):
        y = -hgt / 2 + gap * (k + 0.5)
        lbox(F, (w, fin, depth), (0, y, 0.0012), look, bevel=0.0007, taper=0.0008)


@clustered
def hinge(p0, p1, r=0.005, knuckles=5, look="black_metal"):
    """Piano-style hinge: knuckles along p0-p1 with small gaps, and a pin showing at the ends. Every
    other knuckle belongs to the lid and turns with it - so lid_axis() must be this very line, the pin."""
    a, b = Vector(p0), Vector(p1)
    axis = (b - a)
    ln = axis.length
    d = axis.normalized()
    q = d.to_track_quat("Z", "Y")
    seg = ln / knuckles
    for k in range(knuckles):
        c = a + d * (seg * (k + 0.5))
        m = Matrix.Translation(c) @ q.to_matrix().to_4x4() @ Matrix.Translation((0, 0, -seg * 0.46))
        if k % 2:
            with lid():
                prism(circle(r, 14), seg * 0.92, look, bevel=r * 0.15, segs=1, matrix=m)
        else:
            prism(circle(r, 14), seg * 0.92, look, bevel=r * 0.15, segs=1, matrix=m)
    for e, s_ in ((a, -1), (b, 1)):
        m = Matrix.Translation(e + d * s_ * 0.001) @ q.to_matrix().to_4x4() @ Matrix.Translation((0, 0, -0.0015))
        prism(circle(r * 0.45, 10), 0.003, "steel", bevel=0.0003, segs=1, matrix=m)


@clustered
def plate(center, normal, up, w, h, look="steel", image=None, rivet_look="steel"):
    """Riveted data plate, optionally carrying a decal."""
    F = frame(center, normal, up)
    lbox(F, (w, h, 0.0012), (0, 0, 0), look, cut=min(w, h) * 0.08, bevel=0.0004)
    for sx in (-1, 1):
        for sy in (-1, 1):
            lcyl(F, 0.0014, 0.0008, (sx * (w / 2 - 0.004), sy * (h / 2 - 0.004), 0.0012), rivet_look, n=8,
                 bevel=0.0005)
    if image:
        nz = Vector(normal).normalized()
        decal(image, tuple(Vector(center) + nz * 0.0012), tuple(nz), up, w * 0.7, depth=0.0015)


def decal(image, center, normal, up, width, height=None, depth=0.01, looks=None, check=True):
    if SHADOW[0]:
        return
    """Project a decal PNG (out/decals/<image>.png) onto the surfaces facing `normal` within `depth`
    of `center`. width/height in metres; height follows the image's aspect if left out."""
    path = os.path.join(DECALS, image + ".png")
    img = bpy.data.images.load(path, check_existing=True)
    if height is None:
        height = width * img.size[1] / img.size[0]
    PROJECTORS.append(dict(img=img, center=Vector(center), normal=Vector(normal).normalized(),
                           up=Vector(up).normalized(), w=width, h=height, depth=depth, looks=looks, check=check))


# --- Overlap check -----------------------------------------------------------------------------------
def check_overlaps(small=0.06, slack=0.0005):
    """Small parts (largest size under `small`) of different clusters whose boxes run into each other by
    more than `slack` in every direction - a lens sunk into a reflector, a screw through a plate. Run
    before assemble(). Boxes are axis-aligned, so a turned part may be reported though it only comes
    close; look at those."""
    boxes = []
    for ob in PARTS:
        if ob.get("hollow"):
            continue
        pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        lo = [min(p[i] for p in pts) for i in range(3)]
        hi = [max(p[i] for p in pts) for i in range(3)]
        size = max(hi[i] - lo[i] for i in range(3))
        boxes.append((ob, lo, hi, size))
    problems = []
    for i, (a, alo, ahi, asz) in enumerate(boxes):
        if asz >= small:
            continue
        for b, blo, bhi, bsz in boxes[i + 1:]:
            if bsz >= small or a["cluster"] == b["cluster"]:
                continue
            if all(min(ahi[k], bhi[k]) - max(alo[k], blo[k]) > slack for k in range(3)):
                problems.append("%s (%s) runs into %s (%s) at %s" % (
                    a.name, a["look"], b.name, b["look"],
                    tuple(round((max(alo[k], blo[k]) + min(ahi[k], bhi[k])) / 2, 3) for k in range(3))))
    return problems


# --- Lid check -------------------------------------------------------------------------------------
def check_lid_attached(touch=0.0015):
    """Every part of the lid must hang on the lid: connected, box to box, to its largest part. A lid
    part that is not would swing up with it and hang in the air (the AFAK's base reflectors did)."""
    lid_parts = [ob for ob in PARTS if ob.data.attributes.get("lid")
                 and abs(ob.data.attributes["lid"].data[0].value - 1.0) < 0.1]
    if not lid_parts:
        return []

    def bounds(ob):
        pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
        return ([min(p[i] for p in pts) - touch for i in range(3)], [max(p[i] for p in pts) + touch for i in range(3)])

    bb = {ob.name: bounds(ob) for ob in lid_parts}
    size = {n: max(hi[i] - lo[i] for i in range(3)) for n, (lo, hi) in bb.items()}
    root = max(size, key=size.get)
    seen, todo = {root}, [root]
    while todo:
        a = todo.pop()
        alo, ahi = bb[a]
        for b, (blo, bhi) in bb.items():
            if b not in seen and all(min(ahi[k], bhi[k]) >= max(alo[k], blo[k]) for k in range(3)):
                seen.add(b)
                todo.append(b)
    return ["%s (%s) is in the lid but does not touch it" % (ob.name, ob["look"]) for ob in lid_parts
            if ob.name not in seen]


# --- Decal check -------------------------------------------------------------------------------------
def check_decals(ob, margin=0.004, grid=9):
    """Every decal has to sit on one flat stretch of surface, with `margin` metres of it free all round:
    no edge, no rounding, no other part in front, no step. Casts rays over the decal's rectangle grown by
    the margin and reports each decal that breaks this. Returns the list of problems."""
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get()
    tree = BVHTree.FromObject(ob, dg)
    problems = []
    for k, p in enumerate(PROJECTORS):
        if not p.get("check", True):
            continue
        z = p["normal"]
        y = (p["up"] - z * p["up"].dot(z)).normalized()
        x = y.cross(z)
        hw, hh = p["w"] / 2 + margin, p["h"] / 2 + margin
        bad = []
        for i in range(grid):
            for j in range(grid):
                u = -hw + 2 * hw * i / (grid - 1)
                v = -hh + 2 * hh * j / (grid - 1)
                origin = p["center"] + x * u + y * v + z * 0.08
                loc, nrm, idx, dist = tree.ray_cast(origin, -z, 0.2)
                where = "%+.0f%%,%+.0f%%" % (100 * u / hw, 100 * v / hh)
                if loc is None:
                    bad.append(("nothing", where))
                elif nrm.dot(z) < 0.985:
                    bad.append(("edge", where))
                elif abs(dist - 0.08) > 0.0012:
                    bad.append(("step %.1fmm" % ((0.08 - dist) * 1000), where))
        if bad:
            kinds = sorted({b[0].split(" ")[0] for b in bad})
            problems.append("%s at %s: %d/%d points off (%s), e.g. %s" % (
                os.path.basename(p["img"].filepath).replace(".png", ""), tuple(round(c, 3) for c in p["center"]),
                len(bad), grid * grid, ",".join(kinds), "; ".join("%s %s" % b for b in bad[:4])))
    return problems


# --- Materials for baking -------------------------------------------------------------------------
def _projector_empty(p, k):
    z = p["normal"]
    y = (p["up"] - z * p["up"].dot(z)).normalized()
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = p["center"]
    e = bpy.data.objects.new("decal_%d" % k, None)
    bpy.context.scene.collection.objects.link(e)
    e.matrix_world = m
    return e


def _build_material(name, lk, projectors, bake_img):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    N = nt.nodes
    L = nt.links
    for n in list(N):
        N.remove(n)

    def node(t, **kw):
        n = N.new(t)
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    def math_(op, a, b=None, clamp=False):
        n = node("ShaderNodeMath", operation=op, use_clamp=clamp)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    def mix(a, b, fac):
        n = node("ShaderNodeMix", data_type="RGBA", blend_type="MIX", clamp_factor=True)
        for sock, v in ((n.inputs[6], a), (n.inputs[7], b), (n.inputs[0], fac)):
            if isinstance(v, (tuple, list)):
                sock.default_value = v
            elif isinstance(v, (int, float)):
                sock.default_value = v
            else:
                L.new(v, sock)
        return n.outputs[2]

    def noise(scale, detail=6.0, rough=0.6, w=None):
        tc = node("ShaderNodeTexCoord")
        n = node("ShaderNodeTexNoise", noise_dimensions="3D")
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough
        L.new(tc.outputs["Object"], n.inputs["Vector"])
        return n.outputs["Fac"]

    def ramp(src, lo, hi):
        n = node("ShaderNodeMapRange", clamp=True)
        n.inputs["From Min"].default_value = lo
        n.inputs["From Max"].default_value = hi
        L.new(src, n.inputs["Value"])
        return n.outputs["Result"]

    geo = node("ShaderNodeNewGeometry")

    # edge mask: where a wide bevel normal turns away from the true normal
    bev = node("ShaderNodeBevel", samples=16)
    bev.inputs["Radius"].default_value = 0.006
    dot = node("ShaderNodeVectorMath", operation="DOT_PRODUCT")
    L.new(bev.outputs["Normal"], dot.inputs[0])
    L.new(geo.outputs["Normal"], dot.inputs[1])
    edge = ramp(math_("SUBTRACT", 1.0, dot.outputs["Value"]), 0.004, 0.07)
    # How worn everything is: field kit that has been carried for a while. Scales every look's wear.
    W = min(1.0, lk["wear"] * WEAR_BOOST)
    # chips: edges broken up by noise, a few big bites among the small ones
    chip_noise = noise(34.0, 8.0, 0.7)
    chips = ramp(math_("MULTIPLY", edge, ramp(chip_noise, 0.47, 0.62)), 0.12, 0.38)
    bites = math_("MULTIPLY", ramp(edge, 0.0, 0.3), ramp(noise(9.0, 3.0, 0.5), 0.64, 0.68))
    chips = math_("MAXIMUM", chips, bites)
    # knocks: small chips away from the edges, where something hit the flat
    knocks = math_("MULTIPLY", ramp(noise(110.0, 2.0, 0.5), 0.72, 0.77), ramp(noise(4.0, 2.0), 0.5, 0.62))
    wear_mask = math_("MULTIPLY", math_("MAXIMUM", chips, knocks), W, clamp=True)

    # scratches: straight thin lines in a few directions, broken into short random runs - a band
    # texture gives the lines, a noise stretched along them picks the few that show
    lines = None
    for rot, sc, dens, seed in ((0.5, 70.0, 0.66, 0.0), (-0.8, 90.0, 0.68, 3.1), (1.35, 55.0, 0.7, 7.7),
                                (2.2, 110.0, 0.7, 12.4), (-1.9, 80.0, 0.72, 5.3)):
        tcx = node("ShaderNodeTexCoord")
        mpx = node("ShaderNodeMapping")
        mpx.inputs["Location"].default_value = (seed, seed * 0.7, seed * 1.3)
        mpx.inputs["Rotation"].default_value = (0.3 * rot, 0.2 * rot, rot)
        L.new(tcx.outputs["Object"], mpx.inputs["Vector"])
        band = node("ShaderNodeTexWave", wave_type="BANDS", bands_direction="X", wave_profile="SIN")
        band.inputs["Scale"].default_value = sc
        band.inputs["Distortion"].default_value = 0.6
        band.inputs["Detail"].default_value = 1.0
        L.new(mpx.outputs["Vector"], band.inputs["Vector"])
        line = ramp(band.outputs["Fac"], 0.975, 0.997)
        # the mask: long along the line (y, z of the mapped space), short across it (x)
        mk = node("ShaderNodeMapping")
        mk.inputs["Scale"].default_value = (sc * 0.5, 4.0, 4.0)
        L.new(mpx.outputs["Vector"], mk.inputs["Vector"])
        nz = node("ShaderNodeTexNoise", noise_dimensions="3D")
        nz.inputs["Scale"].default_value = 1.0
        nz.inputs["Detail"].default_value = 2.0
        L.new(mk.outputs["Vector"], nz.inputs["Vector"])
        line = math_("MULTIPLY", line, ramp(nz.outputs["Fac"], dens, dens + 0.05))
        lines = line if lines is None else math_("MAXIMUM", lines, line)
    scr = node("ShaderNodeTexWave", wave_type="BANDS", bands_direction="DIAGONAL")
    scr.inputs["Scale"].default_value = 140.0
    scr.inputs["Distortion"].default_value = 18.0
    scr.inputs["Detail"].default_value = 4.0
    tc = node("ShaderNodeTexCoord")
    L.new(tc.outputs["Object"], scr.inputs["Vector"])
    hair = math_("MULTIPLY", ramp(scr.outputs["Fac"], 0.94, 0.99), ramp(noise(6.0), 0.55, 0.7))
    scratch = math_("MULTIPLY", math_("MAXIMUM", lines, math_("MULTIPLY", hair, 0.7)), W * 1.2, clamp=True)
    wear_mask = math_("MAXIMUM", wear_mask, math_("MULTIPLY", scratch, 0.75), clamp=True)
    # scuffs: dull, slightly lighter patches where things rub, anywhere on the surface
    scuff = math_("MULTIPLY", ramp(noise(14.0, 6.0, 0.7), 0.52, 0.72), W * 0.45, clamp=True)

    # cavity grime from ambient occlusion
    ao = node("ShaderNodeAmbientOcclusion", samples=16, only_local=True)
    ao.inputs["Distance"].default_value = 0.03
    cavity = math_("MULTIPLY", ramp(ao.outputs["AO"], 0.9, 0.3), lk["grime"] * 0.6, clamp=True)
    # contact shadow: tight occlusion where parts meet
    ao2 = node("ShaderNodeAmbientOcclusion", samples=16, only_local=True)
    ao2.inputs["Distance"].default_value = 0.006
    contact = math_("MULTIPLY", ramp(ao2.outputs["AO"], 0.95, 0.4), 0.55, clamp=True)
    # dust: settles on upward faces and low on the sides
    up = node("ShaderNodeSeparateXYZ")
    L.new(geo.outputs["Normal"], up.inputs[0])
    dust = math_("MULTIPLY", ramp(up.outputs["Z"], 0.4, 0.95), ramp(noise(9.0, 5.0, 0.65), 0.45, 0.8))
    dust = math_("MULTIPLY", dust, 0.3 * lk["grime"], clamp=True)
    # run-down streaks on walls: noise stretched along z
    tcs = node("ShaderNodeTexCoord")
    mp = node("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (70.0, 70.0, 4.0)
    L.new(tcs.outputs["Object"], mp.inputs["Vector"])
    sn = node("ShaderNodeTexNoise", noise_dimensions="3D")
    sn.inputs["Scale"].default_value = 1.0
    sn.inputs["Detail"].default_value = 3.0
    L.new(mp.outputs["Vector"], sn.inputs["Vector"])
    wall = ramp(math_("ABSOLUTE", up.outputs["Z"]), 0.6, 0.2)
    streak = math_("MULTIPLY", math_("MULTIPLY", ramp(sn.outputs["Fac"], 0.52, 0.7), wall),
                   lk["streaks"] * lk["grime"] * 0.55, clamp=True)

    # colour
    base = lk["color"]
    mottle = math_("MULTIPLY", math_("SUBTRACT", noise(3.5, 4.0, 0.5), 0.5), lk["mottle"] * 2.0)
    bright = node("ShaderNodeMix", data_type="RGBA", blend_type="ADD", clamp_factor=True)
    bright.inputs[0].default_value = 1.0
    bright.inputs[6].default_value = base
    comb = node("ShaderNodeCombineXYZ")
    for s in ("X", "Y", "Z"):
        L.new(mottle, comb.inputs[s])
    L.new(comb.outputs[0], bright.inputs[7])
    col = bright.outputs[2]
    # every part a touch different, as real parts from different batches are
    pr = node("ShaderNodeAttribute", attribute_type="GEOMETRY", attribute_name="part_rand")
    shade = node("ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY", clamp_factor=True)
    shade.inputs[0].default_value = 1.0
    L.new(col, shade.inputs[6])
    sc = node("ShaderNodeCombineXYZ")
    for s_, k_ in (("X", 0.07), ("Y", 0.06), ("Z", 0.08)):
        L.new(math_("ADD", 1.0, math_("MULTIPLY", math_("SUBTRACT", pr.outputs["Fac"], 0.5), k_)), sc.inputs[s_])
    L.new(sc.outputs[0], shade.inputs[7])
    col = shade.outputs[2]
    # sun fading on top faces, a little lighter
    col = mix(col, tuple(min(1.0, c * 1.1) for c in base[:3]) + (1.0,), math_("MULTIPLY", ramp(up.outputs["Z"], 0.5, 1.0), 0.25))

    # decals sit under the wear and grime, like real paint
    spec_decal = None
    for k, p in projectors:
        tcd = node("ShaderNodeTexCoord", object=p["empty"])
        sep = node("ShaderNodeSeparateXYZ")
        L.new(tcd.outputs["Object"], sep.inputs[0])
        uvc = node("ShaderNodeCombineXYZ")
        L.new(math_("ADD", math_("DIVIDE", sep.outputs["X"], p["w"]), 0.5), uvc.inputs["X"])
        L.new(math_("ADD", math_("DIVIDE", sep.outputs["Y"], p["h"]), 0.5), uvc.inputs["Y"])
        tex = node("ShaderNodeTexImage", image=p["img"], extension="CLIP", interpolation="Cubic")
        L.new(uvc.outputs[0], tex.inputs["Vector"])
        facing = node("ShaderNodeVectorMath", operation="DOT_PRODUCT")
        L.new(geo.outputs["Normal"], facing.inputs[0])
        facing.inputs[1].default_value = tuple(p["normal"])
        near = ramp(math_("ABSOLUTE", sep.outputs["Z"]), p["depth"], p["depth"] * 0.6)
        a = math_("MULTIPLY", math_("MULTIPLY", tex.outputs["Alpha"], ramp(facing.outputs["Value"], 0.55, 0.8)),
                  near)
        col = mix(col, tex.outputs["Color"], a)
        spec_decal = a if spec_decal is None else math_("MAXIMUM", spec_decal, a)

    if lk["primer"] is not None:
        # paint chips to primer, deeper chips to bare metal
        col = mix(col, lk["primer"], wear_mask)
        col = mix(col, lk["wear_color"], ramp(wear_mask, 0.55, 0.85))
    else:
        col = mix(col, lk["wear_color"], wear_mask)
    rust = None
    if lk["rust"] > 0:
        # rust where the paint is gone and in the seams that hold water, in two browns
        rust_chip = math_("MULTIPLY", wear_mask, ramp(noise(30.0, 6.0, 0.65), 0.25, 0.55))
        rust_seam = math_("MULTIPLY", cavity, ramp(noise(7.0, 4.0, 0.6), 0.5, 0.7))
        rust = math_("MULTIPLY", math_("MAXIMUM", rust_chip, rust_seam), lk["rust"] * 1.7, clamp=True)
        rust_col = mix(srgb(118, 58, 24), srgb(62, 34, 20), ramp(noise(60.0, 4.0, 0.6), 0.3, 0.7))
        col = mix(col, rust_col, rust)
    col = mix(col, tuple(min(1.0, c * 1.25 + 0.02) for c in lk["color"][:3]) + (1.0,), scuff)
    grime_col = tuple(c * 0.35 for c in lk["color"][:3]) + (1.0,)
    col = mix(col, grime_col, cavity)
    col = mix(col, tuple(c * 0.25 for c in lk["color"][:3]) + (1.0,), contact)
    col = mix(col, srgb(74, 66, 50), streak)
    if rust is not None:
        # rust runs down from the damage with the rain
        col = mix(col, srgb(96, 52, 26), math_("MULTIPLY", streak, lk["rust"] * 0.9, clamp=True))
    col = mix(col, srgb(150, 138, 110), dust)

    emit_co = node("ShaderNodeEmission")
    L.new(col, emit_co.inputs["Color"])

    # smdi: R 1, G specular, B gloss
    spec = math_("ADD", lk["spec"], math_("MULTIPLY", wear_mask, max(0.0, lk["spec"] * 1.5 - lk["spec"])))
    gloss = math_("ADD", lk["gloss"], math_("MULTIPLY", wear_mask, lk["wear_gloss"] - lk["gloss"]))
    gloss = math_("SUBTRACT", gloss, math_("MULTIPLY", math_("ADD", math_("ADD", cavity, dust), math_("ADD", streak, scuff)),
                                           0.25), clamp=True)
    if rust is not None:   # rust is dull
        gloss = math_("SUBTRACT", gloss, math_("MULTIPLY", rust, 0.45), clamp=True)
    if spec_decal is not None:  # paint is a touch glossier than the surface under it
        gloss = math_("ADD", gloss, math_("MULTIPLY", spec_decal, 0.05), clamp=True)
    comb = node("ShaderNodeCombineXYZ")
    comb.inputs["X"].default_value = 1.0
    L.new(spec, comb.inputs["Y"])
    L.new(gloss, comb.inputs["Z"])
    emit_sm = node("ShaderNodeEmission")
    L.new(comb.outputs[0], emit_sm.inputs["Color"])

    # normals: rounded edges plus surface grain
    nb = node("ShaderNodeBevel", samples=16)
    nb.inputs["Radius"].default_value = lk["bevel"]
    # dents: a slow wave over the panels, more on worn kit
    dent = node("ShaderNodeBump")
    dent.inputs["Strength"].default_value = 0.25 * W
    dent.inputs["Distance"].default_value = 0.002
    L.new(ramp(noise(6.0, 3.0, 0.55), 0.35, 0.75), dent.inputs["Height"])
    L.new(nb.outputs["Normal"], dent.inputs["Normal"])
    # scratches and chips cut into the surface
    cut = node("ShaderNodeBump", invert=True)
    cut.inputs["Strength"].default_value = 0.6
    cut.inputs["Distance"].default_value = 0.0003
    L.new(math_("MAXIMUM", scratch, math_("MULTIPLY", wear_mask, 0.6)), cut.inputs["Height"])
    L.new(dent.outputs["Normal"], cut.inputs["Normal"])
    bump = node("ShaderNodeBump")
    bump.inputs["Strength"].default_value = lk["grain"]
    bump.inputs["Distance"].default_value = 0.0004
    L.new(_pattern(node, L, noise, math_, lk["pattern"]), bump.inputs["Height"])
    L.new(cut.outputs["Normal"], bump.inputs["Normal"])
    bsdf = node("ShaderNodeBsdfPrincipled")
    L.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    out = node("ShaderNodeOutputMaterial")
    img = node("ShaderNodeTexImage", image=bake_img)
    N.active = img
    mat["emit_co"] = emit_co.name
    mat["emit_sm"] = emit_sm.name
    mat["bsdf"] = bsdf.name
    return mat


def _pattern(node, L, noise, math_, kind):
    """Height for the surface relief of a look."""
    tc = node("ShaderNodeTexCoord")
    if kind == "stipple":
        v = node("ShaderNodeTexVoronoi", feature="F1")
        v.inputs["Scale"].default_value = 1400.0
        L.new(tc.outputs["Object"], v.inputs["Vector"])
        return math_("ADD", math_("MULTIPLY", v.outputs["Distance"], 0.7), math_("MULTIPLY", noise(300.0, 2.0), 0.3))
    if kind == "rubber":
        v = node("ShaderNodeTexVoronoi", feature="F1")
        v.inputs["Scale"].default_value = 500.0
        L.new(tc.outputs["Object"], v.inputs["Vector"])
        return math_("SUBTRACT", 1.0, v.outputs["Distance"])
    if kind == "brushed":
        mp = node("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (8.0, 2500.0, 2500.0)
        L.new(tc.outputs["Object"], mp.inputs["Vector"])
        n = node("ShaderNodeTexNoise", noise_dimensions="3D")
        n.inputs["Scale"].default_value = 1.0
        n.inputs["Detail"].default_value = 4.0
        L.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n.outputs["Fac"]
    if kind == "weave":
        outs = []
        for d in ("X", "Y"):
            w = node("ShaderNodeTexWave", wave_type="BANDS", bands_direction=d)
            w.inputs["Scale"].default_value = 450.0
            L.new(tc.outputs["Object"], w.inputs["Vector"])
            outs.append(w.outputs["Fac"])
        return math_("MULTIPLY", outs[0], outs[1])
    if kind == "eggcrate":
        # the bumps of egg-crate foam: a grid of soft domes, about 3 cm apart
        outs = []
        for d in ("X", "Y"):
            w = node("ShaderNodeTexWave", wave_type="BANDS", bands_direction=d, wave_profile="SIN")
            w.inputs["Scale"].default_value = 20.0
            L.new(tc.outputs["Object"], w.inputs["Vector"])
            outs.append(w.outputs["Fac"])
        return math_("MULTIPLY", outs[0], outs[1])
    if kind == "smooth":
        return math_("MULTIPLY", noise(200.0, 1.0), 0.1)
    return noise(900.0, 2.0, 0.5)  # paint: orange peel


def _route(mat, which):
    nt = mat.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    for l in list(out.inputs["Surface"].links):
        nt.links.remove(l)
    src = nt.nodes[mat[which]]
    nt.links.new(src.outputs[0], out.inputs["Surface"])


def _set_image(mat, img):
    for n in mat.node_tree.nodes:
        if n.type == "TEX_IMAGE" and n.image is not None and n.image.name.startswith("bake_"):
            n.image = img
            mat.node_tree.nodes.active = n


# --- Assembly --------------------------------------------------------------------------------------
def assemble(name, smooth_angle=40.0):
    """Join every part into one mesh, one material slot per look in use."""
    looks = sorted({ob["look"] for ob in PARTS})
    for ob in PARTS:
        ob.data.materials.clear()
        ob.data.materials.append(bpy.data.materials.get(ob["look"]) or bpy.data.materials.new(ob["look"]))
    bpy.ops.object.select_all(action="DESELECT")
    for ob in PARTS:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = PARTS[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    me = ob.data
    _smooth(me, smooth_angle)
    return ob


def _smooth(me, angle):
    for p in me.polygons:
        p.use_smooth = True
    try:
        me.set_sharp_from_angle(angle=math.radians(angle))
    except AttributeError:
        pass


def unwrap(ob, margin=0.004):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(55), island_margin=margin, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    _grow_decal_islands(ob, DECAL_TEXEL)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.pack_islands(margin=margin, rotate=True, shape_method="CONCAVE")
    bpy.ops.object.mode_set(mode="OBJECT")


# How much finer the texture is on the faces that carry a decal than on the rest (linear): logos and
# lettering stay sharp up close, plain paint and wear do not need it.
DECAL_TEXEL = 2.0


def _grow_decal_islands(ob, factor):
    """Scales the UV islands holding faces under a decal by `factor` about their own centre, before
    packing - so the pack gives them that much more of the texture."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    uv = bm.loops.layers.uv.active
    # islands: faces joined across edges whose UVs agree on both sides
    parent = list(range(len(bm.faces)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def key(l):
        return (round(l[uv].uv.x, 6), round(l[uv].uv.y, 6))

    for e in bm.edges:
        if len(e.link_faces) != 2:
            continue
        f0, f1 = e.link_faces
        uv0 = {l.vert.index: key(l) for l in f0.loops if l.vert in e.verts}
        uv1 = {l.vert.index: key(l) for l in f1.loops if l.vert in e.verts}
        if uv0 == uv1:
            parent[find(f0.index)] = find(f1.index)
    marked = set()
    for f in bm.faces:
        c = f.calc_center_median()
        for p in PROJECTORS:
            n = p["normal"]
            if f.normal.dot(n) < 0.5:
                continue
            d = c - p["center"]
            if abs(d.dot(n)) > p["depth"] + 0.01:
                continue
            right = p["up"].cross(n)
            if abs(d.dot(right)) <= p["w"] / 2 + 0.01 and abs(d.dot(p["up"])) <= p["h"] / 2 + 0.01:
                marked.add(find(f.index))
                break
    groups = {}
    for f in bm.faces:
        r = find(f.index)
        if r in marked:
            groups.setdefault(r, []).append(f)
    for faces in groups.values():
        pts = [l[uv].uv for f in faces for l in f.loops]
        cx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
        cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
        for f in faces:
            for l in f.loops:
                l[uv].uv.x = cx + (l[uv].uv.x - cx) * factor
                l[uv].uv.y = cy + (l[uv].uv.y - cy) * factor
    bm.to_mesh(me)
    bm.free()
    print("decal islands grown:", len(groups), "x%.1f" % factor)


def bake(ob, kit, size=2048, samples=64):
    """Bakes _co, _smdi and _nohq into out/<kit>/. Returns their paths."""
    scene = bpy.context.scene
    scene.cycles.samples = samples
    scene.render.bake.margin = 24
    scene.render.bake.use_clear = True
    os.makedirs(os.path.join(OUT, kit), exist_ok=True)
    # A closed lid lies on the body, so its inside and the body's top would bake as fully shaded and
    # grimy - and both show when the lid opens. Lift the lid well clear for the bake, with the decals
    # printed on it, and put it back afterwards. The UVs do not change, so the texture still fits.
    lift = Vector((0.0, 0.0, 0.0))
    lid_attr = ob.data.attributes.get("lid")
    if LID_AXIS and lid_attr is not None:
        from mathutils.bvhtree import BVHTree
        tree = BVHTree.FromObject(ob, bpy.context.evaluated_depsgraph_get())
        lid_v = [abs(d.value - 1.0) < 0.1 for d in lid_attr.data]
        lift = Vector((0.0, 0.0, 0.6))
        moved = []
        for p in PROJECTORS:
            loc, nrm, idx, dist = tree.ray_cast(p["center"] + p["normal"] * 0.02, -p["normal"], 0.05)
            if idx is not None and lid_v[ob.data.polygons[idx].vertices[0]]:
                p["center"] = p["center"] + lift
                moved.append(p)
        for v, on in zip(ob.data.vertices, lid_v):
            if on:
                v.co += lift
        ob.data.update()
        print("lid lifted for the bake, with", len(moved), "decals")
    empties = [(k, dict(p, empty=_projector_empty(p, k))) for k, p in enumerate(PROJECTORS)]

    img = bpy.data.images.new("bake_" + kit, size, size, alpha=False)
    mats = {}
    for slot in ob.material_slots:
        name = slot.material.name
        lk = LOOKS[name.split(".")[0]]
        projs = [(k, p) for k, p in empties if p["looks"] is None or name.split(".")[0] in p["looks"]]
        m = _build_material("bk_" + name, lk, projs, img)
        slot.material = m
        mats[name] = m

    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    paths = {}
    if scene.world is None:
        scene.world = bpy.data.worlds.new("bake_world")
    scene.world.light_settings.distance = 0.08
    for kind, route, btype in (("co", "emit_co", "EMIT"), ("smdi", "emit_sm", "EMIT"), ("nohq", "bsdf", "NORMAL"),
                               ("as", "bsdf", "AO")):
        target = bpy.data.images.new("bake_%s_%s" % (kit, kind), size, size, alpha=False)
        target.colorspace_settings.name = "sRGB" if kind == "co" else "Non-Color"
        for m in mats.values():
            _route(m, route)
            _set_image(m, target)
        if btype == "NORMAL":
            scene.render.bake.normal_space = "TANGENT"
            bpy.ops.object.bake(type="NORMAL")
        elif btype == "AO":
            bpy.ops.object.bake(type="AO")
        else:
            bpy.ops.object.bake(type="EMIT")
        path = os.path.join(OUT, kit, "%s_%s.png" % (kit, kind))
        target.filepath_raw = path
        target.file_format = "PNG"
        target.save()
        paths[kind] = path
        print("baked", kind, path)
    if lift.length:
        for v, on in zip(ob.data.vertices, lid_v):
            if on:
                v.co -= lift
        ob.data.update()
        for p in moved:
            p["center"] = p["center"] - lift
    return paths


def flip_green(src, dst):
    """Blender bakes OpenGL normals (+Y up), Arma reads DirectX (+Y down): invert green."""
    im = bpy.data.images.load(src)
    import numpy as np
    px = np.empty(len(im.pixels), dtype=np.float32)
    im.pixels.foreach_get(px)
    px = px.reshape(-1, 4)
    px[:, 1] = 1.0 - px[:, 1]
    im.pixels.foreach_set(px.ravel())
    im.filepath_raw = dst
    im.file_format = "PNG"
    im.save()


# --- LODs and the p3d -------------------------------------------------------------------------------
def lod_mesh(ob, ratio=1.0, angle=40.0, drop=0.0, dissolve=0.0, inner=True):
    """A copy of ob's mesh for a LOD, triangulated, as a new mesh datablock. No decimation - it tears
    thin bevelled parts into shards. Instead: drop leaves out every part whose largest size is below it
    (screws, rivets, plates - the 'comp' attribute tells the parts apart), dissolve merges flat faces
    within that many degrees without crossing a UV seam, so the baked texture still fits exactly.
    inner=False leaves out what is packed inside (contents()). ratio is ignored (kept for old callers)."""
    me = ob.data.copy()
    if not inner and me.attributes.get("inner") is not None:
        bm = bmesh.new()
        bm.from_mesh(me)
        layer = bm.verts.layers.int.get("inner")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v[layer]], context="VERTS")
        bm.to_mesh(me)
        bm.free()
    if drop > 0.0:
        comp = me.attributes.get("comp")
        if comp is not None:
            ids = [d.value for d in comp.data]
            lo, hi = {}, {}
            for v, c in zip(me.vertices, ids):
                p = v.co
                if c not in lo:
                    lo[c] = list(p)
                    hi[c] = list(p)
                else:
                    for i in range(3):
                        lo[c][i] = min(lo[c][i], p[i])
                        hi[c][i] = max(hi[c][i], p[i])
            small = {c for c in lo if max(hi[c][i] - lo[c][i] for i in range(3)) < drop}
            bm = bmesh.new()
            bm.from_mesh(me)
            layer = bm.verts.layers.int.get("comp")
            gone = [v for v in bm.verts if v[layer] in small]
            bmesh.ops.delete(bm, geom=gone, context="VERTS")
            bm.to_mesh(me)
            bm.free()
    tmp = bpy.data.objects.new("lod_tmp", me)
    bpy.context.scene.collection.objects.link(tmp)
    if dissolve > 0.0:
        mod = tmp.modifiers.new("flat", "DECIMATE")
        mod.decimate_type = "DISSOLVE"
        mod.angle_limit = math.radians(dissolve)
        mod.delimit = {"UV", "SHARP", "MATERIAL"}
    tmp.modifiers.new("tri", "TRIANGULATE")
    dg = bpy.context.evaluated_depsgraph_get()
    out = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    _smooth(out, angle)
    return out


def hull_tris(me, inflate=0.0):
    """Convex hull of a mesh as game triangles (for shadow and geometry LODs)."""
    bm = bmesh.new()
    for v in me.vertices:
        bm.verts.new(v.co + v.normal * inflate)
    res = bmesh.ops.convex_hull(bm, input=bm.verts)
    for g in res.get("geom_interior", []) + res.get("geom_unused", []):
        if isinstance(g, bmesh.types.BMVert) and g.is_valid and not g.link_faces:
            bm.verts.remove(g)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.normal_update()
    tris = []
    for f in bm.faces:
        tris.append([(_to_game(l.vert.co), _to_game_n(f.normal), (0.0, 0.0)) for l in reversed(f.loops)])
    bm.free()
    return tris


# How a kit lies in the game, if not the way it is built: a 4x4 Matrix applied to everything written
# to the p3d (LODs, shadow, geometry, memory points) but not to the bake or the icons. See
# build_kit.py and kits.EXPORT_ROT.
EXPORT = [None]


def _to_game(v):
    if EXPORT[0] is not None:
        v = EXPORT[0] @ Vector(v)
    return (v[0], -v[1], v[2])


def _to_game_n(n):
    if EXPORT[0] is not None:
        n = (EXPORT[0].to_3x3() @ Vector(n)).normalized()
    return (n[0], -n[1], n[2])


def mesh_tris(me, use_comp=False):
    """Game triangles [(pos, normal, uv, group (see group_id), part)] * 3 from a triangulated mesh, CCW seen from
    outside. use_comp keeps the points of different parts apart when they are welded."""
    me.calc_loop_triangles()
    uv = me.uv_layers.active.data if me.uv_layers.active is not None else None
    cn = me.corner_normals
    lid_attr = me.attributes.get("lid")
    lid_v = [int(round(d.value)) for d in lid_attr.data] if lid_attr is not None else None
    comp_attr = me.attributes.get("comp") if use_comp else None
    comp_v = [d.value for d in comp_attr.data] if comp_attr is not None else None
    tris = []
    for t in me.loop_triangles:
        v0 = me.loops[t.loops[0]].vertex_index
        flag = lid_v[v0] if lid_v is not None else 0
        part = comp_v[v0] if comp_v is not None else 0
        tri = []
        for li in reversed(t.loops):   # the mirror flips the winding
            vi = me.loops[li].vertex_index
            co = me.vertices[vi].co
            n = cn[li].vector
            u, v = uv[li].uv if uv is not None else (0.0, 0.0)
            tri.append((_to_game(co), _to_game_n(n), (u, 1.0 - v), flag, part))
        tris.append(tri)
    return tris


def _weld(tris, eps=1e-6, sel=None):
    pts, pidx, nrm, nidx, faces = [], {}, [], {}, []
    for t in tris:
        f = []
        flag = t[0][3] if len(t[0]) > 3 else 0
        part = t[0][4] if len(t[0]) > 4 else 0
        if sel is not None:
            sel["faces"].append(flag)
        for c in t:
            p, n, uv = c[0], c[1], c[2]
            kp = tuple(round(v / eps) for v in p) + (flag, part)
            if kp not in pidx:
                pidx[kp] = len(pts)
                pts.append(p)
                if sel is not None:
                    sel["points"].append(flag)
            kn = tuple(round(c * 1e5) for c in n)
            if kn not in nidx:
                nidx[kn] = len(nrm)
                nrm.append(n)
            f.append((pidx[kp], nidx[kn], uv))
        faces.append(f)
    return pts, nrm, faces


def _asciiz(s):
    return s.encode("latin1") + b"\0"


def _tagg(name, data):
    return b"\x01" + _asciiz(name) + struct.pack("<I", len(data)) + data


def lod_bytes(resolution, tris, tex, mat, sharp=False, mass=None, props=(), selections=None, points=None):
    """One MLOD (P3DM) LOD. Same layout as EFAK's make_narc.py, checked against BI samples there:
    stored normals and the face winding point inwards, UV origin top left. selections: {group: name}
    of named selections, each made of the triangles of that group (see group_id). points: a
    points-only LOD (memory), as [(name, [positions])]."""
    sel = {"points": [], "faces": []}
    if points is not None:
        pts, nrm, faces = [], [], []
        for _, ps in points:
            pts += list(ps)
    else:
        pts, nrm, faces = _weld(tris, sel=sel)
    out = bytearray(b"P3DM")
    out += struct.pack("<IIIIII", 28, 256, len(pts), len(nrm), len(faces), 0)
    for p in pts:
        out += struct.pack("<fffI", p[0], p[1], p[2], 0)
    for n in nrm:
        out += struct.pack("<fff", -n[0], -n[1], -n[2])
    uvset = bytearray(struct.pack("<I", 0))
    for f in faces:
        f = [f[0], f[2], f[1]]
        out += struct.pack("<I", 3)
        for pi, ni, (u, v) in f:
            out += struct.pack("<IIff", pi, ni, u, v)
            uvset += struct.pack("<ff", u, v)
        out += struct.pack("<IIff", 0, 0, 0, 0)
        out += struct.pack("<I", 0)
        out += _asciiz(tex) + _asciiz(mat)
    out += b"TAGG"
    if sharp:
        edges = set()
        for f in faces:
            for i in range(3):
                a, b = f[i][0], f[(i + 1) % 3][0]
                edges.add((min(a, b), max(a, b)))
        out += _tagg("#SharpEdges#", b"".join(struct.pack("<II", a, b) for a, b in sorted(edges)))
    for gid, name in sorted((selections or {}).items()):
        if gid in sel["points"]:
            data = bytes(1 if s == gid else 0 for s in sel["points"]) + bytes(1 if s == gid else 0 for s in sel["faces"])
            out += _tagg(name, data)
    if points is not None:
        k = 0
        for name, ps in points:
            flags = [0] * len(pts)
            for i in range(k, k + len(ps)):
                flags[i] = 1
            k += len(ps)
            out += _tagg(name, bytes(flags))
    if mass is not None:
        out += _tagg("#Mass#", b"".join(struct.pack("<f", mass / len(pts)) for _ in pts))
    for k, v in props:
        out += _tagg("#Property#", k.encode().ljust(64, b"\0") + v.encode().ljust(64, b"\0"))
    if mass is None and points is None:
        out += _tagg("#UVSet#", bytes(uvset))
    out += _tagg("#EndOfFile#", b"")
    out += struct.pack("<f", resolution)
    return bytes(out), len(pts), len(faces)


def shadow_open_edges(tris):
    """Edges of the shadow LOD not shared by exactly two triangles of the same part. Arma's shadow
    volumes need every part closed; 0 is the only good answer."""
    from collections import Counter
    count = Counter()
    for t in tris:
        part = t[0][4]
        keys = [tuple(round(v * 1e6) for v in c[0]) for c in t]
        for i in range(3):
            a, b = keys[i], keys[(i + 1) % 3]
            count[(part,) + tuple(sorted((a, b)))] += 1
    return sum(1 for v in count.values() if v != 2)


# LOD 1, 2 and 4: (leave out parts smaller than this in metres, merge flat faces within this many degrees)
# (drop parts smaller than, dissolve flat faces within degrees, keep the contents) per LOD 1, 2, 4, 8,
# 16: the contents only matter up close, where someone has the lid open; far away a kit is its case.
LODS = ((0.0, 0.0, True), (0.012, 1.0, True), (0.03, 2.0, False), (0.06, 4.0, False), (0.12, 8.0, False))


def write_p3d(path, ob, tex, mat, shadow=None):
    """shadow: triangles for the shadow LOD (see build_kit.py); a convex hull if left out, which only
    suits shapes without hollows."""
    lods = []
    last = None
    # a small kit must not lose its body: no part above a third of the kit's size is ever dropped
    bb = [ob.matrix_world @ v.co for v in ob.data.vertices]
    span = max(max(p[i] for p in bb) - min(p[i] for p in bb) for i in range(3))
    for i, (drop, dissolve, keep) in enumerate(LODS):
        me = lod_mesh(ob, drop=min(drop, span / 3), dissolve=dissolve, inner=keep)
        data, npt, nf = lod_bytes(float(2 ** i), mesh_tris(me), tex, mat, selections=group_names())
        print("LOD", 2 ** i, "points", npt, "faces", nf)
        lods.append(data)
        last = me
    data, npt, nf = lod_bytes(10000.0, shadow if shadow else hull_tris(last), "", "", sharp=True,
                              selections=group_names() if shadow else None)
    print("shadow faces", nf)
    lods.append(data)
    data, npt, nf = lod_bytes(1e13, hull_tris(last, 0.001), "", "", mass=1.0, props=(("autocenter", "0"),))
    print("geometry faces", nf)
    lods.append(data)
    axes = [("lid_axis", LID_AXIS)] if LID_AXIS else []
    axes += [("latch%d_axis" % (k + 1), list(ax)) for k, ax in enumerate(LATCHES)]
    if axes:
        data, npt, nf = lod_bytes(1e15, [], "", "", points=[(n, [_to_game(a[0]), _to_game(a[1])]) for n, a in axes])
        print("memory points", npt)
        lods.append(data)
    with open(path, "wb") as f:
        f.write(b"MLOD" + struct.pack("<II", 257, len(lods)))
        for l in lods:
            f.write(l)
    print("wrote", path)


def inset_shadow(shadow):
    """The shadow LOD pulled 8 mm inside the kit's surface (a quarter on thin sides), so a shadow never
    shades the kit it belongs to (acne on the shut kit). Used for both the kit's own shadow and its
    caster, so the two are the very same shape and the shadow does not change when a lid opens."""
    xs = [p[0][0] for t in shadow for p in t]
    ys = [p[0][1] for t in shadow for p in t]
    zs = [p[0][2] for t in shadow for p in t]
    c = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2)
    size = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    k = [(d - min(0.016, d * 0.25)) / d if d > 0.01 else 1.0 for d in size]
    return [[(tuple(c[i] + (p[0][i] - c[i]) * k[i] for i in range(3)),) + tuple(p[1:]) for p in t] for t in shadow]


def write_shadow_p3d(path, shadow):
    """A shadow caster for a kit lying in a ground holder, where the game draws no shadow for it: the
    kit's own shadow LOD (lid shut, see inset_shadow) and nothing to see - one tiny face deep inside
    the closed case, so the model is not culled as empty."""
    xs = [p[0][0] for t in shadow for p in t]
    ys = [p[0][1] for t in shadow for p in t]
    zs = [p[0][2] for t in shadow for p in t]
    c = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2)
    n = (0.0, 0.0, 1.0)
    e = 0.0005
    tri = [((c[0], c[1], c[2]), n, (0.0, 0.0)), ((c[0] + e, c[1], c[2]), n, (0.0, 0.0)),
           ((c[0], c[1] + e, c[2]), n, (0.0, 0.0))]
    lods = []
    data, npt, nf = lod_bytes(1.0, [tri], "#(argb,8,8,3)color(0,0,0,0)", "")
    lods.append(data)
    data, npt, nf = lod_bytes(10000.0, shadow, "", "", sharp=True)
    lods.append(data)
    with open(path, "wb") as f:
        f.write(b"MLOD" + struct.pack("<II", 257, len(lods)))
        for l in lods:
            f.write(l)
    print("wrote", path, "shadow faces", nf)


RVMAT = """ambient[]={1,1,1,1};
diffuse[]={1,1,1,1};
forcedDiffuse[]={0,0,0,0};
emmisive[]={0,0,0,1};
specular[]={0.7,0.7,0.7,1};
specularPower=60;
PixelShaderID="Super";
VertexShaderID="Super";
class Stage1 { texture="%(dir)s\\%(kit)s_nohq.paa"; uvSource="tex"; class uvTransform { aside[]={1,0,0}; up[]={0,1,0}; dir[]={0,0,0}; pos[]={0,0,0}; }; };
class Stage2 { texture="#(argb,8,8,3)color(0.5,0.5,0.5,1,DT)"; uvSource="tex"; class uvTransform { aside[]={1,0,0}; up[]={0,1,0}; dir[]={0,0,0}; pos[]={0,0,0}; }; };
class Stage3 { texture="#(argb,8,8,3)color(0,0,0,0,MC)"; uvSource="tex"; class uvTransform { aside[]={1,0,0}; up[]={0,1,0}; dir[]={0,0,0}; pos[]={0,0,0}; }; };
class Stage4 { texture="%(dir)s\%(kit)s_as.paa"; uvSource="tex"; class uvTransform { aside[]={1,0,0}; up[]={0,1,0}; dir[]={0,0,0}; pos[]={0,0,0}; }; };
class Stage5 { texture="%(dir)s\\%(kit)s_smdi.paa"; uvSource="tex"; class uvTransform { aside[]={1,0,0}; up[]={0,1,0}; dir[]={0,0,0}; pos[]={0,0,0}; }; };
class Stage6 { texture="#(ai,64,64,1)fresnel(1.3,0.6)"; uvSource="none"; };
class Stage7 { texture="a3\\data_f\\env_land_co.paa"; useWorldEnvMap="true"; uvSource="none"; };
"""


def downscale(png, size):
    im = bpy.data.images.load(png)
    if im.size[0] > size:
        im.scale(size, size)
    out = png.replace(".png", "_%d.png" % size)
    im.filepath_raw = out
    im.file_format = "PNG"
    im.save()
    return out


def to_paa(png, paa):
    """ImageToPAA picks the compression from the name's suffix (_co, _ca, _nohq, ...), so the PNG
    goes in under the name the PAA will have."""
    import shutil
    import tempfile
    tmp = os.path.join(tempfile.mkdtemp(), os.path.splitext(os.path.basename(paa))[0] + ".png")
    shutil.copyfile(png, tmp)
    # ImageToPAA now and then fails on a file another process still holds: try again before giving up
    import time
    for attempt in range(3):
        r = subprocess.run([IMAGE_TO_PAA, tmp, paa], capture_output=True)
        if r.returncode == 0:
            break
        time.sleep(2)
    else:
        raise RuntimeError("ImageToPAA failed for %s: %s" % (paa, (r.stdout + r.stderr).decode(errors="replace")))
    print("paa", paa)


# --- Icons ------------------------------------------------------------------------------------------
def preview_material(paths, name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    co = nt.nodes.new("ShaderNodeTexImage")
    co.image = bpy.data.images.load(paths["co"])
    nt.links.new(co.outputs["Color"], bsdf.inputs["Base Color"])
    nm = nt.nodes.new("ShaderNodeTexImage")
    nm.image = bpy.data.images.load(paths["nohq"])
    nm.image.colorspace_settings.name = "Non-Color"
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(nm.outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    sm = nt.nodes.new("ShaderNodeTexImage")
    sm.image = bpy.data.images.load(paths["smdi"])
    sm.image.colorspace_settings.name = "Non-Color"
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(sm.outputs["Color"], sep.inputs[0])
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(sep.outputs["Blue"], inv.inputs[1])
    nt.links.new(inv.outputs[0], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Specular IOR Level"])
    return mat


def render_views(ob, paths, kit, views=("icon",), size=1024, samples=128):
    scene = bpy.context.scene
    mat = preview_material(paths, "preview_" + kit)
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.material_index = 0
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.film_transparent = True
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("w")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.5, 0.55, 0.6, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.2

    # from the vertices, not ob.bound_box, which can still hold the lid lifted for the bake
    bb = [ob.matrix_world @ v.co for v in ob.data.vertices]
    lo = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    hi = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    centre = (lo + hi) / 2
    radius = (hi - lo).length / 2

    def light(name, d, energy, size_=0.6):
        l = bpy.data.lights.new(name, "AREA")
        l.energy = energy * (radius / 0.2) ** 2
        l.size = size_ * radius / 0.2
        o = bpy.data.objects.new(name, l)
        o.location = centre + Vector(d).normalized() * radius * 5
        o.rotation_euler = (centre - o.location).to_track_quat("-Z", "Y").to_euler()
        scene.collection.objects.link(o)

    light("key", (-0.7, -0.9, 0.6), 22)
    light("fill", (0.9, -0.4, 0.3), 9)
    light("rim", (0.3, 0.9, 0.7), 18)

    cam = bpy.data.cameras.new("cam")
    cam.lens = 85
    co = bpy.data.objects.new("cam", cam)
    scene.collection.objects.link(co)
    scene.camera = co
    dirs = {"icon": (-0.62, -0.78, 0.55), "front": (0.0, -1.0, 0.15), "back": (0.4, 1.0, 0.4),
            "side": (1.0, -0.15, 0.2), "top": (0.0, -0.3, 1.0), "low": (-0.7, -0.7, 0.08)}
    out = {}
    for v in views:
        d = Vector(dirs[v]).normalized()
        fov = 2 * math.atan(18.0 / cam.lens)   # 36 mm sensor
        dist = radius / math.sin(fov / 2) * (1.02 if v == "icon" else 1.1)
        co.location = centre + d * dist
        co.rotation_euler = (centre - co.location).to_track_quat("-Z", "Y").to_euler()
        path = os.path.join(OUT, kit, "%s_%s.png" % (kit, v))
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        out[v] = path
    return out
