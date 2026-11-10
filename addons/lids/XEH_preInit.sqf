#include "script_component.hpp"

ADDON = false;

#include "XEH_PREP.hpp"

// The holders shown open right now: [holder, [[prop, kit class]], copy, pieces, opened by, only kit,
// indices of the opened pieces].
GVAR(open) = [];
// Slots per holder model, see fnc_holderSlots.
GVAR(slots) = createHashMap;
// Prop class per item class, see fnc_propOf.
GVAR(propOf) = createHashMap;
// Shadow casters per holder (its efku_lids_key): [holder, pieces, [[caster, piece index, prop config]], last place].
GVAR(casters) = createHashMap;
GVAR(nextKey) = 0;
GVAR(tick) = 0;
// What EFAK's kit window shows on the ground: [holder, kit class] or [].
GVAR(kitWindow) = [];

[
    QGVAR(mode),
    "LIST",
    ["Open kit lids", "When a kit lying on the ground swings
its lid open.

Never: kits on the ground stay shut.

Kit window: when you open its kit
window, and shut again when you close it.

Inventory and kit window: also when you
look into a pile with kits in it."],
    "EFAK: UNSC Edition",
    [[0, 1, 2], ["Never", "Kit window", "Inventory and kit window"], 1],
    1
] call CBA_fnc_addSetting;

[
    QGVAR(sync),
    "CHECKBOX",
    ["Others see it", "Other players nearby see the lids you
open swing open and shut too.

Off: only you see them."],
    "EFAK: UNSC Edition",
    true,
    1
] call CBA_fnc_addSetting;

ADDON = true;
