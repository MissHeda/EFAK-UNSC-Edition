#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * On the server: something was taken out of a kit item (Item_<kit>), or its inventory was closed.
 * Once no kit is left in it, the kit item goes - the kit is in someone's hands now - and whatever else
 * was put into it falls to the ground where it stood, so it is no box to keep things in. One that
 * is attached (PH Vehicles Arsenal) stays while PH keeps track of it, and goes once PH lets go of it,
 * if still without a kit.
 *
 * Arguments:
 * 0: Kit item <OBJECT>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_item] call efku_boxes_fnc_dropTaken;
 *
 * Public: No
 */

params ["_drop"];

if (!isServer || {isNull _drop}) exitWith {};

private _noKit = {
    params ["_drop"];
    (itemCargo _drop) findIf {
        getNumber (configFile >> "CfgWeapons" >> _x >> "EFAK_prototype") == 1
            || {getNumber (configFile >> "CfgWeapons" >> _x >> "EFAK_instanceId") > 0}
    } == -1
};
private _away = {
    params ["_drop"];
    private _rest = (itemCargo _drop) isNotEqualTo [] || {(magazineCargo _drop) isNotEqualTo []}
        || {(weaponCargo _drop) isNotEqualTo []} || {(backpackCargo _drop) isNotEqualTo []};
    if (_rest) then {
        private _ground = createVehicle ["GroundWeaponHolder", getPosATL _drop, [], 0, "CAN_COLLIDE"];
        // uniforms, vests and backpacks with what is in them
        private _containers = everyContainer _drop;
        private _skip = _containers apply {toLowerANSI (_x select 0)};
        {
            _x params ["_class", "_from"];
            private _before = (everyContainer _ground) apply {_x select 1};
            if (isClass (configFile >> "CfgVehicles" >> _class)) then {
                _ground addBackpackCargoGlobal [_class, 1];
            } else {
                _ground addItemCargoGlobal [_class, 1];
            };
            private _to = ((everyContainer _ground) apply {_x select 1}) select {!(_x in _before)};
            if (_to isEqualTo []) then {continue};
            _to = _to select 0;
            (getItemCargo _from) params ["_classes", "_counts"];
            {_to addItemCargoGlobal [_x, _counts select _forEachIndex]} forEach _classes;
            {_to addMagazineAmmoCargo [_x select 0, 1, _x select 1]} forEach (magazinesAmmoCargo _from);
            {_to addWeaponWithAttachmentsCargoGlobal [_x, 1]} forEach (weaponsItemsCargo _from);
        } forEach _containers;
        // the rest, less the containers already moved
        (getItemCargo _drop) params ["_classes", "_counts"];
        {
            private _n = _counts select _forEachIndex;
            private _class = _x;
            _n = _n - ({_x isEqualTo toLowerANSI _class} count _skip);
            if (_n > 0) then {_ground addItemCargoGlobal [_class, _n]};
        } forEach _classes;
        {_ground addMagazineAmmoCargo [_x select 0, 1, _x select 1]} forEach (magazinesAmmoCargo _drop);
        {_ground addWeaponWithAttachmentsCargoGlobal [_x, 1]} forEach (weaponsItemsCargo _drop);
        {
            private _class = _x;
            if ((_skip findIf {_x isEqualTo toLowerANSI _class}) == -1) then {_ground addBackpackCargoGlobal [_class, 1]};
        } forEach (backpackCargo _drop);
        _ground setPosATL (getPosATL _drop);
    };
    deleteVehicle _drop;
};

// a moment for the cargo change to arrive
[{
    params ["_drop", "_noKit", "_away"];
    if (isNull _drop || {!([_drop] call _noKit)}) exitWith {};
    if (isNull attachedTo _drop) exitWith {[_drop] call _away};
    // attached and without a kit: once PH lets go of it, it goes - unless a kit was put back (once)
    if (_drop getVariable [QGVAR(awaitRelease), false]) exitWith {};
    _drop setVariable [QGVAR(awaitRelease), true];
    [{isNull (_this select 0) || {isNull attachedTo (_this select 0)}}, {
        params ["_drop", "_noKit", "_away"];
        if (isNull _drop) exitWith {};
        _drop setVariable [QGVAR(awaitRelease), nil];
        if ([_drop] call _noKit) then {[_drop] call _away};
    }, [_drop, _noKit, _away]] call CBA_fnc_waitUntilAndExecute;
}, [_drop, _noKit, _away], 0.5] call CBA_fnc_waitAndExecute;
