#include "script_component.hpp"

// Opens the lid of a kit lying on the ground while someone has the inventory open on it. Purely local
// and visual: only the player looking sees it, nothing about the kit changes.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"efku_main", "cba_main", "cba_xeh", "cba_settings"};
        author = "Miss Heda";
        url = "https://github.com/MissHeda/EFAK-UNSC-Edition";
        VERSION_CONFIG;
    };
};

// The lids' sounds, made by tools/make_sounds.py: case, med (with the field generator's beeps) and
// pouch, each opening and closing.
#define LID_SOUND(NAME) class DOUBLES(ADDON,NAME) { name = ""; sound[] = {QPATHTOF(sounds\NAME.ogg), 1, 1}; titles[] = {}; }
class CfgSounds {
    LID_SOUND(case_open);
    LID_SOUND(case_close);
    LID_SOUND(med_open);
    LID_SOUND(med_close);
    LID_SOUND(pouch_open);
    LID_SOUND(pouch_close);
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
