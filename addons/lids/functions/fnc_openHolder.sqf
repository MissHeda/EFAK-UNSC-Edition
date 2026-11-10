#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * Opens the lids of the kits in one ground holder, locally. The holder is hidden; each kit is shown
 * by its prop (efku_lidProp of its class) on the very slot the holder had it on, and swings its lid
 * open. When the holder holds more than kits, a local copy of it shows the rest - with an empty
 * stand-in where each opened kit was, so everything else keeps its place.
 *
 * Arguments:
 * 0: Holder <OBJECT>
 * 1: Only this kit class, "" for every kit in the holder <STRING> (default: "")
 * 2: Who opens it: "kit" (the kit window), "inventory", or another player's, see fnc_requestOpen
 *    <STRING> (default: "kit"). A holder someone already has open just counts them in.
 * 3: Open at once, without the swing and sound <BOOL> (default: false)
 *
 * Return Value:
 * Opened <BOOL>
 *
 * Example:
 * [_holder] call efku_lids_fnc_openHolder;
 *
 * Public: No
 */

params ["_holder", ["_only", ""], ["_source", "kit"], ["_instant", false]];

if (isNull _holder) exitWith {false};
if !(_holder isKindOf "WeaponHolder" || {_holder isKindOf "WeaponHolderSimulated"}) exitWith {false};
// Open already: count this one in, so it stays open until everyone who opened it has closed it.
private _known = GVAR(open) findIf {(_x select 0) isEqualTo _holder};
if (_known != -1) exitWith {
    ((GVAR(open) select _known) select 4) pushBackUnique _source;
    true
};

private _pieces = [_holder] call FUNC(holderPieces);
private _slots = [_holder] call FUNC(holderSlots);
private _only = toLowerANSI _only;

// The kits to open: those with a prop, on a slot the holder has.
private _kits = [];
{
    _x params ["_kind", "_class"];

    if (_kind isEqualTo "item" && {_forEachIndex < count _slots} && {_only isEqualTo "" || {(toLowerANSI _class) isEqualTo _only}}) then {
        private _propClass = [_class] call FUNC(propOf);

        if (_propClass isNotEqualTo "") then {
            _kits pushBack [_forEachIndex, _class, _propClass];
        };
    };
} forEach _pieces;

// One stand-in class per opened kit entry: more than that many stay shut.
private _entries = [];
_kits = _kits select {
    private _entry = (_pieces select (_x select 0)) select 3;
    _entries pushBackUnique _entry;
    (_entries find _entry) < STAND_INS
};

if (_kits isEqualTo []) exitWith {false};

// Everything else in the holder, on a local copy of it: entry by entry as the holder has them, an
// opened kit's entry taken by a stand-in of its own (one class each - two of a class would merge).
private _copy = objNull;
if (count _pieces > count _kits) then {
    _copy = (typeOf _holder) createVehicleLocal [0, 0, 0];
    _copy setVariable [QGVAR(copy), true];
    _copy enableSimulation false;
    _copy setVectorDirAndUp [vectorDirVisual _holder, vectorUpVisual _holder];
    _copy setPosWorld (getPosWorldVisual _holder);

    private _opened = [];
    {_opened pushBackUnique ((_pieces select (_x select 0)) select 3)} forEach _kits;
    private _done = -1;
    {
        _x params ["_kind", "_class", "_data", "_entry"];

        if (_entry == _done) then {continue};
        _done = _entry;

        private _standIn = _opened find _entry;
        if (_standIn != -1) then {
            _copy addItemCargo [format [QGVAR(standIn_%1), _standIn], _data];
            continue;
        };

        switch (_kind) do {
            case "weapon": {_copy addWeaponWithAttachmentsCargo [_data, 1]};
            case "magazine": {_copy addMagazineAmmoCargo [_class, 1, _data]};
            case "backpack": {_copy addBackpackCargo [_class, 1]};
            default {_copy addItemCargo [_class, _data]};
        };
    } forEach _pieces;
};

private _props = [];
{
    _x params ["_index", "_class", "_propClass"];

    private _prop = _propClass createVehicleLocal [0, 0, 0];
    [_holder, _slots select _index, _prop] call FUNC(placeProp);

    if (_instant) then {
        _prop animateSource ["lid", 1, true];
    } else {
        _prop animateSource ["lid", 1];
        _prop say3D [format [QGVAR(%1_open), getText (configOf _prop >> "efku_sound")], 20, 0.96 + random 0.08];
    };

    _props pushBack [_prop, _class];
} forEach _kits;

_holder hideObject true;

GVAR(open) pushBack [_holder, _props, _copy, [_holder] call FUNC(holderPieces), [_source], _only, _kits apply {_x select 0}];

// The kits' casters go now, not on the next tick: the props cast the same shadow from here on.
[false] call FUNC(shadows);

true
