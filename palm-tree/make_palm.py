"""Palm-frond can holder (units: mm). Base is a ringed palm-trunk stump with a
can well; the lily's closing petals are replaced by palm fronds that curve in
around the can.

Usage: python3 make_palm.py            -> palm_holder_closed.stl, palm_holder_open.stl
Each part is built as a closed surface with outward normals (volume checked)
and the parts overlap so a slicer unions them. Static poses only: no levers.
"""
import numpy as np

CAN_R = 33.5          # 12 oz slim/standard can ~66 mm dia
WELL_R = 34.5
BASE_H = 36.0
WELL_DEPTH = 32.0   # well floor 4 mm above the bottom
TRUNK_R = 46.0
N_FRONDS = 9
PAD_R = 100.0         # floating lily-pad-style disc radius
PAD_H = 24.0
WALL = 1.6            # shell wall of the sealed air chamber (print >=100% perimeters)
PLASTIC = 1.27e-3     # g/mm^3 (PETG; PLA ~1.24e-3)
CAN_G = 380.0         # full 12 oz can
CAN_H = 122.0        # standard 12 oz can height (slim cans are ~146)
CAN_COG = 55.0        # can centre of gravity above the well floor
WATER = 1.0e-3        # g/mm^3


class Mesh:
    def __init__(self):
        self.t = []

    def quad(self, a, b, c, d):
        self.t += [(a, b, c), (a, c, d)]

    def tri(self, a, b, c):
        self.t.append((a, b, c))

    def volume(self):
        a = np.array(self.t, float)
        return np.einsum("ij,ij->i", a[:, 0], np.cross(a[:, 1], a[:, 2])).sum() / 6

    def array(self):
        a = np.array(self.t, np.float32)
        if self.volume() < 0:           # make normals point outward
            a = a[:, ::-1]
        return a


def revolve(profile, seg=72):
    """Closed (r,z) loop revolved around z. Loop order: any; orientation auto-fixed."""
    m = Mesh()
    ang = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    for i in range(len(profile)):
        r0, z0 = profile[i]; r1, z1 = profile[(i + 1) % len(profile)]
        for j in range(seg):
            a, b = ang[j], ang[(j + 1) % seg]
            p = lambda r, z, t: np.array([r * np.cos(t), r * np.sin(t), z])
            if r0 == 0 and r1 == 0:
                continue
            if r0 == 0:
                m.tri(p(0, z0, a), p(r1, z1, a), p(r1, z1, b))
            elif r1 == 0:
                m.tri(p(r0, z0, a), p(0, z1, a), p(r0, z0, b))
            else:
                m.quad(p(r0, z0, a), p(r1, z1, a), p(r1, z1, b), p(r0, z0, b))
    return m


def outer_profile():
    """Pad + ringed trunk collar + can well, as an (r,z) loop (well floor at z=6)."""
    pts = [(0, 0), (PAD_R, 0), (PAD_R, PAD_H)]
    n = 8
    for k in range(n + 1):
        z = PAD_H + k * (BASE_H - PAD_H) / n
        bump = 2.0 if k % 2 else 0.0
        taper = 4 * (1 - (z - PAD_H) / (BASE_H - PAD_H))
        pts.append((TRUNK_R + taper + bump, z))
    pts += [(WELL_R + 6, BASE_H), (WELL_R, BASE_H), (WELL_R, BASE_H - WELL_DEPTH), (0, BASE_H - WELL_DEPTH)]
    return pts


def cavity_profile():
    """Sealed air chamber inside the pad and collar (ring around the well)."""
    wi = WELL_R + WALL
    return [(wi, WALL), (PAD_R - WALL, WALL), (PAD_R - WALL, PAD_H - WALL), (43.0, PAD_H - WALL),
            (43.0, BASE_H - WALL), (wi, BASE_H - WALL)]


def frond(angle, closed, length=78.0, w0=7.5, thick=1.8, curl=70.0):
    """Feather palm frond rooted on the stump rim, arching up and (closed) inward.

    Path is a circular-ish arc in the radial plane; blade has a midrib and
    pinnate leaflet teeth along both edges, tapering to a point.
    """
    m = Mesh()
    rad = np.array([np.cos(angle), np.sin(angle), 0.0])
    tan = np.array([-np.sin(angle), np.cos(angle), 0.0])
    z = np.array([0, 0, 1.0])
    root = rad * (WELL_R + 5.5) + z * BASE_H
    N = 34
    s = np.linspace(0, 1, N)
    # heading angle from vertical (+ = outward). Closed: starts outward-ish then curls in.
    if closed:
        phi = np.radians(8 - curl * s ** 1.15)
    else:
        phi = np.radians(40 + 25 * s + 55 * s ** 2)
    ds = length / (N - 1)
    pos = [root]
    for i in range(1, N):
        h = phi[i]
        pos.append(pos[-1] + ds * (rad * np.sin(h) + z * np.cos(h)))
    pos = np.array(pos)
    width = w0 * np.sin(np.pi * np.clip(s * 0.97 + 0.02, 0, 1)) ** 0.6 * (1 - 0.3 * s)
    width[0] = w0 * 0.55
    # pinnate leaflet teeth: every other station sticks out, tip tapers away
    teeth = np.where(np.arange(N) % 2 == 0, 1.55, 0.85) * (s > 0.10)
    teeth[teeth == 0] = 1.0
    width = width * teeth
    width[-1] = 0.0
    # local frames: width along tangential dir (twisted slightly), thickness normal to path
    L, R, T, B = [], [], [], []
    for i in range(N):
        d = pos[min(i + 1, N - 1)] - pos[max(i - 1, 0)]
        d /= np.linalg.norm(d)
        nrm = np.cross(tan, d); nrm /= np.linalg.norm(nrm)
        half = nrm * thick / 2
        L.append(pos[i] + tan * width[i]); R.append(pos[i] - tan * width[i])
        T.append(half); B.append(-half)
    for i in range(N - 1):
        m.quad(L[i] + T[i], L[i + 1] + T[i + 1], R[i + 1] + T[i + 1], R[i] + T[i])
        m.quad(R[i] + B[i], R[i + 1] + B[i + 1], L[i + 1] + B[i + 1], L[i] + B[i])
        m.quad(L[i] + B[i], L[i + 1] + B[i + 1], L[i + 1] + T[i + 1], L[i] + T[i])
        m.quad(R[i] + T[i], R[i + 1] + T[i + 1], R[i + 1] + B[i + 1], R[i] + B[i])
    m.quad(L[0] + T[0], R[0] + T[0], R[0] + B[0], L[0] + B[0])
    m.quad(R[-1] + B[-1], R[-1] + T[-1], L[-1] + T[-1], L[-1] + B[-1])
    return m, pos


def rib(pos, r0=1.5, r1=0.5, sides=8):
    """Closed tapered midrib tube along the frond path (printability + look)."""
    m = Mesh()
    rings = []
    N = len(pos)
    for i, p in enumerate(pos):
        d = pos[min(i + 1, N - 1)] - pos[max(i - 1, 0)]; d /= np.linalg.norm(d)
        ref = np.array([0, 0, 1.0]) if abs(d[2]) < .9 else np.array([1.0, 0, 0])
        n = np.cross(d, ref); n /= np.linalg.norm(n); b = np.cross(d, n)
        r = r0 + (r1 - r0) * i / (N - 1)
        rings.append([p + r * (np.cos(a) * n + np.sin(a) * b) for a in np.linspace(0, 2 * np.pi, sides, endpoint=False)])
    for i in range(N - 1):
        for j in range(sides):
            k = (j + 1) % sides
            m.quad(rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j])
    for ring, c in ((rings[0], pos[0]), (rings[-1], pos[-1])):
        for j in range(sides):
            m.tri(c, ring[j], ring[(j + 1) % sides])
    return m


def tuned_curl():
    """Largest curl for which no frond point gets inside the can radius."""
    lo, hi = 0.0, 90.0
    for _ in range(40):
        mid = (lo + hi) / 2
        _, pos = frond(0.0, True, curl=mid)
        if np.hypot(pos[:, 0], pos[:, 1]).min() >= CAN_R + 1.6:
            lo = mid
        else:
            hi = mid
    return lo


def build(closed):
    hull = revolve(outer_profile())
    cav = revolve(cavity_profile())
    curl = tuned_curl()
    fronds = []
    for i in range(N_FRONDS):
        a = 2 * np.pi * i / N_FRONDS
        f, pos = frond(a, closed, curl=curl)
        fronds += [f, rib(pos)]
    return hull, cav, fronds


def props(arr):
    """Volume and z-moment (sum of tet volume * tet centroid z) of a closed oriented mesh."""
    v = np.einsum("ij,ij->i", arr[:, 0], np.cross(arr[:, 1], arr[:, 2])) / 6
    return v.sum(), (v * arr[:, :, 2].sum(1) / 4).sum()


def float_report(hull, cav, fronds, extra=None):
    H, C = hull.array().astype(float), cav.array().astype(float)
    vh, mh = props(H); vc, mc = props(C)
    vf = mf = 0.0
    for f in fronds:
        v, m = props(f.array().astype(float)); vf += v; mf += m
    plastic_v = vh - vc + vf
    m_plastic = plastic_v * PLASTIC
    zc_plastic = (mh - mc + mf) / plastic_v
    # displaced volume of the sealed hull envelope below waterline d (well stays dry)
    prof = outer_profile()
    def r_out(z):
        # outer radius at height z along the exterior (pad + collar) wall
        rs = [(a, b) for a, b in prof[1:-4]]
        zs = [b for a, b in rs]; rr = [a for a, b in rs]
        return np.interp(z, zs, rr)
    zz = np.linspace(0, BASE_H, 3001)
    area = np.pi * np.where(zz <= PAD_H, PAD_R, r_out(zz)) ** 2
    dz = np.diff(zz)
    seg_v = (area[1:] + area[:-1]) / 2 * dz
    cumV = np.concatenate([[0], np.cumsum(seg_v)])
    cumM = np.concatenate([[0], np.cumsum(seg_v * (zz[1:] + zz[:-1]) / 2)])
    extra_m, extra_zm = extra if extra else (0.0, 0.0)
    M = m_plastic + CAN_G + extra_m
    d = float(np.interp(M / WATER, cumV, zz))
    V = M / WATER
    KB = float(np.interp(d, zz, cumM) / np.interp(d, zz, cumV))
    I = np.pi * float(np.where(d <= PAD_H, PAD_R, r_out(d))) ** 4 / 4
    KG = (m_plastic * zc_plastic + CAN_G * (BASE_H - WELL_DEPTH + CAN_COG) + extra_zm) / M
    GM = KB + I / V - KG
    buoy_max = cumV[-1] * WATER
    print(f"  plastic: {plastic_v/1000:.0f} cm3 solid, {m_plastic:.0f} g (PETG)  |  sealed chamber {vc/1000:.0f} cm3")
    print(f"  with a full can ({CAN_G:.0f} g){' + lid' if extra else ''}: draft {d:.1f} mm of {BASE_H:.0f}, freeboard {BASE_H-d:.1f} mm (pad top {PAD_H-d:+.1f} mm vs water)")
    print(f"  hull buoyancy at full submersion {buoy_max:.0f} g  vs  load {M:.0f} g  -> {'FLOATS' if M < buoy_max else 'SINKS'}")
    print(f"  stability GM = {GM:.0f} mm ({'stable' if GM > 15 else 'marginal/UNSTABLE'});  empty draft ~{float(np.interp(m_plastic/WATER, cumV, zz)):.1f} mm, KG {KG:.0f}")
    assert M < buoy_max and GM > 15 and PAD_H - d >= 3, 'float check failed'


def write_stl(parts, path):
    arr = np.concatenate(parts)
    nrm = np.cross(arr[:, 1] - arr[:, 0], arr[:, 2] - arr[:, 0])
    ln = np.linalg.norm(nrm, axis=1, keepdims=True); ln[ln == 0] = 1
    rec = np.zeros(len(arr), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = nrm / ln, arr
    with open(path, "wb") as f:
        f.write(b"palm frond can holder".ljust(80, b" "))
        f.write(np.uint32(len(arr)).tobytes()); f.write(rec.tobytes())
    mn, mx = arr.reshape(-1, 3).min(0), arr.reshape(-1, 3).max(0)
    print(f"{path}: {len(arr)} tris, bbox {np.round(mx - mn, 1)} mm")


if __name__ == "__main__":
    import make_lid
    lid_mass, lid_cog = make_lid.build_and_write()
    floor_z = BASE_H - WELL_DEPTH
    extra = (lid_mass, lid_mass * (floor_z + CAN_H + lid_cog))
    for closed, name in ((True, "palm_holder_closed.stl"), (False, "palm_holder_open.stl")):
        hull, cav, fronds = build(closed)
        parts = [hull.array(), cav.array()[:, ::-1]] + [f.array() for f in fronds]  # cavity faces inward
        write_stl(parts, name)
        if closed:
            fr = np.concatenate([f.array() for f in fronds]).reshape(-1, 3); fr = fr[fr[:, 2] > BASE_H]
            print(f"  min frond radius above base {np.hypot(fr[:, 0], fr[:, 1]).min():.1f} mm (can r={CAN_R}); curl={tuned_curl():.1f} deg; "
                  f"frond tops at z={fr[:, 2].max():.0f}, can rim at z={floor_z + CAN_H:.0f}")
        float_report(hull, cav, fronds, extra if closed else None)
