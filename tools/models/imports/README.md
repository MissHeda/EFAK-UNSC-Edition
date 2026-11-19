# Models from other mods

Some of what is packed inside the kits is not built in this repository but taken from other Halo
mods for Arma 3: their model (debinarized to MLOD with `debin`) and their colour texture (PAA
converted to PNG). `unsc_lib.imported()` puts the mesh into a kit; the bake copies the texture into
the kit's own texture, so the mod ships no file of theirs as such - but the shapes and prints are
theirs. **Their licences apply to those pieces.** Check them before any public release, and credit
the authors in the mod's description.

| Folder | Piece | From | File there | Licence |
|---|---|---|---|---|
| `optre/biofoam.p3d` | Biofoam canister | Operation: TREBUCHET (Workshop 769440155), Article 2 Studios | `\OPTRE_Weapons\items\Biofoam.p3d` | not stated in the mod's readme - ask / check their page |
| `optre/ma5ammo.p3d` | Sealed M118 7.62x51 ammo pack | Operation: TREBUCHET | `\OPTRE_Weapons\Ammo\MA5Ammo.p3d` | as above |
| `optre/rifle_packet.p3d` | Rifle ammo packet (not used yet) | Operation: TREBUCHET | `\OPTRE_Weapons\ammoPackets\rifle_packet.p3d` | as above |
| `optre/ma5_mag.p3d` | MA5 series magazine | Operation: TREBUCHET | `\OPTRE_Weapons\magazines\ma5_series_mag.p3d` | as above |
| `optre/br_mag.p3d` | BR magazine | Operation: TREBUCHET | `\OPTRE_Weapons\br\BR_Magazine.p3d` | as above |
| `optre/m41_heat.p3d` | M41 twin HEAT tube | Operation: TREBUCHET | `\OPTRE_Weapons\Rockets\m41_spkr_types\heat.p3d` | as above |
| `optre/lykoi_mag.p3d` | M44 Lykoi HEAT rocket | Operation: TREBUCHET | `\OPTRE_Weapons_AT\M44_Lykoi\M44_Lykoi_Mag_Ground.p3d` | as above |
| `optre/srs99c_mag.p3d` | SRS99C magazine | Operation: TREBUCHET | `\OPTRE_Weapons\Sniper\SRS99C_Mag.p3d` | as above |
| `optre/m99_mag.p3d` | M99 Stanchion magazine | Operation: TREBUCHET | `\OPTRE_Weapons\Sniper\M99_Magazine.p3d` | as above |
| `optre/pkt_145.p3d` | 14.5x114 ammo packet (APFSDS and HEDP print) | Operation: TREBUCHET | `\OPTRE_WeaponsmmoPacketsV2\dataex114rndex114_4rnd_apfsds.p3d` | as above |
| `unsci/injector.p3d` | UNSC auto-injector | UNSC Infirmary (Workshop 3568544071), Im Kreepy | `unsci_items\data\unsci_injector.p3d` | its LICENSE.txt: attribution, non-commercial, Arma only, share alike |
| `unsci/medigel_tube.p3d` | Medigel tube | UNSC Infirmary | `unsci_items\data\unsci_medigel_tube.p3d` | as above |

Not usable: The Cole Protocol's ammo packages (`props\Military\Supplies\AmmoPackage_01`) are
encrypted ODOL; only their texture was looked at as a reference.

Everything else in the kits - the cases (the ordnance case and its bumpers too), the foil ammunition sacks, the foam, dressings, gauze, saline, tourniquet, shears,
splint, vials, pill boxes, gloves, tools, mask, filters and all prints on them - is built in
`kits.py` / `interiors.py` and drawn in `make_decals.py`.
