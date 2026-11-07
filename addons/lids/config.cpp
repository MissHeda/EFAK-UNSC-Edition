#include "script_component.hpp"

// Opens the lid of a kit lying on the ground while its kit window (EFAK) is open, and only that kit's.
// Purely local and visual: only the player looking sees it, nothing about the kit changes.
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

// Take opened kits' places on the holder's copy, so the rest of the pile keeps its slots (see
// fnc_openHolder): one class per kit entry, STAND_INS of them. Never in anyone's hands.
#define STAND_IN(N) class DOUBLES(GVAR(standIn),N): GVAR(standIn) {}
class CfgWeapons {
    class FirstAidKit;
    class GVAR(standIn): FirstAidKit {
        scope = 1;
        scopeCurator = 0;
        scopeArsenal = 0;
        model = "\A3\Weapons_F\empty.p3d";
    };
    STAND_IN(0); STAND_IN(1); STAND_IN(2); STAND_IN(3); STAND_IN(4); STAND_IN(5);
    STAND_IN(6); STAND_IN(7); STAND_IN(8); STAND_IN(9); STAND_IN(10); STAND_IN(11);
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
