#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Gives the kits lying in ground holders near the camera their shadow. The game draws none for
 * items in a holder; each kit gets a local caster (the kit's own shadow LOD on an otherwise invisible
 * model, data\<kit>_shadow.p3d) on its very slot. Casters follow holders that move (a kit dropped,
 * falling, tipping) and hide while the kit is shown open by its prop, which casts its own.
 *
 * Arguments:
 * 0: Look for new and gone holders too, not only follow known ones <BOOL> (default: false)
 *
 * Return Value:
 * None
 *
 * Example:
 * [true] call efku_lids_fnc_shadows;
 *
 * Public: No
 */

params [["_scan", false]];

if (_scan) then {
    private _seen = [];

    {
        private _holder = _x;

        if (_holder getVariable [QGVAR(copy), false]) then {continue};
        if ((itemCargo _holder) findIf {([_x] call FUNC(propOf)) isNotEqualTo ""} == -1) then {continue};

        private _key = hashValue _holder;
        _seen pushBack _key;

        private _pieces = [_holder] call FUNC(holderPieces);
        private _known = GVAR(casters) getOrDefault [_key, []];

        if (_known isNotEqualTo [] && {(_known select 1) isEqualTo _pieces}) then {continue};

        {deleteVehicle (_x select 0)} forEach (_known param [2, []]);

        private _slots = [_holder] call FUNC(holderSlots);
        private _casters = [];

        {
            _x params ["_kind", "_class"];

            if (_kind isNotEqualTo "item" || {_forEachIndex >= count _slots}) then {continue};

            private _propClass = [_class] call FUNC(propOf);
            if (_propClass isEqualTo "") then {continue};

            private _config = configFile >> "CfgVehicles" >> _propClass;
            private _model = getText (_config >> "model");
            _model = (_model select [0, count _model - 4]) + "_shadow.p3d";

            private _caster = createSimpleObject [_model, [0, 0, 0], true];
            _casters pushBack [_caster, _forEachIndex, _config];
        } forEach _pieces;

        GVAR(casters) set [_key, [_holder, _pieces, _casters, []]];
    } forEach (nearestObjects [positionCameraToWorld [0, 0, 0], ["WeaponHolder", "WeaponHolderSimulated"], SHADOW_RANGE]);

    {
        if !(_x in _seen) then {
            {deleteVehicle (_x select 0)} forEach ((GVAR(casters) get _x) select 2);
            GVAR(casters) deleteAt _x;
        };
    } forEach (keys GVAR(casters));
};

// Follow the holders: put the casters where the kits are, show the ones whose kit is not open.
private _gone = [];
{
    _y params ["_holder", "", "_casters", "_at"];

    if (isNull _holder) then {
        {deleteVehicle (_x select 0)} forEach _casters;
        _gone pushBack _x;
        continue;
    };

    private _now = [getPosWorldVisual _holder, vectorDirVisual _holder, vectorUpVisual _holder];
    private _i = GVAR(open) findIf {(_x select 0) isEqualTo _holder};
    private _opened = if (_i == -1) then {[]} else {(GVAR(open) select _i) param [6, []]};

    if (_now isNotEqualTo _at) then {
        private _slots = [_holder] call FUNC(holderSlots);
        {
            _x params ["_caster", "_index", "_config"];
            [_holder, _slots select _index, _caster, _config] call FUNC(placeProp);
        } forEach _casters;
        _y set [3, _now];
    };

    {
        _x params ["_caster", "_index"];
        private _hide = _index in _opened;
        if (isObjectHidden _caster isNotEqualTo _hide) then {_caster hideObject _hide};
    } forEach _casters;
} forEach GVAR(casters);

{GVAR(casters) deleteAt _x} forEach _gone;
