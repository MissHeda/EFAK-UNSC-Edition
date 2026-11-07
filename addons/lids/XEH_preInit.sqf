#include "script_component.hpp"

ADDON = false;

#include "XEH_PREP.hpp"

// The holders shown open right now: [holder, [[prop, kit class]], copy, pieces, opened by, only kit].
GVAR(open) = [];
// Slots per holder model, see fnc_holderSlots.
GVAR(slots) = createHashMap;
// Prop class per item class, see fnc_propOf.
GVAR(propOf) = createHashMap;
// Shadow casters per holder (hashValue): [holder, pieces, [[caster, piece index, prop config]], last place].
GVAR(casters) = createHashMap;
GVAR(tick) = 0;
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
