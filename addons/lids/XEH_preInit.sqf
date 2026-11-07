#include "script_component.hpp"

ADDON = false;

#include "XEH_PREP.hpp"

// The holders shown open right now: [holder, [[prop, kit class]], copy, pieces, opened by, only kit].
GVAR(open) = [];
// Slots per holder model, see fnc_holderSlots.
GVAR(slots) = createHashMap;
// What EFAK's kit window shows on the ground: [holder, kit class] or [].
GVAR(kitWindow) = [];

[
    QGVAR(enabled),
    "CHECKBOX",
    ["Open kit lids", "When you open the inventory on kits lying
on the ground, or a kit's window, their lids
swing open while you look inside.

Only you see it."],
    "EFAK: UNSC Edition",
    true
] call CBA_fnc_addSetting;

ADDON = true;
