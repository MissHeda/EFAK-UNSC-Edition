#include "script_component.hpp"

// New models and pictures for EFAK's five kits. Only the values that change the look are set here -
// names, contents, weights and the rest stay EFAK's, so an EFAK update carries straight through. The
// instance classes (efak_IFAK_1 ...) inherit from the classes below, so they need nothing of their own.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"efku_main", "efak_kits"};
        author = "Miss Heda";
        url = "https://github.com/MissHeda/EFAK-UNSC-Edition";
        VERSION_CONFIG;
    };
};

#define KIT_LOOK(CLASS,FILE) \
    class CLASS: EFAK_KitBase { \
        model = QPATHTOF(data\FILE.p3d); \
        picture = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        editorPreview = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        efku_lidProp = QUOTE(DOUBLES(efku_LidProp,FILE)); \
    }

class CfgWeapons {
    class EFAK_KitBase;
    KIT_LOOK(efak_IFAK,ifak);
    KIT_LOOK(efak_AFAK,afak);
    KIT_LOOK(efak_MFAK,mfak);
    KIT_LOOK(efak_MFAKPlus,mfakplus);
    KIT_LOOK(efak_NarcBox,narcbox);
};

// The pictures in the kit window, the menus and the arsenal, and the artwork behind a kit's contents.
#define KIT_ICONS(KIT,FILE) \
    class KIT { \
        icon = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        iconContents = QPATHTOF(ui\DOUBLES(FILE,ca).paa); \
        background = QPATHTOF(ui\DOUBLES(FILE,bg_ca).paa); \
    }

class EFAK_Kits {
    KIT_ICONS(IFAK,ifak);
    KIT_ICONS(AFAK,afak);
    KIT_ICONS(MFAK,mfak);
    KIT_ICONS(MFAKPlus,mfakplus);
    KIT_ICONS(NarcBox,narcbox);
};

class EFAK_KitGroups {
    class FirstAid {
        icon = QPATHTOF(ui\ifak_ca.paa);
    };
};

// The animated stand-ins for kits on the ground, see efku_LidProp in the main addon.
#define LID_PROP(FILE) \
    class DOUBLES(efku_LidProp,FILE): efku_LidProp { \
        model = QPATHTOF(data\FILE.p3d); \
    }

class CfgVehicles {
    class efku_LidProp;
    LID_PROP(ifak);
    LID_PROP(afak);
    LID_PROP(mfak);
    LID_PROP(mfakplus);
    LID_PROP(narcbox);
};
