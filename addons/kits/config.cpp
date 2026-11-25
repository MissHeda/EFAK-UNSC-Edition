#include "script_component.hpp"

// New models and pictures for EFAK's five kits. Only the values that change the look are set here -
// names, contents, weights and the rest stay EFAK's, so an EFAK update carries straight through. The
// instance classes (efak_IFAK_1 ...) inherit from the classes below, so they need nothing of their own.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {"efku_Box_ifak", "efku_Box_afak", "efku_Box_mfak", "efku_Box_mfakplus", "efku_Box_narcbox", "Item_efak_IFAK", "Item_efak_AFAK", "Item_efak_MFAK", "Item_efak_MFAKPlus", "Item_efak_NarcBox"};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"efku_main", "efku_boxes", "efak_kits"};
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
#define LID_PROP(FILE,SOUND) \
    class DOUBLES(efku_LidProp,FILE): efku_LidProp { \
        model = QPATHTOF(data\DOUBLES(FILE,open).p3d); \
        efku_sound = #SOUND; \
    }

class CfgVehicles {
    class efku_LidProp;
    class efku_boxes_base;
    class efku_boxes_drop;
    LID_PROP(ifak,med);
    LID_PROP(afak,med);
    LID_PROP(mfak,case);
    LID_PROP(mfakplus,case);
    LID_PROP(narcbox,case);

    // the kits as boxes (addons/boxes), packed with each kit's default contents
    KIT_BOX(ifak,efak_IFAK,"IFAK (box)",med,60,1)};
    KIT_BOX(afak,efak_AFAK,"AFAK (box)",med,150,1)};
    KIT_BOX(mfak,efak_MFAK,"MFAK (box)",case,400,1)};
    KIT_BOX(mfakplus,efak_MFAKPlus,"MFAK+ (box)",case,600,2)};
    KIT_BOX(narcbox,efak_NarcBox,"Narc Box (box)",case,60,1)};
    // and as items on the ground
    KIT_ITEM(ifak,efak_IFAK,"IFAK",med);
    KIT_ITEM(afak,efak_AFAK,"AFAK",med);
    KIT_ITEM(mfak,efak_MFAK,"MFAK",case);
    KIT_ITEM(mfakplus,efak_MFAKPlus,"MFAK+",case);
    KIT_ITEM(narcbox,efak_NarcBox,"Narc Box",case);
};
