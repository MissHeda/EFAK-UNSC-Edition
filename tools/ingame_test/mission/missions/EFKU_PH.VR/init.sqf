// Kits placed as items (Zeus style, dropped from a little height) must be real kit instances and lie
// upright without being picked up; a kit dropped beside a vehicle must show in PH Vehicles Arsenal's
// tuning list. Needs -Extra 3817737577.
if (!hasInterface) exitWith {};

[] spawn {
    waitUntil {!isNull player && {time > 1}};
    disableUserInput true;
    private _c = (getPosATL player) vectorAdd [0, 6, 0];
    _c set [2, 0];
    private _items = [];
    {
        private _p = _c vectorAdd [(_forEachIndex - 1) * 1.2, 0, 0.4];
        private _i = createVehicle [_x, _p, [], 0, "CAN_COLLIDE"];
        _i setPosATL _p;
        _i setDir (_forEachIndex * 40);
        _items pushBack _i;
    } forEach ["Item_efak_AFAK", "Item_eup_AmmoBag", "Item_eup_CBRNBag"];
    sleep 4;
    {diag_log format ["EFKUTEST ITEM %1 cargo %2 up %3 z %4 ph %5", typeOf _x, itemCargo _x, vectorUp _x, (getPosATL _x) select 2, _x getVariable ["PHVA_tuningAllowed", false]]} forEach _items;

    private _cam = "camera" camCreate (_c vectorAdd [0, -3, 2]);
    _cam cameraEffect ["internal", "back"];
    showCinemaBorder false;
    private _shot = {
        params ["_name", "_pos", "_target", ["_fov", 0.6]];
        _cam camSetPos _pos;
        _cam camSetTarget _target;
        _cam camSetFov _fov;
        _cam camCommit 0;
        sleep 2;
        diag_log format ["EFKUTEST SHOT ph_%1", _name];
        sleep 1.2;
    };
    ["items", _c vectorAdd [0, -2.5, 1.2], _c, 0.6] call _shot;

    // a kit dropped beside an offroader
    private _car = createVehicle ["C_Offroad_01_F", _c vectorAdd [0, 9, 0], [], 0, "CAN_COLLIDE"];
    _car setDir 90;
    player setPosATL ((getPosATL _car) vectorAdd [-1.5, -3.2, 0]);
    diag_log format ["EFKUTEST MODELS item %1 ground %2 sim %3", getText (configFile >> "CfgVehicles" >> "Item_efak_AFAK" >> "model"), getText (configFile >> "CfgVehicles" >> "GroundWeaponHolder" >> "model"), getText (configFile >> "CfgVehicles" >> "Item_Base_F" >> "simulation")];
    private _kit = (itemCargo (_items select 0)) select 0;
    deleteVehicle (_items select 0);
    private _gh = createVehicle ["GroundWeaponHolder", (getPosATL player) vectorAdd [0.5, 0.5, 0], [], 0, "CAN_COLLIDE"];
    _gh addItemCargoGlobal [_kit, 1];
    sleep 0.5;
    [player, _gh, _kit] call efku_boxes_fnc_onPut;
    sleep 2;
    private _near = (_car nearObjects 8) select {getNumber (configOf _x >> "efku_item") == 1};
    diag_log format ["EFKUTEST DROPPED old %1 new %2 cargo %3", isNull _gh, _near apply {typeOf _x}, _near apply {itemCargo _x}];
    private _list = [_car] call PHVA_fnc_serverNearbyList;
    diag_log format ["EFKUTEST PHLIST %1", _list apply {if (_x isEqualType objNull) then {typeOf _x} else {_x}}];
    ["drop", (getPosATL _car) vectorAdd [-3, -6, 2], (getPosATL _car) vectorAdd [-1, -2.7, 0], 0.6] call _shot;
    diag_log "EFKUTEST DONE";
};
