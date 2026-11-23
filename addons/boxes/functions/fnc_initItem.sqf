#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * A kit placed as an item (Eden, Zeus, a script) or one dropped beside a vehicle: on the server, a
 * moment later, its kit becomes a real kit instance packed with the defaults - as if a player had
 * dropped it, so nobody has to pick it up first - and it is set down upright on the ground. PH
 * Vehicles Arsenal may attach it.
 *
 * Arguments:
 * 0: Item holder <OBJECT>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_holder] call efku_boxes_fnc_initItem;
 *
 * Public: No
 */

params ["_holder"];

if (!isServer || {is3DEN}) exitWith {};
if (getNumber (configOf _holder >> "efku_item") != 1) exitWith {};

[{
    params ["_holder"];
    if (isNull _holder) exitWith {};

    // prototypes for instances, filled with the defaults
    if (!isNil "efak_core_fnc_allocateInstance") then {
        {
            if (getNumber (configFile >> "CfgWeapons" >> _x >> "EFAK_prototype") != 1) then {continue};
            private _instance = [_x] call efak_core_fnc_allocateInstance;
            if (_instance isEqualTo "") then {continue};
            [_instance, -1] call efak_core_fnc_fillNewInstance;
            // the new one first: a holder with nothing left in it is deleted
            _holder addItemCargoGlobal [_instance, 1];
            _holder addItemCargoGlobal [_x, -1];
        } forEach (itemCargo _holder);
    };

    // upright, on the ground unless it was put on something
    if (isNull attachedTo _holder) then {
        // onto whatever is below it (the ground, a table, a deck), within 2 m
        private _from = (getPosASL _holder) vectorAdd [0, 0, 0.05];
        private _hit = lineIntersectsSurfaces [_from, _from vectorAdd [0, 0, -2], _holder, objNull, true, 1, "GEOM", "FIRE"];
        if (_hit isNotEqualTo []) then {
            (_hit select 0) params ["_at", "_normal"];
            _holder setPosASL _at;
            _holder setVectorUp _normal;
        } else {
            _holder setVectorUp (surfaceNormal getPosATL _holder);
        };
    };

    _holder setVariable ["PHVA_tuningAllowed", true, true];
}, [_holder], FILL_DELAY] call CBA_fnc_waitAndExecute;
