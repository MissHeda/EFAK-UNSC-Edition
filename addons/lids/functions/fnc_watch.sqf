#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Runs a few times a second. Opens the kit shown in EFAK's kit window when it lies on the ground,
 * and keeps open holders true to what they hold: one that changed (something taken out or put in)
 * is laid out anew, at once; one that is gone takes its props with it.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call efku_lids_fnc_watch;
 *
 * Public: No
 */

// The kit window: the kit it shows, and where that kit is.
private _want = [];
if (GVAR(enabled) && {!isNull (uiNamespace getVariable ["efak_gui_display", displayNull])}) then {
    private _owner = missionNamespace getVariable ["efak_gui_owner", objNull];
    private _kit = missionNamespace getVariable ["efak_gui_kitClass", ""];

    if (!isNull _owner && {_kit isNotEqualTo ""} && {_owner isKindOf "WeaponHolder" || {_owner isKindOf "WeaponHolderSimulated"}}) then {
        _want = [_owner, _kit];
    };
};

if (_want isNotEqualTo GVAR(kitWindow)) then {
    ["kit"] call FUNC(closeLids);
    GVAR(kitWindow) = _want;
};

if (_want isNotEqualTo [] && {(GVAR(open) findIf {(_x select 0) isEqualTo (_want select 0)}) == -1}) then {
    [_want select 0, _want select 1, "kit"] call FUNC(openHolder);
};

// Holders that changed while open.
{
    _x params ["_holder", "_props", "_copy", "_pieces", "_by", "_only"];

    if (isNull _holder || {([_holder] call FUNC(holderPieces)) isNotEqualTo _pieces}) then {
        {deleteVehicle (_x select 0)} forEach _props;
        GVAR(open) deleteAt (GVAR(open) findIf {(_x select 0) isEqualTo _holder && {(_x select 1) isEqualTo _props}});
        [_holder, [], _copy] call FUNC(restoreHolder);
        [_holder, _only, _by, true] call FUNC(openHolder);
    };
} forEach +GVAR(open);

// Shadows: new and gone holders once a second, moving ones every time.
GVAR(tick) = GVAR(tick) + 1;
[GVAR(tick) % 5 == 0] call FUNC(shadows);
