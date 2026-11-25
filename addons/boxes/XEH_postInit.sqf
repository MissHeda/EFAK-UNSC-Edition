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
            private _box = _x;
            {
                if ((_x select 0) == _owner) then {[_box, _owner, false, _x select 1] call FUNC(use)};
            } forEach +(_box getVariable [QGVAR(users), []]);
        } forEach +GVAR(users);
    }];
};

if (!hasInterface) exitWith {};

// The kit window (EFAK) open on a kit in a box or kit item: its lid opens, as the inventory's does.
// Checked every frame, so going from the inventory to the kit window hardly moves the lid.
GVAR(kitBox) = objNull;
[{
    private _want = objNull;
    if ((missionNamespace getVariable ["efku_lids_mode", 1]) > 0 && {!isNull (uiNamespace getVariable ["efak_gui_display", displayNull])}) then {
        private _owner = missionNamespace getVariable ["efak_gui_owner", objNull];
        if (!isNull _owner && {_owner isKindOf QGVAR(base) || {_owner isKindOf QGVAR(drop)}}) then {_want = _owner};
    };
    if (_want isEqualTo GVAR(kitBox)) exitWith {};
    if (!isNull GVAR(kitBox)) then {[QGVAR(use), [GVAR(kitBox), clientOwner, false, "kit"]] call CBA_fnc_serverEvent};
    if (!isNull _want) then {[QGVAR(use), [_want, clientOwner, true, "kit"]] call CBA_fnc_serverEvent};
    GVAR(kitBox) = _want;
}] call CBA_fnc_addPerFrameHandler;

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
