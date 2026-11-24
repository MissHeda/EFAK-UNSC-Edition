#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The player opened or closed an inventory: tells the server when a kit box is in it, so its lid
 * swings open, and shut again when the player is done. Off with the lids setting "Never".
 *
 * Arguments:
 * 0: Container <OBJECT>
 * 1: Second container <OBJECT>
 * 2: Opened <BOOL>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_box, objNull, true] call efku_boxes_fnc_onInventory;
 *
 * Public: No
 */

params ["_container", "_second", "_opened"];

if (!isNull GVAR(current)) then {
    [QGVAR(use), [GVAR(current), clientOwner, false]] call CBA_fnc_serverEvent;
    GVAR(current) = objNull;
};
if (!_opened || {(missionNamespace getVariable ["efku_lids_mode", 1]) == 0}) exitWith {};

// only what was opened: a box that merely stands near (the ground tab) stays shut
private _box = [_container] select {!isNull _x && {_x isKindOf QGVAR(base)}};
if (_box isEqualTo []) exitWith {};
GVAR(current) = _box select 0;
[QGVAR(use), [GVAR(current), clientOwner, true]] call CBA_fnc_serverEvent;
