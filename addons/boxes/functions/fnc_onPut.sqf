#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * A player put something down. A kit dropped on the ground beside a vehicle, with PH Vehicles
 * Arsenal loaded, goes into a kit holder of its own (Item_<kit>) - PH only lists ground holders that
 * hold a firearm, but takes this one - so it can be attached to the vehicle.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Container <OBJECT>
 * 2: Item <STRING>
 *
 * Return Value:
 * None
 *
 * Example:
 * [player, _holder, "efak_AFAK_3"] call efku_boxes_fnc_onPut;
 *
 * Public: No
 */

params ["_unit", "_container", "_item"];

if (!local _unit || {isNil "PHVA_tuningRadius"}) exitWith {};
if !(_container isKindOf "GroundWeaponHolder") exitWith {};
if (getNumber (configOf _container >> "efku_item") == 1) exitWith {};
// the lids' stand-in pile is only for the eye
if (_container getVariable ["efku_lids_copy", false]) exitWith {};

private _cfg = configFile >> "CfgWeapons" >> _item;
private _kit = getText (_cfg >> "ace_arsenal_uniqueBase");
if (_kit isEqualTo "") then {_kit = _item};
if !(isClass (configFile >> "CfgVehicles" >> ("Item_" + _kit))) exitWith {};

private _radius = missionNamespace getVariable ["PHVA_tuningRadius", 6];
if ((nearestObjects [_container, ["LandVehicle", "Air", "Ship"], _radius]) isEqualTo []) exitWith {};

// Once the inventory is closed: changed under the open inventory, the pile it still shows could
// hand the kit out a second time. Only if the kit is still there then.
[{isNull findDisplay 602}, {
    params ["_container", "_item"];
    if (isNull _container || {!(_item in itemCargo _container)}) exitWith {};
    // still beside a vehicle
    private _radius = missionNamespace getVariable ["PHVA_tuningRadius", 6];
    if ((nearestObjects [_container, ["LandVehicle", "Air", "Ship"], _radius]) isEqualTo []) exitWith {};
    [QGVAR(toItem), _this] call CBA_fnc_serverEvent;
}, [_container, _item, "Item_" + _kit]] call CBA_fnc_waitUntilAndExecute;
