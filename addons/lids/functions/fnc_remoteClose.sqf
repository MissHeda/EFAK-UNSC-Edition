#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Another player closed what they had opened from one source (fnc_requestClose): close it here too.
 *
 * Arguments:
 * 0: Their source <STRING>
 * 1: Their client id <NUMBER>
 *
 * Return Value:
 * None
 *
 * Example:
 * ["kit", 3] call efku_lids_fnc_remoteClose;
 *
 * Public: No
 */

params ["_source", "_owner"];

if (!hasInterface || {_owner == clientOwner}) exitWith {};

[format ["remote%1_%2", _owner, _source]] call FUNC(closeLids);
