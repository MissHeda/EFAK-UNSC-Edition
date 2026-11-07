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
         wear_gloss=0.5, bevel=0.0025, primer=None, pattern="paint", streaks=0.5):
    return dict(color=color, wear_color=wear_color or color, wear=wear, grime=grime, mottle=mottle,
                grain=grain, spec=spec, gloss=gloss, wear_gloss=wear_gloss, bevel=bevel, primer=primer,
                pattern=pattern, streaks=streaks)


STEEL = srgb(150, 152, 154)
PRIMER = srgb(118, 112, 96)

LOOKS = {
    # UNSC olive drab: paint over metal (chips show primer, then steel) or moulded polymer
    "olive": look(srgb(92, 97, 64), srgb(140, 138, 116), wear=0.45, grime=0.55, spec=0.1, gloss=0.28,
                  pattern="stipple", grain=0.25),
    "olive_dark": look(srgb(66, 70, 46), srgb(120, 120, 98), wear=0.45, grime=0.55, spec=0.1, gloss=0.26,
                       pattern="stipple", grain=0.25),
    "olive_green": look(srgb(78, 96, 54), STEEL, wear=0.45, grime=0.5, spec=0.14, gloss=0.34, primer=PRIMER),
    "olive_tan": look(srgb(104, 96, 66), STEEL, wear=0.5, grime=0.6, spec=0.1, gloss=0.25, primer=PRIMER),
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
    "shell_dark": look(srgb(72, 75, 78), STEEL, wear=0.45, grime=0.5, spec=0.18, gloss=0.38, primer=srgb(96, 98, 98)),
    # EUP colours
    "hazard_yellow": look(srgb(206, 168, 44), STEEL, wear=0.55, grime=0.55, spec=0.16, gloss=0.38, primer=PRIMER),
    "hazmat_white": look(srgb(196, 196, 186), srgb(150, 150, 142), wear=0.35, grime=0.7, spec=0.2, gloss=0.42,
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
    "steel": look(srgb(96, 98, 100), srgb(180, 182, 184), wear=0.6, grime=0.4, spec=0.5, gloss=0.55,
                  wear_gloss=0.75, grain=0.25, bevel=0.0012, pattern="brushed"),
    "black_metal": look(srgb(28, 29, 30), STEEL, wear=0.55, grime=0.25, spec=0.35, gloss=0.5,
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
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world = matrix
    ob["look"] = mat
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


def prism(profile, depth, look="olive", loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.002, segs=2, name="part",
          taper=0.0, matrix=None):
    """A 2D outline (local x, y; counter-clockwise) extruded along local z from 0 to depth, edges
    bevelled. taper shrinks the top outline by that much (a draft/chamfered top)."""
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
        taper=0.0):
    """Box of size (sx, sy, sz) centred at center. The outline (with optional cut corners) lies across
    `axis` and is extruded along it: axis z cuts the corners seen from above, y seen from the front,
    x seen from the side."""
    sx, sy, sz = size
    cx, cy, cz = center
    if axis == "z":
        return prism(rect(sx, sy, cut, cuts), sz, look, (cx, cy, cz - sz / 2), (0, 0, 0), bevel, segs, name,
                     taper)
    if axis == "y":
        # outline in x/z, extruded towards -y (the front): rotate local z onto -y
        return prism(rect(sx, sz, cut, cuts), sy, look, (cx, cy + sy / 2, cz), (90, 0, 0), bevel, segs, name,
                     taper)
    # axis x: outline in y/z, extruded along +x
    return prism(rect(sy, sz, cut, cuts), sx, look, (cx - sx / 2, cy, cz), (90, 0, 90), bevel, segs, name,
                 taper)


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


def bolt(center, normal, r=0.0035, look="steel", up=(0, 0, 1)):
    """Hex-head bolt on a washer."""
    F = frame(center, normal, up)
    lcyl(F, r * 1.45, r * 0.28, look=look, n=16, bevel=r * 0.08)
    prism(circle(r, 6), r * 0.75, look, bevel=r * 0.12, segs=1,
          matrix=F @ Matrix.Translation((0, 0, r * 0.26)))


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


def toggle_latch(center, normal, up=(0, 0, 1), w=0.032, h=0.05, look="black_metal"):
    """Over-centre toggle latch: base plate on the body, lever, wire hook, keeper on the lid.
    center is where the seam is; the latch hangs below it and grips above it."""
    F = frame(center, normal, up)
    lbox(F, (w, h * 0.42, 0.003), (0, -h * 0.36, 0), look, cut=0.003, bevel=0.0008)
    for sx in (-1, 1):
        lbox(F, (0.003, h * 0.22, 0.008), (sx * w * 0.36, -h * 0.3, 0), look, bevel=0.0006)
    lcyl(F, 0.0022, w * 0.78, (0, -h * 0.3, 0.007), "steel", n=10, axis="x")
    lbox(F, (w * 0.72, h * 0.62, 0.004), (0, -h * 0.12, 0.007), look, cut=0.004, cuts=(1, 1, 0, 0),
         bevel=0.0012, segs=2)
    lbox(F, (w * 0.5, h * 0.12, 0.002), (0, -h * 0.36, 0.011), look, bevel=0.0005)
    for sx in (-1, 1):
        lbox(F, (0.0018, h * 0.42, 0.0018), (sx * w * 0.26, h * 0.12, 0.0075), "steel", bevel=0)
    lbox(F, (w * 0.56, 0.0022, 0.0022), (0, h * 0.33, 0.0065), "steel", bevel=0)
    lbox(F, (w * 0.8, h * 0.16, 0.0055), (0, h * 0.36, 0), look, cut=0.002, bevel=0.0008)


def vents(center, normal, up, n, w, gap, fin=0.004, depth=0.003, look="dark_poly"):
    """A row of n louvre fins, w long, stacked along up with `gap` between, in a frame."""
    F = frame(center, normal, up)
    hgt = n * gap
    lbox(F, (w + 0.008, hgt + 0.006, 0.0015), (0, 0, 0), look, bevel=0.0006)
    for k in range(n):
        y = -hgt / 2 + gap * (k + 0.5)
        lbox(F, (w, fin, depth), (0, y, 0.0012), look, bevel=0.0007, taper=0.0008)


def hinge(p0, p1, r=0.005, knuckles=5, look="black_metal"):
    """Piano-style hinge: knuckles along p0-p1 with small gaps, and a pin showing at the ends."""
    a, b = Vector(p0), Vector(p1)
    axis = (b - a)
    ln = axis.length
    d = axis.normalized()
    q = d.to_track_quat("Z", "Y")
    seg = ln / knuckles
    for k in range(knuckles):
        c = a + d * (seg * (k + 0.5))
        m = Matrix.Translation(c) @ q.to_matrix().to_4x4() @ Matrix.Translation((0, 0, -seg * 0.46))
        prism(circle(r, 14), seg * 0.92, look, bevel=r * 0.15, segs=1, matrix=m)
    for e, s_ in ((a, -1), (b, 1)):
        m = Matrix.Translation(e + d * s_ * 0.001) @ q.to_matrix().to_4x4() @ Matrix.Translation((0, 0, -0.0015))
        prism(circle(r * 0.45, 10), 0.003, "steel", bevel=0.0003, segs=1, matrix=m)


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
        decal(image, tuple(Vector(center) + nz * 0.0012), tuple(nz), up, w * 0.86, depth=0.0015)


def decal(image, center, normal, up, width, height=None, depth=0.01, looks=None):
    """Project a decal PNG (out/decals/<image>.png) onto the surfaces facing `normal` within `depth`
    of `center`. width/height in metres; height follows the image's aspect if left out."""
    path = os.path.join(DECALS, image + ".png")
    img = bpy.data.images.load(path, check_existing=True)
    if height is None:
        height = width * img.size[1] / img.size[0]
    PROJECTORS.append(dict(img=img, center=Vector(center), normal=Vector(normal).normalized(),
                           up=Vector(up).normalized(), w=width, h=height, depth=depth, looks=looks))


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
    # chips: edges broken up by noise
    chip_noise = noise(48.0, 8.0, 0.7)
    chips = ramp(math_("MULTIPLY", edge, ramp(chip_noise, 0.3, 0.7)), 0.15, 0.42)
    wear_mask = math_("MULTIPLY", chips, lk["wear"], clamp=True)
    # scratches: fine streaks
    scr = node("ShaderNodeTexWave", wave_type="BANDS", bands_direction="DIAGONAL")
    scr.inputs["Scale"].default_value = 140.0
    scr.inputs["Distortion"].default_value = 18.0
    scr.inputs["Detail"].default_value = 4.0
    tc = node("ShaderNodeTexCoord")
    L.new(tc.outputs["Object"], scr.inputs["Vector"])
    scratch = math_("MULTIPLY", ramp(scr.outputs["Fac"], 0.93, 0.99), ramp(noise(6.0), 0.5, 0.65))
    wear_mask = math_("MAXIMUM", wear_mask, math_("MULTIPLY", scratch, lk["wear"] * 0.8), clamp=True)
    # scuffs: dull, slightly lighter patches where things rub, anywhere on the surface
    scuff = math_("MULTIPLY", ramp(noise(14.0, 6.0, 0.7), 0.58, 0.75), lk["wear"] * 0.35, clamp=True)

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
    col = mix(col, tuple(min(1.0, c * 1.25 + 0.02) for c in lk["color"][:3]) + (1.0,), scuff)
    grime_col = tuple(c * 0.35 for c in lk["color"][:3]) + (1.0,)
    col = mix(col, grime_col, cavity)
    col = mix(col, tuple(c * 0.25 for c in lk["color"][:3]) + (1.0,), contact)
    col = mix(col, srgb(74, 66, 50), streak)
    col = mix(col, srgb(150, 138, 110), dust)

    emit_co = node("ShaderNodeEmission")
    L.new(col, emit_co.inputs["Color"])

    # smdi: R 1, G specular, B gloss
    spec = math_("ADD", lk["spec"], math_("MULTIPLY", wear_mask, max(0.0, lk["spec"] * 1.5 - lk["spec"])))
    gloss = math_("ADD", lk["gloss"], math_("MULTIPLY", wear_mask, lk["wear_gloss"] - lk["gloss"]))
    gloss = math_("SUBTRACT", gloss, math_("MULTIPLY", math_("ADD", math_("ADD", cavity, dust), math_("ADD", streak, scuff)),
                                           0.25), clamp=True)
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
    bump = node("ShaderNodeBump")
    bump.inputs["Strength"].default_value = lk["grain"]
    bump.inputs["Distance"].default_value = 0.0004
    L.new(_pattern(node, L, noise, math_, lk["pattern"]), bump.inputs["Height"])
    L.new(nb.outputs["Normal"], bump.inputs["Normal"])
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
    bpy.ops.uv.pack_islands(margin=margin, rotate=True, shape_method="CONCAVE")
    bpy.ops.object.mode_set(mode="OBJECT")


def bake(ob, kit, size=2048, samples=64):
    """Bakes _co, _smdi and _nohq into out/<kit>/. Returns their paths."""
    scene = bpy.context.scene
    scene.cycles.samples = samples
    scene.render.bake.margin = 24
    scene.render.bake.use_clear = True
    os.makedirs(os.path.join(OUT, kit), exist_ok=True)
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
def lod_mesh(ob, ratio, angle=40.0):
    """A decimated copy of ob's mesh (ratio 1 = as is), triangulated, as a new mesh datablock."""
    tmp = ob.copy()
    tmp.data = ob.data.copy()
    bpy.context.scene.collection.objects.link(tmp)
    if ratio < 1.0:
        mod = tmp.modifiers.new("dec", "DECIMATE")
        mod.ratio = ratio
        mod.use_collapse_triangulate = True
    mod = tmp.modifiers.new("tri", "TRIANGULATE")
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    _smooth(me, angle)
    return me


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


def _to_game(v):
    return (v[0], -v[1], v[2])


def _to_game_n(n):
    return (n[0], -n[1], n[2])


def mesh_tris(me):
    """Game triangles [(pos, normal, uv)] * 3 from a triangulated mesh, CCW seen from outside."""
    me.calc_loop_triangles()
    uv = me.uv_layers.active.data
    cn = me.corner_normals
    tris = []
    for t in me.loop_triangles:
        tri = []
        for li in reversed(t.loops):   # the mirror flips the winding
            co = me.vertices[me.loops[li].vertex_index].co
            n = cn[li].vector
            u, v = uv[li].uv
            tri.append((_to_game(co), _to_game_n(n), (u, 1.0 - v)))
        tris.append(tri)
    return tris


def _weld(tris, eps=1e-6):
    pts, pidx, nrm, nidx, faces = [], {}, [], {}, []
    for t in tris:
        f = []
        for p, n, uv in t:
            kp = tuple(round(c / eps) for c in p)
            if kp not in pidx:
                pidx[kp] = len(pts)
                pts.append(p)
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


def lod_bytes(resolution, tris, tex, mat, sharp=False, mass=None, props=()):
    """One MLOD (P3DM) LOD. Same layout as EFAK's make_narc.py, checked against BI samples there:
    stored normals and the face winding point inwards, UV origin top left."""
    pts, nrm, faces = _weld(tris)
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
    if mass is not None:
        out += _tagg("#Mass#", b"".join(struct.pack("<f", mass / len(pts)) for _ in pts))
    for k, v in props:
        out += _tagg("#Property#", k.encode().ljust(64, b"\0") + v.encode().ljust(64, b"\0"))
    if mass is None:
        out += _tagg("#UVSet#", bytes(uvset))
    out += _tagg("#EndOfFile#", b"")
    out += struct.pack("<f", resolution)
    return bytes(out), len(pts), len(faces)


def write_p3d(path, ob, tex, mat, ratios=(1.0, 0.45, 0.16)):
    lods = []
    last = None
    for i, r in enumerate(ratios):
        me = lod_mesh(ob, r)
        data, npt, nf = lod_bytes(float(2 ** i), mesh_tris(me), tex, mat)
        print("LOD", 2 ** i, "points", npt, "faces", nf)
        lods.append(data)
        last = me
    data, npt, nf = lod_bytes(10000.0, hull_tris(last), "", "", sharp=True)
    print("shadow faces", nf)
    lods.append(data)
    data, npt, nf = lod_bytes(1e13, hull_tris(last, 0.001), "", "", mass=1.0, props=(("autocenter", "0"),))
    print("geometry faces", nf)
    lods.append(data)
    with open(path, "wb") as f:
        f.write(b"MLOD" + struct.pack("<II", 257, len(lods)))
        for l in lods:
            f.write(l)
    print("wrote", path)


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
    subprocess.run([IMAGE_TO_PAA, tmp, paa], check=True, capture_output=True)
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

    bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
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
