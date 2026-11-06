"""Sunk-island palm spar can holder (units: mm).

A weighted island 'keel' sits underwater. A sealed hollow palm trunk rises from it to just above the
surface; the can well and the 9 self-closing palm fronds are at the top of the trunk. Steel shot / fishing
weights go in the keel through a watertight screw hatch in the can-well floor (cap + O-ring), reached
from the top once the can is out.

Parts: palm_spar_base.stl x1, palm_frond.stl x9, palm_hatch_cap.stl x1 (+ O-ring 44 x 2.5 mm, 1.75 mm filament pins).
Z=0 is the can-well floor level minus 4; the trunk top (hinge collar) is at Z0.
"""
import sys
import numpy as np
from meshkit import Mesh, slab, props, write_stl, revolve, box, hinge_cyl
import make_palm as mp
from make_palm import lathe, arr, rot_cw, FLOOR, LEDGE, BORE_UP, BORE_LOW, WALL, N, PX, PZ, CAN_R
Z0 = mp.PAD_H                      # trunk top (hinge collar base)
R_B, R_PIPE = 18.4, 20.0           # hatch pipe bore / outer radius
R_TR = 50.0                        # trunk outer radius
SHOT_RHO, SHOT_PACK = 7.85e-3, 0.60
PLASTIC, WATER, CAN_G, CAN_COG = 1.27e-3, 1.0e-3, 380.0, 55.0
FREEBOARD = 45.0                   # waterline at least this far below the trunk top


R_F, RIM = 95.0, 14.0              # float ring: outer radius, flat rim height (45 deg underside)
CN = R_F - R_TR


def rings(z_hi, z_lo):
    """Palm-trunk ring bumps (triangular, print without supports) between two heights, descending."""
    pts = []; z = z_hi
    while z - 8.5 > z_lo:
        pts += [(R_TR, z - 2.5), (R_TR + 1.6, z - 4.5), (R_TR, z - 6.5)]
        z -= 8.0
    return pts


def profiles(Hc, Rk, hk, zr):
    """zr = z of the ring's rim bottom; waterline sits in the rim."""
    zt = Z0 - Hc; zb = zt - hk
    xin = lambda z: Rk - 12 * (z - (zb + 8)) / (zt - zb - 8) - 2.0
    ch = [(0, zb + WALL), (Rk - 2.0, zb + WALL), (Rk - 2.0, zb + 8), (xin(zt - WALL), zt - WALL), (R_B, zt - WALL)]
    outer = ([(R_B, FLOOR), (BORE_LOW, FLOOR), (BORE_LOW, LEDGE), (BORE_UP, LEDGE), (BORE_UP, Z0), (R_TR, Z0)] + rings(Z0 - 6, zr + RIM + 2) + [
              (R_TR, zr + RIM), (R_F, zr + RIM), (R_F, zr), (R_TR, zr - CN)] + rings(zr - CN - 4, zt + 4) + [
              (R_TR, zt), (Rk - 12, zt), (Rk, zb + 8), (Rk, zb), (0, zb)] + ch)
    cav = [(R_PIPE, zt), (R_TR - WALL, zt), (R_TR - WALL, zr - CN + 0.66), (R_F - WALL, zr + 0.66), (R_F - WALL, zr + RIM - WALL),
           (R_TR - WALL, zr + RIM - WALL), (R_TR - WALL, Z0 - WALL), (42.2, Z0 - WALL), (42.2, FLOOR - WALL), (R_PIPE, FLOOR - WALL)]
    void = ch + [(R_B, FLOOR), (0, FLOOR)]
    return zt, zb, outer, cav, void


def _eval(Hc, Rk, hk, ballast_g, parts_extra, zr, seg):
    zt, zb, outer, cav, void = profiles(Hc, Rk, hk, zr)
    hull, cv, vd = lathe(outer, seg), lathe(cav, seg), lathe(void, seg)
    vh, mh = props(hull.array().astype(float)); vc, mc = props(cv.array().astype(float))
    vv, _ = props(vd.array().astype(float))
    ex_mass, ex_zm = parts_extra
    m_plastic = (vh - vc) * PLASTIC + ex_mass
    zc = ((mh - mc) * PLASTIC + ex_zm) / m_plastic
    fill_v = ballast_g / (SHOT_RHO * SHOT_PACK)
    h_fill = fill_v / (np.pi * (Rk - 2.0) ** 2)
    z_bal = zb + WALL + h_fill / 2
    M = m_plastic + ballast_g + CAN_G
    zz = np.linspace(zb, Z0, 8001)
    phi = np.linspace(0, 2 * np.pi, 720, endpoint=False); asc = np.mean(mp.g(phi) ** 2)
    r = np.interp(zz, [zb, zb + 8, zt, zt + 1e-3, zr - CN, zr, zr + RIM, zr + RIM + 1e-3, Z0],
                  [Rk, Rk, Rk - 12, R_TR, R_TR, R_F, R_F, R_TR, R_TR])
    area = np.pi * r ** 2 * np.where((zz < zt) | ((zz > zr - CN) & (zz < zr + RIM)), asc, 1.0)
    seg_v = (area[1:] + area[:-1]) / 2 * np.diff(zz)
    cumV = np.concatenate([[0], np.cumsum(seg_v)]); cumM = np.concatenate([[0], np.cumsum(seg_v * (zz[1:] + zz[:-1]) / 2)])
    if M / WATER >= cumV[-1]:
        return None
    zw = float(np.interp(M / WATER, cumV, zz))
    KB = float(np.interp(zw, zz, cumM) / np.interp(zw, zz, cumV))
    I = np.pi * float(np.interp(zw, zz, r)) ** 4 / 4 * asc ** 2
    KG = (m_plastic * zc + ballast_g * z_bal + CAN_G * (FLOOR + CAN_COG)) / M
    GM = KB + I / (M / WATER) - KG
    return dict(zw=zw, GM=GM, M=M, m_plastic=m_plastic, zb=zb, zt=zt, vv=vv, fill_v=fill_v, KB=KB, KG=KG,
                hull=hull, cav=cv, void=vd, h_fill=h_fill, total_h=Z0 - zb)


def evaluate(Hc, Rk, hk, ballast_g, parts_extra, seg=48):
    """Place the float ring so the waterline sits at the middle of its flat rim (fixed-point iteration)."""
    zr = Z0 - 70.0
    for _ in range(8):
        r = _eval(Hc, Rk, hk, ballast_g, parts_extra, zr, seg)
        if r is None:
            return dict(ok=False, why="sinks (needs taller trunk)")
        zr = r["zw"] - RIM / 2
    r["zr"] = zr; r["fb"] = Z0 - r["zw"]
    r["cap_ok"] = r["fill_v"] <= 0.85 * r["vv"]
    r["ring_clear"] = (zr - CN) - r["zt"]          # ring cone bottom above keel top
    r["ok"] = r["cap_ok"] and r["GM"] > 20 and r["fb"] >= FREEBOARD and r["ring_clear"] >= 10
    return r


def extras():
    """Plastic that isn't in the revolve hull: collar sectors, lugs, 9 fronds (closed), hatch cap."""
    curl = mp.tuned_curl()
    sect, lugs = mp.collar_sectors(), mp.hinge_lugs()
    fr = arr(mp.frond_parts(curl))
    cap = cap_parts()
    m = zm = 0.0
    for a in [arr([s]) for s in sect + lugs] + [fr] * N + [arr(cap)]:
        v, mo = props(a.astype(float)); m += v * PLASTIC; zm += mo * PLASTIC
    return curl, (m, zm), sect, lugs, fr, cap


# ---- hatch: coarse trapezoid thread, O-ring face seal
def helix_ridge(r0, depth, pitch, turns, z0, outward=True, steps=48):
    m = Mesh(); n = int(steps * turns) + 1
    th = np.linspace(0, 2 * np.pi * turns, n)
    sec = [(-0.4, -0.8), (depth, -0.3), (depth, 0.3), (-0.4, 0.8)] if outward else [(0.4, -0.8), (-depth, -0.3), (-depth, 0.3), (0.4, 0.8)]
    rings = [[np.array([(r0 + dr) * np.cos(t), (r0 + dr) * np.sin(t), z0 + pitch * t / (2 * np.pi) + dz]) for dr, dz in sec] for t in th]
    for i in range(n - 1):
        for k in range(4):
            q = (k + 1) % 4
            m.quad(rings[i][k], rings[i][q], rings[i + 1][q], rings[i + 1][k])
    for ring, flip in ((rings[0], False), (rings[-1], True)):
        a, b, c, d = ring
        (m.quad(d, c, b, a) if flip else m.quad(a, b, c, d))
    return m


def cap_parts():
    z_b = FLOOR - 13.0
    core = revolve([(0, z_b), (16.4, z_b), (16.4, FLOOR), (0, FLOOR)], seg=64)
    flange = revolve([(0, FLOOR), (21.0, FLOOR), (21.0, FLOOR + 1.6), (23.8, FLOOR + 1.6), (23.8, FLOOR), (25.0, FLOOR),
                      (25.0, FLOOR + 3.0), (0, FLOOR + 3.0)], seg=96)
    bar = box(-22, 22, -3.5, 3.5, FLOOR + 3.0, FLOOR + 6.0)
    thr = helix_ridge(16.4, 1.6, 4.0, 2.8, z_b + 0.8, True)
    return [core, flange, bar, thr]


def female_thread():
    return helix_ridge(R_B, 1.6, 4.0, 3.0, FLOOR - 13.0 + 0.2, False)


HC, RK, HK, B_NOM = 165.0, 55.0, 26.0, 800.0


def main():
    import os
    curl, ex, sect, lugs, fr, cap = extras()
    delta = mp.checks(curl)
    r = evaluate(HC, RK, HK, B_NOM, ex, seg=120)
    assert r.get("ok", False), r
    hull, cav = r["hull"], r["cav"]
    thr_f = female_thread()
    base_solids = [hull] + sect + lugs + [thr_f]
    cav_in = cav.array()[:, ::-1]
    write_stl(np.concatenate([arr([m]) for m in base_solids] + [cav_in]), "palm_spar_base.stl", b"palm spar base")
    # hatch cap: print flange-down is awkward; flip so the grip bar is on the bed and the thread points up
    capa = arr(cap) @ np.diag([1, -1, -1]).astype(np.float32)
    capa[:, :, 2] -= capa[:, :, 2].min()
    write_stl(capa, "palm_hatch_cap.stl", b"hatch cap")
    fr_closed = fr; fr_rest = rot_cw(fr_closed, delta)
    R = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)
    fp = (fr_rest - np.array([PX, 0, PZ])) @ R.T; fp[..., 2] -= fp[..., 2].min()
    write_stl(fp, "palm_frond.stl", b"palm frond x9")
    for f in ("palm_island_base.stl",):
        if os.path.exists(f): os.remove(f)
    # ---- report
    print(f"\nSpar: {r['total_h']:.0f} mm from keel bottom to trunk top (+ about 80 mm of frond above that); keel r={RK:.0f}, float ring dia {2*R_F:.0f}")
    cap_g = 0.85 * r["vv"] * SHOT_RHO * SHOT_PACK
    print(f"Plastic {r['m_plastic']:.0f} g. Ballast chamber {r['vv']/1000:.0f} cm3 -> holds up to ~{cap_g:.0f} g of steel shot")
    print(f"With can {CAN_G:.0f} g + {B_NOM:.0f} g shot: waterline {r['fb']:.0f} mm below the trunk top, {r['zw'] - r['zb']:.0f} mm draft, GM {r['GM']:.0f} mm")
    print("Ballast range (waterline below trunk top / stability):")
    for B in (500, 650, 800, 950, 1100):
        q = evaluate(HC, RK, HK, B, ex, seg=48)
        print(f"  {B:5d} g shot: " + (q["why"] if "why" in q else f"freeboard {q['fb']:.0f} mm, GM {q['GM']:.0f} mm {'OK' if q['ok'] else '(outside target)'}"))
    r0 = _eval(HC, RK, HK, 0.0, ex, r["zr"], 48)
    # preview data
    rz = lambda a, k: a @ np.array([[np.cos(2*np.pi*k/N), np.sin(2*np.pi*k/N), 0], [-np.sin(2*np.pi*k/N), np.cos(2*np.pi*k/N), 0], [0, 0, 1]])
    np.save("/tmp/s_base.npy", np.concatenate([arr([m]) for m in [hull] + sect + lugs]))
    np.save("/tmp/s_closed.npy", np.concatenate([rz(fr_closed, k) for k in range(N)]))
    np.save("/tmp/s_rest.npy", np.concatenate([rz(fr_rest, k) for k in range(N)]))
    np.save("/tmp/s_water.npy", np.array([r["zw"]]))


if __name__ == "__main__":
    main()
