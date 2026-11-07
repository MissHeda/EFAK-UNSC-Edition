#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * The places a ground holder puts its items at: one per weapon proxy of its model, in the order the
 * proxies are numbered. Each is [corner, direction] in the holder's model space - the corner is
 * where the item's origin goes, on the ground, the direction where the item's front faces.
 *
 * A proxy is a triangle: a corner, a point two metres along the direction and one a metre above the
 * corner. Its average point and bounding box are all the game tells, and they are enough: the
 * corner is the one of the box that, pushed three times its distance to the average point, lands
 * on the opposite one. Read once per model.
 *
 * Arguments:
 * 0: Holder <OBJECT>
 *
 * Return Value:
 * Slots <ARRAY> of [corner <ARRAY>, direction <ARRAY>]
 *
 * Example:
 * [_holder] call efku_lids_fnc_holderSlots;
 *
 * Public: No
 */

params ["_holder"];

private _model = toLowerANSI ((getModelInfo _holder) select 1);
private _slots = GVAR(slots) get _model;

if (!isNil "_slots") exitWith {_slots};

_slots = [];
private _lod = ((allLODs _holder) param [0, []]) param [2, 1];
private _proxies = [];

{
    private _name = toLowerANSI _x;

    if ("proxy:" in _name && {"weapon" in _name}) then {
        private _parts = _name splitString ".";
        _proxies pushBack [parseNumber (_parts select -1), _x];
    };
} forEach (_holder selectionNames _lod);

_proxies sort true;

{
    private _sel = _x select 1;
    private _avg = _holder selectionPosition [_sel, _lod, "AveragePoint"];
    (_holder selectionPosition [_sel, _lod, "BoundingBox"]) params ["_lo", "_hi"];

    private _best = [];
    private _bestErr = 1e9;

    {
        private _ax = _x select 0;
        private _ay = _x select 1;
        private _bx = _ax + 3 * ((_avg select 0) - _ax);
        private _by = _ay + 3 * ((_avg select 1) - _ay);
        private _err = abs (_bx - ((_lo select 0) + (_hi select 0) - _ax)) + abs (_by - ((_lo select 1) + (_hi select 1) - _ay));

        if (_err < _bestErr) then {
            _bestErr = _err;
            _best = [[_ax, _ay, _lo select 2], vectorNormalized [_bx - _ax, _by - _ay, 0]];
        };
    } forEach [
        [_lo select 0, _lo select 1], [_hi select 0, _lo select 1],
        [_lo select 0, _hi select 1], [_hi select 0, _hi select 1]
    ];

    _slots pushBack _best;
} forEach _proxies;

GVAR(slots) set [_model, _slots];

_slots
