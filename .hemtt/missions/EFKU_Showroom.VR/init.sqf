// Showroom for EFAK: UNSC Edition: every kit on the ground on its own, a few piles (mixed, kits only,
// on a table), an ACE Arsenal box, and an action that plays the lids in a loop: open, 2 s, shut, 2 s.
//
//   hemtt launch showroom      (opens in Eden: Play Scenario)
if (!hasInterface) exitWith {};

[] spawn {
    sleep 1;

    // The hand-written mission.sqm has been known to load without a player.
    if (isNull player) then {
        private _unit = (createGroup west) createUnit ["B_Soldier_F", [4096, 4096, 0], [], 0, "NONE"];
        selectPlayer _unit;
    };

    waitUntil {!isNull player && {time > 0}};

    private _center = [4096, 4096, 0];
    player setPosATL _center;
    player setDir 0;
    player addItem "efak_IFAK";
    player addItem "efak_AFAK";

    efku_showroom_labels = [];
    efku_showroom_holders = [];

    private _put = {
        params ["_pos", "_dir", "_cargo", "_label"];

        private _holder = createVehicle ["GroundWeaponHolder", _pos, [], 0, "CAN_COLLIDE"];
        _holder setDir _dir;
        _holder setPosATL _pos;
        {
            _x params ["_kind", "_class", ["_count", 1]];
            switch (_kind) do {
                case "weapon": {_holder addWeaponCargoGlobal [_class, _count]};
                case "magazine": {_holder addMagazineCargoGlobal [_class, _count]};
                case "backpack": {_holder addBackpackCargoGlobal [_class, _count]};
                default {_holder addItemCargoGlobal [_class, _count]};
            };
        } forEach _cargo;
        efku_showroom_holders pushBack _holder;
        efku_showroom_labels pushBack [ASLToAGL ((getPosASL _holder) vectorAdd [0, 0, 0.45]), _label];
        _holder
    };

    // Every kit on its own, in a row in front of the player.
    private _kits = ["efak_IFAK", "efak_AFAK", "efak_MFAK", "efak_MFAKPlus", "efak_NarcBox", "eup_UtilityPouch", "eup_AmmoPouch", "eup_AmmoBag", "eup_EngineerBag", "eup_CBRNBag", "efku_SpecialAmmoCase", "efku_OrdnanceCase"];
    _kits = _kits select {isClass (configFile >> "CfgWeapons" >> _x)};
    {
        private _pos = _center vectorAdd [(_forEachIndex - (count _kits - 1) / 2) * 1.4, 4, 0];
        [_pos, 180, [["item", _x]], getText (configFile >> "CfgWeapons" >> _x >> "displayName")] call _put;
    } forEach _kits;

    // Piles: a soldier's things with kits among them, kits only, and a pile on a table.
    [_center vectorAdd [-3, 8, 0], 160, [
        ["weapon", "arifle_MX_F"], ["magazine", "30Rnd_65x39_caseless_mag", 2], ["item", "efak_IFAK"],
        ["item", "efak_MFAK"], ["item", "FirstAidKit", 3], ["item", "efak_NarcBox"], ["backpack", "B_AssaultPack_rgr"]
    ], "Mixed pile"] call _put;
    [_center vectorAdd [1, 8, 0], 200, [
        ["item", "efak_AFAK"], ["item", "efak_IFAK", 2], ["item", "eup_AmmoPouch"], ["item", "eup_UtilityPouch"]
    ], "Kits pile"] call _put;
    private _table = createVehicle ["Land_CampingTable_F", _center vectorAdd [5, 8, 0], [], 0, "CAN_COLLIDE"];
    _table setDir 180;
    private _top = (getPosATL _table) vectorAdd [0, 0, 0.8];
    private _onTable = [_top, 180, [["item", "efak_MFAKPlus"], ["item", "efak_IFAK"]], "On a table"] call _put;
    _onTable setPosASL ((getPosASL _table) vectorAdd [0, 0, 0.82]);

    // An ACE Arsenal box with everything in it.
    private _box = createVehicle ["B_supplyCrate_F", _center vectorAdd [-3, -4, 0], [], 0, "CAN_COLLIDE"];
    clearItemCargoGlobal _box;
    clearWeaponCargoGlobal _box;
    clearMagazineCargoGlobal _box;
    clearBackpackCargoGlobal _box;
    {_box addItemCargoGlobal [_x, 3]} forEach _kits;
    if (!isNil "ace_arsenal_fnc_initBox") then {
        [_box, true] call ace_arsenal_fnc_initBox;
    };
    efku_showroom_labels pushBack [ASLToAGL ((getPosASL _box) vectorAdd [0, 0, 1.2]), "ACE Arsenal (and every kit)"];

    addMissionEventHandler ["Draw3D", {
        {
            drawIcon3D ["", [0.45, 0.85, 1, 0.9], _x select 0, 0, 0, 0, _x select 1, 2, 0.032, "PuristaMedium", "center"];
        } forEach efku_showroom_labels;
    }];

    // The loop: every lid in the room opens, stays open 2 s, shuts, stays shut 2 s - until switched off.
    efku_showroom_playing = false;
    player addAction ["<t color='#7fd8ff'>Play animation</t>", {
        efku_showroom_playing = true;
        [] spawn {
            while {efku_showroom_playing} do {
                {[_x, "", "showroom"] call efku_lids_fnc_openHolder} forEach efku_showroom_holders;
                sleep 2.6;
                ["showroom"] call efku_lids_fnc_closeLids;
                sleep 2.65;
            };
        };
    }, nil, 10, false, true, "", "!efku_showroom_playing"];
    player addAction ["<t color='#ff9f7f'>Stop animation</t>", {
        efku_showroom_playing = false;
        ["showroom"] call efku_lids_fnc_closeLids;
    }, nil, 10, false, true, "", "efku_showroom_playing"];

    hint "UNSC Edition showroom\n\nScroll menu: Play animation\nACE Arsenal box behind you.";
};
