"""Old-volcano island, two parts that screw together (units: mm).

palm_island.stl  : floating island (can well + hinge collar + sealed air chamber) with a threaded socket underneath.
palm_volcano.stl : old volcano keel (hollow shell around a ballast tube) with a threaded spigot on top and the plug hatch in its base.
Screw the island onto the volcano (clockwise as seen from above). Weights go in through the base plug (cap + O-ring).
Other parts: palm_frond.stl x9, palm_plug_cap.stl x1.
"""
import numpy as np
from meshkit import props, write_stl
import make_palm as mp
import make_spar as ms
import make_volcano as mv
from make_volcano import lathe, flank_r, flank_inset
from make_palm import arr, rot_cw, FLOOR, LEDGE, BORE_UP, BORE_LOW, WALL, N, PX, PZ
W = WALL
Z0 = mp.PAD_H
R_I = 100.0
R_COL = 40.0                       # island collar outer radius
R_FM, DEPTH, CLR = 34.0, 1.6, 0.5  # female thread major radius, thread depth, radial clearance
R_MC = R_FM - CLR - DEPTH          # male core radius (31.9)
R_N, H_F, R_V, P = 40.0, 110.0, 66.0, 2.2
R_B, R_TI = ms.R_B, 28.0
Z_COL_TOP = -(R_I - R_COL)         # funnel ends
Z_JOINT = Z_COL_TOP - 20.0         # island collar bottom face = volcano shoulder top
Z_S = Z_COL_TOP - 2.0              # socket ceiling
Z_T = Z_S - 0.6                    # spigot top
NECK_H = 20.0
Z_FT = Z_JOINT - NECK_H
Z_BASE = Z_FT - H_F
Z_C = Z_T - 2.4                    # ballast ceiling
# keep make_volcano's flank helpers in sync
mv.R_N, mv.H_F, mv.R_V, mv.P, mv.Z_FT, mv.Z_BASE, mv.R_TI, mv.R_I = R_N, H_F, R_V, P, Z_FT, Z_BASE, R_TI, R_I
SHOT_RHO, SHOT_PACK = 7.85e-3, 0.60
PLASTIC, WATER, CAN_G, CAN_COG = 1.27e-3, 1.0e-3, 380.0, 55.0


def island_profiles():
    outer = [(0, FLOOR), (BORE_LOW, FLOOR), (BORE_LOW, LEDGE), (BORE_UP, LEDGE), (BORE_UP, Z0), (R_I - 12, Z0), (R_I, 8), (R_I, 0),
             (R_COL, Z_COL_TOP), (R_COL, Z_JOINT), (R_FM, Z_JOINT), (R_FM, Z_S), (0, Z_S)]
    cz = Z_S + W + 0.3
    r_cone = lambda z: R_I - 1.13 + (z - 1.13)
    air = [(0, cz), (r_cone(cz), cz), (R_I - 1.6, 0.66), (R_I - 1.4, 6.9), (R_I - 12 - 0.9, Z0 - W), (42.2, Z0 - W), (42.2, FLOOR - W), (0, FLOOR - W)]
    return outer, [air]


def volcano_profiles(nflank=36):
    zs = np.linspace(Z_FT, Z_BASE, nflank)
    flank = [(float(flank_r(z)), float(z)) for z in zs]
    outer = ([(0, Z_T), (R_MC, Z_T), (R_MC, Z_JOINT), (R_N, Z_JOINT)] + flank
             + [(R_B, Z_BASE), (R_B, Z_BASE + 14), (R_B + 6, Z_BASE + 14), (R_B + 6, Z_BASE + W), (R_TI, Z_BASE + W), (R_TI, Z_C), (0, Z_C)])
    fz = np.linspace(Z_FT, Z_BASE + W, 60)
    inner = [(float(flank_r(z) - flank_inset(z)), float(z)) for z in fz]
    air = [(R_TI + W, Z_JOINT - W - 0.0), (R_N - W, Z_JOINT - W)] + inner + [(R_TI + W, Z_BASE + W)]
    void = [(R_B + 6, Z_BASE + W), (R_TI, Z_BASE + W), (R_TI, Z_C), (0, Z_C), (0, Z_BASE + 14), (R_B + 6, Z_BASE + 14)]
    return outer, [air], void


def threads():
    male = ms.helix_ridge(R_MC, DEPTH, 4.0, 3.7, Z_JOINT + 0.8, True)
    female = ms.helix_ridge(R_FM, DEPTH, 4.0, 3.8, Z_JOINT + 0.2, False)
    return male, female


def envelope():
    zs = np.linspace(Z_BASE, Z_FT, 80)
    z = list(zs) + [Z_JOINT, Z_COL_TOP, 0.0, 8.0, Z0]
    r = [float(flank_r(v)) for v in zs] + [R_N, R_COL, R_I, R_I, R_I - 12]
    return np.array(z), np.array(r)


def evaluate(ballast, ex, seg=48):
    io, iairs = island_profiles(); vo, vairs, void = volcano_profiles()
    hi, hv = lathe(io, seg), lathe(vo, seg)
    cavs = [lathe(a, seg) for a in iairs + vairs]; vd = lathe(void, seg)
    vol = mom = 0.0
    for h in (hi, hv):
        a, b = props(h.array().astype(float)); vol += a; mom += b
    for c in cavs:
        a, b = props(c.array().astype(float)); vol -= a; mom -= b
    m_pl = vol * PLASTIC + ex[0]
    zc = (mom * PLASTIC + ex[1]) / m_pl
    zs = np.linspace(Z_BASE + W, Z_C, 800)
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
    return dict(zw=zw, GM=GM, m_plastic=m_pl, hi=hi, hv=hv, cavs=cavs, cap_v=cum[-1], top=Z0 - zw)


B_NOM = 1150.0


def main():
    curl, ex, sect, lugs, fr, cap = ms.extras()
    male, female = threads()
    tm = sum(props(arr([t]).astype(float))[0] for t in (male, female)) * PLASTIC
    ex = (ex[0] + props(arr(cap).astype(float))[0] * PLASTIC + tm, ex[1])
    delta = mp.checks(curl)
    print(f"island socket z {Z_JOINT:.0f}..{Z_S:.0f}; volcano base z {Z_BASE:.0f}; total {Z0 - Z_BASE:.0f} mm")
    for B in (900, 1000, 1150, 1300):
        q = evaluate(B, ex)
        print(f"  {B:5d} g: " + ("over capacity or sinks" if q is None else f"island top {q['top']:.0f} mm above water, GM {q['GM']:.0f} mm, plastic {q['m_plastic']:.0f} g"))
    r = evaluate(B_NOM, ex, seg=120)
    assert r is not None and r["GM"] > 30 and r["top"] > 8, r
    iair, vair = r["cavs"][0], r["cavs"][1]
    write_stl(np.concatenate([arr([m]) for m in [r["hi"]] + sect + lugs + [female]] + [iair.array()[:, ::-1]]), "palm_island.stl", b"palm island")
    write_stl(np.concatenate([arr([m]) for m in [r["hv"], male, ms.female_thread(Z_BASE)]] + [vair.array()[:, ::-1]]), "palm_volcano.stl", b"palm volcano")
    capa = arr(cap).copy(); capa[:, :, 2] -= capa[:, :, 2].min()
    write_stl(capa, "palm_plug_cap.stl", b"plug cap")
    fr_rest = rot_cw(fr, delta)
    R = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)
    fp = (fr_rest - np.array([PX, 0, PZ])) @ R.T; fp[..., 2] -= fp[..., 2].min()
    write_stl(fp, "palm_frond.stl", b"palm frond x9")
    cap_g = 0.85 * r["cap_v"] * SHOT_RHO * SHOT_PACK
    print(f"\nWith can + {B_NOM:.0f} g: island top {r['top']:.0f} mm above water, GM {r['GM']:.0f} mm; ballast tube holds ~{cap_g:.0f} g")
    # thread fit check: female ridge tip vs male core, male tip vs female bore
    print(f"thread clearances: male tip {R_MC + DEPTH:.1f} < female bore {R_FM:.1f}; male core {R_MC:.1f} < female ridge tip {R_FM - DEPTH:.1f}")
    rz = lambda a, k: a @ np.array([[np.cos(2*np.pi*k/N), np.sin(2*np.pi*k/N), 0], [-np.sin(2*np.pi*k/N), np.cos(2*np.pi*k/N), 0], [0, 0, 1]])
    np.save("/tmp/i_base.npy", np.concatenate([arr([m]) for m in [r["hi"], r["hv"]] + sect + lugs]))
    np.save("/tmp/i_closed.npy", np.concatenate([rz(fr, k) for k in range(N)]))
    np.save("/tmp/i_rest.npy", np.concatenate([rz(fr_rest, k) for k in range(N)]))
    np.save("/tmp/i_meta.npy", np.array([r["zw"]]))


if __name__ == "__main__":
    main()
