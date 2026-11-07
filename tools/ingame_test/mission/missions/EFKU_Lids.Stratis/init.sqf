if (!hasInterface) exitWith {};

[] spawn {
    waitUntil {!isNull player && {time > 1}};
    disableUserInput true;
    {if (_x != player) then {deleteVehicle _x}} forEach units group player;

    private _c = (getPosATL player) vectorAdd [0, 8, 0];
    _c set [2, 0];
    private _kits = ["efak_IFAK", "efak_AFAK", "efak_MFAK", "efak_MFAKPlus", "efak_NarcBox", "eup_UtilityPouch", "eup_AmmoPouch", "eup_AmmoBag", "eup_EngineerBag", "eup_CBRNBag"];
    private _holders = [];
    {
        private _p = _c vectorAdd [(_forEachIndex mod 5) * 0.9 - 1.8, (floor (_forEachIndex / 5)) * 1.1, 0];
        private _h = createVehicle ["GroundWeaponHolder", _p, [], 0, "CAN_COLLIDE"];
        _h setPosATL _p;
        _h addItemCargoGlobal [_x, 1];
        _holders pushBack _h;
    } forEach _kits;

    player setPosATL (_c vectorAdd [0, -4, 0]);
    player setDir 0;

    private _cam = "camera" camCreate (ASLToAGL ((AGLToASL _c) vectorAdd [0, -2.4, 1.6]));
    _cam camSetTarget (_c vectorAdd [0, 0.55, 0]);
    _cam cameraEffect ["internal", "back"];
    _cam camSetFov 0.75;
    _cam camCommit 0;
    showCinemaBorder false;
    sleep 5;

    {
        diag_log format ["EFKUTEST HOLDER %1 posW %2 posASL %3 dir %4 up %5 bb %6", (itemCargo _x) select 0, getPosWorld _x, getPosASL _x, vectorDir _x, vectorUp _x, boundingBoxReal _x];
    } forEach _holders;
    diag_log "EFKUTEST SHOT closed_front";
    sleep 3;

    {[player, _x] call efku_lids_fnc_openLids} forEach _holders;
    sleep 1.5;
    {
        _x params ["_h", "_p"];
        diag_log format ["EFKUTEST PROP %1 posW %2 propW %3 dir %4 up %5 bb %6", typeOf _p, getPosWorld _h, getPosWorld _p, vectorDir _p, vectorUp _p, boundingBoxReal _p];
    } forEach efku_lids_open;
    diag_log "EFKUTEST SHOT open_front";
    sleep 3;

    _cam camSetPos (_c vectorAdd [3.2, 0.55, 1.1]);
    _cam camSetTarget (_c vectorAdd [0, 0.55, 0]);
    _cam camCommit 0;
    sleep 2;
    diag_log "EFKUTEST SHOT open_side";
    sleep 3;

    {
        _x params ["_name", "_i", "_d"];
        private _hp = getPosATL (_holders select _i);
        _cam camSetPos (_hp vectorAdd [_d * 0.35, -_d, _d * 0.75]);
        _cam camSetTarget (_hp vectorAdd [0, 0, 0.1]);
        _cam camCommit 0;
        sleep 1.5;
        diag_log format ["EFKUTEST SHOT %1", _name];
        sleep 2.5;
    } forEach [["near_ifak", 0, 0.45], ["near_afak", 1, 0.6], ["near_mfak", 2, 0.8], ["near_narc", 4, 0.6], ["near_util", 5, 0.45], ["near_ammo", 6, 0.45], ["near_cbrn", 9, 0.8]];

    call efku_lids_fnc_closeLids;
    sleep 1.5;
    diag_log "EFKUTEST SHOT closed_side";
    sleep 3;
    diag_log "EFKUTEST DONE";
};
