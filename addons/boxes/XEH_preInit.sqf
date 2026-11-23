#include "script_component.hpp"

ADDON = false;

#include "XEH_PREP.hpp"

// Server: the boxes someone has open (each keeps its client ids in efku_boxes_users).
GVAR(users) = [];
// Client: the box this player has open, or objNull.
GVAR(current) = objNull;

ADDON = true;
