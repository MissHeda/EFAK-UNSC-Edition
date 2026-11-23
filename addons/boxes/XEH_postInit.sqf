#include "script_component.hpp"

// Someone opened or closed a box's inventory: the server keeps count and swings the lid.
[QGVAR(use), {_this call FUNC(use)}] call CBA_fnc_addEventHandler;
[QGVAR(toItem), {_this call FUNC(toItem)}] call CBA_fnc_addEventHandler;

if (isServer) then {
    // A player who leaves with a box open closes it.
    addMissionEventHandler ["PlayerDisconnected", {
        params ["", "", "", "", "_owner"];
        {
            if (_owner in (_x getVariable [QGVAR(users), []])) then {[_x, _owner, false] call FUNC(use)};
        } forEach +GVAR(users);
    }];
};

if (!hasInterface) exitWith {};

// A kit dropped beside a vehicle goes into a holder PH Vehicles Arsenal can attach.
["CAManBase", "Put", {_this call FUNC(onPut)}] call CBA_fnc_addClassEventHandler;

["CAManBase", "InventoryOpened", {
    params ["_unit", "_container", ["_second", objNull]];
    if (_unit != ACE_player) exitWith {};
    [_container, _second, true] call FUNC(onInventory);
}] call CBA_fnc_addClassEventHandler;

["CAManBase", "InventoryClosed", {
    params ["_unit"];
    if (_unit != ACE_player) exitWith {};
    [objNull, objNull, false] call FUNC(onInventory);
}] call CBA_fnc_addClassEventHandler;
