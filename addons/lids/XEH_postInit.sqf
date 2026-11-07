#include "script_component.hpp"

if (!hasInterface) exitWith {};

// Kits on the ground lie shut. Only EFAK's kit window opens one - the very kit it shows - and shuts it
// again when the window closes (fnc_watch); opening the inventory on a pile leaves every lid closed.
[{call FUNC(watch)}, 0.2] call CBA_fnc_addPerFrameHandler;
