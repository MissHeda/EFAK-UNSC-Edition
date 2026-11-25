// What deletes the lids' copy pile: variants made the way fnc_openHolder makes it, watched per frame.
if (!hasInterface) exitWith {};
[] spawn {
    waitUntil {!isNull player && {time > 1}};
    disableUserInput true;
    player setPosATL [4080, 4080, 0];
    private _real = {
        params ["_p"];
        private _a = createVehicle ["GroundWeaponHolder", _p, [], 0, "CAN_COLLIDE"];
        _a setPosATL _p;
        _a addItemCargoGlobal ["FirstAidKit", 2];
        _a addMagazineCargoGlobal ["30Rnd_65x39_caseless_mag", 2];
        _a addWeaponCargoGlobal ["arifle_MX_F", 1];
        _a
    };
    private _mk = {
        params ["_name", "_h", "_off", "_clear", "_hide", "_class"];
        private _c = createVehicleLocal [_class, (getPosATL _h) vectorAdd _off, [], 0, "CAN_COLLIDE"];
        if (_clear) then {clearItemCargo _c; clearWeaponCargo _c; clearMagazineCargo _c; clearBackpackCargo _c};
        _c addItemCargo ["FirstAidKit", 2];
        _c addMagazineCargo ["30Rnd_65x39_caseless_mag", 2];
        _c addWeaponCargo ["arifle_MX_F", 1];
        if (_off isEqualTo [0,0,0]) then {_c setPosWorld (getPosWorldVisual _h)};
        _c lockInventory true;
        if (_hide) then {_h hideObject true};
        [_name, _c]
    };
    private _list = [];
    private _i = 0;
    {
        _x params ["_name", "_off", "_clear", "_hide", "_class"];
        private _h = [[4090 + _i * 3, 4100, 0]] call _real;
        _i = _i + 1;
        sleep 0.3;
        _list pushBack ([_name, _h, _off, _clear, _hide, _class] call _mk);
    } forEach [
        ["same_clear_hide", [0,0,0], true, true, "GroundWeaponHolder"],
        ["same_noclear_hide", [0,0,0], false, true, "GroundWeaponHolder"],
        ["same_clear_nohide", [0,0,0], true, false, "GroundWeaponHolder"],
        ["off1m_clear_hide", [0,1,0], true, true, "GroundWeaponHolder"],
        ["same_clear_hide_scripted", [0,0,0], true, true, "GroundWeaponHolder_Scripted"],
        ["same_noclear_hide_scripted", [0,0,0], false, true, "GroundWeaponHolder_Scripted"]
    ];
    private _f0 = diag_frameNo;
    private _last = [];
    while {diag_frameNo - _f0 < 400} do {
        private _now = _list apply {[_x select 0, !isNull (_x select 1)]};
        if (_now isNotEqualTo _last) then {
            diag_log format ["EFKUTEST frame %1 t %2 %3", diag_frameNo - _f0, time, _now];
            _last = _now;
        };
        uiSleep 0.001;
    };
    diag_log "EFKUTEST DONE";
};
