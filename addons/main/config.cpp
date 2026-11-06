#include "script_component.hpp"

// EFAK: UNSC Edition changes how Enhanced First Aid Kits look - models, pictures and the kit window -
// and nothing else. It only overrides values, never copies an EFAK file, so EFAK updates keep working.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"efak_main"};
        author = "Miss Heda";
        url = "https://github.com/MissHeda/EFAK-UNSC-Edition";
        VERSION_CONFIG;
    };
};
