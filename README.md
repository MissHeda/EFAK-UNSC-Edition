# EFAK: UNSC Edition

A look-only add-on for [Enhanced First Aid Kits](https://steamcommunity.com/sharedfiles/filedetails/?id=3809430149)
and [Enhanced Utility Pouches](https://steamcommunity.com/sharedfiles/filedetails/?id=3812667721): every kit
and pouch gets a new model in the style of the UNSC, new inventory pictures, and the kit window turns into
a cyan HUD readout on dark glass. Works with EFAK, EUP or both - whichever is loaded gets the new look.

| Kit | Becomes |
|---|---|
| IFAK | M7 IFAK - angular polymer case with red pull tab and MOLLE back |
| AFAK | M9 AFAK - the flat octagonal field medkit with the medical mark and red reflectors |
| MFAK | MFAK - UNSC supply crate with padded lid and corner posts |
| MFAK+ | MFAK+ - tall UNSC locker tin with fold handles |
| Narc Box | Narc case - moulded launcher-ammo style hard case with yellow stencil |
| Utility Pouch | M12 utility pouch - webbing pouch with moulded lid and buckled straps |
| Ammo Pouch | double magazine pouch with two mags and rounds showing |
| Ammo Bag | steel ammunition crate with folding handle and yellow HE band |
| Engineer Bag | olive tool case with orange bumpers, vents and hazard stripes |
| CBRN Bag | white sealed CBRN container with seal gauge and purge valve |

Needs EFAK or EUP (EFAK 1.4.0 or later for the window colours; older versions still get the models). Changes nothing
but the look: names, contents, weights and settings stay EFAK's, so EFAK updates keep working.

## Building

The models are procedural and come out of Blender (5.x) in one go - geometry, baked texture, normal and
specular maps, LODs, shadow and geometry LODs, and the inventory picture:

```
python tools/models/make_decals.py
blender -b -P tools/models/build_kit.py -- ifak      # any name from BUILDERS in kits.py
python tools/make_ui.py                              # window glass, kit backgrounds, logo
hemtt build
```

`tools/models/kits.py` holds the shapes, `tools/models/unsc_lib.py` the parts, looks and the p3d writer.

## Legal

Halo © Microsoft Corporation. EFAK: UNSC Edition was created under Microsoft's
["Game Content Usage Rules"](https://www.xbox.com/en-US/developers/rules) using assets from Halo, and it is
not endorsed by or affiliated with Microsoft. All models and textures here are made from scratch.
