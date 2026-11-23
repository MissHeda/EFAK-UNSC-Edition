// The kits as world objects (addons/boxes): every box placed as Zeus would, packed after a moment,
// one strapped to the back of an offroader the way PH Vehicles Arsenal attaches it; its inventory is
// opened through the player, the lid has to swing open and shut again. Also the placeable items.
if (!hasInterface) exitWith {};

[] spawn {
    waitUntil {!isNull player && {time > 1}};
    disableUserInput true;
    private _c = (getPosATL player) vectorAdd [0, 6, 0];
    _c set [2, 0];
    private _boxes = ["efku_Box_ifak", "efku_Box_afak", "efku_Box_mfak", "efku_Box_mfakplus", "efku_Box_narcbox",
        "efku_Box_utility_pouch", "efku_Box_ammo_pouch", "efku_Box_ammo_bag", "efku_Box_engineer_bag", "efku_Box_cbrn_bag",
        "efku_Box_special_ammo", "efku_Box_ordnance_crate"];
    private _made = [];
    {
        private _p = _c vectorAdd [(_forEachIndex - 5.5) * 1.5, 0, 0];
        private _b = createVehicle [_x, _p, [], 0, "CAN_COLLIDE"];
        _b setDir 0;
        _b setPosATL _p;
        _made pushBack _b;
    } forEach _boxes;
    {
        private _p = _c vectorAdd [(_forEachIndex - 5.5) * 1.5, 3, 0];
        private _i = createVehicle [_x, _p, [], 0, "CAN_COLLIDE"];
        _i setPosATL _p;
    } forEach ["Item_efak_AFAK", "Item_eup_AmmoBag", "Item_efku_OrdnanceCase"];
    {diag_log format ["EFKUTEST PHYS0 %1 up %2 com %3 sim %4", typeOf _x, vectorUp _x, getCenterOfMass _x, getText (configOf _x >> "simulation")]} forEach _made;
    sleep 3;
    {diag_log format ["EFKUTEST AXIS %1 axis %2 bbox %3 mem %4", typeOf _x, _x selectionPosition ["lid_axis", "Memory"], 0 boundingBoxReal _x, _x selectionNames "Memory"]} forEach [_made select 7, _made select 1];
    {diag_log format ["EFKUTEST PHYS3 %1 up %2", typeOf _x, vectorUp _x]} forEach _made;
    {
        diag_log format ["EFKUTEST BOX %1 packed %2 items %3 mags %4 bbox %5 mass %6", typeOf _x, _x getVariable ["efku_boxes_packed", false],
            getItemCargo _x, getMagazineCargo _x, (0 boundingBoxReal _x) select 1 vectorDiff ((0 boundingBoxReal _x) select 0), getMass _x];
    } forEach _made;

    // strapped onto an offroader's bed
    private _car = createVehicle ["C_Offroad_01_F", _c vectorAdd [0, 9, 0], [], 0, "CAN_COLLIDE"];
    _car setDir 90;
    sleep 1;
    private _ord = _made select 11;
    _ord attachTo [_car, [0, -1.8, 0.05]];
    _ord setDir 0;
    sleep 1;

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
        diag_log format ["EFKUTEST SHOT bx_%1", _name];
        sleep 1.2;
    };
    ["row", _c vectorAdd [0, -7, 3], _c vectorAdd [0, 1, 0], 0.75] call _shot;

    // the player opens the attached box's inventory: the lid opens for everyone
    player setPosATL ((getPosATL _car) vectorAdd [-1.5, -3.2, 0]);
    sleep 0.5;
    player action ["Gear", _ord];
    sleep 2.5;
    diag_log format ["EFKUTEST OPENED dialog %1 lid %2 users %3", !isNull findDisplay 602, _ord animationSourcePhase "lid", _ord getVariable ["efku_boxes_users", []]];
    closeDialog 0;
    (findDisplay 602) closeDisplay 2;
    sleep 0.2;
    // the dialog over the picture would hide it: open the lid the way the server does, for the shot
    [_ord, 99, true] call efku_boxes_fnc_use;
    sleep 1.5;
    ["car_open", (getPosATL _car) vectorAdd [-2.5, -4.5, 2.6], (getPosATL _car) vectorAdd [0, -1.8, 1], 0.6] call _shot;
    [_ord, 99, false] call efku_boxes_fnc_use;
    sleep 2;
    diag_log format ["EFKUTEST CLOSED lid %1 users %2", _ord animationSourcePhase "lid", _ord getVariable ["efku_boxes_users", []]];
    ["car_shut", (getPosATL _car) vectorAdd [-2.5, -4.5, 2.6], (getPosATL _car) vectorAdd [0, -1.8, 1], 0.6] call _shot;
    // the AFAK and the ammo box open, close up
    {
        _x params ["_i", "_name"];
        private _b = _made select _i;
        [_b, 99, true] call efku_boxes_fnc_use;
        sleep 1.5;
        diag_log format ["EFKUTEST LID %1 phase %2 users %3 names %4", _name, _b animationSourcePhase "lid", _b getVariable ["efku_boxes_users", []], animationNames _b];
        [_name, (getPosATL _b) vectorAdd [0.4, -1.3, 1.1], (getPosATL _b) vectorAdd [0, 0, 0.1], 0.6] call _shot;
        [_b, 99, false] call efku_boxes_fnc_use;
    } forEach [[1, "afak"], [7, "ammo"], [10, "spec"], [8, "eng"], [6, "pouch"]];
    diag_log "EFKUTEST DONE";
};
