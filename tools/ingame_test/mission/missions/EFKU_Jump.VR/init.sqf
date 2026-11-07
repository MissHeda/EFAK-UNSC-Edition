// Close look for any jump: each kit shut in its holder, then as its prop with the lid shut, from the
// front and the side at ground level, same camera. Any shift between the pairs is the jump.
if (!hasInterface) exitWith {};
[] spawn {
    waitUntil {!isNull player && {time > 1}};
    disableUserInput true;
    player setPosATL [4090, 4090, 0];
    private _cam = "camera" camCreate [4096, 4096, 1];
    _cam cameraEffect ["internal", "back"];
    showCinemaBorder false;
    {
        _x params ["_kit", "_name"];
        private _p = [4096 + _forEachIndex * 3, 4100, 0];
        private _h = createVehicle ["GroundWeaponHolder", _p, [], 0, "CAN_COLLIDE"];
        _h setDir 0;
        _h setPosATL _p;
        _h addItemCargoGlobal [_kit, 1];
        sleep 2;
        private _views = [["front", [0, -0.9, 0.06]], ["side", [0.9, 0, 0.06]]];
        {
            _x params ["_v", "_o"];
            _cam camSetPos (_p vectorAdd _o);
            _cam camSetTarget (_p vectorAdd [0, 0, 0.04]);
            _cam camSetFov 0.3;
            _cam camCommit 0;
            sleep 1.5;
            diag_log format ["EFKUTEST SHOT j_%1_%2_item", _name, _v];
            sleep 1;
        } forEach _views;
        diag_log format ["EFKUTEST POS holder %1 asl %2 slots0 %3", getPosWorld _h, getPosASL _h, ([_h] call efku_lids_fnc_holderSlots) select 0];
        [_h] call efku_lids_fnc_openHolder;
        private _prop = (((efku_lids_open select 0) select 1) select 0) select 0;
        _prop animateSource ["lid", 0, true];
        diag_log format ["EFKUTEST POS prop %1 bb %2", getPosWorld _prop, boundingBoxReal _prop];
        {
            _x params ["_v", "_o"];
            _cam camSetPos (_p vectorAdd _o);
            _cam camSetTarget (_p vectorAdd [0, 0, 0.04]);
            _cam camCommit 0;
            sleep 1.5;
            diag_log format ["EFKUTEST SHOT j_%1_%2_prop", _name, _v];
            sleep 1;
        } forEach _views;
        ["", true] call efku_lids_fnc_closeLids;
    } forEach [["efak_IFAK", "ifak"], ["efak_MFAK", "mfak"], ["efak_AFAK", "afak"]];
    diag_log "EFKUTEST DONE";
};
