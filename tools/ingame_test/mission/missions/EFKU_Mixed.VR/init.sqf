// Mixed piles: a kit and other things. A is the real lids path; B-G are bare local copies made in
// different ways, next to it, to see which of them the engine draws.
if (!hasInterface) exitWith {};
[] spawn {
    waitUntil {!isNull player && {time > 1}};
    disableUserInput true;
    player setPosATL [4080, 4080, 0];
    private _cam = "camera" camCreate [4096, 4096, 1];
    _cam cameraEffect ["internal", "back"];
    showCinemaBorder false;

    private _fill = {
        params ["_h", ["_kit", true], ["_standIn", false]];
        if (_kit) then {_h addItemCargo ["efak_IFAK", 1]};
        if (_standIn) then {_h addItemCargo ["efku_lids_standIn_0", 1]};
        _h addItemCargo ["FirstAidKit", 2];
        _h addMagazineCargo ["30Rnd_65x39_caseless_mag", 2];
        _h addWeaponCargo ["arifle_MX_F", 1];
    };
    private _pos = {[4090 + _this * 2.5, 4100, 0]};

    // A: the real pile, opened by the lids
    private _a = createVehicle ["GroundWeaponHolder", 0 call _pos, [], 0, "CAN_COLLIDE"];
    _a setPosATL (0 call _pos);
    {_a addItemCargoGlobal _x} forEach [["efak_IFAK", 1], ["FirstAidKit", 2]];
    _a addMagazineCargoGlobal ["30Rnd_65x39_caseless_mag", 2];
    _a addWeaponCargoGlobal ["arifle_MX_F", 1];

    // B: local, stand-in instead of the kit, left running
    private _b = createVehicleLocal ["GroundWeaponHolder", 1 call _pos, [], 0, "CAN_COLLIDE"];
    [_b, false, true] call _fill;
    // C: local, no stand-in, left running
    private _c = createVehicleLocal ["GroundWeaponHolder", 2 call _pos, [], 0, "CAN_COLLIDE"];
    [_c, false, false] call _fill;
    // D: local, kit itself, left running
    private _d = createVehicleLocal ["GroundWeaponHolder", 3 call _pos, [], 0, "CAN_COLLIDE"];
    [_d, true, false] call _fill;
    // E: local, stand-in, locked and frozen
    private _e = createVehicleLocal ["GroundWeaponHolder", 4 call _pos, [], 0, "CAN_COLLIDE"];
    [_e, false, true] call _fill;
    _e lockInventory true;
    _e enableSimulation false;
    // F: local _Scripted, stand-in
    private _f = createVehicleLocal ["GroundWeaponHolder_Scripted", 5 call _pos, [], 0, "CAN_COLLIDE"];
    [_f, false, true] call _fill;
    // G: global, stand-in
    private _g = createVehicle ["GroundWeaponHolder", 6 call _pos, [], 0, "CAN_COLLIDE"];
    _g setPosATL (6 call _pos);
    _g addItemCargoGlobal ["efku_lids_standIn_0", 1];
    _g addItemCargoGlobal ["FirstAidKit", 2];
    _g addMagazineCargoGlobal ["30Rnd_65x39_caseless_mag", 2];
    _g addWeaponCargoGlobal ["arifle_MX_F", 1];

    sleep 2;
    _cam camSetPos [4097.5, 4095, 2.2];
    _cam camSetTarget [4097.5, 4100, 0];
    _cam camSetFov 0.9;
    _cam camCommit 0;
    sleep 1.5;
    {
        diag_log format ["EFKUTEST %1 obj %2 null %3 hidden %4 sim %5 cargo %6 %7 %8", _x select 1, _x select 0, isNull (_x select 0), isObjectHidden (_x select 0), simulationEnabled (_x select 0), getItemCargo (_x select 0), magazineCargo (_x select 0), weaponCargo (_x select 0)];
    } forEach [[_a, "A"], [_b, "B"], [_c, "C"], [_d, "D"], [_e, "E"], [_f, "F"], [_g, "G"]];
    diag_log "EFKUTEST SHOT m_all_before";
    sleep 1;

    // A opened the way the lids do it
    private _ok = [_a, "", "kit"] call efku_lids_fnc_openHolder;
    sleep 2;
    {
        _x params ["_h", "_props", "_copy"];
        diag_log format ["EFKUTEST OPEN ok %1 holderHidden %2 copy %3 null %4 hidden %5 sim %6 locked %7 dist %8 cargo %9 %10 %11 props %12", _ok, isObjectHidden _h, _copy, isNull _copy, isObjectHidden _copy, simulationEnabled _copy, lockedInventory _copy, _copy distance _h, getItemCargo _copy, magazineCargo _copy, weaponCargo _copy, _props apply {[typeOf (_x select 0), getPosATL (_x select 0)]}];
    } forEach efku_lids_open;
    diag_log format ["EFKUTEST MODEL holder %1 copy %2", getModelInfo _a, getModelInfo ((efku_lids_open select 0) select 2)];
    diag_log "EFKUTEST SHOT m_all_open";
    sleep 1;
    _cam camSetPos [4090, 4098.3, 1.0];
    _cam camSetTarget [4090, 4100, 0];
    _cam camSetFov 0.6;
    _cam camCommit 0;
    sleep 1.5;
    diag_log "EFKUTEST SHOT m_a_open_close";
    sleep 1;
    // the copy alone shown, holder too
    private _copy = (efku_lids_open select 0) select 2;
    _a hideObject false;
    sleep 0.5;
    diag_log "EFKUTEST SHOT m_a_holder_shown";
    sleep 1;
    _a hideObject true;
    if (!isNull _copy) then {
        _copy setPosATL ((getPosATL _a) vectorAdd [0, -1, 0]);
        sleep 0.5;
        diag_log format ["EFKUTEST COPYMOVED %1 hidden %2", getPosATL _copy, isObjectHidden _copy];
        diag_log "EFKUTEST SHOT m_a_copy_moved";
        sleep 1;
    };
    _copy setPosWorld (getPosWorld _a);
    // a kit put in while open: the pile is rebuilt
    _a addItemCargoGlobal ["efak_AFAK", 1];
    sleep 1;
    diag_log format ["EFKUTEST REBUILT %1", efku_lids_open apply {[isNull (_x select 2), getItemCargo (_x select 2), count (_x select 1)]}];
    diag_log "EFKUTEST SHOT m_a_after_put";
    sleep 1;
    private _s = createVehicle ["WeaponHolderSimulated", [4090, 4097, 0.3], [], 0, "CAN_COLLIDE"];
    _s addItemCargoGlobal ["efak_IFAK", 1];
    _s addMagazineCargoGlobal ["30Rnd_65x39_caseless_mag", 2];
    sleep 2;
    [_s, "", "kit"] call efku_lids_fnc_openHolder;
    sleep 1;
    _cam camSetPos [4090, 4095.5, 1.0];
    _cam camSetTarget [4090, 4097, 0];
    _cam camCommit 0;
    sleep 1;
    diag_log format ["EFKUTEST SIM %1", efku_lids_open apply {[typeOf (_x select 0), typeOf (_x select 2), getItemCargo (_x select 2), magazineCargo (_x select 2), simulationEnabled (_x select 2)]}];
    diag_log "EFKUTEST SHOT m_sim_open";
    sleep 1;
    ["kit", true] call efku_lids_fnc_closeLids;
    sleep 2;
    diag_log "EFKUTEST DONE";
};
