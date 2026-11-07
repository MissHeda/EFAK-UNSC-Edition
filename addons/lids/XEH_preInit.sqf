#include "script_component.hpp"

ADDON = false;

#include "XEH_PREP.hpp"

// The kits shown open right now: [holder, prop, item class].
GVAR(open) = [];

[
    QGVAR(enabled),
    "CHECKBOX",
    ["Open kit lids", "When you open the inventory on a kit lying on its own on the ground,
its lid swings open while you look inside.

Only you see it."],
    "EFAK: UNSC Edition",
    true
] call CBA_fnc_addSetting;

ADDON = true;
