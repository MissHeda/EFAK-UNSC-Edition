#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * A kit came into the world as an item (Item_<kit>: Eden, Zeus, a script, a kit dropped beside a
 * vehicle, a PH Vehicles Arsenal preset): on the server, a moment later, its kit prototype becomes a
 * real kit instance packed with the defaults - as if a player had dropped it, so nobody has to pick it
 * up first.
 * Placed in Eden or by Zeus, it then becomes what a dropped kit is: the kit lying on the ground in a
 * ground holder of the engine's own - opened by double click, gone once the kit is taken. Only a kit
 * item PH Vehicles Arsenal holds (attached, or brought back from a preset) or one a kit dropped
 * beside a vehicle became (fnc_toItem) stays one, set down on whatever is below it, for PH to attach.
 *
 * Arguments:
 * 0: Kit item <OBJECT>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_item] call efku_boxes_fnc_initItem;
 *
 * Public: No
 */

params ["_holder"];

if (!isServer || {is3DEN}) exitWith {};

[{
    params ["_holder"];
    // PH's placement preview is left as it is
    if (isNull _holder || {IS_PREVIEW(_holder)}) exitWith {};

    // prototypes for instances, filled with the defaults (only prototypes: a restored or reused
    // item that already holds an instance keeps it)
    if (!isNil "efak_core_fnc_allocateInstance") then {
        {
            if (getNumber (configFile >> "CfgWeapons" >> _x >> "EFAK_prototype") != 1) then {continue};
            private _instance = [_x] call efak_core_fnc_allocateInstance;
            if (_instance isEqualTo "") then {continue};
            [_instance, -1] call efak_core_fnc_fillNewInstance;
            _holder addItemCargoGlobal [_instance, 1];
            _holder addItemCargoGlobal [_x, -1];
        } forEach (itemCargo _holder);
    };

    // PH's: stays as it is
    if (!isNull attachedTo _holder) exitWith {
        _holder setVariable ["PHVA_tuningAllowed", true, true];
    };

    // onto whatever is below it (the ground, a table, a deck), within 2 m
    private _from = (getPosASL _holder) vectorAdd [0, 0, 0.05];
    private _hit = lineIntersectsSurfaces [_from, _from vectorAdd [0, 0, -2], _holder, objNull, true, 1, "GEOM", "FIRE"];
    private _at = getPosASL _holder;
    private _up = surfaceNormal getPosATL _holder;
    if (_hit isNotEqualTo []) then {
        _at = (_hit select 0) select 0;
        _up = (_hit select 0) select 1;
    };

    // stays a kit item: dropped beside a vehicle (fnc_toItem), for PH to attach; nothing below it
    // (PH brings what it attaches to life high above the vehicle, and attaches it a moment later);
    // named in Eden, or holding containers with things in them - a holder in its place would lose those
    if (_holder getVariable [QGVAR(keep), false]
        || {_hit isEqualTo [] && {((getPosATL _holder) select 2) > 2}}
        || {vehicleVarName _holder isNotEqualTo ""}
        || {(everyContainer _holder) isNotEqualTo []}) exitWith {
        _holder setPosASL _at;
        _holder setVectorUp _up;
        _holder setVariable ["PHVA_tuningAllowed", true, true];
    };

    // placed: into a ground holder, as a dropped kit lies
    private _ground = createVehicle ["GroundWeaponHolder", [0, 0, 0], [], 0, "CAN_COLLIDE"];
    {
        _x params ["_classes", "_counts"];
        {_ground addItemCargoGlobal [_x, _counts select _forEachIndex]} forEach _classes;
    } forEach [getItemCargo _holder];
    {_ground addMagazineAmmoCargo [_x select 0, 1, _x select 1]} forEach (magazinesAmmoCargo _holder);
    {_ground addWeaponWithAttachmentsCargoGlobal [_x, 1]} forEach (weaponsItemsCargo _holder);
    {_ground addBackpackCargoGlobal [_x, 1]} forEach (backpackCargo _holder);
    _ground setDir (getDir _holder);
    _ground setPosASL _at;

    // Zeus keeps the say over it
    {
        if (_holder in curatorEditableObjects _x) then {_x addCuratorEditableObjects [[_ground], false]};
    } forEach allCurators;

    deleteVehicle _holder;
}, [_holder], FILL_DELAY] call CBA_fnc_waitAndExecute;
