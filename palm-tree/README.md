# Palm spar can holder (sunk island ballast)

A weighted island "keel" sits underwater. A sealed palm trunk rises from it through a float ring at the
waterline; the can well and 9 self-closing palm fronds are at the top of the trunk.

## Print list (FDM, brown ASA/PETG, solid walls / 4+ perimeters)

| File | Qty | Notes |
|---|---|---|
| `palm_spar_base.stl` | 1 | Keel + trunk + float ring + can well + hinge collar. About 190 x 190 x 203 mm. Sealed chambers must be watertight. No supports inside. |
| `palm_frond.stl` | **9** | Frond + stem lever, supplied standing on its edge. |
| `palm_hatch_cap.stl` | 1 | Screw cap for the ballast hatch (grip bar on the bed, thread up). |

Also buy: **O-ring 44 mm ID x 2.5 mm** (silicone), **9 x 12 mm pins** of 1.75 mm filament, **steel shot or steel
fishing weights, about 800-1000 g**.

## Ballast
Open the hatch in the middle of the can-well floor (remove the can first): unscrew the cap and drop the weights
down the pipe into the keel. Fill with about 800-1000 g. Less than ~700 g is unstable; more than ~1100 g
sits too low in the water. Fit the O-ring in the groove under the cap flange before screwing it back in.
To remove weights, turn the whole unit upside down and pour them out.

## How the fronds work
With no can, the fronds lie open and the stems stick up into the well. Setting a can in pushes the stems
down, which flips the fronds up and in around the can.

`python3 make_spar.py` regenerates the files (needs numpy). The earlier floating-island and coconut-lid
generators (`make_palm.py`, `make_lid.py`) are kept; the lid is paused.
