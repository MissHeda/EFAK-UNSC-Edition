#include "\x\cba\addons\main\script_macros_common.hpp"
#include "\x\cba\addons\xeh\script_xeh.hpp"

// Functions live in each addon's functions folder, compiled through CBA.
#undef PREP
#define PREP(fncName) [QPATHTOF(functions\DOUBLES(fnc,fncName).sqf), QFUNC(fncName)] call CBA_fnc_compileFunction

// A kit as a world object (addons/boxes): the kit's model standing up (<kit>_box.p3d), contents under the lid, the
// box's name, the kit it packs, the lid's sound, how much it holds and its size as ACE cargo. The
// class body stays open for what a box adds (efku_extra[]), and is closed by the caller.
#define KIT_BOX(FILE,KIT,NAME,SOUND,LOAD,SIZE) \
    class DOUBLES(efku_Box,FILE): efku_boxes_base { \
        scope = 2; \
        scopeCurator = 2; \
        displayName = NAME; \
        model = QPATHTOF(data\DOUBLES(FILE,box).p3d); \
        editorPreview = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        icon = "iconCrateSupp"; \
        efku_kit = #KIT; \
        efku_sound = #SOUND; \
        maximumLoad = LOAD; \
        ace_cargo_size = SIZE;

// A kit as a placeable item (Eden and Zeus, "Kits"; it then lies in a ground holder, as a dropped kit
// does), and what a kit dropped beside a vehicle becomes: a world object with the kit in its inventory,
// not a ground holder, so PH Vehicles Arsenal can attach it and restore it from a preset. It goes away
// once emptied. See efku_boxes_fnc_initItem.
#define KIT_ITEM(FILE,KIT,NAME) \
    class DOUBLES(Item,KIT): efku_boxes_drop { \
        scope = 2; \
        scopeCurator = 2; \
        displayName = NAME; \
        model = QPATHTOF(data\DOUBLES(FILE,box).p3d); \
        editorPreview = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        class TransportItems { \
            class KIT { \
                name = #KIT; \
                count = 1; \
            }; \
        }; \
    }
