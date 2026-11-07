"""Old-volcano island (units: mm).

A flat island floats at the waterline with the can well and 9 self-closing palm fronds on it. Under it hangs an old
volcano: narrow neck, concave flanks eroded by radial gullies, flaring to a wide base. The volcano is a hollow sealed
shell (buoyant) around a central ballast tube; steel shot / weights go in through a watertight screw plug in the
middle of the base (cap + O-ring): stand the unit on its crown to open it.

Parts: palm_volcano_island.stl x1, palm_frond.stl x9, palm_plug_cap.stl x1 (+ O-ring 44 x 2.5 mm, 1.75 mm filament pins).
"""
import os
import numpy as np
from meshkit import Mesh, props, write_stl
import make_palm as mp
import make_spar as ms
from make_palm import arr, rot_cw, FLOOR, LEDGE, BORE_UP, BORE_LOW, WALL, N, PX, PZ
Z0 = mp.PAD_H
R_I = 100.0                        # island radius
R_N, NECK_H = 31.0, 20.0           # volcano neck radius / vertical length
R_V, H_F, P = 72.0, 110.0, 2.2     # base radius, flank height, concavity
R_B = ms.R_B                       # plug bore
R_TI = 28.0                        # ballast tube inner radius
W = WALL
Z_NT = -(R_I - R_N)                # island underside (45 deg funnel) ends here
Z_FT = Z_NT - NECK_H               # flank starts
Z_BASE = Z_FT - H_F
Z_C = Z_NT + 2.4                   # ballast ceiling
SHOT_RHO, SHOT_PACK = 7.85e-3, 0.60
PLASTIC, WATER, CAN_G, CAN_COG = 1.27e-3, 1.0e-3, 380.0, 55.0
GULLY, LOBES = 1.2, 11


def flank_r(z):
    t = np.clip((Z_FT - z) / H_F, 0, 1)
    return R_N + (R_V - R_N) * t ** P


def flank_inset(z):
    t = np.clip((Z_FT - z) / H_F, 1e-6, 1)
    slope = (R_V - R_N) * P * t ** (P - 1) / H_F
    return W / np.cos(np.arctan(slope))


def warp(r, z, phi):
    """Island outline wobble above the volcano; eroded gullies on the flanks."""
    k = np.clip((r - 45) / 30, 0, 1) * np.clip((z + 75) / 20, 0, 1)
    out = r * (1 + (mp.g(phi) - 1) * k)
    fade = np.clip((Z_FT - z) / 25, 0, 1) * np.clip((r - 33) / 12, 0, 1)
    return out + GULLY * fade * np.sin(LOBES * phi + 0.08 * (Z_FT - z))


def lathe(profile, seg=120):
    m = Mesh()
    ang = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    P_ = lambda r, z, t: (lambda rr: np.array([rr * np.cos(t), rr * np.sin(t), z]))(warp(r, z, t))
    for i in range(len(profile)):
        (r0, z0), (r1, z1) = profile[i], profile[(i + 1) % len(profile)]
        for j in range(seg):
            a, b = ang[j], ang[(j + 1) % seg]
            if r0 == 0 and r1 == 0:
                continue
            if r0 == 0:
                m.tri(P_(0, z0, a), P_(r1, z1, a), P_(r1, z1, b))
            elif r1 == 0:
                m.tri(P_(r0, z0, a), P_(0, z1, a), P_(r0, z0, b))
            else:
                m.quad(P_(r0, z0, a), P_(r1, z1, a), P_(r1, z1, b), P_(r0, z0, b))
    return m


def profiles(nflank=36):
    zs = np.linspace(Z_FT, Z_BASE, nflank)
    flank = [(float(flank_r(z)), float(z)) for z in zs]
    outer = ([(0, FLOOR), (BORE_LOW, FLOOR), (BORE_LOW, LEDGE), (BORE_UP, LEDGE), (BORE_UP, Z0), (R_I - 12, Z0), (R_I, 8), (R_I, 0),
              (R_N, Z_NT)] + flank
             + [(R_B, Z_BASE), (R_B, Z_BASE + 14), (R_B + 6, Z_BASE + 14), (R_B + 6, Z_BASE + W), (R_TI, Z_BASE + W), (R_TI, Z_C), (0, Z_C)])
    cz = Z_C + W + 0.3
    r_cone = lambda z: R_I - 1.13 + (z - 1.13)
    island_air = [(0, cz), (r_cone(cz), cz), (R_I - 1.6, 0.66), (R_I - 1.4, 6.9), (R_I - 12 - 0.9, Z0 - W), (42.2, Z0 - W), (42.2, FLOOR - W), (0, FLOOR - W)]
    # hollow volcano shell: air between the ballast tube wall and the flank (offset inward)
    r_tube_out = R_TI + W
    fz = np.linspace(Z_FT, Z_BASE + W, 60)
    inner = [(float(flank_r(z) - flank_inset(z)), float(z)) for z in fz]
    start = next(i for i, (r, z) in enumerate(inner) if r >= r_tube_out + 1.6)
    inner = inner[start:]
    air = [(r_tube_out, inner[0][1])] + inner + [(r_tube_out, Z_BASE + W)]
    void = [(R_B + 6, Z_BASE + W), (R_TI, Z_BASE + W), (R_TI, Z_C), (0, Z_C), (0, Z_BASE + 14), (R_B + 6, Z_BASE + 14)]
    return outer, [island_air, air], void


def envelope():
    zs = np.linspace(Z_BASE, Z_FT, 80)
    z = list(zs) + [Z_NT, 0.0, 8.0, Z0]
    r = [float(flank_r(v)) for v in zs] + [R_N, R_I, R_I, R_I - 12]
    return np.array(z), np.array(r)


def evaluate(ballast, ex, seg=48):
    outer, airs, void = profiles()
    hull = lathe(outer, seg); cavs = [lathe(a, seg) for a in airs]; vd = lathe(void, seg)
    vh, mh = props(hull.array().astype(float)); vv, _ = props(vd.array().astype(float))
    vc = mc = 0.0
    for c in cavs:
        a, b = props(c.array().astype(float)); vc += a; mc += b
    m_pl = (vh - vc) * PLASTIC + ex[0]
    zc = ((mh - mc) * PLASTIC + ex[1]) / m_pl
    zs = np.linspace(Z_BASE + W, Z_C, 600)
    a_c = np.pi * (R_TI ** 2 - np.where(zs < Z_BASE + 14, (R_B + 6) ** 2, 0.0))
    cum = np.concatenate([[0], np.cumsum((a_c[1:] + a_c[:-1]) / 2 * np.diff(zs))])
    cumM = np.concatenate([[0], np.cumsum((a_c[1:] * zs[1:] + a_c[:-1] * zs[:-1]) / 2 * np.diff(zs))])
    fill_v = ballast / (SHOT_RHO * SHOT_PACK)
    if fill_v > 0.85 * cum[-1]:
        return None
    hf = float(np.interp(fill_v, cum, zs)); z_bal = float(np.interp(hf, zs, cumM) / fill_v)
    M = m_pl + ballast + CAN_G
    ze, re_ = envelope()
    zz = np.linspace(Z_BASE, Z0, 9001); r = np.interp(zz, ze, re_)
    phis = np.linspace(0, 2 * np.pi, 90, endpoint=False)
    area = np.pi * r ** 2 * np.where(zz > -75, ms.warp_area(r, phis), 1.0)
    seg_v = (area[1:] + area[:-1]) / 2 * np.diff(zz)
    cumV = np.concatenate([[0], np.cumsum(seg_v)]); cumMV = np.concatenate([[0], np.cumsum(seg_v * (zz[1:] + zz[:-1]) / 2)])
    if M / WATER >= cumV[-1]:
        return None
    zw = float(np.interp(M / WATER, cumV, zz))
    KB = float(np.interp(zw, zz, cumMV) / np.interp(zw, zz, cumV))
    rw = float(np.interp(zw, zz, r)); I = np.pi * rw ** 4 / 4 * float(ms.warp_area(np.array([rw]), phis)[0])
    KG = (m_pl * zc + ballast * z_bal + CAN_G * (FLOOR + CAN_COG)) / M
    GM = KB + I / (M / WATER) - KG
    return dict(zw=zw, GM=GM, M=M, m_plastic=m_pl, hull=hull, cavs=cavs, cap_v=cum[-1], top=Z0 - zw)


B_NOM = 1000.0


def main():
    curl, ex, sect, lugs, fr, cap = ms.extras()
    ex = (ex[0] + props(arr(cap).astype(float))[0] * PLASTIC, ex[1])
    delta = mp.checks(curl)
    print(f"keel: base z={Z_BASE:.0f}; island top z={Z0}; total {Z0 - Z_BASE:.0f} mm (+ crown and ~80 mm fronds)")
    for B in (700, 850, 1000, 1150):
        q = evaluate(B, ex)
        print(f"  {B:5d} g: " + ("over capacity or sinks" if q is None else f"island top {q['top']:.0f} mm above water, GM {q['GM']:.0f} mm, plastic {q['m_plastic']:.0f} g"))
    r = evaluate(B_NOM, ex, seg=120)
    assert r is not None and r["GM"] > 30 and r["top"] > 8, r
    hull = r["hull"]
    parts = [arr([m]) for m in [hull] + sect + lugs + [ms.female_thread(Z_BASE)]] + [c.array()[:, ::-1] for c in r["cavs"]]
    write_stl(np.concatenate(parts), "palm_volcano_island.stl", b"palm volcano island")
    capa = arr(cap).copy(); capa[:, :, 2] -= capa[:, :, 2].min()
    write_stl(capa, "palm_plug_cap.stl", b"plug cap")
    fr_rest = rot_cw(fr, delta)
    R = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)
    fp = (fr_rest - np.array([PX, 0, PZ])) @ R.T; fp[..., 2] -= fp[..., 2].min()
    write_stl(fp, "palm_frond.stl", b"palm frond x9")
    cap_g = 0.85 * r["cap_v"] * SHOT_RHO * SHOT_PACK
    print(f"\nWith can + {B_NOM:.0f} g shot: island top {r['top']:.0f} mm above water, GM {r['GM']:.0f} mm; tube holds up to ~{cap_g:.0f} g")
    rz = lambda a, k: a @ np.array([[np.cos(2*np.pi*k/N), np.sin(2*np.pi*k/N), 0], [-np.sin(2*np.pi*k/N), np.cos(2*np.pi*k/N), 0], [0, 0, 1]])
    np.save("/tmp/i_base.npy", np.concatenate([arr([m]) for m in [hull] + sect + lugs]))
    np.save("/tmp/i_closed.npy", np.concatenate([rz(fr, k) for k in range(N)]))
    np.save("/tmp/i_rest.npy", np.concatenate([rz(fr_rest, k) for k in range(N)]))
    np.save("/tmp/i_meta.npy", np.array([r["zw"]]))


if __name__ == "__main__":
    main()
