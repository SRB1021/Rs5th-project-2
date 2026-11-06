# Palm spar can holder (sunk island ballast)

Bowl-shaped island underwater -> slim ringed palm trunk -> lily pad at the waterline -> crown at the top with the
can well and 9 self-closing palm fronds.

## Print list (FDM, brown ASA/PETG, solid walls / 4+ perimeters)

| File | Qty | Notes |
|---|---|---|
| `palm_spar_base.stl` | 1 | Island + trunk + lily pad + crown. About 180 x 180 x 235 mm. Contains sealed chambers; no supports needed inside them. |
| `palm_frond.stl` | **9** | Frond + stem lever, supplied standing on its edge. |
| `palm_plug_cap.stl` | 1 | Screw plug for the island (grip bar on the bed, thread up). |

Also buy: **O-ring 44 mm ID x 2.5 mm** (silicone), **9 x 12 mm pins** cut from 1.75 mm filament,
**steel shot / steel fishing weights, about 1050 g** (anything from 900 to 1350 g is fine).
Free extra: a few pieces of **pool noodle / closed-cell foam**.

## Ballast
Stand the unit on its crown. Unscrew the plug in the middle of the island's underside and pour in about 1050 g of
shot. **Fill the leftover space in the island with foam pieces** so that even if the plug ever leaks, the island
still floats. Put the O-ring in the groove on the plug flange (a smear of silicone grease helps), screw the
plug in firmly. To remove weights, turn it upside down and pour them out.

## How the fronds work
With no can, the fronds lie open and the stems stick up into the well. Setting a can in pushes the stems
down, which flips the fronds up and in around the can.

## Calculated (not printed/tested)
Float height and stability were calculated, not measured. With a full can, waterline is ~52 mm below the crown top and stability
margin 38 mm; with 900-1350 g of shot it stays between 29 and 52 mm. The hinge, thread and seal fits are
designed with generous clearances but are untested.

`python3 make_spar.py` regenerates the files (needs numpy). Earlier variants (`make_palm.py`, `make_lid.py`) are
kept; the coconut lid is paused.
