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

    private _prop = _propClass createVehicleLocal [0, 0, 0];
    _prop setVectorDirAndUp [_holder vectorModelToWorldVisual [sin _turn, cos _turn, 0], vectorUpVisual _holder];
    _prop setPosWorld (_holder modelToWorldVisualWorld _offset);

    _holder hideObject true;
    _prop animateSource ["lid", 1];

    GVAR(open) pushBack [_holder, _prop, _item];
} forEach [_container, _second];
