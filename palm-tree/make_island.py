"""Palm island on a volcano keel (units: mm).

A flat island floats at the waterline; the can well and the 9 self-closing palm fronds are on it. Under it hangs a
volcano-shaped ballast keel (narrow neck, flaring to a wide base). Steel shot / fishing weights go in through a
watertight screw plug in the middle of the volcano's base (cap + O-ring): stand the unit on its crown to open it.

Parts: palm_volcano_island.stl x1, palm_frond.stl x9, palm_plug_cap.stl x1 (+ O-ring 44 x 2.5 mm, 1.75 mm filament pins).
Z=0 is the island's flat underside rim; the island top is at Z0.
"""
import os
import numpy as np
from meshkit import props, write_stl
import make_palm as mp
import make_spar as ms
from make_palm import lathe, arr, rot_cw, FLOOR, LEDGE, BORE_UP, BORE_LOW, WALL, N, PX, PZ
Z0, PAD_R = mp.PAD_H, mp.PAD_R
R_B = ms.R_B
R_N, NECK_H = 26.0, 12.0            # volcano neck radius / vertical neck length
R_V = 62.0                          # volcano base radius (45 deg flank)
SHOT_RHO, SHOT_PACK = 7.85e-3, 0.60
PLASTIC, WATER, CAN_G, CAN_COG = 1.27e-3, 1.0e-3, 380.0, 55.0
Z_NECK_TOP = -(PAD_R - R_N)                    # funnel (island underside) ends here: -74
Z_FLARE_TOP = Z_NECK_TOP - NECK_H
Z_BASE = Z_FLARE_TOP - (R_V - R_N)             # -122
W = WALL


def profiles():
    r_in = lambda z: R_N + (Z_FLARE_TOP - z) - 2.26            # inner flare line
    z_neck_in = Z_FLARE_TOP - (R_N - 2.26 - (R_N - 1.6)) - 0     # placeholder replaced below
    # inner flare meets the neck's inner wall (R_N - W) here:
    z_join = Z_FLARE_TOP - ((R_N - W) - (R_N - 2.26))            # flare inner r equals R_N-2.26 at Z_FLARE_TOP
    floor_z = Z_BASE + W
    ceil_z = Z_NECK_TOP + 2.4                                    # ballast ceiling (plate under island cavity)
    chamber = [(R_B + 6, Z_BASE + 14), (R_B + 6, floor_z), (r_in(floor_z), floor_z), (R_N - W, Z_FLARE_TOP + 0.0),
               (R_N - W, ceil_z), (0, ceil_z)]
    outer = [(0, FLOOR), (BORE_LOW, FLOOR), (BORE_LOW, LEDGE), (BORE_UP, LEDGE), (BORE_UP, Z0), (88, Z0), (PAD_R, 8), (PAD_R, 0),
             (R_N, Z_NECK_TOP), (R_N, Z_FLARE_TOP), (R_V, Z_BASE), (R_B, Z_BASE), (R_B, Z_BASE + 14)] + chamber
    cz = ceil_z + W + 0.3                                         # island cavity bottom (plate above ballast ceiling)
    r_cone = lambda z: PAD_R - 1.13 + (z - 1.13)                  # inner funnel line r(z)
    cav = [(0, cz), (r_cone(cz), cz), (98.4, 0.66), (98.6, 6.9), (87.1, Z0 - W), (42.2, Z0 - W), (42.2, FLOOR - W), (0, FLOOR - W)]
    void = [(R_B + 6, floor_z)] + chamber[2:] + [(0, Z_BASE + 14), (R_B + 6, Z_BASE + 14)]
    return outer, cav, void, floor_z, ceil_z


def envelope():
    return (np.array([Z_BASE, Z_FLARE_TOP, Z_NECK_TOP, 0.0, 8.0, Z0]), np.array([R_V, R_N, R_N, PAD_R, PAD_R, 88.0]))


def evaluate(ballast, ex, seg=48):
    outer, cav, void, floor_z, ceil_z = profiles()
    hull, cv, vd = lathe(outer, seg), lathe(cav, seg), lathe(void, seg)
    vh, mh = props(hull.array().astype(float)); vc, mc = props(cv.array().astype(float)); vv, _ = props(vd.array().astype(float))
    m_pl = (vh - vc) * PLASTIC + ex[0]
    zc = ((mh - mc) * PLASTIC + ex[1]) / m_pl
    # ballast fill height inside the volcano chamber
    zs = np.linspace(floor_z, ceil_z, 800)
    r_c = np.interp(zs, [floor_z, Z_FLARE_TOP, ceil_z], [R_V - 2.26 - (R_V - R_N) + (R_V - R_N) - 0.0, R_N - W, R_N - W])
    r_c = np.where(zs < Z_FLARE_TOP, R_N + (Z_FLARE_TOP - zs) - 2.26, R_N - W)
    a_c = np.pi * (r_c ** 2 - np.where(zs < Z_BASE + 14, (R_B + 6) ** 2, 0.0))
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
    area = np.pi * r ** 2 * ms.warp_area(r, phis)
    seg_v = (area[1:] + area[:-1]) / 2 * np.diff(zz)
    cumV = np.concatenate([[0], np.cumsum(seg_v)]); cumMV = np.concatenate([[0], np.cumsum(seg_v * (zz[1:] + zz[:-1]) / 2)])
    if M / WATER >= cumV[-1]:
        return None
    zw = float(np.interp(M / WATER, cumV, zz))
    KB = float(np.interp(zw, zz, cumMV) / np.interp(zw, zz, cumV))
    rw = float(np.interp(zw, zz, r)); I = np.pi * rw ** 4 / 4 * float(ms.warp_area(np.array([rw]), phis)[0])
    KG = (m_pl * zc + ballast * z_bal + CAN_G * (FLOOR + CAN_COG)) / M
    GM = KB + I / (M / WATER) - KG
    return dict(zw=zw, GM=GM, M=M, m_plastic=m_pl, KB=KB, KG=KG, hull=hull, cav=cv, cap_v=cum[-1], top=Z0 - zw)


B_NOM = 650.0


def main():
    curl, ex, sect, lugs, fr, cap = ms.extras()
    ex = (ex[0] + props(arr(cap).astype(float))[0] * PLASTIC, ex[1])
    delta = mp.checks(curl)
    r = evaluate(B_NOM, ex, seg=120)
    assert r is not None and r["GM"] > 30 and r["top"] > 8, r
    hull, cav = r["hull"], r["cav"]
    write_stl(np.concatenate([arr([m]) for m in [hull] + sect + lugs + [ms.female_thread(Z_BASE)]] + [cav.array()[:, ::-1]]),
              "palm_volcano_island.stl", b"palm volcano island")
    capa = arr(cap).copy(); capa[:, :, 2] -= capa[:, :, 2].min()
    write_stl(capa, "palm_plug_cap.stl", b"plug cap")
    fr_rest = rot_cw(fr, delta)
    R = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)
    fp = (fr_rest - np.array([PX, 0, PZ])) @ R.T; fp[..., 2] -= fp[..., 2].min()
    write_stl(fp, "palm_frond.stl", b"palm frond x9")
    for f in ("palm_spar_base.stl",):
        if os.path.exists(f): os.remove(f)
    cap_g = 0.85 * r["cap_v"] * SHOT_RHO * SHOT_PACK
    print(f"\nHeight {Z0 - Z_BASE:.0f} mm (volcano base to island top) + ~80 mm of fronds; island dia {2*PAD_R}, volcano base dia {2*R_V:.0f}")
    print(f"Plastic {r['m_plastic']:.0f} g. Volcano holds up to ~{cap_g:.0f} g shot. With can + {B_NOM:.0f} g: island top {r['top']:.0f} mm above water, GM {r['GM']:.0f} mm")
    print("Ballast tolerance:")
    for B in (400, 500, 650, 750):
        q = evaluate(B, ex)
        print(f"  {B:4d} g: island top {q['top']:.0f} mm above water, GM {q['GM']:.0f} mm")
    rz = lambda a, k: a @ np.array([[np.cos(2*np.pi*k/N), np.sin(2*np.pi*k/N), 0], [-np.sin(2*np.pi*k/N), np.cos(2*np.pi*k/N), 0], [0, 0, 1]])
    np.save("/tmp/i_base.npy", np.concatenate([arr([m]) for m in [hull] + sect + lugs]))
    np.save("/tmp/i_closed.npy", np.concatenate([rz(fr, k) for k in range(N)]))
    np.save("/tmp/i_rest.npy", np.concatenate([rz(fr_rest, k) for k in range(N)]))
    np.save("/tmp/i_meta.npy", np.array([r["zw"]]))


if __name__ == "__main__":
    main()
