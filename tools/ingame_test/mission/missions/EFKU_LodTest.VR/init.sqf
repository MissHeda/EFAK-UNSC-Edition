// Which LOD is drawn from where: an open kit (its prop) and a shut one side by side, photographed from
// 1.3 to 40 m at the game's own field of view. Built with EFKU_LODTEST the LODs are colour-coded.
if (!hasInterface) exitWith {};
[] spawn {
    waitUntil {!isNull player && {time > 1}};
    disableUserInput true;
    player setPosATL [4050, 4050, 0];
    private _cam = "camera" camCreate [4096, 4096, 1];
    _cam cameraEffect ["internal", "back"];
    showCinemaBorder false;
    private _kit = "efak_MFAK";
    private _p = [4096, 4100, 0];
    {
        private _h = createVehicle ["GroundWeaponHolder", _p vectorAdd [_x, 0, 0], [], 0, "CAN_COLLIDE"];
        _h setDir 180;
        _h setPosATL (_p vectorAdd [_x, 0, 0]);
        _h addItemCargoGlobal [_kit, 1];
        if (_x < 0) then {[_h] spawn {sleep 1; [_this select 0] call efku_lids_fnc_openHolder}};
    } forEach [-0.4, 0.4];
    sleep 4;
    {
        _cam camSetPos (_p vectorAdd [0, -_x, 1.6]);
        _cam camSetTarget (_p vectorAdd [0, 0, 0.05]);
        _cam camSetFov 0.75;
        _cam camCommit 0;
        sleep 2.5;
        diag_log format ["EFKUTEST SHOT lod_%1", _x * 10];
        sleep 1;
    } forEach [1.3, 2.5, 4, 6, 9, 13, 20, 30, 40];
    diag_log "EFKUTEST DONE";
};
