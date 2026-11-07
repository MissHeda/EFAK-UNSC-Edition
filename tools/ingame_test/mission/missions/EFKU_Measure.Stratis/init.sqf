// Measures where a kit's prop stands against the kit in its holder: the same camera shoots the
// kit in its holder, then the prop with its lid shut (the holder hidden). Any shift between the two
// pictures is the jump a player sees when the lid opens.
if (!hasInterface) exitWith {};

[] spawn {
    waitUntil {!isNull player && {time > 1}};
    disableUserInput true;
    {if (_x != player) then {deleteVehicle _x}} forEach units group player;

    private _c = (getPosATL player) vectorAdd [0, 8, 0];
    _c set [2, 0];
    player setPosATL (_c vectorAdd [0, -4, 0]);
    private _kits = ["efak_IFAK", "efak_AFAK", "efak_MFAK", "efak_MFAKPlus", "efak_NarcBox", "eup_UtilityPouch", "eup_AmmoPouch", "eup_AmmoBag", "eup_EngineerBag", "eup_CBRNBag"];
    private _cam = "camera" camCreate (_c vectorAdd [0, 0, 2]);
    _cam cameraEffect ["internal", "back"];
    showCinemaBorder false;

    private _views = [["top", [0, -0.001, 2.6]], ["front", [0, -2.6, 0.12]]];
    {
        private _kit = _x;
        private _name = ["ifak", "afak", "mfak", "mfakplus", "narcbox", "util", "pouch", "ammobag", "engineer", "cbrn"] select _forEachIndex;
        private _p = _c vectorAdd [_forEachIndex * 3, 0, 0];
        {
            _x params ["_view", "_off"];
            _cam camSetPos (_p vectorAdd _off);
            _cam camSetTarget (_p vectorAdd [0, 0, 0.05]);
            _cam camSetFov 0.25;
            _cam camCommit 0;
            sleep 1.2;
            diag_log format ["EFKUTEST SHOT m_%1_%2_bg", _name, _view];
            sleep 1.5;
        } forEach _views;
        private _h = createVehicle ["GroundWeaponHolder", _p, [], 0, "CAN_COLLIDE"];
        _h setPosATL _p;
        _h addItemCargoGlobal [_kit, 1];
        sleep 1;
        {
            _x params ["_view", "_off"];
            _cam camSetPos (_p vectorAdd _off);
            _cam camSetTarget (_p vectorAdd [0, 0, 0.05]);
            _cam camSetFov 0.25;
            _cam camCommit 0;
            sleep 1.2;
            diag_log format ["EFKUTEST SHOT m_%1_%2_item", _name, _view];
            sleep 1.5;
        } forEach _views;
        [_h, "", "kit"] call efku_lids_fnc_openHolder;
        diag_log format ["EFKUTEST POS holder %1 prop %2", getPosWorld _h, getPosWorld ((efku_lids_open select ((count efku_lids_open) - 1)) select 1)];
        private _prop = (efku_lids_open select ((count efku_lids_open) - 1)) select 1;
        _prop animateSource ["lid", 0, true];
        sleep 1;
        {
            _x params ["_view", "_off"];
            _cam camSetPos (_p vectorAdd _off);
            _cam camSetTarget (_p vectorAdd [0, 0, 0.05]);
            _cam camCommit 0;
            sleep 1.2;
            diag_log format ["EFKUTEST SHOT m_%1_%2_prop", _name, _view];
            sleep 1.5;
        } forEach _views;
        call efku_lids_fnc_closeLids;
        sleep 1;
    } forEach _kits;
    diag_log "EFKUTEST DONE";
};
