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

private _cfg = configFile >> "CfgWeapons" >> _item;
private _kit = getText (_cfg >> "ace_arsenal_uniqueBase");
if (_kit isEqualTo "") then {_kit = _item};
if !(isClass (configFile >> "CfgVehicles" >> ("Item_" + _kit))) exitWith {};

private _radius = missionNamespace getVariable ["PHVA_tuningRadius", 6];
if ((nearestObjects [_container, ["LandVehicle", "Air", "Ship"], _radius]) isEqualTo []) exitWith {};

[QGVAR(toItem), [_container, _item, "Item_" + _kit]] call CBA_fnc_serverEvent;
