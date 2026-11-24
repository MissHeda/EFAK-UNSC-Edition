#include "..\script_component.hpp"
/*
 * Author: Miss Heda
 * On the client, with a box or kit item open in the inventory: a double click on a kit in the
 * container list opens it, as one on the ground does. EFAK listens for that only on the ground list
 * and the player's own containers; a box shows what it holds in the container list next to them.
 * A kit EFAK already offers there (CBA's menu, for kits the player has carried) is left to EFAK.
 *
 * Arguments:
 * None
 *
 * Return Value:
 * None
 *
 * Example:
 * call efku_boxes_fnc_hookDoubleClick;
 *
 * Public: No
 */

if (isNil "efak_core_fnc_openKit" || {!(missionNamespace getVariable ["efak_core_doubleClickOpen", true])}) exitWith {};

private _ctrl = (findDisplay 602) displayCtrl 640;
if (isNull _ctrl || {_ctrl getVariable [QGVAR(hooked), false]}) exitWith {};
_ctrl setVariable [QGVAR(hooked), true];
// CBA listens on this list only if some item had its menu when the inventory opened
_ctrl setVariable [QGVAR(cba), !isNil "cba_ui_ItemContextMenuOptions"];

_ctrl ctrlAddEventHandler ["LBDblClick", {
    params ["_ctrl", "_index"];

    private _item = [_ctrl lbData _index, _ctrl lnbData [_index, 0]] select (ctrlType _ctrl == 102);
    if !([_item] call efak_core_fnc_isKit) exitWith {};
    if ((_ctrl getVariable [QGVAR(cba), false]) && {(toLowerANSI _item) in (missionNamespace getVariable ["efak_core_contextMenuRegistered", createHashMap])}) exitWith {};

    private _owner = [_item, missionNamespace getVariable [QGVAR(opened), objNull]] call efak_core_fnc_findKitHolder;
    if (isNull _owner) exitWith {};

    [_owner, _item] call efak_core_fnc_openKit;
}];
