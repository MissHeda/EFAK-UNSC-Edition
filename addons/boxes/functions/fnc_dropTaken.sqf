#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * On the server: something was taken out of a kit item (Item_<kit>). Once nothing is left in it the
 * kit item goes away - the kit is in someone's hands now. One that is attached (PH Vehicles Arsenal)
 * stays while PH keeps track of it, and goes once PH lets go of it, if still empty.
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

// a moment for the cargo change to arrive
private _empty = {
    params ["_drop"];
    (itemCargo _drop) isEqualTo [] && {(magazineCargo _drop) isEqualTo []}
        && {(weaponCargo _drop) isEqualTo []} && {(backpackCargo _drop) isEqualTo []}
};
[{
    params ["_drop", "_empty"];
    if (isNull _drop || {!([_drop] call _empty)}) exitWith {};
    if (isNull attachedTo _drop) exitWith {deleteVehicle _drop};
    // attached and empty: once PH lets go of it, it goes - unless something was put back in (once)
    if (_drop getVariable [QGVAR(awaitRelease), false]) exitWith {};
    _drop setVariable [QGVAR(awaitRelease), true];
    [{isNull (_this select 0) || {isNull attachedTo (_this select 0)}}, {
        params ["_drop", "_empty"];
        if (isNull _drop) exitWith {};
        _drop setVariable [QGVAR(awaitRelease), nil];
        if ([_drop] call _empty) then {deleteVehicle _drop};
    }, [_drop, _empty]] call CBA_fnc_waitUntilAndExecute;
}, [_drop, _empty], 0.5] call CBA_fnc_waitAndExecute;
