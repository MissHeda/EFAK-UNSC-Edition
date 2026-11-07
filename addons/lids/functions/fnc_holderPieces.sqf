#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Everything a ground holder holds, one entry per piece, in the order the holder lays the pieces
 * out on its slots (see fnc_holderSlots): weapons, magazines, items, backpacks.
 *
 * Arguments:
 * 0: Holder <OBJECT>
 *
 * Return Value:
 * Pieces <ARRAY> of [kind <STRING>, class <STRING>, data <ANY>, entry <NUMBER>]
 *   kind "weapon" (data: weaponsItems entry), "magazine" (data: rounds), "item" (data: how many
 *   the item's cargo entry holds), "backpack"; entry counts the holder's cargo entries - items of
 *   one class put down together are one entry, and lie next to each other
 *
 * Example:
 * [_holder] call efku_lids_fnc_holderPieces;
 *
 * Public: No
 */

params ["_holder"];

private _pieces = [];

private _entry = 0;

{_pieces pushBack ["weapon", _x select 0, _x, _entry]; _entry = _entry + 1} forEach (weaponsItemsCargo _holder);
{_pieces pushBack ["magazine", _x select 0, _x select 1, _entry]; _entry = _entry + 1} forEach (magazinesAmmoCargo _holder);
(getItemCargo _holder) params [["_classes", []], ["_counts", []]];
{
    private _count = _counts select _forEachIndex;
    for "_i" from 1 to _count do {_pieces pushBack ["item", _x, _count, _entry]};
    _entry = _entry + 1;
} forEach _classes;
{_pieces pushBack ["backpack", _x, 0, _entry]; _entry = _entry + 1} forEach (backpackCargo _holder);

_pieces
