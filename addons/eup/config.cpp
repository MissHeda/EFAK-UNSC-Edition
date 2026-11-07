#include "script_component.hpp"

// The same for Enhanced Utility Pouches: new models and pictures for its five pouches. Skipped
// without a word when EUP is not loaded, so this mod works with EFAK alone, EUP alone or both.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"efku_main", "eup_pouches"};
        skipWhenMissingDependencies = 1;
        author = "Miss Heda";
        url = "https://github.com/MissHeda/EFAK-UNSC-Edition";
        VERSION_CONFIG;
    };
};

#define POUCH_LOOK(CLASS,FILE) \
    class CLASS: eup_PouchBase { \
        model = QPATHTOF(data\FILE.p3d); \
        picture = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        editorPreview = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        efku_lidProp = QUOTE(DOUBLES(efku_LidProp,FILE)); \
    }

class CfgWeapons {
    class eup_PouchBase;
    POUCH_LOOK(eup_UtilityPouch,utility_pouch);
    POUCH_LOOK(eup_AmmoPouch,ammo_pouch);
    POUCH_LOOK(eup_AmmoBag,ammo_bag);
    POUCH_LOOK(eup_EngineerBag,engineer_bag);
    POUCH_LOOK(eup_CBRNBag,cbrn_bag);
};

#define POUCH_ICONS(KIT,FILE) \
    class KIT { \
        icon = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        iconContents = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        background = QPATHTOF(ui\DOUBLES(FILE,bg_ca).paa); \
    }

class EFAK_Kits {
    POUCH_ICONS(EUP_UtilityPouch,utility_pouch);
    POUCH_ICONS(EUP_AmmoPouch,ammo_pouch);
    POUCH_ICONS(EUP_AmmoBag,ammo_bag);
    POUCH_ICONS(EUP_EngineerBag,engineer_bag);
    POUCH_ICONS(EUP_CBRNBag,cbrn_bag);
};

class EFAK_KitGroups {
    class Pouches {
        icon = QPATHTOF(ui\utility_pouch_ca.paa);
    };
};

// The animated stand-ins for kits on the ground, see efku_LidProp in the main addon.
#define LID_PROP(FILE,SOUND) \
    class DOUBLES(efku_LidProp,FILE): efku_LidProp { \
        model = QPATHTOF(data\FILE.p3d); \
        efku_sound = #SOUND; \
    }

class CfgVehicles {
    class efku_LidProp;
    LID_PROP(utility_pouch,pouch);
    LID_PROP(ammo_pouch,pouch);
    LID_PROP(ammo_bag,case);
    LID_PROP(engineer_bag,case);
    LID_PROP(cbrn_bag,case);
};
