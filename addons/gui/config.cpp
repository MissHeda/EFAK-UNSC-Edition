#include "script_component.hpp"

// The kit window in UNSC colours: a cyan readout on dark glass with HUD frame corners. Uses EFAK's
// theme hook (class EFAK_Theme, EFAK 1.4.0 and later); an older EFAK just ignores it.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"efku_main", "efak_gui"};
        author = "Miss Heda";
        url = "https://github.com/MissHeda/EFAK-UNSC-Edition";
        VERSION_CONFIG;
    };
};

class EFAK_Theme {
    accent[] = {0.36, 0.82, 0.96, 1};
    accentHover[] = {0.56, 0.9, 1, 1};
    accentSoft[] = {0.36, 0.82, 0.96, 0.2};
    onAccent[] = {0.02, 0.07, 0.1, 1};
    window[] = {0.025, 0.05, 0.06, 0.84};
    glossPouch = QPATHTOF(ui\gloss_pouch_ca.paa);
    glossContents = QPATHTOF(ui\gloss_contents_ca.paa);
};
