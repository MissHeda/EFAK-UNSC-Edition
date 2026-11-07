"""Renders an SVG to a white-on-transparent PNG mask, in background Blender (no SVG library needed):

    blender -b -P tools/models/svg_to_png.py -- in.svg out.png [height_px]

make_decals.py colours and places the masks.
"""
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
src, dst = argv[0], argv[1]
height = int(argv[2]) if len(argv) > 2 else 1024

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_curve.svg(filepath=src)
obs = [o for o in bpy.context.scene.objects if o.type == "CURVE"]
for o in obs:
    o.data.fill_mode = "BOTH"
    o.data.dimensions = "2D"

# frame the drawing: its bounds in world space
pts = []
for o in obs:
    for c in o.bound_box:
        pts.append(o.matrix_world @ __import__("mathutils").Vector(c))
x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
w, h = x1 - x0, y1 - y0
pad = 0.02 * max(w, h)

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "FLAT"
scene.display.shading.color_type = "SINGLE"
scene.display.shading.single_color = (1, 1, 1)
scene.view_settings.view_transform = "Standard"
scene.render.film_transparent = True
scene.render.resolution_y = height
scene.render.resolution_x = max(8, round(height * (w + 2 * pad) / (h + 2 * pad)))
scene.render.filter_size = 1.0

cam = bpy.data.cameras.new("cam")
cam.type = "ORTHO"
cam.ortho_scale = max(w, h) + 2 * pad
co = bpy.data.objects.new("cam", cam)
scene.collection.objects.link(co)
co.location = ((x0 + x1) / 2, (y0 + y1) / 2, 10)
scene.camera = co
scene.render.filepath = dst
scene.render.image_settings.color_mode = "RGBA"
bpy.ops.render.render(write_still=True)
print("svg", src, "->", dst, scene.render.resolution_x, "x", scene.render.resolution_y)
