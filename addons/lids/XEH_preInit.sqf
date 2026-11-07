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
    ["Open kit lids", "A kit lying on the ground stays shut.
When you open its kit window, its lid
swings open while you look inside, and
shuts again when you close the window.

Only you see it."],
    "EFAK: UNSC Edition",
    true
] call CBA_fnc_addSetting;

ADDON = true;
