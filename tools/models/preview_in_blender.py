"""Builds one kit in the OPEN Blender (through the MCP bridge) for a look round: the parts, their
looks as flat viewport colours, no bake. The lid swings open when OPEN is true.

    node ~/.claude/blender-bridge/run.js tools/models/preview_in_blender.py

Set KIT (and OPEN) below, or run with the environment variable EFKU_KIT. Everything lands in a
collection "efku_<kit>" that is replaced on the next run; the rest of the scene stays as it is.
"""
import os
import sys

KIT = os.environ.get("EFKU_KIT", "ammo_bag")
OPEN = os.environ.get("EFKU_OPEN", "1") == "1"
HERE = r"C:\Users\Heda\GitHub Repos\EFAK-UNSC-Edition\tools\models"

import bpy  # noqa: E402

if HERE not in sys.path:
    sys.path.insert(0, HERE)
for m in ("unsc_lib", "kits", "interiors"):
    if m in sys.modules:
        del sys.modules[m]
import unsc_lib as U  # noqa: E402
import kits  # noqa: E402

name = "efku_" + KIT
old = bpy.data.collections.get(name)
if old is not None:
    for ob in list(old.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(old)

scene = bpy.context.scene
col = bpy.data.collections.new(name)
scene.collection.children.link(col)

# build into the scene collection, then move into ours
before = set(bpy.data.objects)
# no U.reset() here: that wipes the whole file; only the builder's own state is cleared
import random
random.seed(7)
U.PARTS.clear()
U.PROJECTORS.clear()
U.LID_AXIS.clear()
U.LATCHES.clear()
U.GROUP[:] = [""]
U.CLUSTER[:] = [None]
U.SHADOW[0] = False
if bpy.context.object and bpy.context.object.mode != "OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")
kits.BUILDERS[KIT]()
ob = U.assemble(KIT)
U.PROJECTORS.clear()
for o in set(bpy.data.objects) - before:
    if o.name in scene.collection.objects:
        scene.collection.objects.unlink(o)
    if o.name not in col.objects:
        col.objects.link(o)

# flat viewport colours per look
for slot in ob.material_slots:
    lk = U.LOOKS.get(slot.material.name.split(".")[0])
    if lk:
        c = lk["color"]
        slot.material.diffuse_color = (c[0], c[1], c[2], 1.0)
        slot.material.roughness = 1.0 - lk["gloss"]
        slot.material.metallic = lk["spec"] * 2
if OPEN:
    U.swing_lid(ob)
ob.select_set(True)
bpy.context.view_layer.objects.active = ob

# solid shading with material colours, frame the kit
for area in bpy.context.screen.areas:
    if area.type == "VIEW_3D":
        for space in area.spaces:
            if space.type == "VIEW_3D":
                space.shading.type = "SOLID"
                space.shading.color_type = "MATERIAL"
                space.shading.light = "STUDIO"
        with bpy.context.temp_override(area=area, region=[r for r in area.regions if r.type == "WINDOW"][0]):
            bpy.ops.view3d.view_selected()
print("built", KIT, "faces", len(ob.data.polygons), "open" if OPEN else "shut")
