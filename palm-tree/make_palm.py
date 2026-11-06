"""Floating palm island can holder with self-closing palm-frond 'petals' (units: mm).

Parts (print list):
  palm_island_base.stl  x1   island float (sealed air chamber) + collar with 9 hinge slots + decorative palm tree
  palm_frond.stl        x9   frond + knuckle + 'stem' lever; 1.75 mm filament pin (12 mm) through each hinge
  palm_lid_ring.stl / palm_lid_dome.stl  x1  hinged coconut can lid (see make_lid.py), 19 mm pin
How it works: with no can, each frond lies open over the island and its stem sticks up into the well.
Setting a can in pushes the stems down; the fronds flip up and curl in around the can.
"""
import numpy as np
from meshkit import (Mesh, revolve, sector, hinge_cyl, slab, tube, sphere, xform, props, write_stl)
import make_lid

CAN_R, CAN_H = 33.5, 122.0           # 12 oz can
PAD_R, PAD_H, WALL = 100.0, 26.0, 1.6
FLOOR, LEDGE = 4.0, 9.0
BORE_UP, BORE_LOW = 40.6, 34.5
COLLAR_R, COLLAR_H = 46.0, 12.0
TOP = PAD_H + COLLAR_H
N = 9
PX, PZ = 40.5, PAD_H + 6.0           # hinge pivot (radius, height) in each slot
TAIL_L, TAIL_T, TIP_R = 19.0, 2.4, 35.0
SLOT_DA = np.arcsin(6.4 / PX)        # half-angle of each slot
LUG_R, HOLE_R = 3.2, 1.1
PLASTIC, WATER, CAN_G, CAN_COG = 1.27e-3, 1.0e-3, 380.0, 55.0


def g(phi):  # island outline wobble
    return 1 + 0.045 * np.sin(3 * phi + 0.7) + 0.03 * np.sin(5 * phi + 2.1)


def lathe(profile, seg=120):
    """Revolve a closed (r,z) loop with the island's wobbly outline applied to r > 45."""
    m = Mesh()
    ang = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    def P(r, z, t):
        k = np.clip((r - 45) / 30, 0, 1)
        rr = r * (1 + (g(t) - 1) * k)
        return np.array([rr * np.cos(t), rr * np.sin(t), z])
    for i in range(len(profile)):
        (r0, z0), (r1, z1) = profile[i], profile[(i + 1) % len(profile)]
        for j in range(seg):
            a, b = ang[j], ang[(j + 1) % seg]
            if r0 == 0 and r1 == 0:
                continue
            if r0 == 0:
                m.tri(P(0, z0, a), P(r1, z1, a), P(r1, z1, b))
            elif r1 == 0:
                m.tri(P(r0, z0, a), P(0, z1, a), P(r0, z0, b))
            else:
                m.quad(P(r0, z0, a), P(r1, z1, a), P(r1, z1, b), P(r0, z0, b))
    return m


def rotz(m, a):
    c, s = np.cos(a), np.sin(a)
    return xform(m, [[c, -s, 0], [s, c, 0], [0, 0, 1]], [0, 0, 0])


def rot_cw(arr, d, pivot=(PX, 0.0, PZ)):
    """Rotate points clockwise (in the r-z plane) by d about the hinge axis (parallel to y)."""
    p = np.asarray(arr, float) - pivot
    x, z = p[..., 0].copy(), p[..., 2].copy()
    p[..., 0] = x * np.cos(d) + z * np.sin(d)
    p[..., 2] = -x * np.sin(d) + z * np.cos(d)
    return p + pivot


# ---------------------------------------------------------------- island base
def island_profile():
    return [(0, 0), (PAD_R, 0), (PAD_R, 8), (88, PAD_H), (BORE_UP, PAD_H), (BORE_UP, LEDGE),
            (BORE_LOW, LEDGE), (BORE_LOW, FLOOR), (0, FLOOR)]


def cavity_profile():
    return [(42.2, WALL), (98.4, WALL), (98.6, 6.9), (87.1, PAD_H - WALL), (42.2, PAD_H - WALL)]


def collar_sectors():
    out = []
    prof = [(BORE_UP, PAD_H), (COLLAR_R, PAD_H)]
    for k in range(1, 9):
        prof.append((COLLAR_R + (1.5 if k % 2 else 0.0), PAD_H + COLLAR_H * k / 8))
    prof.append((BORE_UP, TOP))
    for k in range(N):
        a = 2 * np.pi * k / N
        out.append(sector(prof, a + SLOT_DA, a + 2 * np.pi / N - SLOT_DA, seg=10))
    return out


def hinge_lugs():
    out = []
    for k in range(N):
        for y0, y1 in ((3.4, 8.6), (-8.6, -3.4)):
            out.append(rotz(hinge_cyl(PX, PZ, y0, y1, LUG_R, HOLE_R), 2 * np.pi * k / N))
    return out


def palm_tree(phi=np.radians(220), R=66.0, height=62.0):
    """Small decorative palm on the island, standing in the gap between two open fronds."""
    parts = []
    base = np.array([R * np.cos(phi), R * np.sin(phi), PAD_H - 1.0])
    lean = np.array([np.cos(phi + 0.9), np.sin(phi + 0.9), 0.0])
    n = 28; t = np.linspace(0, 1, n)
    path = [base + lean * 11 * ti**1.5 * 1.0 + np.array([0, 0, height * ti]) for ti in t]
    radii = [(4.3 - 1.6 * ti) * (1 + 0.07 * (np.sin(ti * 2 * np.pi * 9) > 0.3)) for ti in t]
    parts.append(tube(path, radii, sides=14))
    top = path[-1]
    rng = np.random.default_rng(3)
    for i in range(8):
        a = 2 * np.pi * i / 8 + rng.uniform(-.1, .1)
        d = np.array([np.cos(a), np.sin(a), 0.0]); tg = np.array([-np.sin(a), np.cos(a), 0.0])
        L, M = 24.0, 14
        pos = [top.copy()]
        for j in range(1, M):
            s = j / (M - 1); eta = np.radians(38 - 95 * s)
            pos.append(pos[-1] + (L / (M - 1)) * (d * np.cos(eta) + np.array([0, 0, np.sin(eta)])))
        s = np.linspace(0, 1, M)
        w = 4.2 * np.sin(np.pi * np.clip(s * 0.95 + 0.03, 0, 1)) ** 0.7 * np.where(np.arange(M) % 2 == 0, 1.3, 0.85)
        w[-1] = 0.0
        parts.append(slab(pos, w, 1.4, tg))
        parts.append(tube(pos, np.linspace(0.9, 0.5, M), sides=6))
    for a in (0.3, 2.4, 4.5):
        parts.append(sphere(top + np.array([3.6 * np.cos(a), 3.6 * np.sin(a), -3.2]), 2.9))
    return parts


# ---------------------------------------------------------------- frond (local frame, CLOSED pose)
def tail_angle():
    return -np.arccos((TIP_R - PX) / TAIL_L)


def blade_path(curl, M=34, length=78.0, lean=8.0):
    s = np.linspace(0, 1, M)
    phi = np.radians(lean - curl * s ** 1.15)
    ds = length / (M - 1)
    pos = [np.array([PX, 0.0, PZ])]
    for i in range(1, M):
        pos.append(pos[-1] + ds * np.array([np.sin(phi[i]), 0.0, np.cos(phi[i])]))
    return s, np.array(pos)


def tuned_curl():
    lo, hi = 0.0, 90.0
    for _ in range(40):
        mid = (lo + hi) / 2
        s, pos = blade_path(mid)
        rib = 1.5 + (0.5 - 1.5) * s
        if (pos[:, 0] - rib - 0.9).min() >= CAN_R + 0.2:
            lo = mid
        else:
            hi = mid
    return lo


def frond_parts(curl, w0=6.0):
    s, pos = blade_path(curl)
    M = len(s)
    w = w0 * np.sin(np.pi * np.clip(s * 0.97 + 0.02, 0, 1)) ** 0.6 * (1 - 0.3 * s)
    w[0] = w0 * 0.55
    teeth = np.where(np.arange(M) % 2 == 0, 1.55, 0.85) * (s > 0.10); teeth[teeth == 0] = 1.0
    w = w * teeth; w[-1] = 0.0
    tg = np.array([0, 1.0, 0])
    parts = [slab(pos, w, 1.8, tg), tube(pos, 1.5 + (0.5 - 1.5) * s, sides=8)]
    th = tail_angle()
    tp = [np.array([PX, 0, PZ]) + t * np.array([np.cos(th), 0, np.sin(th)]) for t in np.linspace(0, TAIL_L, 8)]
    parts.append(slab(tp, np.linspace(3.0, 2.2, 8), TAIL_T, tg))
    parts.append(hinge_cyl(PX, PZ, -3.0, 3.0, LUG_R, HOLE_R))
    return parts


def arr(parts):
    return np.concatenate([p.array() for p in parts])


def inside_island(x, z):
    return (z < PAD_H) & (x > BORE_UP) | (z < LEDGE) & (x > BORE_LOW) | (z < FLOOR)


def checks(curl):
    th = tail_angle() % (2 * np.pi)
    delta = th - np.pi                                   # closed -> rest rotation (clockwise)
    print(f"curl {curl:.1f} deg; stem angle closed {np.degrees(th):.0f} deg, rest 180 deg; frond swing {np.degrees(delta):.0f} deg")
    # stem sweep clearance vs island (tail outline at 2 edges across the whole swing)
    worst = 9e9
    for ang in np.linspace(np.pi, th, 40):
        for off in (-TAIL_T / 2, TAIL_T / 2):
            for t in np.linspace(0, TAIL_L, 30):
                x = PX + t * np.cos(ang) - off * np.sin(ang); z = PZ + t * np.sin(ang) + off * np.cos(ang)
                if inside_island(x, z):
                    worst = min(worst, -1)
    print("  stem sweep vs island/bore:", "CLEAR" if worst > 0 else "COLLIDES")
    s, pos = blade_path(curl)
    cl = pos.copy()
    rest = rot_cw(pos, delta)
    r_rest = np.hypot(rest[:, 0], rest[:, 1])
    ztop = np.interp(r_rest, [0, 88, 100], [PAD_H, PAD_H, 8])
    print(f"  closed: frond min radius {np.hypot(cl[:,0], cl[:,1]).min():.1f} (can {CAN_R}); tip z {cl[-1,2]:.0f}, can rim z {FLOOR+CAN_H:.0f}")
    print(f"  rest: lowest frond point above island top by {(rest[:,2]-ztop-1.5).min():.1f} mm; reach r={r_rest.max():.0f}, tip z {rest[-1,2]:.0f}")
    return delta


def float_report(base_solids, cavs, fronds_closed, palm, extra):
    vol = mom = 0.0
    for a in base_solids + fronds_closed * N + palm:
        v, m = props(a); vol += v; mom += m
    for a in cavs:
        v, m = props(a); vol -= v; mom -= m
    m_plastic = vol * PLASTIC; zc = mom / vol
    zz = np.linspace(0, TOP, 4001)
    phi = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    ascale = np.mean(((1 + (g(phi) - 1)))**2)
    r = np.interp(zz, [0, 8, PAD_H, PAD_H + 0.001, TOP], [PAD_R, PAD_R, 88, COLLAR_R, COLLAR_R])
    area = np.pi * (r**2) * np.where(zz <= PAD_H, ascale, 1.0)
    seg = (area[1:] + area[:-1]) / 2 * np.diff(zz)
    cumV = np.concatenate([[0], np.cumsum(seg)]); cumM = np.concatenate([[0], np.cumsum(seg * (zz[1:] + zz[:-1]) / 2)])
    em, ezm = extra
    M = m_plastic + CAN_G + em
    d = float(np.interp(M / WATER, cumV, zz)); V = M / WATER
    KB = float(np.interp(d, zz, cumM) / np.interp(d, zz, cumV))
    rw = float(np.interp(d, zz, r)) * np.sqrt(ascale)
    I = np.pi * rw**4 / 4
    KG = (m_plastic * zc + CAN_G * (FLOOR + CAN_COG) + ezm) / M
    GM = KB + I / V - KG
    print(f"  plastic {m_plastic:.0f} g (PETG, solid walls); with can {CAN_G:.0f} g + lid {em:.0f} g: draft {d:.1f} mm, island top {PAD_H-d:+.1f} mm above water")
    print(f"  buoyancy at island-top waterline {np.interp(PAD_H, zz, cumV)*WATER:.0f} g vs load {M:.0f} g; GM {GM:.0f} mm -> "
          f"{'FLOATS, stable' if (PAD_H - d >= 3 and GM > 15) else 'PROBLEM'}")
    assert PAD_H - d >= 3 and GM > 15


def main():
    import os
    for f in ("palm_holder_closed.stl", "palm_holder_open.stl"):
        if os.path.exists(f): os.remove(f)
    curl = tuned_curl()
    delta = checks(curl)
    # base
    hull = lathe(island_profile()); cav = lathe(cavity_profile())
    sectors, lugs, palm = collar_sectors(), hinge_lugs(), palm_tree()
    base_parts = [hull] + sectors + lugs + palm
    base_arr = [arr([m]) for m in [hull] + sectors + lugs]
    palm_arr = [arr([m]) for m in palm]
    cav_out = cav.array().astype(float)
    cav_arr = [cav_out[:, ::-1].astype(np.float32)]   # inward-facing copy for the STL
    # fronds
    fr = frond_parts(curl)
    fr_closed = arr(fr)
    fr_rest = rot_cw(fr_closed, delta)
    # lid
    lid_mass, lid_cog = make_lid.build_and_write()
    extra = (lid_mass, lid_mass * (FLOOR + CAN_H + lid_cog))
    # stl export
    write_stl(np.concatenate([arr([hull])] + [arr([m]) for m in sectors + lugs + palm] + [cav_arr[0].astype(np.float32)]),
              "palm_island_base.stl", b"palm island base")
    # frond exported at rest pose, standing on its edge (y up) for printing
    R = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)
    fp = (fr_rest - np.array([PX, 0, PZ])) @ R.T
    fp[..., 2] -= fp[..., 2].min()
    write_stl(fp, "palm_frond.stl", b"palm frond x9")
    float_report(base_arr, [cav_out], [fr_closed], palm_arr, extra)
    # preview data
    rz = lambda a, k: (lambda c, s: a @ np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]]))(np.cos(2*np.pi*k/N), np.sin(2*np.pi*k/N))
    base_all = np.concatenate([arr([hull])] + [arr([m]) for m in sectors + lugs + palm])
    np.save("/tmp/p_base.npy", base_all)
    np.save("/tmp/p_closed.npy", np.concatenate([rz(fr_closed, k) for k in range(N)]))
    np.save("/tmp/p_rest.npy", np.concatenate([rz(fr_rest, k) for k in range(N)]))
    # frond vs palm proximity in rest pose
    pv = np.concatenate(palm_arr).reshape(-1, 3)[::3]
    fv = np.concatenate([rz(fr_rest, k) for k in range(N)]).reshape(-1, 3)[::4]
    dmin = min(np.linalg.norm(fv[i:i+800, None, :] - pv[None], axis=2).min() for i in range(0, len(fv), 800))
    print(f"  palm tree to nearest open frond: {dmin:.1f} mm")


if __name__ == "__main__":
    main()
