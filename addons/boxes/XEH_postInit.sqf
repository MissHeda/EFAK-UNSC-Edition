#include "script_component.hpp"

// Someone opened or closed a box's inventory: the server keeps count and swings the lid.
[QGVAR(use), {_this call FUNC(use)}] call CBA_fnc_addEventHandler;
[QGVAR(toItem), {_this call FUNC(toItem)}] call CBA_fnc_addEventHandler;
[QGVAR(dropTaken), {_this call FUNC(dropTaken)}] call CBA_fnc_addEventHandler;

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

// A kit item someone took the kit out of goes away once it is empty.
["CAManBase", "Take", {
    params ["_unit", "_container"];
    if (local _unit && {getNumber (configOf _container >> "efku_item") == 1}) then {
        [QGVAR(dropTaken), [_container]] call CBA_fnc_serverEvent;
    };
}] call CBA_fnc_addClassEventHandler;

["CAManBase", "InventoryOpened", {
    params ["_unit", "_container", ["_second", objNull]];
    if (_unit != ACE_player) exitWith {};
    [_container, _second, true] call FUNC(onInventory);
    GVAR(opened) = _container;
    // A kit in a box or kit item opens by double click, as one on the ground does (EFAK only listens
    // on the ground list; a box shows what it holds in the container list next to it).
    if (_container isKindOf QGVAR(base) || {_container isKindOf QGVAR(drop)}) then {
        [{!isNull findDisplay 602}, {call FUNC(hookDoubleClick)}, [], 5] call CBA_fnc_waitUntilAndExecute;
    };
}] call CBA_fnc_addClassEventHandler;

["CAManBase", "InventoryClosed", {
    params ["_unit"];
    if (_unit != ACE_player) exitWith {};
    [objNull, objNull, false] call FUNC(onInventory);
    // a kit item emptied some other way than a Take (dragged into a vehicle, a script) goes as well
    private _opened = missionNamespace getVariable [QGVAR(opened), objNull];
    GVAR(opened) = objNull;
    if (!isNull _opened && {getNumber (configOf _opened >> "efku_item") == 1}) then {
        [QGVAR(dropTaken), [_opened]] call CBA_fnc_serverEvent;
    };
}] call CBA_fnc_addClassEventHandler;
