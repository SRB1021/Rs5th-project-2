# Palm island can holder + coconut lid

Print list (FDM, brown ASA/PETG, solid walls / 4+ perimeters):

| File | Qty | Notes |
|---|---|---|
| `palm_island_base.stl` | 1 | Floating island with sealed air chamber, hinge slots and a small palm tree. No supports inside the chamber. |
| `palm_frond.stl` | **9** | Frond + stem lever. Supplied standing on its edge, print as is. |
| `palm_lid_ring.stl` | 1 | Snap-on ring for a 12 oz can rim. Supplied plate-down. |
| `palm_lid_dome.stl` | 1 | Hinged half-coconut dome. |

Pins: 1.75 mm filament, **9 x 12 mm** for the fronds, **1 x 19 mm** for the lid. A drop of glue on the pin ends (not the knuckle).

How it works: with no can, the fronds lie open and the stems stick up into the well. Setting a can in pushes the stems down, which flips the fronds up and in around the can.

`python3 make_palm.py` regenerates everything (needs numpy).
