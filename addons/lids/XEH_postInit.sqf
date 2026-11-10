#include "script_component.hpp"

if (!hasInterface) exitWith {};

// Kits on the ground lie shut. EFAK's kit window opens the kit it shows (fnc_watch); with the lids set
// to open in the inventory as well, so does looking into a pile (fnc_openLids). Other players' opens
// arrive as events (fnc_requestOpen / fnc_requestClose).
[{call FUNC(watch)}, 0.2] call CBA_fnc_addPerFrameHandler;

["CAManBase", "InventoryOpened", {
    params ["_unit"];

    if (_unit isEqualTo (call CBA_fnc_currentUnit)) then {
        _this call FUNC(openLids);
    };

    // true here would stop the inventory from opening
    false
}] call CBA_fnc_addClassEventHandler;

["CAManBase", "InventoryClosed", {
    params ["_unit"];

    if (_unit isEqualTo (call CBA_fnc_currentUnit)) then {
        ["inventory"] call FUNC(requestClose);
    };
}] call CBA_fnc_addClassEventHandler;

[QGVAR(remoteOpen), {_this call FUNC(remoteOpen)}] call CBA_fnc_addEventHandler;
[QGVAR(remoteClose), {_this call FUNC(remoteClose)}] call CBA_fnc_addEventHandler;
