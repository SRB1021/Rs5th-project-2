# Palm island on an old volcano (two parts that screw together)

A flat island floats at the waterline with the can well and 9 self-closing palm fronds on it. Under it hangs an old
volcano (narrow neck, concave flanks with erosion gullies, wide base) that holds the ballast. The island screws onto the
volcano, so each can be printed in its own color.

## Print list (FDM, PETG recommended, 100% infill / solid walls)

| File | Qty | Suggested color | Notes |
|---|---|---|---|
| `palm_island.stl` | 1 | sand / tan | Island with a threaded socket underneath. About 200 x 200 x 119 mm. Print standing on the collar. |
| `palm_volcano.stl` | 1 | dark brown / gray | Volcano with a threaded spigot on top and the ballast hatch in its base. About 133 x 133 x 148 mm. |
| `palm_frond.stl` | **9** | green | Frond + stem lever, supplied standing on its edge. |
| `palm_plug_cap.stl` | 1 | same as volcano | Screw plug for the base hatch (grip bar on the bed, thread up). |

Also buy: **O-ring 44 mm ID x 2.5 mm** (silicone), **9 x 12 mm pins** cut from 1.75 mm filament,
**steel shot / steel fishing weights, about 1150 g** (1000 to 1300 g is fine; the tube holds ~1320 g).
Free extra: a few pieces of **pool noodle / closed-cell foam**.

## Assembly
1. Ballast: stand the volcano on its spigot end (upside down). Unscrew the plug in the middle of the base, pour in about 1150 g of
   shot, pack leftover space in the tube with foam, put the O-ring in the groove on the plug flange (a smear of silicone
   grease helps), and screw the plug in firmly.
2. Hinge pins: push a 12 mm filament pin through each frond knuckle and its two lugs on the island collar.
3. Screw the island onto the volcano spigot (clockwise as seen from above) until the island collar sits on the volcano shoulder.
   A bead of silicone sealant or a drop of thread-locker on the thread keeps it from ever unscrewing.

## How the fronds work
With no can, the fronds lie open and the stems stick up into the well. Setting a can in pushes the stems down,
which flips the fronds up and in around the can.

## Calculated (not printed or tested)
With a full can and 1150 g of shot the island top sits ~26 mm above the water and the stability margin is ~42 mm.
With 1000-1300 g the margin stays between 30 and 46 mm; do not use much less than 1000 g. The island and the volcano
each hold their own sealed chamber, so the screw joint does not have to be watertight. The hinge, thread and seal fits use
generous clearances but are untested.

`python3 make_volcano2.py` regenerates the files (needs numpy). Earlier variants (`make_volcano.py` one-piece, `make_island.py`,
`make_spar.py`, `make_palm.py`, `make_lid.py`) are kept; `make_volcano2.py` imports helpers from them. The coconut lid is paused.
