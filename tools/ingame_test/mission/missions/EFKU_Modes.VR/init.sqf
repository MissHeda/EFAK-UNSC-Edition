// Checks the lid modes and the bookkeeping behind MP sync, in singleplayer: the inventory opens lids
// only in "Inventory and kit window", a remote player's open is counted apart from ours, and the
// shadow casters hide and come back in the very frame the props appear and go.
if (!hasInterface) exitWith {};
[] spawn {
    waitUntil {!isNull player && {time > 1}};
    disableUserInput true;
    player setPosATL [4090, 4090, 0];
    private _p = [4096, 4100, 0];
    private _h = createVehicle ["GroundWeaponHolder", _p, [], 0, "CAN_COLLIDE"];
    _h setPosATL _p;
    _h addItemCargoGlobal ["efak_IFAK", 1];
    _h addItemCargoGlobal ["efak_MFAK", 1];
    sleep 2;
    private _casterHidden = {
        private _e = efku_lids_casters get (str (_h getVariable ["efku_lids_key", -1]));
        if (isNil "_e") then {_e = (values efku_lids_casters) param [0, []]};
        (_e param [2, []]) apply {isObjectHidden (_x select 0)}
    };
    diag_log format ["EFKUTEST casters before %1", call _casterHidden];

    efku_lids_mode = 1;
    [player, _h] call efku_lids_fnc_openLids;
    diag_log format ["EFKUTEST mode1 inventory open count %1", count efku_lids_open];

    efku_lids_mode = 2;
    [player, _h] call efku_lids_fnc_openLids;
    diag_log format ["EFKUTEST mode2 inventory open count %1 users %2 casters same frame %3", count efku_lids_open, (efku_lids_open param [0, []]) param [4, []], call _casterHidden];
    sleep 1;

    [_h, "", "kit", 99] call efku_lids_fnc_remoteOpen;
    diag_log format ["EFKUTEST + remote users %1", (efku_lids_open select 0) select 4];
    ["inventory"] call efku_lids_fnc_requestClose;
    diag_log format ["EFKUTEST - inventory: open %1 users %2", count efku_lids_open, (efku_lids_open param [0, []]) param [4, []]];
    ["kit", 99] call efku_lids_fnc_remoteClose;
    diag_log format ["EFKUTEST - remote: open %1 hidden holder %2 casters %3", count efku_lids_open, isObjectHidden _h, call _casterHidden];
    sleep 1.2;
    diag_log format ["EFKUTEST after swing: holder hidden %1 casters %2", isObjectHidden _h, call _casterHidden];

    efku_lids_mode = 0;
    [player, _h] call efku_lids_fnc_openLids;
    diag_log format ["EFKUTEST mode0 open count %1", count efku_lids_open];
    diag_log "EFKUTEST DONE";
};
