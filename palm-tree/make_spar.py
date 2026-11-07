"""Palm spar can holder, sketch-style (units: mm).

Bowl-shaped weighted island underwater -> slim ringed palm trunk -> flat lily pad at the waterline ->
flared crown at the top with the can well and 9 self-closing palm fronds.
Weights (steel shot / fishing weights) go into the island through a watertight screw plug in the middle of its
underside (cap + O-ring): stand the unit on its crown to open it.

Parts: palm_spar_base.stl x1, palm_frond.stl x9, palm_plug_cap.stl x1 (+ O-ring 44 x 2.5 mm, 1.75 mm filament pins).
Z=0 is the crown cylinder's bottom; the well floor is at FLOOR, the hinge collar at Z0.
"""
import numpy as np
from meshkit import Mesh, props, write_stl, revolve, box
import make_palm as mp
from make_palm import lathe, arr, rot_cw, FLOOR, LEDGE, BORE_UP, BORE_LOW, WALL, N, PX, PZ
Z0 = mp.PAD_H
R_B = 18.4                          # plug bore radius
R_T = 34.0                          # slim trunk radius
R_C = 50.0                          # crown (can well section) radius
CROWN_CONE = R_C - R_T              # 45 deg flare, 16 mm
R_F, RIM = 90.0, 30.0               # lily pad radius, flat rim height (45 deg underside)
CN = R_F - R_T
NOPAD = False                       # True: plain slim trunk, no lily pad / bulge
HK = 60.0                           # island height
SHOT_RHO, SHOT_PACK = 7.85e-3, 0.60
PLASTIC, WATER, CAN_G, CAN_COG = 1.27e-3, 1.0e-3, 380.0, 55.0
FREEBOARD = 45.0
ISL_R = 66.0


def rings(z_hi, z_lo, r):
    pts = []; z = z_hi
    while z - 8.5 > z_lo:
        pts += [(r, z - 2.5), (r + 1.5, z - 4.5), (r, z - 6.5)]
        z -= 8.0
    return pts


def profiles(zt, zr):
    """zt = island top (trunk base); zr = z of the pad's rim bottom."""
    zb = zt - HK
    W = WALL
    cone_z = -CROWN_CONE
    island_out = [(R_T + 6, zb + 59), (R_T + 18, zb + 54), (R_T + 27, zb + 46), (ISL_R, zb + 38), (ISL_R, zb + 34), (32, zb)]
    chamber = [(R_B + 6, zb + 14), (R_B + 6, zb + W), (31.3, zb + W), (ISL_R - 2.3, zb + 34), (ISL_R - 2.3, zb + 38),
               (59.3, zb + 45), (51.0, zb + 52.3), (40.0, zb + 57.3), (R_T - W, zb + HK - 1.6), (0, zb + HK - 1.6)]
    head = [(0, FLOOR), (BORE_LOW, FLOOR), (BORE_LOW, LEDGE), (BORE_UP, LEDGE), (BORE_UP, Z0), (R_C, Z0), (R_C, 0), (R_T, cone_z)]
    if NOPAD:
        mid = rings(cone_z - 3, zt + 4, R_T)
    else:
        mid = (rings(cone_z - 3, zr + RIM + 2, R_T) + [(R_T, zr + RIM), (R_F, zr + RIM), (R_F, zr), (R_T, zr - CN)]
               + rings(zr - CN - 4, zt + 4, R_T))
    outer = head + mid + [(R_T, zt)] + island_out + [(R_B, zb), (R_B, zb + 14)] + chamber
    padc = [] if NOPAD else [(R_T - W, zr - CN + 0.66), (R_F - W, zr + 0.66), (R_F - W, zr + RIM - W), (R_T - W, zr + RIM - W)]
    cav = [(0, zt), (R_T - W, zt)] + padc + [(R_T - W, cone_z + 0.66), (R_C - W, 0.66), (R_C - W, Z0 - W), (42.2, Z0 - W), (42.2, FLOOR - W), (0, FLOOR - W)]
    void = [(R_B + 6, zb + W)] + chamber[2:] + [(0, zb + 14), (R_B + 6, zb + 14)]
    return zb, outer, cav, void


def envelope(zt, zr):
    zb = zt - HK
    z = [zb, zb + 34, zb + 38, zb + 46, zb + 54, zb + 59, zt]
    r = [32, ISL_R, ISL_R, R_T + 27, R_T + 18, R_T + 6, R_T]
    if not NOPAD:
        z += [zr - CN, zr, zr + RIM, zr + RIM + 1e-3]; r += [R_T, R_F, R_F, R_T]
    z += [-CROWN_CONE, 0.0, Z0]; r += [R_T, R_C, R_C]
    return np.array(z), np.array(r)


def warp_area(rr, phis):
    k = np.clip((rr - 45) / 30, 0, 1)
    return np.mean((1 + (mp.g(phis)[None, :] - 1) * k[:, None]) ** 2, axis=1)


def eval_at(Hc, ballast, ex, zr, seg):
    zt = Z0 - 16.0 - Hc          # trunk runs from the crown cone (z=-16) down Hc
    zt = -CROWN_CONE - Hc
    zb, outer, cav, void = profiles(zt, zr)
    hull, cv, vd = lathe(outer, seg), lathe(cav, seg), lathe(void, seg)
    vh, mh = props(hull.array().astype(float)); vc, mc = props(cv.array().astype(float)); vv, _ = props(vd.array().astype(float))
    m_pl = (vh - vc) * PLASTIC + ex[0]
    zc = ((mh - mc) * PLASTIC + ex[1]) / m_pl
    # ballast height from the chamber's volume profile (approximate bowl)
    zs = np.linspace(0, HK, 600)
    r_c = np.interp(zs, [W := WALL, 34, 38, 45, 52.3, 57.3, HK - 1.6], [31.3, ISL_R - 2.3, ISL_R - 2.3, 59.3, 51.0, 40.0, R_T - WALL])
    a_c = np.pi * (r_c ** 2 - np.where(zs < 14, (R_B + 6) ** 2, 0.0))
    cum = np.concatenate([[0], np.cumsum((a_c[1:] + a_c[:-1]) / 2 * np.diff(zs))]); cumM = np.concatenate([[0], np.cumsum((a_c[1:] * zs[1:] + a_c[:-1] * zs[:-1]) / 2 * np.diff(zs))])
    fill_v = ballast / (SHOT_RHO * SHOT_PACK)
    if fill_v > cum[-1] * 0.85:
        return None
    hf = float(np.interp(fill_v, cum, zs)); z_bal = zb + float(np.interp(hf, zs, cumM) / fill_v)
    M = m_pl + ballast + CAN_G
    ze, re_ = envelope(zt, zr)
    zz = np.linspace(zb, Z0, 9001); r = np.interp(zz, ze, re_)
    phis = np.linspace(0, 2 * np.pi, 90, endpoint=False)
    area = np.pi * r ** 2 * warp_area(r, phis)
    seg_v = (area[1:] + area[:-1]) / 2 * np.diff(zz)
    cumV = np.concatenate([[0], np.cumsum(seg_v)]); cumMV = np.concatenate([[0], np.cumsum(seg_v * (zz[1:] + zz[:-1]) / 2)])
    if M / WATER >= cumV[-1]:
        return None
    zw = float(np.interp(M / WATER, cumV, zz))
    KB = float(np.interp(zw, zz, cumMV) / np.interp(zw, zz, cumV))
    rw = float(np.interp(zw, zz, r)); I = np.pi * rw ** 4 / 4 * float(warp_area(np.array([rw]), phis)[0]) ** 1.0
    KG = (m_pl * zc + ballast * z_bal + CAN_G * (FLOOR + CAN_COG)) / M
    GM = KB + I / (M / WATER) - KG
    return dict(zw=zw, GM=GM, M=M, m_plastic=m_pl, zb=zb, zt=zt, vv=vv, KB=KB, KG=KG, hull=hull, cav=cv, cap_v=cum[-1], zr=zr, total_h=Z0 - zb)


def evaluate(Hc, ballast, ex, seg=48):
    zr = -CROWN_CONE - 40.0
    for _ in range(10):
        r = eval_at(Hc, ballast, ex, zr, seg)
        if r is None:
            return dict(ok=False, why="sinks / chamber too small")
        zr = r["zw"] - RIM / 2
    r = eval_at(Hc, ballast, ex, zr, seg)
    if r is None:
        return dict(ok=False, why="sinks / chamber too small")
    r["fb"] = Z0 - r["zw"]
    r["gap"] = (zr - CN) - r["zt"]
    r["ok"] = r["GM"] > 20 and r["fb"] >= FREEBOARD and r["gap"] >= 8
    return r


# ---- plug: coarse trapezoid thread + O-ring face seal (local frame: island bottom face at z=0)
def helix_ridge(r0, depth, pitch, turns, z0, outward=True, steps=48):
    m = Mesh(); n = int(steps * turns) + 1
    th = np.linspace(0, 2 * np.pi * turns, n)
    sec = [(-0.4, -0.8), (depth, -0.3), (depth, 0.3), (-0.4, 0.8)] if outward else [(0.4, -0.8), (-depth, -0.3), (-depth, 0.3), (0.4, 0.8)]
    rings_ = [[np.array([(r0 + dr) * np.cos(t), (r0 + dr) * np.sin(t), z0 + pitch * t / (2 * np.pi) + dz]) for dr, dz in sec] for t in th]
    for i in range(n - 1):
        for k in range(4):
            q = (k + 1) % 4
            m.quad(rings_[i][k], rings_[i][q], rings_[i + 1][q], rings_[i + 1][k])
    for ring, flip in ((rings_[0], False), (rings_[-1], True)):
        a, b, c, d = ring
        (m.quad(d, c, b, a) if flip else m.quad(a, b, c, d))
    return m


def cap_parts():
    core = revolve([(0, 0), (16.4, 0), (16.4, 13.0), (0, 13.0)], seg=64)
    flange = revolve([(0, -3.0), (25.0, -3.0), (25.0, 0), (23.8, 0), (23.8, -1.6), (21.0, -1.6), (21.0, 0), (0, 0)], seg=96)
    bar = box(-22, 22, -3.5, 3.5, -6.0, -3.0)
    return [core, flange, bar, helix_ridge(16.4, 1.6, 4.0, 2.8, 0.8, True)]


def female_thread(zb):
    return helix_ridge(R_B, 1.6, 4.0, 3.0, zb + 0.2, False)


def extras():
    curl = mp.tuned_curl()
    sect, lugs = mp.collar_sectors(), mp.hinge_lugs()
    fr = arr(mp.frond_parts(curl)); cap = cap_parts()
    m = zm = 0.0
    for a in [arr([s]) for s in sect + lugs] + [fr] * N:
        v, mo = props(a.astype(float)); m += v * PLASTIC; zm += mo * PLASTIC
    return curl, (m, zm), sect, lugs, fr, cap


HC = 120.0
B_NOM = 1050.0


def main():
    curl, ex, sect, lugs, fr, cap = extras()
    v, mo = props(arr(cap).astype(float)); cap_m = v * PLASTIC
    ex = (ex[0] + cap_m, ex[1])
    delta = mp.checks(curl)
    r = evaluate(HC, B_NOM, ex, seg=120)
    assert r.get("ok", False), r
    zb = r["zb"]; hull, cav = r["hull"], r["cav"]
    base_solids = [hull] + sect + lugs + [female_thread(zb)]
    write_stl(np.concatenate([arr([m]) for m in base_solids] + [cav.array()[:, ::-1]]), "palm_spar_base.stl", b"palm spar base")
    capa = arr(cap).copy(); capa[:, :, 2] -= capa[:, :, 2].min()
    write_stl(capa, "palm_plug_cap.stl", b"plug cap")
    fr_rest = rot_cw(fr, delta)
    R = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)
    fp = (fr_rest - np.array([PX, 0, PZ])) @ R.T; fp[..., 2] -= fp[..., 2].min()
    write_stl(fp, "palm_frond.stl", b"palm frond x9")
    import os
    for f in ("palm_hatch_cap.stl",):
        if os.path.exists(f): os.remove(f)
    chamber_cm3 = r["cap_v"] / 1000
    print(f"\nHeight {r['total_h']:.0f} mm (island bottom to crown top) + ~80 mm of fronds; island dia {2*ISL_R:.0f}, lily pad dia {2*R_F:.0f}")
    print(f"Plastic {r['m_plastic']:.0f} g. Ballast bowl {chamber_cm3:.0f} cm3. With can + {B_NOM:.0f} g shot: waterline {r['fb']:.0f} mm below crown top, GM {r['GM']:.0f} mm")
    print("Ballast tolerance (pad fixed in place: waterline below crown top / stability):")
    for d in (-300, -150, 0, 150, 300):
        q = eval_at(HC, B_NOM + d, ex, r["zr"], 48)
        print(f"  {B_NOM + d:5.0f} g: " + ("sinks / chamber too small" if q is None else f"{Z0 - q['zw']:.0f} mm / GM {q['GM']:.0f} mm"))
    # no-can condition + leak case (chamber air lost): how far does it sink?
    rz = lambda a, k: a @ np.array([[np.cos(2*np.pi*k/N), np.sin(2*np.pi*k/N), 0], [-np.sin(2*np.pi*k/N), np.cos(2*np.pi*k/N), 0], [0, 0, 1]])
    np.save("/tmp/s_base.npy", np.concatenate([arr([m]) for m in [hull] + sect + lugs]))
    np.save("/tmp/s_closed.npy", np.concatenate([rz(fr, k) for k in range(N)]))
    np.save("/tmp/s_rest.npy", np.concatenate([rz(fr_rest, k) for k in range(N)]))
    np.save("/tmp/s_meta.npy", np.array([r["zw"], r["zr"], r["zt"], zb]))


if __name__ == "__main__":
    main()
