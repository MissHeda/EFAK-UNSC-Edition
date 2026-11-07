#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Opens the lids of every kit in the ground holders the player just opened the inventory on, a pile
 * of many things as well as a kit on its own (see fnc_openHolder). fnc_closeLids puts everything
 * back.
 *
 * Arguments:
 * 0: Unit <OBJECT>
 * 1: Container <OBJECT>
 * 2: Second container <OBJECT> (default: objNull)
 *
 * Return Value:
 * None
 *
 * Example:
 * [player, _holder] call efku_lids_fnc_openLids;
 *
 * Public: No
 */

params ["", "_container", ["_second", objNull]];

{
    [_x, "", "inventory"] call FUNC(openHolder);
} forEach [_container, _second];
