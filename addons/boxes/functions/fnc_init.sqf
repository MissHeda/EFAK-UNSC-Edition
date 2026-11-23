#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * A kit box came into the world (Eden, Zeus, a script, a vehicle preset): on the server, pack it a
 * moment later, unless something else filled it first.
 *
 * Arguments:
 * 0: Box <OBJECT>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_box] call efku_boxes_fnc_init;
 *
 * Public: No
 */

params ["_box"];

if (!isServer || {is3DEN}) exitWith {};

// PH Vehicles Arsenal lists it even when Zeus did not place it
_box setVariable ["PHVA_tuningAllowed", true, true];

[{
    params ["_box"];
    if (isNull _box) exitWith {};
    [_box] call FUNC(fill);
}, [_box], FILL_DELAY] call CBA_fnc_waitAndExecute;
