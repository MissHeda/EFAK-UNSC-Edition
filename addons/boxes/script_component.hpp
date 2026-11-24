#define COMPONENT boxes
#define COMPONENT_BEAUTIFIED EFAK UNSC - Boxes
#include "\z\efku\addons\main\script_mod.hpp"
#include "\z\efku\addons\main\script_macros.hpp"

// How long after a box appears the server waits before packing it, so that what Eden, Zeus or a
// vehicle preset puts in it first counts (seconds).
#define FILL_DELAY 1

// PH Vehicles Arsenal's placement preview: a local copy (no net ID in MP) it freezes and makes
// pass-through right after creating it (in SP, where everything has a net ID, only that tells).
// Checked a moment after init, once PH has set it up. Left alone: not filled, moved or listed.
#define IS_PREVIEW(OBJ) (netId OBJ isEqualTo "0:0" || {!simulationEnabled OBJ && {(getPhysicsCollisionFlag OBJ) isEqualTo [false]}})
