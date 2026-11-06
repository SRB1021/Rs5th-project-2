"""Small triangle-mesh toolkit shared by the palm holder and coconut lid generators (units: mm)."""
import numpy as np


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
        """Triangles as float32 (n,3,3), flipped if needed so normals point outward."""
        a = np.array(self.t, np.float32)
        return a[:, ::-1] if self.volume() < 0 else a


def props(arr):
    """Volume and z-moment (sum tet volume * tet centroid z) of a closed oriented mesh."""
    arr = np.asarray(arr, float)
    v = np.einsum("ij,ij->i", arr[:, 0], np.cross(arr[:, 1], arr[:, 2])) / 6
    return v.sum(), (v * arr[:, :, 2].sum(1) / 4).sum()


def write_stl(arr, path, header=b"palm"):
    arr = np.asarray(arr, np.float32)
    nrm = np.cross(arr[:, 1] - arr[:, 0], arr[:, 2] - arr[:, 0])
    ln = np.linalg.norm(nrm, axis=1, keepdims=True); ln[ln == 0] = 1
    rec = np.zeros(len(arr), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = nrm / ln, arr
    with open(path, "wb") as f:
        f.write(header.ljust(80, b" ")[:80]); f.write(np.uint32(len(arr)).tobytes()); f.write(rec.tobytes())
    mn, mx = arr.reshape(-1, 3).min(0), arr.reshape(-1, 3).max(0)
    print(f"{path}: {len(arr)} tris, bbox {np.round(mx - mn, 1)} mm")


def revolve(profile, seg=72):
    """Full revolve of a closed (r,z) loop about z (orientation fixed by volume sign)."""
    m = Mesh()
    ang = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    P = lambda r, z, t: np.array([r * np.cos(t), r * np.sin(t), z])
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


def earclip(poly):
    """Triangulate a simple CCW polygon; returns index triples."""
    idx = list(range(len(poly))); out = []
    cr = lambda a, b, c: (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
    inside = lambda p, a, b, c: cr(a, b, p) >= 0 and cr(b, c, p) >= 0 and cr(c, a, p) >= 0
    while len(idx) > 3:
        for k in range(len(idx)):
            i0, i1, i2 = idx[k-1], idx[k], idx[(k+1) % len(idx)]
            a, b, c = poly[i0], poly[i1], poly[i2]
            if cr(a, b, c) <= 0 or any(inside(poly[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            out.append((i0, i1, i2)); idx.pop(k); break
        else:
            raise RuntimeError("earclip failed")
    out.append(tuple(idx))
    return out


def sector(profile, a0, a1, seg=8):
    """Closed solid: (r,z) profile revolved over [a0,a1] with end caps."""
    pr = [tuple(p) for p in profile]
    if sum(pr[i][0]*pr[(i+1) % len(pr)][1] - pr[(i+1) % len(pr)][0]*pr[i][1] for i in range(len(pr))) < 0:
        pr.reverse()
    m = Mesh()
    ang = np.linspace(a0, a1, seg + 1)
    P = lambda r, z, t: np.array([r*np.cos(t), r*np.sin(t), z])
    for i in range(len(pr)):
        (r0, z0), (r1, z1) = pr[i], pr[(i+1) % len(pr)]
        for j in range(seg):
            m.quad(P(r0, z0, ang[j]), P(r0, z0, ang[j+1]), P(r1, z1, ang[j+1]), P(r1, z1, ang[j]))
    for (i, j, k) in earclip(pr):
        m.tri(P(*pr[i], a0), P(*pr[j], a0), P(*pr[k], a0))
        m.tri(P(*pr[k], a1), P(*pr[j], a1), P(*pr[i], a1))
    return m


def box(x0, x1, y0, y1, z0, z1):
    m = Mesh()
    c = [np.array([x, y, z], float) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    for q in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        m.quad(*[c[i] for i in q])
    return m


def sphere(c, r, nu=14, nv=8):
    m = Mesh()
    P = lambda u, t: np.asarray(c, float) + r*np.array([np.sin(t)*np.cos(u), np.sin(t)*np.sin(u), np.cos(t)])
    for i in range(nu):
        for j in range(nv):
            u0, u1 = 2*np.pi*i/nu, 2*np.pi*(i+1)/nu; t0, t1 = np.pi*j/nv, np.pi*(j+1)/nv
            a, b, c2, d = P(u0, t0), P(u1, t0), P(u1, t1), P(u0, t1)
            m.tri(a, c2, d) if j == 0 else (m.tri(a, b, c2) if j == nv-1 else m.quad(a, b, c2, d))
    return m


def xform(m, R, t):
    out = Mesh(); R = np.asarray(R, float); t = np.asarray(t, float)
    out.t = [tuple(R @ np.asarray(p) + t for p in tri) for tri in m.t]
    return out


def hinge_cyl(cx, cz, y0, y1, r_out, r_hole, seg=24):
    """Hollow cylinder with axis along +y through (cx, *, cz), spanning y0..y1."""
    lug = revolve([(r_hole, 0), (r_out, 0), (r_out, y1 - y0), (r_hole, y1 - y0)], seg=seg)
    return xform(lug, [[1, 0, 0], [0, 0, 1], [0, -1, 0]], [cx, y0, cz])   # local z -> +y


def slab(pos, half_w, thick, tan):
    """Closed ribbon along a polyline: width along `tan`, thickness normal to path and `tan`."""
    m = Mesh(); N = len(pos); pos = np.asarray(pos, float); tan = np.asarray(tan, float)
    L, R, T = [], [], []
    for i in range(N):
        d = pos[min(i + 1, N - 1)] - pos[max(i - 1, 0)]; d /= np.linalg.norm(d)
        n = np.cross(tan, d); n /= np.linalg.norm(n)
        L.append(pos[i] + tan * half_w[i]); R.append(pos[i] - tan * half_w[i]); T.append(n * thick / 2)
    for i in range(N - 1):
        m.quad(L[i] + T[i], L[i+1] + T[i+1], R[i+1] + T[i+1], R[i] + T[i])
        m.quad(R[i] - T[i], R[i+1] - T[i+1], L[i+1] - T[i+1], L[i] - T[i])
        m.quad(L[i] - T[i], L[i+1] - T[i+1], L[i+1] + T[i+1], L[i] + T[i])
        m.quad(R[i] + T[i], R[i+1] + T[i+1], R[i+1] - T[i+1], R[i] - T[i])
    m.quad(L[0] + T[0], R[0] + T[0], R[0] - T[0], L[0] - T[0])
    m.quad(R[-1] - T[-1], R[-1] + T[-1], L[-1] + T[-1], L[-1] - T[-1])
    return m


def tube(pos, radii, sides=8):
    m = Mesh(); N = len(pos); pos = np.asarray(pos, float); rings = []
    for i, p in enumerate(pos):
        d = pos[min(i + 1, N - 1)] - pos[max(i - 1, 0)]; d /= np.linalg.norm(d)
        ref = np.array([0, 0, 1.0]) if abs(d[2]) < .9 else np.array([1.0, 0, 0])
        n = np.cross(d, ref); n /= np.linalg.norm(n); b = np.cross(d, n)
        rings.append([p + radii[i] * (np.cos(a) * n + np.sin(a) * b) for a in np.linspace(0, 2*np.pi, sides, endpoint=False)])
    for i in range(N - 1):
        for j in range(sides):
            k = (j + 1) % sides
            m.quad(rings[i][j], rings[i][k], rings[i+1][k], rings[i+1][j])
    for ring, c in ((rings[0], pos[0]), (rings[-1], pos[-1])):
        for j in range(sides):
            m.tri(c, ring[j], ring[(j + 1) % sides])
    return m
