"""Reference pictures of MLOD p3d files (debinarized with debin): the first LOD, textured where the
PAA next to it has been converted to PNG, rendered from four sides into out/ref/<name>_<view>.png,
and its size printed. For looking at other mods' models while building our own - nothing of
theirs ends up in the mod.

    blender -b -P tools/models/ref_p3d.py -- <file.p3d> [<png dir>] [--views icon,front,top,side]
"""
import os
import struct
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import unsc_lib as U  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
path = argv[0]
pngdir = argv[1] if len(argv) > 1 and not argv[1].startswith("--") else os.path.dirname(path)
views = ["icon", "front", "top", "side"]
if "--views" in argv:
    views = argv[argv.index("--views") + 1].split(",")


def read_mlod(path):
    """First LOD of an MLOD: points, faces as [(point, uv)...], texture per face."""
    with open(path, "rb") as f:
        data = f.read()
    assert data[:4] == b"MLOD", "not an MLOD file"
    n_lods = struct.unpack_from("<I", data, 8)[0]
    off = 12
    lods = []
    for _ in range(n_lods):
        assert data[off:off + 4] == b"P3DM", "not a P3DM LOD"
        _, _, npts, nnorm, nfaces, _ = struct.unpack_from("<IIIIII", data, off + 4)
        off += 28
        pts = []
        for i in range(npts):
            x, y, z, _ = struct.unpack_from("<fffI", data, off)
            pts.append((x, -y, z))   # back from game space to our Blender space
            off += 16
        off += 12 * nnorm
        faces = []
        for i in range(nfaces):
            nv = struct.unpack_from("<I", data, off)[0]
            off += 4
            verts = []
            for k in range(4):
                pi, ni, u, v = struct.unpack_from("<IIff", data, off)
                off += 16
                if k < nv:
                    verts.append((pi, (u, 1.0 - v)))
            flags = struct.unpack_from("<I", data, off)[0]
            off += 4
            tex_end = data.index(b"\0", off)
            tex = data[off:tex_end].decode("latin-1")
            off = tex_end + 1
            mat_end = data.index(b"\0", off)
            off = mat_end + 1
            faces.append((verts, tex))   # as stored: with the mirrored y that is outward here
        # taggs
        assert data[off:off + 4] == b"TAGG"
        off += 4
        resolution = None
        while True:
            active = data[off]
            off += 1
            name_end = data.index(b"\0", off)
            name = data[off:name_end].decode("latin-1")
            off = name_end + 1
            size = struct.unpack_from("<I", data, off)[0]
            off += 4
            if name == "#EndOfFile#":
                break
            off += size
        resolution = struct.unpack_from("<f", data, off)[0]
        off += 4
        lods.append((resolution, pts, faces))
    lods.sort(key=lambda l: l[0])
    return lods[0]


res, pts, faces = read_mlod(path)
name = os.path.splitext(os.path.basename(path))[0].replace("_mlod", "")
bpy.ops.wm.read_homefile(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
me = bpy.data.meshes.new(name)
texs = sorted({t for _, t in faces})
me.from_pydata(pts, [], [[v[0] for v in vs] for vs, _ in faces])
uv = me.uv_layers.new()
k = 0
for (vs, _), poly in zip(faces, me.polygons):
    for v, li in zip(vs, poly.loop_indices):
        uv.data[li].uv = v[1]
mats = {}
for t in texs:
    m = bpy.data.materials.new(os.path.basename(t) or "none")
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.6
    base = os.path.splitext(os.path.basename(t))[0]
    png = os.path.join(pngdir, base + ".png")
    if os.path.exists(png):
        img = m.node_tree.nodes.new("ShaderNodeTexImage")
        img.image = bpy.data.images.load(png)
        m.node_tree.links.new(img.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1)
    mats[t] = len(me.materials)
    me.materials.append(m)
for (vs, t), poly in zip(faces, me.polygons):
    poly.material_index = mats[t]
me.validate()
me.update()
ob = bpy.data.objects.new(name, me)
scene.collection.objects.link(ob)
lo = [min(p[i] for p in pts) for i in range(3)]
hi = [max(p[i] for p in pts) for i in range(3)]
print("SIZE", name, "x %.3f y %.3f z %.3f m" % tuple(hi[i] - lo[i] for i in range(3)), "textures", texs)
out = os.path.join(U.OUT, "ref")
os.makedirs(out, exist_ok=True)
paths = {"preview": None}
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.film_transparent = True
scene.render.resolution_x = scene.render.resolution_y = 768
scene.view_settings.view_transform = "Standard"
world = bpy.data.worlds.new("w")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
import math
from mathutils import Vector
centre = Vector([(lo[i] + hi[i]) / 2 for i in range(3)])
radius = (Vector(hi) - Vector(lo)).length / 2
sun = bpy.data.lights.new("sun", "SUN")
sun.energy = 3.0
so = bpy.data.objects.new("sun", sun)
scene.collection.objects.link(so)
so.rotation_euler = (math.radians(50), 0, math.radians(30))
cam = bpy.data.cameras.new("cam")
cam.lens = 85
co = bpy.data.objects.new("cam", cam)
scene.collection.objects.link(co)
scene.camera = co
dirs = {"icon": (-0.62, -0.78, 0.55), "front": (0.0, -1.0, 0.15), "back": (0.4, 1.0, 0.4),
        "side": (1.0, -0.15, 0.2), "top": (0.0, -0.3, 1.0)}
for v in views:
    d = Vector(dirs[v]).normalized()
    fov = 2 * math.atan(18.0 / cam.lens)
    dist = radius / math.sin(fov / 2) * 1.1
    co.location = centre + d * dist
    co.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = os.path.join(out, "%s_%s.png" % (name, v))
    bpy.ops.render.render(write_still=True)
    print("ref", scene.render.filepath)
