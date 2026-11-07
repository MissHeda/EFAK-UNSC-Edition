#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Opens the lids of the kits in the ground holders the player just opened the inventory on: a holder
 * that holds nothing but one kit is hidden, locally, and the kit's prop (efku_lidProp of its class)
 * takes its place and swings its lid open. fnc_closeLids puts everything back.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Container <OBJECT>
 * 2: Second container <OBJECT> (default: objNull)
 *
 * Return Value:
 * None
 *
 * Example:
 * [player, _holder] call efku_lids_fnc_openLids;
 *
 * Public: No
 */

params ["", "_container", ["_second", objNull]];

{
    private _holder = _x;

    if (isNull _holder) then {continue};
    if !(_holder isKindOf "WeaponHolder" || {_holder isKindOf "WeaponHolderSimulated"}) then {continue};
    if ((GVAR(open) findIf {(_x select 0) isEqualTo _holder}) != -1) then {continue};

    // Only a kit lying on its own: with anything else in the holder, hiding it would hide that too.
    private _cargo = (itemCargo _holder) + (weaponCargo _holder) + (magazineCargo _holder) + (backpackCargo _holder);

    if (count _cargo != 1) then {continue};

    private _item = _cargo select 0;
    private _propClass = getText (configFile >> "CfgWeapons" >> _item >> "efku_lidProp");
    private _propConfig = configFile >> "CfgVehicles" >> _propClass;

    if (_propClass isEqualTo "" || {!isClass _propConfig}) then {continue};

    private _offset = getArray (_propConfig >> "efku_offset");
    if (count _offset != 3) then {_offset = [0, 0, 0]};
    private _turn = getNumber (_propConfig >> "efku_turn");

    // Where the kit lies: on whatever surface is under the holder (ground, a table, a crate), not at
    // the holder's own centre, which floats above it.
    private _ground = getPosASLVisual _holder;
    private _hits = lineIntersectsSurfaces [_ground vectorAdd [0, 0, 0.5], _ground vectorAdd [0, 0, -2], _holder, objNull, true, 1, "GEOM", "NONE"];
    if (_hits isNotEqualTo []) then {
        _ground = (_hits select 0) select 0;
    };

    // In a holder a kit shows its front against the holder's own direction (measured in game). The
    // kit models are built with their top along the model's y axis and their front along z (the
    // way a holder shows items upright), so the prop points y up and z where the front faces.
    private _front = _holder vectorModelToWorldVisual [-(sin _turn), -(cos _turn), 0];
    _front = vectorNormalized [_front select 0, _front select 1, 0];

    private _prop = _propClass createVehicleLocal [0, 0, 0];
    _prop setVectorDirAndUp [[0, 0, 1], _front];
    _prop setPosWorld (_ground vectorAdd (_holder vectorModelToWorldVisual _offset));

    _holder hideObject true;
    _prop animateSource ["lid", 1];

    GVAR(open) pushBack [_holder, _prop, _item];
} forEach [_container, _second];
