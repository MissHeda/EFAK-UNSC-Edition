// Checks the lids on piles: which slot each piece of a mixed pile lies on (numbers drawn at the
// slots fnc_holderSlots works out, with the piece fnc_holderPieces expects there), the pile opened,
// and a single kit seen from the side, closed in its holder and as a prop, for any jump.
if (!hasInterface) exitWith {};

[] spawn {
    waitUntil {!isNull player && {time > 1}};
    disableUserInput true;
    {if (_x != player) then {deleteVehicle _x}} forEach units group player;

    private _c = (getPosATL player) vectorAdd [0, 8, 0];
    _c set [2, 0];
    player setPosATL (_c vectorAdd [0, -6, 0]);
    private _cam = "camera" camCreate (_c vectorAdd [0, 0, 3]);
    _cam cameraEffect ["internal", "back"];
    showCinemaBorder false;

    // a pile, put together in a mixed order
    private _h = createVehicle ["GroundWeaponHolder", _c, [], 0, "CAN_COLLIDE"];
    _h setPosATL _c;
    _h setDir 30;
    _h addItemCargoGlobal ["efak_IFAK", 1];
    _h addWeaponCargoGlobal ["arifle_MX_F", 1];
    _h addMagazineCargoGlobal ["30Rnd_65x39_caseless_mag", 2];
    _h addBackpackCargoGlobal ["B_AssaultPack_rgr", 1];
    _h addItemCargoGlobal ["efak_MFAK", 1];
    _h addItemCargoGlobal ["FirstAidKit", 3];
    _h addItemCargoGlobal ["efak_NarcBox", 1];
    sleep 1;

    private _pieces = [_h] call efku_lids_fnc_holderPieces;
    private _slots = [_h] call efku_lids_fnc_holderSlots;
    diag_log format ["EFKUTEST PIECES %1", _pieces apply {_x select 1}];
    diag_log format ["EFKUTEST SLOTS %1", _slots];
    efkutest_labels = [];
    {
        if (_forEachIndex < count _pieces) then {
            efkutest_labels pushBack [_h modelToWorldVisual ((_x select 0) vectorAdd [0, 0, 0.02]), format ["%1 %2", _forEachIndex, (_pieces select _forEachIndex) select 1]];
        };
    } forEach _slots;
    addMissionEventHandler ["Draw3D", {
        {drawIcon3D ["", [1, 0.2, 0.2, 1], _x select 0, 0, 0, 0, _x select 1, 2, 0.035, "PuristaBold"]} forEach efkutest_labels;
    }];

    _cam camSetPos (_c vectorAdd [0, -0.001, 4.2]);
    _cam camSetTarget _c;
    _cam camSetFov 0.6;
    _cam camCommit 0;
    sleep 2;
    diag_log "EFKUTEST SHOT stack_closed";
    sleep 1.5;
    efkutest_labels = [];
    private _t = "GroundWeaponHolder" createVehicleLocal [0, 0, 0];
    _t addItemCargo ["efku_lids_standIn_0", 1];
    diag_log format ["EFKUTEST STANDIN class %1 added %2", isClass (configFile >> "CfgWeapons" >> "efku_lids_standIn_0"), getItemCargo _t];
    deleteVehicle _t;
    [_h] call efku_lids_fnc_openHolder;
    sleep 1.5;
    diag_log format ["EFKUTEST OPEN orig %1 copy %2", getItemCargo _h, getItemCargo ((efku_lids_open select 0) select 2)];
    diag_log "EFKUTEST SHOT stack_open";
    sleep 1.5;
    _cam camSetPos (_c vectorAdd [1.6, -2.4, 1.4]);
    _cam camSetTarget _c;
    _cam camCommit 0;
    sleep 1.5;
    diag_log "EFKUTEST SHOT stack_open_side";
    sleep 1.5;
    ["", true] call efku_lids_fnc_closeLids;

    // one kit from the side, with the lid shut: in its holder, then as a prop
    {
        private _kit = _x;
        private _p = _c vectorAdd [4 + _forEachIndex * 2, 0, 0];
        private _k = createVehicle ["GroundWeaponHolder", _p, [], 0, "CAN_COLLIDE"];
        _k setPosATL _p;
        _k setDir 20;
        _k addItemCargoGlobal [_kit, 1];
        sleep 1;
        _cam camSetPos (_p vectorAdd [0, -2.6, 0.1]);
        _cam camSetTarget (_p vectorAdd [0, 0, 0.05]);
        _cam camSetFov 0.25;
        _cam camCommit 0;
        sleep 1.5;
        diag_log format ["EFKUTEST SHOT side_%1_item", _kit];
        sleep 1.5;
        [_k] call efku_lids_fnc_openHolder;
        {(_x select 0) animateSource ["lid", 0, true]} forEach ((efku_lids_open select 0) select 1);
        sleep 1;
        diag_log format ["EFKUTEST SHOT side_%1_prop", _kit];
        sleep 1.5;
        ["", true] call efku_lids_fnc_closeLids;
        _cam camSetPos (_p vectorAdd [0, -0.001, 1.6]);
        _cam camCommit 0;
        sleep 1.5;
        diag_log format ["EFKUTEST SHOT top_%1_item", _kit];
        sleep 1.5;
        [_k] call efku_lids_fnc_openHolder;
        sleep 1.5;
        diag_log format ["EFKUTEST SHOT top_%1_open", _kit];
        sleep 1.5;
        ["", true] call efku_lids_fnc_closeLids;
    } forEach ["efak_IFAK", "efak_MFAK"];
    diag_log "EFKUTEST DONE";
};
