"""Writes addons/kits/data/model.cfg and addons/eup/data/model.cfg:

    python tools/models/make_model_cfg.py

Every kit's lid turns about its hinge's pin (memory points "lid_axis") when the animation source "lid"
goes from 0 to 1. Kits with latches first swing those out (selections "latch<k>" about "latch<k>_axis",
made by bail_latch() in unsc_lib) in the first LATCH_PHASE of the source, so they hang down before the
lid moves; closing runs backwards - lid shut, then the latches. In an inventory or a holder the model
stays shut; efku_lids shows a ground kit by an animated prop while its kit window is open.

Signs checked in game (2026-11-07): back hinges open with a positive angle, the IFAK's front hinge
(at the foot of its lid) with a negative one. A latch swings out with a negative angle: bail_latch
builds every latch so that it turns the same way about its own pin.
"""
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LATCH_PHASE = 0.3
LATCH_ANGLE = -2.9   # about 166 degrees: out, down, and hanging a little clear of the case

# addon: [(kit, lid angle, latches, comment)]
KITS = {
    "kits": [
        ("ifak", -1.66, 1, "front lid, hinged at its foot (opens away from the latch); the IFAK lies on its\n"
                           "    // back, so it swings up about 95 degrees. The latch hangs down its end."),
        ("afak", 1.75, 1, "upper half hinged at the back: up about 100 degrees"),
        ("mfak", 1.75, 2, "lid cap hinged at the back: up about 100 degrees"),
        ("mfakplus", 1.75, 2, "lid cap hinged at the back: up about 100 degrees"),
        ("narcbox", 1.75, 2, "upper shell hinged at the back: up about 100 degrees"),
    ],
    "eup": [
        ("utility_pouch", 1.92, 0, "lid and flap hinged at the back: up about 110 degrees"),
        ("ammo_pouch", 1.92, 0, "both lids hinged at the back: up about 110 degrees"),
        ("ammo_bag", 1.75, 2, "lid cap hinged at the back: up about 100 degrees"),
        ("engineer_bag", 1.75, 2, "lid cap hinged at the back: up about 100 degrees"),
        ("cbrn_bag", 1.75, 2, "lid cap hinged at the back: up about 100 degrees"),
        ("special_ammo", 1.75, 2, "lid cap hinged at the back: up about 100 degrees"),
        ("ordnance_crate", 1.75, 2, "upper shell hinged at the back: up about 100 degrees"),
    ],
}


def anim(name, axis, lo, hi, angle):
    return """            class %s {
                type = "rotation";
                source = "lid";
                selection = "%s";
                axis = "%s";
                memory = 1;
                minValue = %s;
                maxValue = %s;
                angle0 = 0;
                angle1 = %s;
            };
""" % (name, name, axis, lo, hi, angle)


def model_cfg(kits):
    head = "// Made by tools/models/make_model_cfg.py - change it there.\n//\n// " + \
        __doc__.strip().split("\n\n", 1)[1].replace("\n", "\n// ").replace("// \n", "//\n") + "\n"
    out = [head, "class CfgSkeletons {\n    class Default {\n        isDiscrete = 1;\n        skeletonInherit = \"\";\n"
                 "        skeletonBones[] = {};\n    };\n"]
    for n in sorted({k[2] for k in kits}):
        bones = ['"lid", ""'] + ['"latch%d", ""' % (i + 1) for i in range(n)]
        out.append("    class efku_lid%s: Default {\n        skeletonBones[] = {%s};\n    };\n"
                   % (n or "", ", ".join(bones)))
    out.append("};\n\nclass CfgModels {\n    class Default {\n        sectionsInherit = \"\";\n        sections[] = {};\n"
               "        skeletonName = \"\";\n    };\n")
    for kit, angle, latches, comment in kits:
        out.append("    // %s\n" % comment)
        if latches:
            out.append("    // %s first: %s out and %s down\n" % (
                ("both latches", "they swing", "hang") if latches > 1 else ("the latch", "it swings", "hangs")))
        out.append("    class %s: Default {\n        skeletonName = \"efku_lid%s\";\n        class Animations {\n"
                   % (kit, latches or ""))
        for i in range(latches):
            out.append(anim("latch%d" % (i + 1), "latch%d_axis" % (i + 1), 0, LATCH_PHASE, LATCH_ANGLE))
        out.append(anim("lid", "lid_axis", LATCH_PHASE if latches else 0, 1, angle))
        out.append("        };\n    };\n")
    out.append("    // the open twins the lids addon swings open (contents in every LOD): same skeleton and animations\n")
    for kit, *_ in kits:
        out.append("    class %s_open: %s {};\n" % (kit, kit))
    out.append("    // the kits as world objects (addons/boxes): the open twin standing up, same animations\n")
    for kit, *_ in kits:
        out.append("    class %s_box: %s {};\n" % (kit, kit))
    out.append("    // shadow casters for kits lying in ground holders (efku_lids), no animation\n")
    for kit, *_ in kits:
        out.append("    class %s_shadow: Default {};\n" % kit)
    out.append("};\n")
    return "".join(out)


for addon, kits in KITS.items():
    path = os.path.join(REPO, "addons", addon, "data", "model.cfg")
    with open(path, "w", newline="\n") as f:
        f.write(model_cfg(kits))
    print("wrote", path)
