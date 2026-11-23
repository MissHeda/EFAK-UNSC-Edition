#include "script_component.hpp"

// The same for Enhanced Utility Pouches: new models and pictures for its five pouches - and two
// cases of this mod's own next to them, special ammunition and explosives + ordnance. Skipped
// without a word when EUP is not loaded, so this mod works with EFAK alone, EUP alone or both.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {"efku_Box_utility_pouch", "efku_Box_ammo_pouch", "efku_Box_ammo_bag", "efku_Box_engineer_bag", "efku_Box_cbrn_bag", "efku_Box_special_ammo", "efku_Box_ordnance_crate", "Item_eup_UtilityPouch", "Item_eup_AmmoPouch", "Item_eup_AmmoBag", "Item_eup_EngineerBag", "Item_eup_CBRNBag", "Item_efku_SpecialAmmoCase", "Item_efku_OrdnanceCase"};
        weapons[] = {"efku_SpecialAmmoCase", "efku_OrdnanceCase"};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"efku_main", "efku_boxes", "eup_pouches"};
        skipWhenMissingDependencies = 1;
        author = "Miss Heda";
        url = "https://github.com/MissHeda/EFAK-UNSC-Edition";
        VERSION_CONFIG;
    };
};

// Size of the generated pool of instance classes per case (tools/generate_instances.py)
#define EFKU_INSTANCES_PER_CASE 300

#define POUCH_LOOK(CLASS,FILE) \
    class CLASS: eup_PouchBase { \
        model = QPATHTOF(data\FILE.p3d); \
        picture = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        editorPreview = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        efku_lidProp = QUOTE(DOUBLES(efku_LidProp,FILE)); \
    }

// EUP's three bags are hard boxes here, and are called that.
#define BOX_LOOK(CLASS,FILE,NAME,DESC) \
    class CLASS: eup_PouchBase { \
        model = QPATHTOF(data\FILE.p3d); \
        displayName = NAME; \
        descriptionShort = DESC; \
        picture = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        editorPreview = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        efku_lidProp = QUOTE(DOUBLES(efku_LidProp,FILE)); \
    }

// The two cases are items like EUP's pouches (its base class), only brought by this mod.
#define CASE_ITEM(CLASS,FILE,NAME,DESC,EMPTY,MASS) \
    class CLASS: eup_PouchBase { \
        model = QPATHTOF(data\FILE.p3d); \
        scope = 2; \
        scopeArsenal = 2; \
        displayName = NAME; \
        descriptionShort = DESC; \
        picture = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        editorPreview = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        efku_lidProp = QUOTE(DOUBLES(efku_LidProp,FILE)); \
        EFAK_emptyWeight = EMPTY; \
        class ItemInfo: CBA_MiscItem_ItemInfo { \
            mass = MASS; \
        }; \
    }

class CfgWeapons {
    class eup_PouchBase;
    class CBA_MiscItem_ItemInfo;
    POUCH_LOOK(eup_UtilityPouch,utility_pouch);
    POUCH_LOOK(eup_AmmoPouch,ammo_pouch);
    BOX_LOOK(eup_AmmoBag,ammo_bag,"Ammo Box","A box of ammunition for the team - belts, magazines, grenades, rockets. Takes magazines only.");
    BOX_LOOK(eup_EngineerBag,engineer_bag,"Engineer Box","Tools and explosives in one box - toolkit, wire cutter, defusal kit, charges and mines.");
    BOX_LOOK(eup_CBRNBag,cbrn_bag,"CBRN Box","Protective gear in one box - CBRN suit, respirator, breathing set, detector watch, filters and decon kit.");

    // Masses as EUP has them: the room the packed case takes, about 40% of its default capacity;
    // EFAK_emptyWeight is what the empty case weighs (1 mass unit = 0.1 lb).
    CASE_ITEM(efku_SpecialAmmoCase,special_ammo,"Special Ammunition Box","A box for the marksmen's ammunition: sniper magazines and sealed packets of rounds. Takes magazines only.",12,95);
    CASE_ITEM(efku_OrdnanceCase,ordnance_crate,"Explosives + Ordnance Box","A padded box for rockets and missiles, demolition charges, mines and hand grenades. Takes nothing else.",18,120);

    #include "CfgWeapons_instances.hpp"
};

#define POUCH_ICONS(KIT,FILE) \
    class KIT { \
        icon = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        iconContents = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        background = QPATHTOF(ui\DOUBLES(FILE,bg_ca).paa); \
    }

#define BOX_ICONS(KIT,FILE,NAME) \
    class KIT { \
        shortName = NAME; \
        icon = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        iconContents = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        background = QPATHTOF(ui\DOUBLES(FILE,bg_ca).paa); \
    }

// What the two cases share with EUP's pouches: not medical, in the pouches' menu and settings
// category, carried like a bag (the hard realism modes unload them into the backpack).
#define CASE_COMMON(FILE) \
    icon = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
    iconContents = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
    background = QPATHTOF(ui\DOUBLES(FILE,bg_ca).paa); \
    instances = EFKU_INSTANCES_PER_CASE; \
    defaultContents = ""; \
    itemFilter = 0; \
    useInTreatments = 0; \
    bag = 1; \
    group = "Pouches"; \
    settingsCategory = "Enhanced Utility Pouches"

class EFAK_Kits {
    POUCH_ICONS(EUP_UtilityPouch,utility_pouch);
    POUCH_ICONS(EUP_AmmoPouch,ammo_pouch);
    BOX_ICONS(EUP_AmmoBag,ammo_bag,"Ammo Box");
    BOX_ICONS(EUP_EngineerBag,engineer_bag,"Engineer Box");
    BOX_ICONS(EUP_CBRNBag,cbrn_bag,"CBRN Box");

    // Magazines only, like the ammo bag - the one the marksmen's ammunition is kept apart in.
    class EFKU_SpecialAmmoCase {
        item = "efku_SpecialAmmoCase";
        shortName = "Special Ammunition Box";
        capacity = 240;
        itemTypes[] = {"magazine"};
        CASE_COMMON(special_ammo);
    };

    // Rockets, missiles, charges and mines. ACE sorts magazines by their type number: "secondary"
    // (512) is unguided rockets and everything that is put down, and the guided ones (768, 1536 -
    // Titan, NLAW, Vorona) are "unknown" to it (measured in game, 2026-11-20). Hand grenades are the same kind of magazine as rifle
    // magazines to the game, so no type lets them in: the whitelist names them - the game's, ACE's
    // and OPTRE's frag, stun, incendiary and smoke grenades (a * stands for any ending). A mission
    // adds another mod's in the case's whitelist setting.
    class EFKU_OrdnanceCase {
        item = "efku_OrdnanceCase";
        shortName = "Explosives + Ordnance Box";
        capacity = 300;
        itemTypes[] = {"magazine/secondary", "magazine/unknown"};
        whitelist = "HandGrenade, MiniGrenade, SmokeShell*, ACE_M84, ACE_M14, ACE_CTS9, OPTRE_M9_Frag, OPTRE_M2_Smoke*, OPTRE_c7_remote_throwable_sticky_mag";
        CASE_COMMON(ordnance_crate);
    };
};

class EFAK_KitGroups {
    class Pouches {
        icon = QPATHTOF(ui\utility_pouch_ca.paa);
    };
};

// What the cases in a crate or vehicle hold and what they are called, next to EUP's fields in the
// framework's Eden attribute category (see EUP's Cfg3DEN.hpp; the framework does the rest).
#define CRATE_CASE_ATTRIBUTES(CASE,NAME) \
    class efak_core_crate_##CASE { \
        displayName = QUOTE(NAME contents); \
        tooltip = "$STR_efak_core_3DEN_CrateContents_Tooltip"; \
        property = QUOTE(efak_core_crate_##CASE); \
        control = "EditMulti3"; \
        expression = "if (!is3DEN && {isServer} && {_value isNotEqualTo ''}) then {[_this,'%s',_value] call efak_core_fnc_fillCrateKits}"; \
        defaultValue = "''"; \
        typeName = "STRING"; \
        validate = "none"; \
        condition = "objectHasInventoryCargo"; \
    }; \
    class efak_core_crateName_##CASE { \
        displayName = QUOTE(NAME name); \
        tooltip = "$STR_efak_core_3DEN_CrateName_Tooltip"; \
        property = QUOTE(efak_core_crateName_##CASE); \
        control = "Edit"; \
        expression = "if (!is3DEN && {isServer} && {_value isNotEqualTo ''}) then {[_this,'%s',_value] call efak_core_fnc_nameCrateKits}"; \
        defaultValue = "''"; \
        typeName = "STRING"; \
        validate = "none"; \
        condition = "objectHasInventoryCargo"; \
    }

class Cfg3DEN {
    class Object {
        class AttributeCategories {
            class efak_core_attributes {
                class Attributes {
                    CRATE_CASE_ATTRIBUTES(efku_SpecialAmmoCase,Special Ammunition Box);
                    CRATE_CASE_ATTRIBUTES(efku_OrdnanceCase,Explosives + Ordnance Box);
                    // EUP's own fields, under the boxes' names
                    class efak_core_crate_eup_AmmoBag {displayName = "Ammo Box contents";};
                    class efak_core_crateName_eup_AmmoBag {displayName = "Ammo Box name";};
                    class efak_core_crate_eup_EngineerBag {displayName = "Engineer Box contents";};
                    class efak_core_crateName_eup_EngineerBag {displayName = "Engineer Box name";};
                    class efak_core_crate_eup_CBRNBag {displayName = "CBRN Box contents";};
                    class efak_core_crateName_eup_CBRNBag {displayName = "CBRN Box name";};
                };
            };
        };
    };
};

// The animated stand-ins for kits on the ground, see efku_LidProp in the main addon.
#define LID_PROP(FILE,SOUND) \
    class DOUBLES(efku_LidProp,FILE): efku_LidProp { \
        model = QPATHTOF(data\DOUBLES(FILE,open).p3d); \
        efku_sound = #SOUND; \
    }

class CfgVehicles {
    class efku_LidProp;
    class efku_boxes_base;
    class Item_Base_F;
    LID_PROP(utility_pouch,pouch);
    LID_PROP(ammo_pouch,pouch);
    LID_PROP(ammo_bag,case);
    LID_PROP(engineer_bag,case);
    LID_PROP(cbrn_bag,case);
    LID_PROP(special_ammo,case);
    LID_PROP(ordnance_crate,case);

    // the pouches and boxes as world objects (addons/boxes): the default contents of their kit, and
    // for the three this mod adds, what forward's unit carries in them (classes of mods that are not
    // loaded are skipped)
    KIT_BOX(utility_pouch,eup_UtilityPouch,"Utility Pouch (box)",pouch,60,1)};
    KIT_BOX(ammo_pouch,eup_AmmoPouch,"Ammo Pouch (box)",pouch,100,1)};
    KIT_BOX(ammo_bag,eup_AmmoBag,"Ammo Box",case,600,2)
        efku_extra[] = {"OPTRE_32Rnd_762x51_Mag", 10, "OPTRE_36Rnd_95x40_Mag", 6, "OPTRE_M9_Frag", 4};
    };
    KIT_BOX(engineer_bag,eup_EngineerBag,"Engineer Box",case,500,2)
        efku_extra[] = {"DemoCharge_Remote_Mag", 2};
    };
    KIT_BOX(cbrn_bag,eup_CBRNBag,"CBRN Box",case,500,2)};
    KIT_BOX(special_ammo,efku_SpecialAmmoCase,"Special Ammunition Box",case,600,2)
        efku_extra[] = {"OPTRE_4Rnd_145x114_APFSDS_Mag", 4, "OPTRE_4Rnd_145x114_HEDP_Mag", 2, "OPTRE_4Rnd_145x114_HVAP_Mag", 2};
    };
    KIT_BOX(ordnance_crate,efku_OrdnanceCase,"Explosives + Ordnance Box",case,800,3)
        efku_extra[] = {"OPTRE_M41_Twin_HEAT_G", 2, "OPTRE_M44_Lykoi_HEAT_mag", 2, "OPTRE_M9_Frag", 4};
    };
    KIT_ITEM(eup_UtilityPouch,"Utility Pouch");
    KIT_ITEM(eup_AmmoPouch,"Ammo Pouch");
    KIT_ITEM(eup_AmmoBag,"Ammo Box");
    KIT_ITEM(eup_EngineerBag,"Engineer Box");
    KIT_ITEM(eup_CBRNBag,"CBRN Box");
    KIT_ITEM(efku_SpecialAmmoCase,"Special Ammunition Box");
    KIT_ITEM(efku_OrdnanceCase,"Explosives + Ordnance Box");
};
