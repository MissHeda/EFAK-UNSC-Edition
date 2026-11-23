// Measures The Cole Protocol's health pack (the model is encrypted, so only the game can tell its
// size) and photographs it from five sides, against a 10 cm grid of markers.
if (!hasInterface) exitWith {};

[] spawn {
    waitUntil {!isNull player && {time > 1}};
    disableUserInput true;
    private _p = (getPosATL player) vectorAdd [0, 6, 0];
    _p set [2, 0];
    private _o = createSimpleObject ["\TCP\Weapons\Items\HealthPack\healthPack.p3d", ATLToASL _p, true];
    private _bb = 0 boundingBoxReal _o;
    private _bbv = 1 boundingBoxReal _o;
    diag_log format ["EFKUTEST TCPBOX visual %1 geo %2 selections %3", _bb, _bbv, _o selectionNames "Memory"];
    diag_log format ["EFKUTEST TCPMASS %1", getNumber (configFile >> "CfgWeapons" >> "TCP_HealthPack" >> "ItemInfo" >> "mass")];
    _o setPosASL ((ATLToASL _p) vectorAdd [0, 0, -((_bb select 0) select 2)]);
    private _cam = "camera" camCreate (_p vectorAdd [0, 0, 2]);
    _cam cameraEffect ["internal", "back"];
    showCinemaBorder false;
    {
        _x params ["_view", "_off"];
        _cam camSetPos (_p vectorAdd _off);
        _cam camSetTarget (_p vectorAdd [0, 0, 0.06]);
        _cam camSetFov 0.12;
        _cam camCommit 0;
        sleep 2;
        diag_log format ["EFKUTEST SHOT tcp_%1", _view];
        sleep 1.5;
    } forEach [["top", [0, -0.001, 3]], ["front", [0, -3, 0.06]], ["side", [3, 0, 0.06]], ["iso", [1.6, -2, 1.6]], ["back", [0, 3, 0.06]]];
    diag_log "EFKUTEST DONE";
};
