#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Closes every lid fnc_openLids opened: the lid swings shut, then the prop goes and the kit in its
 * holder shows again. A kit that was taken out meanwhile loses its prop at once.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call efku_lids_fnc_closeLids;
 *
 * Public: No
 */

{
    _x params ["_holder", "_prop", "_item"];

    private _cargo = if (isNull _holder) then {[]} else {
        (itemCargo _holder) + (weaponCargo _holder) + (magazineCargo _holder) + (backpackCargo _holder)
    };

    if (_cargo isEqualTo [_item]) then {
        _prop animateSource ["lid", 0];
        _prop say3D [format [QGVAR(%1_close), getText (configOf _prop >> "efku_sound")], 20, 0.96 + random 0.08];

        [{
            params ["_holder", "_prop"];

            deleteVehicle _prop;
            _holder hideObject false;
        }, [_holder, _prop], 0.65] call CBA_fnc_waitAndExecute;
    } else {
        deleteVehicle _prop;

        if (!isNull _holder) then {
            _holder hideObject false;
        };
    };
} forEach GVAR(open);

GVAR(open) = [];
