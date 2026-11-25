#!/usr/bin/env python3
"""Generates the pool of instance classes of the two cases this mod adds itself.

They are kits of Enhanced First Aid Kits' framework, which keeps contents per class name: every kit
type ships one prototype plus a pool of concrete classes inheriting from it, and a prototype a
player picks up is swapped for a free one (see Enhanced First Aid Kits' tools/generate_instances.py).

Usage:  python tools/generate_instances.py
"""
import io
import os

# Keep in sync with EFKU_INSTANCES_PER_CASE in addons/eup/config.cpp
INSTANCES = 300

CASES = ["efku_SpecialAmmoCase", "efku_OrdnanceCase"]

HEADER = """// One concrete class per case instance.
"""

TEMPLATE = (
    'class {kit}_{i}: {kit} {{'
    'scope = 1; scopeCurator = 0; ace_arsenal_hide = 1; ace_arsenal_uniqueBase = "{kit}"; '
    'EFAK_prototype = 0; EFAK_instanceId = {i};'
    '}};'
)

OUT = os.path.join(os.path.dirname(__file__), "..", "addons", "eup", "CfgWeapons_instances.hpp")


def main():
    lines = [HEADER]
    for kit in CASES:
        lines.append("// %s instances" % kit)
        for i in range(1, INSTANCES + 1):
            lines.append(TEMPLATE.format(kit=kit, i=i))
        lines.append("")
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))
    print("wrote %s (%d classes)" % (os.path.normpath(OUT), len(CASES) * INSTANCES))


if __name__ == "__main__":
    main()
