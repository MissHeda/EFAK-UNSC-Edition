#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Closes the lids fnc_openHolder opened: the lids swing shut, then the props and the holder's copy
 * go and the holder shows again. Kits taken out meanwhile lose their props at once.
 *
 * Arguments:
 * 0: Only those opened by, "inventory" or "kit", "" for all <STRING> (default: "")
 * 1: At once, without the swing and sound <BOOL> (default: false)
 *
 * Return Value:
 * None
 *
 * Example:
 * ["inventory"] call efku_lids_fnc_closeLids;
 *
 * Public: No
 */

params [["_source", ""], ["_instant", false]];

private _closing = GVAR(open) select {_source isEqualTo "" || {(_x select 4) isEqualTo _source}};
GVAR(open) = GVAR(open) - _closing;

{
    _x params ["_holder", "_props", "_copy"];

    private _left = if (isNull _holder) then {[]} else {itemCargo _holder};
    private _swing = [];

    {
        _x params ["_prop", "_class"];

        if (!_instant && {_class in _left}) then {
            _prop animateSource ["lid", 0];
            _prop say3D [format [QGVAR(%1_close), getText (configOf _prop >> "efku_sound")], 20, 0.96 + random 0.08];
            _swing pushBack _prop;
        } else {
            deleteVehicle _prop;
        };
    } forEach _props;

    if (_swing isEqualTo []) then {
        [_holder, [], _copy] call FUNC(restoreHolder);
    } else {
        [FUNC(restoreHolder), [_holder, _swing, _copy], 0.65] call CBA_fnc_waitAndExecute;
    };
} forEach _closing;
