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

// Test driver (tools/ingame_test only): close-ups of a few kits from the side their lid opens to,
// shut (for the shadow) and open.
[] spawn {
    waitUntil {!isNil "efku_showroom_playing"};
    sleep 3;
    disableUserInput true;
    private _cam = "camera" camCreate [4096, 4093, 3.2];
    _cam cameraEffect ["internal", "back"];
    showCinemaBorder false;
    // the row from further away, for the far LODs
    {
        _x params ["_d", "_fov"];
        _cam camSetPos [4096, 4100 - _d, 1.6];
        _cam camSetTarget [4096, 4100, 0];
        _cam camSetFov _fov;
        _cam camCommit 0;
        sleep 2.5;
        diag_log format ["EFKUTEST SHOT sr_far_%1", _d];
        sleep 1;
    } forEach [[8, 0.75], [25, 0.25], [60, 0.11]];
    {
        _x params ["_i", "_name"];
        private _p = [4096 + (_i - 5.5) * 1.4, 4100, 0];   // the row of twelve kits
        private _h = efku_showroom_holders select _i;
        // shut, low from the front corner: the faces, the handles and the shadow on the ground
        _cam camSetPos (_p vectorAdd [0.95, -1.15, 0.5]);
        _cam camSetTarget (_p vectorAdd [0, 0, 0.08]);
        _cam camSetFov 0.5;
        _cam camCommit 0;
        sleep 2;
        diag_log format ["EFKUTEST SHOT sr_%1_shut", _name];
        sleep 1;
        [_h] call efku_lids_fnc_openHolder;
        sleep 1.5;
        // the way a player sees it: standing over it, and from four metres, at the game's own field of view
        {
            _x params ["_view", "_off", "_fov"];
            _cam camSetPos (_p vectorAdd _off);
            _cam camSetTarget (_p vectorAdd [0, 0, 0.05]);
            _cam camSetFov _fov;
            _cam camCommit 0;
            sleep 2;
            diag_log format ["EFKUTEST SHOT sr_%1_%2", _name, _view];
            sleep 1;
        } forEach [["eye", [0.15, -0.7, 1.1], 0.75], ["far", [0.3, -4, 1.6], 0.75], ["open", [0.25, -0.75, 0.75], 0.45]];
        ["", true] call efku_lids_fnc_closeLids;
        sleep 0.5;
    } forEach [[1, "afak"], [6, "pouch"], [7, "ammo"], [11, "ordnance"]];
    diag_log format ["EFKUTEST CASTERS %1", count efku_lids_casters];
    // the two cases of this mod's own: registered as kits, their instance pool there
    diag_log format ["EFKUTEST KITS %1", ["EFKU_SpecialAmmoCase", "EFKU_OrdnanceCase"] apply {
        private _item = getText (configFile >> "EFAK_Kits" >> _x >> "item");
        [_x, isClass (configFile >> "EFAK_Kits" >> _x), isClass (configFile >> "CfgWeapons" >> (_item + "_300")),
            getText (configFile >> "CfgWeapons" >> _item >> "displayName")]
    }];
    // what the ordnance case takes: rockets, charges and grenades, no rifle magazines
    diag_log format ["EFKUTEST ORDNANCE %1", ["HandGrenade", "MiniGrenade", "SmokeShellRed", "ACE_M84", "DemoCharge_Remote_Mag",
        "MRAWS_HEAT_F", "Titan_AA", "NLAW_F", "Vorona_HEAT", "APERSMine_Range_Mag", "30Rnd_65x39_caseless_mag",
        "1Rnd_HE_Grenade_shell", "FirstAidKit"] apply {
        [_x, (["efku_OrdnanceCase", _x] call efak_core_fnc_isItemAllowed) select 0]
    }];
    // the names the boxes go by, on the item and one of its instances
    diag_log format ["EFKUTEST NAMES %1", ["eup_AmmoBag", "eup_EngineerBag_7", "eup_CBRNBag", "efku_SpecialAmmoCase_3", "efku_OrdnanceCase",
        "eup_UtilityPouch"] apply {getText (configFile >> "CfgWeapons" >> _x >> "displayName")}];
    diag_log "EFKUTEST DONE";
};
