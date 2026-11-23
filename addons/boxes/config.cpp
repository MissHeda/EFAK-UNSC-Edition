#include "script_component.hpp"

// Every kit as a world object: a box placed in Eden or Zeus, carried, loaded, attached to a vehicle
// (PH Vehicles Arsenal), packed with what its kit holds. Its inventory is open to anyone close
// enough - by the vanilla action or ACE's - and its lid swings open while someone looks inside.
// The box classes themselves are in addons/kits and addons/eup, next to the kits they show.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"efku_main", "efku_lids", "cba_main", "cba_xeh"};
        author = "Miss Heda";
        url = "https://github.com/MissHeda/EFAK-UNSC-Edition";
        VERSION_CONFIG;
    };
};

class CfgEditorCategories {
    class EdCat_efku {
        displayName = "UNSC Kits";
    };
};

class CfgEditorSubcategories {
    class EdSubcat_efku_boxes {
        displayName = "Kit boxes";
    };
    class EdSubcat_efku_items {
        displayName = "Kits";
    };
};

// What a box class sets, besides its model, names and pictures:
//   efku_kit        the kit it is: its default contents (EFAK's setting for that kit) are packed
//   efku_extra[]    more to pack, {class, count, class, count, ...}; classes of mods that are not
//                   loaded are skipped
//   efku_sound      the lid's sound set in efku_lids: case, med or pouch
class CfgVehicles {
    class ReammoBox_F;
    class GVAR(base): ReammoBox_F {
        scope = 1;
        scopeCurator = 0;
        author = "Miss Heda";
        editorCategory = "EdCat_efku";
        editorSubcategory = "EdSubcat_efku_boxes";
        vehicleClass = "Ammo";
        displayName = "UNSC kit box";
        destrType = "DestructNo";
        maximumLoad = 400;
        efku_kit = "";
        efku_extra[] = {};
        efku_sound = "case";
        class TransportItems {};
        class TransportMagazines {};
        class TransportWeapons {};
        class TransportBackpacks {};
        class AnimationSources {
            class lid {
                source = "user";
                animPeriod = 1;
                initPhase = 0;
            };
        };
        // ACE: dragged, carried, loaded as cargo, opened from the interaction menu
        ace_cargo_canLoad = 1;
        ace_cargo_size = 1;
        ace_dragging_canDrag = 1;
        ace_dragging_dragPosition[] = {0, 1.2, 0};
        ace_dragging_canCarry = 1;
        ace_dragging_carryPosition[] = {0, 1, 1};
        class ACE_Actions {
            class ACE_MainActions {
                displayName = "$STR_ace_interaction_MainAction";
                selection = "";
                distance = 4;
                condition = "true";
                class GVAR(open) {
                    displayName = "$STR_A3_Gear1";
                    condition = "alive _target";
                    statement = "_player action ['Gear', _target]";
                    icon = "\a3\ui_f\data\igui\cfg\actions\gear_ca.paa";
                    exceptions[] = {"isNotInside", "isNotSitting"};
                };
            };
        };
    };
};

class Extended_PreInit_EventHandlers {
    class ADDON {
        init = QUOTE(call COMPILE_FILE(XEH_preInit));
    };
};

class Extended_PostInit_EventHandlers {
    class ADDON {
        init = QUOTE(call COMPILE_FILE(XEH_postInit));
    };
};

class Extended_Init_EventHandlers {
    class GVAR(base) {
        class ADDON {
            init = QUOTE(_this call FUNC(init));
        };
    };
    // the kits placed as items (efku_item = 1; the function skips every other item)
    class Item_Base_F {
        class ADDON {
            init = QUOTE(_this call FUNC(initItem));
        };
    };
};
