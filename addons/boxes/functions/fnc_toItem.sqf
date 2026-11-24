#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * On the server: moves one dropped kit out of a ground holder into a kit item of its own
 * (Item_<kit>, a world object PH Vehicles Arsenal can attach), where it lay (see fnc_onPut).
 *
 * Arguments:
 * 0: Ground holder <OBJECT>
 * 1: Kit (instance or prototype) <STRING>
 * 2: Kit item class <STRING>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_holder, "efak_AFAK_3", "Item_efak_AFAK"] call efku_boxes_fnc_toItem;
 *
 * Public: No
 */

params ["_container", "_item", "_class"];

if (!isServer || {isNull _container} || {!(_item in itemCargo _container)}) exitWith {};

// A holder this deleted a moment ago: it only turns null the frame after, and a second call in that
// frame would still find the kit in it and make a second kit item with the same kit in it
if (_container in (missionNamespace getVariable [QGVAR(deleted), []])) exitWith {};

private _pos = getPosATL _container;
private _dir = getDir _container;

// out of the holder first, then into the kit item: never in both
private _alone = (itemCargo _container) isEqualTo [_item] && {(magazineCargo _container) isEqualTo []}
    && {(weaponCargo _container) isEqualTo []} && {(backpackCargo _container) isEqualTo []};
if (_alone) then {
    if (isNil QGVAR(deleted)) then {GVAR(deleted) = []};
    GVAR(deleted) pushBack _container;
    [{GVAR(deleted) = GVAR(deleted) - [objNull, _this]}, _container] call CBA_fnc_execNextFrame;
    deleteVehicle _container;
} else {
    _container addItemCargoGlobal [_item, -1];
};

private _new = createVehicle [_class, [0, 0, 0], [], 0, "CAN_COLLIDE"];
// stays a kit item, for PH to attach (fnc_initItem)
_new setVariable [QGVAR(keep), true];
// the dropped kit instead of the prototype the class brings (not a holder: empty is fine)
clearItemCargoGlobal _new;
_new addItemCargoGlobal [_item, 1];
_new setDir _dir;
_new setPosATL _pos;

// Zeus keeps the say over it
{_x addCuratorEditableObjects [[_new], false]} forEach allCurators;
