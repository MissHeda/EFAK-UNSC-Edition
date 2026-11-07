#include "script_component.hpp"

if (!hasInterface) exitWith {};

["CAManBase", "InventoryOpened", {
    params ["_unit"];

    if (GVAR(enabled) && {_unit isEqualTo (call CBA_fnc_currentUnit)}) then {
        _this call FUNC(openLids);
    };

    // true here would stop the inventory from opening
    false
}] call CBA_fnc_addClassEventHandler;

["CAManBase", "InventoryClosed", {
    params ["_unit"];

    if (_unit isEqualTo (call CBA_fnc_currentUnit)) then {
        call FUNC(closeLids);
    };
}] call CBA_fnc_addClassEventHandler;
