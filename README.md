# EFAK: UNSC Edition

An add-on for [Enhanced First Aid Kits](https://steamcommunity.com/sharedfiles/filedetails/?id=3809430149)
and [Enhanced Utility Pouches](https://steamcommunity.com/sharedfiles/filedetails/?id=3812667721): every kit
and pouch gets a new model in the style of the UNSC, new inventory pictures, and the kit window turns into
a cyan HUD readout on dark glass. Works with EFAK, EUP or both - whichever is loaded gets the new look.

| Kit | Becomes |
|---|---|
| IFAK | IFAK - angular polymer case with a front lid, red pull tab and MOLLE back |
| AFAK | AFAK - the flat octagonal field medkit with the medical mark and red reflectors |
| MFAK | khaki UNSC medical case in the style of Halo Infinite's crates: black frame, EGB emblem |
| MFAK+ | the same family, taller, olive |
| Narc Box | narc case - moulded launcher-ammo style hard case with yellow stencil |
| Utility Pouch | utility pouch - webbing pouch with moulded lid, straps over the flap to buckles |
| Ammo Pouch | double magazine pouch - two moulded cells, each closed by its own lid and snap |
| Ammo Bag | "Ammo Box": olive UNSC ammunition case with Marine Corps insignia and folding handle |
| Engineer Bag | "Engineer Box": grey UNSC tool case with hazard stripes |
| CBRN Bag | "CBRN Box": white UNSC case with yellow band, seal gauge and purge valve |

With Enhanced Utility Pouches loaded the add-on also brings two boxes of its own (kits of the same
framework, listed with the pouches in the menu, the arsenal and the settings):

| Box | Takes | Looks like |
|---|---|---|
| Special Ammunition Box (`efku_SpecialAmmoCase`) | magazines | the ammunition case under its own stencil: eight SRS99 magazines standing in cut foam, 14.5x114 packets and foil sacks inside |
| Explosives + Ordnance Box (`efku_OrdnanceCase`) | rockets, missiles, charges, mines, hand grenades | a long red-brown rocket case (78 cm) with tan corner bumpers and three folding handles: an M41 twin HEAT tube and an M44 Lykoi HEAT rocket inside |

Kits on the ground lie shut. Open a kit's window and that kit's lid unlatches and swings open while you
look inside, and shuts again when you close the window (only you see it; switch it off in the addon
options, "Open kit lids").

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

`tools/models/kits.py` holds the shapes, `tools/models/unsc_lib.py` the parts, looks and the p3d writer. Every
build checks that each decal sits on one flat face with 4 mm clear all round and stops if one does not
(`blender -b -P tools/models/build_kit.py -- <kit> --check` runs only the check). Parts made inside
`with lid():` form the lid, which turns about `lid_axis` (the hinge's pin; every other knuckle goes with the
lid). `bail_latch()` builds a draw latch that works: bracket on the body, keeper on the lid, and the lever with
its bail as a part of its own (`latch<k>`), which swings out and hangs down before the lid opens. The
`model.cfg` files come from `python tools/models/make_model_cfg.py`.

## Legal

Halo © Microsoft Corporation. EFAK: UNSC Edition was created under Microsoft's
["Game Content Usage Rules"](https://www.xbox.com/en-US/developers/rules) using assets from Halo, and it is
not endorsed by or affiliated with Microsoft. Models and textures are made from scratch; the UNSC emblem
(Eagle, Globe and Banner), the UNSC Marine Corps insignia and the UNSC wordmark in `tools/models/logos` are
Microsoft's marks, in versions taken from [Halopedia](https://www.halopedia.org/Symbols_of_the_UNSC).
