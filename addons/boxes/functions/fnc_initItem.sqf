#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * A kit came into the world as an item (Item_<kit>: Eden, Zeus, a script, a kit dropped beside a
 * vehicle, a PH Vehicles Arsenal preset): on the server, a moment later, its kit prototype becomes a
 * real kit instance packed with the defaults - as if a player had dropped it, so nobody has to pick it
 * up first - and, unless something holds it, it is set down on whatever is below it. PH may attach it.
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
// a copy made on one machine only (PH's placement preview) is left as it is
if (netId _holder isEqualTo "0:0") exitWith {};

[{
    params ["_holder"];
    if (isNull _holder) exitWith {};

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

    // onto whatever is below it (the ground, a table, a deck), within 2 m - not when attached
    if (isNull attachedTo _holder) then {
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
