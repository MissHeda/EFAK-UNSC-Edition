#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Packs a kit box with what its kit holds when new: EFAK's default contents for that kit (its CBA
 * setting, with the mission's rules applied) and the box's own extras. Only once per box, and only
 * an empty one - a box a mission maker filled in Eden, or one that comes back with its cargo, keeps
 * what it has.
 *
 * Arguments:
 * 0: Box <OBJECT>
 * 1: Pack it again even when packed or not empty <BOOL> (default: false)
 *
 * Return Value:
 * Packed <BOOL>
 *
 * Example:
 * [_box] call efku_boxes_fnc_fill;
 *
 * Public: Yes
 */

params ["_box", ["_force", false]];

if (!isServer) exitWith {false};
if (!_force && {_box getVariable [QGVAR(packed), false]}) exitWith {false};
_box setVariable [QGVAR(packed), true, true];

private _cargo = (getItemCargo _box select 0) + (getMagazineCargo _box select 0) + (getWeaponCargo _box select 0)
    + (getBackpackCargo _box select 0);
if (!_force && {_cargo isNotEqualTo []}) exitWith {false};

private _cfg = configOf _box;
private _kit = getText (_cfg >> "efku_kit");
private _list = [];
if (_kit isNotEqualTo "" && {!isNil "efak_core_fnc_getDefaultContents"}) then {
    _list append ([_kit] call efak_core_fnc_getDefaultContents);
};
private _extra = getArray (_cfg >> "efku_extra");
for "_i" from 0 to (count _extra - 2) step 2 do {
    _list pushBack [_extra select _i, _extra select (_i + 1)];
};

{
    _x params ["_class", ["_count", 1]];
    switch (true) do {
        case (isClass (configFile >> "CfgMagazines" >> _class)): {_box addMagazineCargoGlobal [_class, _count]};
        case (isClass (configFile >> "CfgVehicles" >> _class)): {_box addBackpackCargoGlobal [_class, _count]};
        case (isClass (configFile >> "CfgWeapons" >> _class)): {
            if (getNumber (configFile >> "CfgWeapons" >> _class >> "type") in [1, 2, 4]) then {
                _box addWeaponCargoGlobal [_class, _count];
            } else {
                _box addItemCargoGlobal [_class, _count];
            };
        };
        default {};
    };
} forEach _list;

true
