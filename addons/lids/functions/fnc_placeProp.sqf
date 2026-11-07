#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Puts a kit's prop exactly where the holder draws the kit on one of its slots: in the holder's own
 * frame, so it follows the holder wherever it lies - on a slope, a table, tipped over.
 *
 * The kit models are built with their top along the model's y axis and their front along z (the
 * way a holder lays items down), so the prop points y along the holder's up and z along the slot.
 * efku_offset of the prop is a small correction in the slot's frame: [right, forward, up].
 *
 * Arguments:
 * 0: Holder <OBJECT>
 * 1: Slot, see fnc_holderSlots <ARRAY>
 * 2: Prop <OBJECT>
 *
 * Return Value:
 * None
 *
 * Example:
 * [_holder, _slot, _prop] call efku_lids_fnc_placeProp;
 *
 * Public: No
 */

params ["_holder", "_slot", "_prop"];
_slot params ["_corner", "_dir"];

private _config = configOf _prop;
private _offset = getArray (_config >> "efku_offset");
if (count _offset != 3) then {_offset = [0, 0, 0]};

private _turn = getNumber (_config >> "efku_turn");
_dir = [
    (_dir select 0) * cos _turn + (_dir select 1) * sin _turn,
    (_dir select 1) * cos _turn - (_dir select 0) * sin _turn,
    0
];
private _right = [_dir select 1, -(_dir select 0), 0];

private _local = _corner
    vectorAdd (_right vectorMultiply (_offset select 0))
    vectorAdd (_dir vectorMultiply (_offset select 1))
    vectorAdd [0, 0, _offset select 2];

_prop setVectorDirAndUp [_holder vectorModelToWorldVisual [0, 0, 1], _holder vectorModelToWorldVisual _dir];
_prop setPosWorld (_holder modelToWorldVisualWorld _local);
