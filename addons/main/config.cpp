#include "script_component.hpp"

// EFAK: UNSC Edition changes how Enhanced First Aid Kits look - models, pictures and the kit window -
// and nothing else. It only overrides values, never copies an EFAK file, so EFAK updates keep working.
class CfgPatches {
    class ADDON {
        name = COMPONENT_NAME;
        units[] = {};
        weapons[] = {};
        requiredVersion = REQUIRED_VERSION;
        requiredAddons[] = {"efak_main", "A3_Data_F_Decade_Loadorder"};
        author = "Miss Heda";
        url = "https://github.com/MissHeda/EFAK-UNSC-Edition";
        VERSION_CONFIG;
    };
};

// What efku_lids puts in place of a kit lying on the ground while someone has the inventory open: the
// kit's own model, whose lid can swing open (model.cfg). Each kit class names its prop in efku_lidProp.
//   efku_offset[]  where the kit sits in its ground holder, in the holder's model space (metres)
//   efku_turn      how far the kit is turned in the holder, degrees about its up axis
class CfgVehicles {
    class NonStrategic;
    class efku_LidProp: NonStrategic {
        scope = 1;
        scopeCurator = 0;
        displayName = "UNSC kit";
        destrType = "DestructNo";
        efku_offset[] = {0, 0, 0};
        efku_turn = 0;
        class AnimationSources {
            class lid {
                source = "user";
                animPeriod = 0.6;
                initPhase = 0;
            };
        };
    };
};
