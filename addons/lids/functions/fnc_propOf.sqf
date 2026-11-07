#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The prop class of an item (efku_lidProp in its CfgWeapons class), "" for anything that is no kit
 * with a prop. Remembered per class.
 *
 * Arguments:
 * 0: Item class <STRING>
 *
 * Return Value:
 * Prop class <STRING>
 *
 * Example:
 * ["efak_IFAK_7"] call efku_lids_fnc_propOf;
 *
 * Public: No
 */

params ["_class"];

private _key = toLowerANSI _class;
private _prop = GVAR(propOf) get _key;

if (isNil "_prop") then {
    _prop = getText (configFile >> "CfgWeapons" >> _class >> "efku_lidProp");
    if (_prop isNotEqualTo "" && {!isClass (configFile >> "CfgVehicles" >> _prop)}) then {_prop = ""};
    GVAR(propOf) set [_key, _prop];
};

_prop
