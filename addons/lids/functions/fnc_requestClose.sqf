#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Closes what this player opened from one source, here and - with "Others see it" on - for every
 * other player (fnc_remoteClose).
 *
 * Arguments:
 * 0: The source: "kit" or "inventory" <STRING>
 *
 * Return Value:
 * None
 *
 * Example:
 * ["kit"] call efku_lids_fnc_requestClose;
 *
 * Public: No
 */

params ["_source"];

private _had = (GVAR(open) findIf {_source in (_x select 4)}) != -1;

[_source] call FUNC(closeLids);

if (_had && {GVAR(sync)} && {isMultiplayer}) then {
    [QGVAR(remoteClose), [_source, clientOwner]] call CBA_fnc_globalEvent;
};
