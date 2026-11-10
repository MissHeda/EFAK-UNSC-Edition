#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Another player opened a holder's lids (fnc_requestOpen): open them here as well, counted as theirs,
 * so their close shuts only what they opened. Far away holders are left alone.
 *
 * Arguments:
 * 0: Holder <OBJECT>
 * 1: Only this kit class, "" for every kit <STRING>
 * 2: Their source <STRING>
 * 3: Their client id <NUMBER>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_holder, "", "kit", 3] call efku_lids_fnc_remoteOpen;
 *
 * Public: No
 */

params ["_holder", "_only", "_source", "_owner"];

if (!hasInterface || {_owner == clientOwner} || {!GVAR(sync)} || {GVAR(mode) == 0}) exitWith {};
if (isNull _holder || {(_holder distance positionCameraToWorld [0, 0, 0]) > REMOTE_RANGE}) exitWith {};

[_holder, _only, format ["remote%1_%2", _owner, _source]] call FUNC(openHolder);
