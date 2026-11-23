#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Server: a client opened or closed a kit box's inventory. The lid opens with the first and shuts
 * when the last one is done - for everyone, attached to a vehicle or not.
 *
 * Arguments:
 * 0: Box <OBJECT>
 * 1: Client <NUMBER>
 * 2: Opened <BOOL>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_box, 3, true] call efku_boxes_fnc_use;
 *
 * Public: No
 */

params ["_box", "_client", "_opened"];

if (!isServer || {isNull _box}) exitWith {};

private _users = _box getVariable [QGVAR(users), []];
private _was = _users isNotEqualTo [];
if (_opened) then {
    _users pushBackUnique _client;
} else {
    _users = _users - [_client];
};
_box setVariable [QGVAR(users), _users];
if (_users isEqualTo []) then {GVAR(users) = GVAR(users) - [_box]} else {GVAR(users) pushBackUnique _box};
private _is = _users isNotEqualTo [];
if (_was isEqualTo _is) exitWith {};

_box animateSource ["lid", [0, 1] select _is];
private _sound = getText (configOf _box >> "efku_sound");
playSound3D [format ["z\efku\addons\lids\sounds\%1_%2.ogg", _sound, ["close", "open"] select _is], _box, false,
    getPosASL _box, 1.5, 1, 25];
