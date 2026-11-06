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
import kits  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
kit = argv[0]
fast = "--fast" in argv
views = ["icon"]
if "--views" in argv:
    views = argv[argv.index("--views") + 1].split(",")

U.reset()
size = kits.BUILDERS[kit]()
ob = U.assemble(kit)
print("parts joined:", len(ob.data.polygons), "faces")
U.unwrap(ob, margin=0.003)

if fast:
    paths = U.bake(ob, kit, size=512, samples=8)
    U.render_views(ob, paths, kit, views, size=512, samples=24)
    sys.exit(0)

paths = U.bake(ob, kit, size=size, samples=64)
data = os.path.join(U.REPO, "addons", "kits", "data")
ui = os.path.join(U.REPO, "addons", "kits", "ui")
os.makedirs(data, exist_ok=True)
os.makedirs(ui, exist_ok=True)
game_dir = "z\\efku\\addons\\kits\\data"

nohq_dx = os.path.join(U.OUT, kit, "%s_nohq_dx.png" % kit)
U.flip_green(paths["nohq"], nohq_dx)
U.to_paa(paths["co"], os.path.join(data, kit + "_co.paa"))
U.to_paa(nohq_dx, os.path.join(data, kit + "_nohq.paa"))
U.to_paa(paths["smdi"], os.path.join(data, kit + "_smdi.paa"))
with open(os.path.join(data, kit + ".rvmat"), "w", newline="\n") as f:
    f.write(U.RVMAT % {"dir": game_dir, "kit": kit})

U.write_p3d(os.path.join(data, kit + ".p3d"), ob, game_dir + "\\%s_co.paa" % kit, game_dir + "\\%s.rvmat" % kit)

shots = U.render_views(ob, paths, kit, views, size=1024, samples=128)
U.to_paa(shots["icon"], os.path.join(ui, kit + "_ca.paa"))
print("done", kit)
