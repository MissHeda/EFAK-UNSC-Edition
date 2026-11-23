#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * On the server: moves one dropped kit out of a ground holder into a kit holder of its own, where
 * it lay (see fnc_onPut).
 *
 * Arguments:
 * 0: Ground holder <OBJECT>
 * 1: Kit (instance or prototype) <STRING>
 * 2: Item holder class <STRING>
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

private _pos = getPosATL _container;
private _new = createVehicle [_class, [0, 0, 0], [], 0, "CAN_COLLIDE"];
_new setDir (getDir _container);
_new setPosATL _pos;
// the dropped kit in, the prototype the class brings out - in that order: an empty holder is deleted
_new addItemCargoGlobal [_item, 1];
_new addItemCargoGlobal [_class select [5], -1];

private _alone = (itemCargo _container) isEqualTo [_item] && {(magazineCargo _container) isEqualTo []}
    && {(weaponCargo _container) isEqualTo []} && {(backpackCargo _container) isEqualTo []};
if (_alone) then {
    deleteVehicle _container;
} else {
    _container addItemCargoGlobal [_item, -1];
};

// Zeus keeps the say over it
{_x addCuratorEditableObjects [[_new], false]} forEach allCurators;
