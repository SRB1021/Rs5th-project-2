"""Coconut can lid (units: mm), 'Fizzy Frog'-style: a ring that snaps onto the rim of a
standard can plus a hinged coconut dome that latches shut and seals the opening.

Assembled coordinates: z=0 is the top of the can rim, can axis = z. Hinge at -X, latch at +X.
Hinge pin: a 1.75 mm filament offcut (2.2 mm hole). Ring is exported flipped
(plate on the bed, snap fingers up); dome is exported flange-down.
"""
import numpy as np
from meshkit import Mesh, revolve, earclip, sector, box, sphere, xform

RIM_R = 33.0          # can top rim outer radius (12 oz can ~66 mm)
OPEN_R = 30.5         # opening left in the ring plate (access to pull tab / sip)
PLATE_R = 38.5
PLATE_T = 3.0
DOME_R, DOME_WALL = 38.5, 2.0
DOME_H = DOME_R        # true hemisphere: half a coconut
HINGE_X, HINGE_Z = -40.5, 3.6
PIN_HOLE, LUG_R = 1.1, 3.6
PLASTIC = 1.27e-3


def hinge_lug(y0, y1):
    lug = revolve([(PIN_HOLE, 0), (LUG_R, 0), (LUG_R, y1 - y0), (PIN_HOLE, y1 - y0)], seg=24)
    R = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]             # local z -> +y
    return xform(lug, R, [HINGE_X, y0, HINGE_Z])


def ring_parts():
    parts = []
    # plate with a sealing tongue that plugs into the dome
    parts.append(revolve([(OPEN_R, 0), (PLATE_R, 0), (PLATE_R, PLATE_T), (36.2, PLATE_T), (36.2, PLATE_T + 1.8),
                          (34.8, PLATE_T + 1.8), (34.8, PLATE_T), (OPEN_R, PLATE_T)], seg=96))
    # six flexing snap fingers hanging down outside the can; hook sits under the rim bead
    finger = [(33.9, 0.5), (35.5, 0.5), (35.5, -9.5), (32.4, -9.5), (30.6, -8.2), (30.6, -4.6), (33.9, -4.6)]
    for k in range(6):
        c = np.radians(30 + 60*k)
        parts.append(sector(finger, c - np.radians(11), c + np.radians(11), seg=6))
    # hinge lugs (outer pair) and latch catch
    parts += [hinge_lug(3.4, 9.4), hinge_lug(-9.4, -3.4)]
    parts.append(box(-42.0, -PLATE_R + 1.0, -9.4, 9.4, 0, PLATE_T))                        # lug base bridge to plate
    parts.append(box(PLATE_R - 1.0, 41.2, -6, 6, PLATE_T - 1.5, PLATE_T))              # latch catch (underside z=1.5)
    parts.append(box(PLATE_R - 1.0, PLATE_R + 0.5, -6, 6, 0, PLATE_T))                     # catch stem to plate
    return parts


def husk_shell(z0, nt=36, nphi=144):
    """Closed hollow hemisphere (half a coconut): fibrous husk ridges outside, smooth inside."""
    m = Mesh()
    t = np.linspace(0, np.pi/2, nt + 1)
    phi = np.linspace(0, 2*np.pi, nphi, endpoint=False)
    def pt(R, ti, pj, fib):
        # fibres run pole -> equator, slightly twisted; fade to 0 at the pole
        r = R * (1 + fib * 0.013 * np.cos(ti) * (0.5 + 0.5*np.sin(30*pj + 5*ti)))
        return np.array([r*np.cos(ti)*np.cos(pj), r*np.cos(ti)*np.sin(pj), z0 + r*np.sin(ti)])
    O = [[pt(DOME_R, ti, pj, 1) for pj in phi] for ti in t]
    I = [[pt(DOME_R - DOME_WALL, ti, pj, 0) for pj in phi] for ti in t]
    for i in range(nt):
        for j in range(nphi):
            k = (j + 1) % nphi
            if i < nt - 1:
                m.quad(O[i][j], O[i][k], O[i+1][k], O[i+1][j])
                m.quad(I[i][j], I[i+1][j], I[i+1][k], I[i][k])
            else:
                m.tri(O[i][j], O[i][k], O[nt][0])
                m.tri(I[i][k], I[i][j], I[nt][0])
    for j in range(nphi):
        k = (j + 1) % nphi
        m.quad(O[0][j], I[0][j], I[0][k], O[0][k])               # bottom rim face
    return m


def dome_parts():
    parts = [husk_shell(PLATE_T)]
    # thin flange (the hinge/latch land) flush with the husk
    parts.append(revolve([(DOME_R - 2.0, PLATE_T), (39.2, PLATE_T), (39.2, PLATE_T + 1.6), (DOME_R - 2.0, PLATE_T + 1.6)], seg=96))
    # hinge lug (middle) with a bridge to the flange
    parts.append(hinge_lug(-3.0, 3.0))
    parts.append(box(HINGE_X, -DOME_R + 1.0, -3.0, 3.0, PLATE_T, PLATE_T + 2.0))
    # latch: tab hanging from the flange at +X with an inward bump that snaps under the catch
    parts.append(box(38.0, 43.0, -6, 6, PLATE_T, PLATE_T + 2.0))
    parts.append(box(41.4, 43.0, -6, 6, -0.3, PLATE_T))
    parts.append(box(40.7, 41.4, -5, 5, 0.2, 1.3))
    return parts


def _arr(parts):
    return np.concatenate([p.array() for p in parts])


def _write(arr, path):
    nrm = np.cross(arr[:, 1] - arr[:, 0], arr[:, 2] - arr[:, 0])
    ln = np.linalg.norm(nrm, axis=1, keepdims=True); ln[ln == 0] = 1
    rec = np.zeros(len(arr), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = nrm / ln, arr
    with open(path, "wb") as f:
        f.write(b"coconut can lid".ljust(80, b" ")); f.write(np.uint32(len(arr)).tobytes()); f.write(rec.tobytes())
    mn, mx = arr.reshape(-1, 3).min(0), arr.reshape(-1, 3).max(0)
    print(f"{path}: {len(arr)} tris, bbox {np.round(mx - mn, 1)} mm")


def build_and_write():
    ring, dome = _arr(ring_parts()), _arr(dome_parts())
    np.save("/tmp/lid_assembled.npy", np.concatenate([ring, dome]))   # for previews
    # export in print orientation
    flip = ring @ np.diag([1, -1, -1]).astype(np.float32)               # 180 deg about X (det=+1, winding kept)
    flip[:, :, 2] -= flip[:, :, 2].min()
    _write(flip, "palm_lid_ring.stl")
    d = dome.copy(); d[:, :, 2] -= d[:, :, 2].min()
    _write(d, "palm_lid_dome.stl")
    vol = lambda a: np.einsum("ij,ij->i", a[:, 0], np.cross(a[:, 1], a[:, 2])).sum() / 6
    mass = (vol(ring) + vol(dome)) * PLASTIC * 0.55      # ~55% effective after sparse infill in the dome
    cog = float(np.concatenate([ring, dome])[:, :, 2].mean())
    print(f"  lid ~{mass:.0f} g, clips onto 66 mm can rim (12 oz); pin: 1.75 mm filament in the 2.2 mm hinge hole")
    return mass, cog


if __name__ == "__main__":
    build_and_write()
