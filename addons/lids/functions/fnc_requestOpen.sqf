#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Opens a holder's lids here and, with "Others see it" on, for every other player too: they run
 * fnc_openHolder themselves (fnc_remoteOpen), each with their own local props.
 *
 * Arguments:
 * 0: Holder <OBJECT>
 * 1: Only this kit class, "" for every kit in the holder <STRING>
 * 2: Who opens it here: "kit" or "inventory" <STRING>
 *
 * Return Value:
 * Opened <BOOL>
 *
 * Example:
 * [_holder, "efak_IFAK_7", "kit"] call efku_lids_fnc_requestOpen;
 *
 * Public: No
 */

params ["_holder", "_only", "_source"];

private _opened = [_holder, _only, _source] call FUNC(openHolder);

if (_opened && {GVAR(sync)} && {isMultiplayer}) then {
    [QGVAR(remoteOpen), [_holder, _only, _source, clientOwner]] call CBA_fnc_globalEvent;
};

_opened
