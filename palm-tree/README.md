# Palm island on an old volcano

A flat island floats at the waterline with the can well and 9 self-closing palm fronds on it. Under it hangs an old
volcano (narrow neck, concave flanks with erosion gullies, wide base). The volcano is a hollow sealed shell around a
central ballast tube.

## Print list (FDM, brown ASA/PETG, solid walls / 4+ perimeters)

| File | Qty | Notes |
|---|---|---|
| `palm_volcano_island.stl` | 1 | Island + volcano. About 200 x 200 x 238 mm. Sealed chambers; overhangs are limited so no supports are needed. |
| `palm_frond.stl` | **9** | Frond + stem lever, supplied standing on its edge. |
| `palm_plug_cap.stl` | 1 | Screw plug for the volcano base (grip bar on the bed, thread up). |

Also buy: **O-ring 44 mm ID x 2.5 mm** (silicone), **9 x 12 mm pins** cut from 1.75 mm filament,
**steel shot / steel fishing weights, about 1000 g** (850 to 1150 g works; the tube holds ~1200 g).
Free extra: a few pieces of **pool noodle / closed-cell foam**.

## Ballast
Stand the unit on its crown (upside down). Unscrew the plug in the middle of the volcano base and pour in about 1000 g of
shot. Pack any leftover space in the tube with foam pieces. Put the O-ring in the groove on the plug flange (a smear of
silicone grease helps) and screw the plug in firmly. To remove weights, turn the unit upside down and pour them out.

## How the fronds work
With no can, the fronds lie open and the stems stick up into the well. Setting a can in pushes the stems down,
which flips the fronds up and in around the can.

## Calculated (not printed or tested)
With a full can and 1000 g of shot the island top sits ~26 mm above the water and the stability margin is ~46 mm.
With 850-1150 g the margin stays between 32 and 50 mm; below ~800 g it gets marginal, so do not use less.
The hinge, thread and seal fits use generous clearances but are untested.

`python3 make_volcano.py` regenerates the files (needs numpy). Earlier variants (`make_island.py`, `make_spar.py`,
`make_palm.py`, `make_lid.py`) are kept; the coconut lid is paused.
