#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * InventoryOpened: with the lids set to open in the inventory too, opens every kit in the ground
 * holders the player is looking into. InventoryClosed shuts them (fnc_requestClose "inventory").
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Container <OBJECT>
 * 2: Second container <OBJECT> (default: objNull)
 *
 * Return Value:
 * None
 *
 * Example:
 * [player, _holder] call efku_lids_fnc_openLids;
 *
 * Public: No
 */

params ["", "_container", ["_second", objNull]];

if (GVAR(mode) < 2) exitWith {};

{
    if (!isNull _x) then {
        [_x, "", "inventory"] call FUNC(requestOpen);
    };
} forEach ([_container] + ([[_second], []] select (isNull _second || {!isNull attachedTo _second})));
// (the ground tab beside another container: not a pile fixed to a vehicle the player did not open)
