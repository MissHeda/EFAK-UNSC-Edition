#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Closes the lids fnc_openHolder opened: the lids swing shut, then the props and the holder's copy
 * go and the holder shows again. Kits taken out meanwhile lose their props at once. A holder still
 * open for someone else (another source, another player) only loses this one and stays open.
 *
 * Arguments:
 * 0: Only those opened by this source (see fnc_openHolder), "" for all <STRING> (default: "")
 * 1: At once, without the swing and sound <BOOL> (default: false)
 *
 * Return Value:
 * None
 *
 * Example:
 * ["kit"] call efku_lids_fnc_closeLids;
 *
 * Public: No
 */

params [["_source", ""], ["_instant", false]];

private _closing = [];
{
    private _users = _x select 4;
    if (_source isEqualTo "") then {
        _users resize 0;
    } else {
        private _i = _users find _source;
        if (_i != -1) then {_users deleteAt _i};
    };
    if (_users isEqualTo []) then {_closing pushBack _x};
} forEach GVAR(open);
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
        // Marks this close as the latest, see fnc_restoreHolder; the kits' casters stay hidden while
        // the props swing shut and cast the shadow themselves (fnc_shadows).
        _holder setVariable [QGVAR(closing), _swing];
        _holder setVariable [QGVAR(closingIndices), _x select 6];
        [FUNC(restoreHolder), [_holder, _swing, _copy], 1.05] call CBA_fnc_waitAndExecute;
    };
} forEach _closing;
