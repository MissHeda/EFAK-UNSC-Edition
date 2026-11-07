#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Takes a closed holder's props and copy away and shows the holder again - unless it has been
 * opened anew meanwhile, then it stays hidden behind its new props, or closed anew, then the later
 * close shows it when its own lids are shut.
 *
 * Arguments:
 * 0: Holder <OBJECT>
 * 1: Props, the swinging ones fnc_closeLids waited for, or [] <ARRAY>
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

// Only the latest close shows the holder: an earlier one's delayed call must not show it while the
// later lids still swing shut. Compared before the props go (deleted ones would all look alike).
private _latest = !isNull _holder && {(_holder getVariable [QGVAR(closing), []]) isEqualTo _props};

{deleteVehicle _x} forEach _props;
deleteVehicle _copy;

if (!_latest) exitWith {};
_holder setVariable [QGVAR(closing), nil];

if ((GVAR(open) findIf {(_x select 0) isEqualTo _holder}) == -1) then {
    _holder hideObject false;
};
