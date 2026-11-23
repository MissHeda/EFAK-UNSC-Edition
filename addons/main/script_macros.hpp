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

// A kit as a placeable item (Eden and Zeus, "Kits"): a ground holder with one kit in it, which the
// lids addon opens like any other kit on the ground.
#define KIT_ITEM(KIT,NAME) \
    class DOUBLES(Item,KIT): Item_Base_F { \
        scope = 2; \
        scopeCurator = 2; \
        author = "Miss Heda"; \
        displayName = NAME; \
        editorCategory = "EdCat_efku"; \
        editorSubcategory = "EdSubcat_efku_items"; \
        vehicleClass = "Items"; \
        efku_item = 1; \
        model = "\A3\Weapons_f\dummyweapon.p3d"; \
        class TransportItems { \
            class KIT { \
                name = #KIT; \
                count = 1; \
            }; \
        }; \
    }
