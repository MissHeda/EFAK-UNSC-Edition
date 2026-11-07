"""Builds one kit from start to end, in background Blender:

    blender -b -P tools/models/build_kit.py -- <kit> [--fast] [--views icon,front,...]

kit: ifak, afak, mfak, mfakplus or narcbox (see kits.py). Needs the decals first
(python tools/models/make_decals.py). Writes
    addons/kits/data/<kit>.p3d, <kit>.rvmat, <kit>_co.paa, <kit>_nohq.paa, <kit>_smdi.paa
    addons/kits/ui/<kit>_ca.paa (inventory picture, from the icon render)
    tools/models/out/<kit>/ (the PNGs and the renders, not in git)
--fast bakes at 512 with few samples, to look at shapes quickly; it writes no game files.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unsc_lib as U  # noqa: E402

# Blender exits 0 even when the script fails: make a failure a failure
def _fail(kind, value, tb):
    import traceback
    traceback.print_exception(kind, value, tb)
    os._exit(1)


sys.excepthook = _fail
import kits  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
kit = argv[0]
fast = "--fast" in argv
views = ["icon"]
if "--views" in argv:
    views = argv[argv.index("--views") + 1].split(",")

# The shadow LOD first: the same parts, sharp and without the small ones, each a closed volume. A
# convex hull would span the hollows (under a handle, round a cut corner) and shade the model itself.
U.reset()
U.SHADOW[0] = True
kits.BUILDERS[kit]()
shadow_ob = U.assemble(kit + "_shadow")
# Ground holders put an item's origin 4.3 cm above the ground (dummyweapon.p3d's proxies, measured in
# game), made for models centred on their origin. Ours stand on it, so every kit is set down by that
# much on export - in its holder it then rests on the ground, and so does its prop.
HOLDER_LIFT = 0.043352
drop = Matrix.Translation((0, 0, -HOLDER_LIFT))
U.EXPORT[0] = drop
# A kit that lies on its back in the game is turned only on export, then set down again: centred on
# the origin, its lowest point on it - where a holder puts the model.
if kit in kits.EXPORT_ROT:
    rot = U._euler(kits.EXPORT_ROT[kit]).to_matrix().to_4x4()
    pts = [rot @ (shadow_ob.matrix_world @ v.co) for v in shadow_ob.data.vertices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    U.EXPORT[0] = drop @ Matrix.Translation((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2, -lo.z)) @ rot
    print("export turn", kits.EXPORT_ROT[kit], "shift", tuple(round(c, 4) for c in U.EXPORT[0].translation))
shadow_tris = U.mesh_tris(U.lod_mesh(shadow_ob, 1.0), use_comp=True)
print("shadow parts:", len({t[0][4] for t in shadow_tris}), "triangles:", len(shadow_tris))
open_edges = U.shadow_open_edges(shadow_tris)
if open_edges:
    raise SystemExit("shadow LOD of %s has %d open edges" % (kit, open_edges))
U.SHADOW[0] = False
U.PARTS.clear()
U.PROJECTORS.clear()
U.LID_AXIS.clear()

U.reset()
size = kits.BUILDERS[kit]()
overlaps = U.check_overlaps() + U.check_lid_attached()
for line in overlaps:
    print("OVERLAP", kit, line)
ob = U.assemble(kit)
print("parts joined:", len(ob.data.polygons), "faces")
problems = U.check_decals(ob)
for line in problems:
    print("DECAL", kit, line)
if "--check" in argv:
    print("DECALCHECK", kit, "ok" if not problems else "%d problems" % len(problems))
    print("OVERLAPCHECK", kit, "ok" if not overlaps else "%d problems" % len(overlaps))
    sys.exit(0)
if problems and not fast:
    raise SystemExit("decals of %s run over edges or lack room, see DECAL lines above" % kit)
if overlaps and not fast:
    raise SystemExit("small parts of %s run into each other, see OVERLAP lines above" % kit)
U.unwrap(ob, margin=0.003)

if fast:
    paths = U.bake(ob, kit, size=512, samples=8)
    U.render_views(ob, paths, kit, views, size=512, samples=24)
    sys.exit(0)

paths = U.bake(ob, kit, size=size, samples=128)
addon = kits.ADDON[kit]
data = os.path.join(U.REPO, "addons", addon, "data")
ui = os.path.join(U.REPO, "addons", addon, "ui")
os.makedirs(data, exist_ok=True)
os.makedirs(ui, exist_ok=True)
game_dir = "z\\efku\\addons\\%s\\data" % addon

nohq_dx = os.path.join(U.OUT, kit, "%s_nohq_dx.png" % kit)
U.flip_green(paths["nohq"], nohq_dx)
U.to_paa(paths["co"], os.path.join(data, kit + "_co.paa"))
U.to_paa(nohq_dx, os.path.join(data, kit + "_nohq.paa"))
# specular and ambient shadow carry no fine detail: half size is plenty
U.to_paa(U.downscale(paths["smdi"], size // 2), os.path.join(data, kit + "_smdi.paa"))
U.to_paa(U.downscale(paths["as"], size // 2), os.path.join(data, kit + "_as.paa"))
with open(os.path.join(data, kit + ".rvmat"), "w", newline="\n") as f:
    f.write(U.RVMAT % {"dir": game_dir, "kit": kit})

U.write_p3d(os.path.join(data, kit + ".p3d"), ob, game_dir + "\\%s_co.paa" % kit, game_dir + "\\%s.rvmat" % kit,
            shadow=shadow_tris)
U.write_shadow_p3d(os.path.join(data, kit + "_shadow.p3d"), shadow_tris)

shots = U.render_views(ob, paths, kit, views, size=1024, samples=128)
U.to_paa(shots["icon"], os.path.join(ui, kit + "_ca.paa"))
print("done", kit)
