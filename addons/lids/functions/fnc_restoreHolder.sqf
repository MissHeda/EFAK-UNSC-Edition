#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Takes a closed holder's props and copy away and shows the holder again - unless it has been
 * opened anew meanwhile, then it stays hidden behind its new props.
 *
 * Arguments:
 * 0: Holder <OBJECT>
 * 1: Props <ARRAY>
 * 2: Copy <OBJECT>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_holder, _props, _copy] call efku_lids_fnc_restoreHolder;
 *
 * Public: No
 */

params ["_holder", "_props", "_copy"];

{deleteVehicle _x} forEach _props;
deleteVehicle _copy;

if (!isNull _holder && {(GVAR(open) findIf {(_x select 0) isEqualTo _holder}) == -1}) then {
    _holder hideObject false;
};
