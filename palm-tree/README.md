# Palm island on a volcano keel

A flat island floats at the waterline with the can well and 9 self-closing palm fronds on it. Under it hangs a
volcano-shaped ballast keel (narrow neck, wide base).

## Print list (FDM, brown ASA/PETG, solid walls / 4+ perimeters)

| File | Qty | Notes |
|---|---|---|
| `palm_volcano_island.stl` | 1 | Island + volcano. About 200 x 200 x 160 mm. Sealed chambers; every overhang is 45 degrees or less (no supports). |
| `palm_frond.stl` | **9** | Frond + stem lever, supplied standing on its edge. |
| `palm_plug_cap.stl` | 1 | Screw plug for the volcano base (grip bar on the bed, thread up). |

Also buy: **O-ring 44 mm ID x 2.5 mm** (silicone), **9 x 12 mm pins** cut from 1.75 mm filament,
**steel shot / steel fishing weights, about 650 g** (anything from 400 to 780 g is fine; the volcano holds ~780 g).
Free extra: a few pieces of **pool noodle / closed-cell foam**.

## Ballast
Stand the unit on its crown (upside down). Unscrew the plug in the middle of the volcano base and pour in about 650 g of
shot. Pack the leftover space with foam pieces so the volcano still floats if the plug ever leaks. Put the O-ring in the
groove on the plug flange (a smear of silicone grease helps) and screw the plug in firmly. To remove weights,
turn the unit upside down and pour them out.

## How the fronds work
With no can, the fronds lie open and the stems stick up into the well. Setting a can in pushes the stems down,
which flips the fronds up and in around the can.

## Calculated (not printed or tested)
With a full can and 650 g of shot the island top sits ~24 mm above the water and the stability margin is
~61 mm. With 400-780 g of shot the margin stays between 35 and 63 mm. The hinge, thread and seal fits
use generous clearances but are untested.

`python3 make_island.py` regenerates the files (needs numpy). Earlier variants (`make_spar.py` slim-trunk spar,
`make_palm.py` floating island, `make_lid.py` coconut lid) are kept; the lid is paused.
