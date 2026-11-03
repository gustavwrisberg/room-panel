"""Build a 3D scene (GLB) of the room panel PCB with the C4002 radar and the
Waveshare 2.9" display, straight from the KiCad board file.

Coordinates: X right, Y up (= -KiCad y), Z out of the board top. mm.
"""
import json, math, re, sys
import numpy as np, sexpdata, trimesh
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely import affinity
sys.path.insert(0, "."); import stepcolor

PCB = sys.argv[1]; K3D = sys.argv[2]; EASY = sys.argv[3]; OUT = sys.argv[4]
T = 1.6                      # board thickness
S = lambda x: str(x)

data = sexpdata.loads(open(PCB, encoding="utf-8").read())
def items(node, name): return [n for n in node if isinstance(n, list) and n and S(n[0]) == name]
def one(node, name):
    r = items(node, name); return r[0] if r else None
def xy(n): return float(n[1]), float(n[2])

meshes = []   # (trimesh, rgba, metal, rough, name)
def add(m, rgb, metal=0.0, rough=0.6, name=""):
    meshes.append((m, rgb, metal, rough, name))

def extrude(geom, z0, h):
    out = []
    geoms = getattr(geom, "geoms", [geom])
    for g in geoms:
        if g.is_empty or g.area < 1e-6: continue
        m = trimesh.creation.extrude_polygon(g, h); m.apply_translation((0, 0, z0)); out.append(m)
    return trimesh.util.concatenate(out) if out else None

# ------------------------------------------------------------------ board
edge = None
for r in items(data, "gr_rect"):
    if S(one(r, "layer")[1]) == "Edge.Cuts":
        (x0, y0), (x1, y1) = xy(one(r, "start")), xy(one(r, "end")); edge = box(x0, -y1, x1, -y0)
BX0, BY0, BX1, BY1 = x0, y0, x1, y1

holes, pads, silk = [], [], []
def fp_tf(fpat):
    fx, fy = float(fpat[1]), float(fpat[2]); rot = float(fpat[3]) if len(fpat) > 3 else 0.0
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    def f(lx, ly):                     # footprint-local KiCad (y down) -> 3D
        X, Y = lx, -ly
        return (fx + X * c - Y * s, -fy + X * s + Y * c)
    return f, rot, (fx, fy)

footprints = []
for fp in items(data, "footprint"):
    fid = S(fp[1]); layer = S(one(fp, "layer")[1])
    f, rot, pos = fp_tf(one(fp, "at"))
    ref = next(S(p[2]) for p in items(fp, "property") if S(p[1]) == "Reference")
    footprints.append((ref, fid, f, rot, pos, fp))
    for pad in items(fp, "pad"):
        kind, shape = S(pad[2]), S(pad[3])
        at = one(pad, "at"); px, py = float(at[1]), float(at[2]); pa = float(at[3]) if len(at) > 3 else 0.0
        w, h = float(one(pad, "size")[1]), float(one(pad, "size")[2])
        lays = [S(l) for l in one(pad, "layers")[1:]]
        if not any(l in ("F.Cu", "*.Cu") for l in lays): continue
        if shape == "circle": g = Point(0, 0).buffer(w / 2, 24)
        elif shape == "oval":
            r_ = min(w, h) / 2; g = LineString([(-(w / 2 - r_), 0), (w / 2 - r_, 0)]).buffer(r_, 16) if w >= h else LineString([(0, -(h / 2 - r_)), (0, h / 2 - r_)]).buffer(r_, 16)
        elif shape == "roundrect":
            rr = one(pad, "roundrect_rratio"); rr = float(rr[1]) * min(w, h) if rr else 0
            g = box(-w / 2 + rr, -h / 2 + rr, w / 2 - rr, h / 2 - rr).buffer(rr, 8) if rr > 0 else box(-w / 2, -h / 2, w / 2, h / 2)
        else: g = box(-w / 2, -h / 2, w / 2, h / 2)
        # pad angle in the file is absolute (includes footprint rotation)
        g = affinity.rotate(g, pa, origin=(0, 0))
        cx, cy = f(px, py); g = affinity.translate(g, cx, cy)
        dr = one(pad, "drill")
        if dr is not None and len(dr) > 1:
            d = float(dr[1]) if S(dr[1]) != "oval" else float(dr[2])
            holes.append(Point(cx, cy).buffer(d / 2, 24))
            if kind == "np_thru_hole": continue
        pads.append(g)
    # silkscreen graphics
    for kind in ("fp_line", "fp_rect", "fp_circle", "fp_arc", "fp_poly"):
        for gr in items(fp, kind):
            if S(one(gr, "layer")[1]) != "F.SilkS": continue
            st = one(gr, "stroke"); wdt = float(one(st, "width")[1]) if st else 0.12
            if kind == "fp_line": g = LineString([f(*xy(one(gr, "start"))), f(*xy(one(gr, "end")))])
            elif kind == "fp_rect":
                (a, b), (c_, d) = xy(one(gr, "start")), xy(one(gr, "end"))
                g = LineString([f(a, b), f(c_, b), f(c_, d), f(a, d), f(a, b)])
            elif kind == "fp_circle":
                c0 = f(*xy(one(gr, "center"))); e = f(*xy(one(gr, "end")))
                g = Point(c0).buffer(math.dist(c0, e), 32).exterior
            elif kind == "fp_arc":
                g = LineString([f(*xy(one(gr, k))) for k in ("start", "mid", "end")])
            else:
                g = LineString([f(*xy(p)) for p in items(one(gr, "pts"), "xy")] + [f(*xy(items(one(gr, "pts"), "xy")[0]))])
            silk.append(g.buffer(wdt / 2, 6))

copper = []
for seg in items(data, "segment"):
    if S(one(seg, "layer")[1]) != "F.Cu": continue
    a, b = xy(one(seg, "start")), xy(one(seg, "end")); w = float(one(seg, "width")[1])
    copper.append(LineString([(a[0], -a[1]), (b[0], -b[1])]).buffer(w / 2, 8))
for v in items(data, "via"):
    a = xy(one(v, "at")); copper.append(Point(a[0], -a[1]).buffer(float(one(v, "size")[1]) / 2, 16))
    holes.append(Point(a[0], -a[1]).buffer(float(one(v, "drill")[1]) / 2, 12))
for z in items(data, "zone"):
    for fpoly in items(z, "filled_polygon"):
        if S(one(fpoly, "layer")[1]) != "F.Cu": continue
        pts = [(float(p[1]), -float(p[2])) for p in items(one(fpoly, "pts"), "xy")]
        copper.append(Polygon(pts).buffer(0))

holes_u = unary_union(holes)
board = edge.buffer(0).difference(holes_u)
add(extrude(board, 0, T), (0.012, 0.14, 0.055), 0.0, 0.7, "board")
cu = unary_union(copper).difference(holes_u).intersection(edge)
add(extrude(cu, T, 0.035), (0.04, 0.25, 0.09), 0.05, 0.6, "copper")
pad_u = unary_union(pads).difference(holes_u)
add(extrude(pad_u, T, 0.06), (0.82, 0.82, 0.80), 0.9, 0.3, "pads")
silk_u = unary_union(silk).difference(pad_u.buffer(0.1)).intersection(edge)
add(extrude(silk_u, T + 0.035, 0.03), (0.95, 0.95, 0.93), 0.0, 0.7, "silk")
# plated barrel ring inside holes (dark)
add(extrude(holes_u.buffer(0.02).difference(holes_u.buffer(-0.12)), 0, T + 0.05), (0.6, 0.6, 0.58), 0.9, 0.35, "barrels")

# ------------------------------------------------------------------ STEP models
STD = {
    "R_0402_1005Metric": f"{K3D}/Resistor_SMD.3dshapes/R_0402_1005Metric.step",
    "C_0402_1005Metric": f"{K3D}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step",
    "C_0805_2012Metric": f"{K3D}/Capacitor_SMD.3dshapes/C_0805_2012Metric.step",
    "JST_PH_B8B-PH-K_1x08_P2.00mm_Vertical": f"{K3D}/Connector_JST.3dshapes/JST_PH_B8B-PH-K_1x08_P2.00mm_Vertical.step",
    "PinSocket_1x04_P2.54mm_Vertical": f"{K3D}/Connector_PinSocket_2.54mm.3dshapes/PinSocket_1x04_P2.54mm_Vertical.step",
    "C4002": f"{K3D}/Connector_PinSocket_2.54mm.3dshapes/PinSocket_1x05_P2.54mm_Horizontal.step",
}
RECENTER = {"SW-SMD_BMQ22-N1A1-2012-A": (24.38, 59.08, 1.65)}   # STEP origin differs from the .wrl
cache = {}
def model_chunks(path):
    if path not in cache: cache[path] = stepcolor.load(path)
    return cache[path]

def Rxyz(rx, ry, rz):
    rx, ry, rz = map(math.radians, (rx, ry, rz))
    X = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
    Y = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
    Z = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
    return Z @ Y @ X

SKIP = {"J2", "J4"}          # J2 not populated; SCD41 wires are soldered straight into J4
BOTTOM = {"J3"}              # fitted on the back of the board (no room under the front panel)
by_col = {}
for ref, fid, f, rot, pos, fp in footprints:
    if ref in SKIP: continue
    name = fid.split(":")[1]
    for mdl in items(fp, "model"):
        mp = S(mdl[1]); base = mp.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        path = STD.get(name) if "KICAD10_3DMODEL_DIR" in mp else f"{EASY}/{base}.step"
        if not path: continue
        off = [float(v) for v in one(one(mdl, "offset"), "xyz")[1:]]
        rr = [float(v) for v in one(one(mdl, "rotate"), "xyz")[1:]]
        R_m = Rxyz(-rr[0], -rr[1], -rr[2])
        R_f = Rxyz(0, 0, rot)
        rc = np.array(RECENTER.get(name, (0, 0, 0)))
        for v, idx, col in model_chunks(path):
            p = (v - rc) @ R_m.T + np.array(off)
            zb = T
            if ref in BOTTOM:          # flip about the pin row (local x axis) onto the back side
                p = p * np.array([1, -1, -1]); zb = 0.0
            p = p @ R_f.T + np.array([pos[0], -pos[1], zb])
            by_col.setdefault(tuple(round(c, 3) for c in col), []).append(trimesh.Trimesh(p, idx, process=False))
for col, ms in by_col.items():
    m = trimesh.util.concatenate(ms)
    metal = 0.85 if (min(col) > 0.5 and max(col) - min(col) < 0.25) else 0.0
    add(m, col, metal, 0.35 if metal else 0.55, "model")

def bx(x0, y0, z0, x1, y1, z1):
    m = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0)); m.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)); return m
def rbx(x0, y0, z0, x1, y1, z1, r):
    g = box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, 8); return extrude(g, z0, z1 - z0)

# ------------------------------------------------------------------ XIAO ESP32-C6 (simplified)
ref, fid, f, rot, pos, fp = next(x for x in footprints if x[0] == "U2")
def xl(x0, y0, x1, y1):      # footprint-local rect (KiCad y down) -> 3D polygon
    return Polygon([f(x0, y0), f(x1, y0), f(x1, y1), f(x0, y1)])
xb = extrude(xl(0, -21.0, 17.8, 0).buffer(0.6, 8).buffer(-0.6, 8), T + 0.06, 1.0)
add(xb, (0.10, 0.12, 0.16), 0, 0.5, "xiao_pcb")
cast = unary_union([Point(f(xx, yy)).buffer(0.8, 16) for xx in (0, 17.8) for yy in np.arange(-18.12, -2.0, 2.54)])
add(extrude(cast.intersection(xl(0, -21, 17.8, 0)), T + 0.06, 1.0), (0.85, 0.7, 0.35), 0.9, 0.3, "xiao_castell")
add(extrude(xl(3.4, -14.6, 14.4, -3.2), T + 1.06, 2.0), (0.62, 0.62, 0.62), 0.8, 0.45, "xiao_can")
usb = xl(4.43, -22.55, 13.37, -15.2).buffer(0.3, 8).buffer(-0.3, 8)
add(extrude(usb, T + 1.06, 3.2), (0.60, 0.60, 0.62), 0.85, 0.35, "xiao_usb")
add(extrude(xl(6.4, -22.6, 11.4, -22.4), T + 2.0, 1.2), (0.05, 0.05, 0.05), 0, 0.5, "xiao_usb_hole")
for (a, b) in ((2.0, -20.5), (14.0, -20.5)):
    add(extrude(xl(a, b, a + 2.6, b + 1.6), T + 1.06, 0.6), (0.85, 0.85, 0.85), 0.6, 0.4, "xiao_btn")
add(extrude(xl(5.0, -2.6, 12.8, -0.8), T + 1.06, 0.8), (0.92, 0.92, 0.88), 0, 0.5, "xiao_ant")

# ------------------------------------------------------------------ C4002 radar module (simplified)
ref, fid, f, rot, pos, fp = next(x for x in footprints if x[0] == "J1")
R = Polygon([f(-23, -5.5), f(3, -5.5), f(3, 16.5), f(-23, 16.5)])
rx0, ry0, rx1, ry1 = R.bounds
rz = T + 2.6
add(extrude(box(*R.bounds).buffer(0.0), rz, 1.0), (0.03, 0.10, 0.30), 0, 0.75, "radar_pcb")
ant = []
for i in range(2):
    for j in range(3):
        ant.append(box(rx0 + 3.0 + i * 5.5, ry1 - 5.0 - j * 4.2, rx0 + 6.2 + i * 5.5, ry1 - 2.0 - j * 4.2))
for j in range(3):
    ant.append(box(rx1 - 9.0, ry1 - 5.0 - j * 4.2, rx1 - 5.8, ry1 - 2.0 - j * 4.2))
feeds = [LineString([((a.bounds[0] + a.bounds[2]) / 2, a.bounds[1]), ((a.bounds[0] + a.bounds[2]) / 2, a.bounds[1] - 1.2)]).buffer(0.15) for a in ant]
add(extrude(unary_union(ant + feeds), rz + 1.0, 0.04), (0.72, 0.48, 0.14), 0.7, 0.4, "radar_ant")
add(extrude(box(rx0 + 4, ry0 + 3.0, rx0 + 9, ry0 + 8.0), rz + 1.0, 0.9), (0.08, 0.08, 0.08), 0, 0.45, "radar_ic")
add(extrude(box(rx0 + 12, ry0 + 3.5, rx0 + 15, ry0 + 6.0), rz + 1.0, 0.7), (0.08, 0.08, 0.08), 0, 0.45, "radar_ic2")
for k in range(5):           # header pins down into the socket
    px, py = f(0, k * 2.54)
    add(bx(px - 0.32, py - 0.32, T + 0.4, px + 0.32, py + 0.32, rz), (0.85, 0.7, 0.35), 0.9, 0.3, "radar_pins")

# ------------------------------------------------------------------ Waveshare 2.9" e-Paper module (simplified)
DX0 = BX1 + 4.0; DW, DH = 89.5, 38.0
cy = -(BY0 + BY1) / 2
DY0 = cy - DH / 2
dz0 = T + 8.0 - 1.2 - 1.6           # glass front flush with the case front (8 mm above the PCB)
add(rbx(DX0, DY0, dz0, DX0 + DW, DY0 + DH, dz0 + 1.6, 1.0), (0.06, 0.06, 0.07), 0, 0.5, "disp_pcb")
for (hx, hy) in ((2.5, 2.5), (DW - 2.5, 2.5), (2.5, DH - 2.5), (DW - 2.5, DH - 2.5)):
    add(extrude(Point(DX0 + hx, DY0 + hy).buffer(1.5, 24).difference(Point(DX0 + hx, DY0 + hy).buffer(1.0, 24)), dz0 + 1.6, 0.03), (0.86, 0.62, 0.22), 0.6, 0.35, "disp_holes")
    add(extrude(Point(DX0 + hx, DY0 + hy).buffer(1.0, 24), dz0 + 1.6, 0.031), (0.02, 0.02, 0.02), 0, 0.9, "disp_holes_d")
GX0 = DX0 + 5.25; GW, GH = 79.0, 36.7; GY0 = cy - GH / 2
gz = dz0 + 1.6
add(bx(GX0, GY0, gz, GX0 + GW, GY0 + GH, gz + 1.15), (0.80, 0.80, 0.78), 0.0, 0.35, "glass")
# FPC fold at the left end
add(bx(GX0 - 1.2, cy - 7, gz - 0.3, GX0 + 0.2, cy + 7, gz + 0.9), (0.80, 0.50, 0.15), 0.2, 0.5, "fpc")
AW, AH = 66.9, 29.1; AX0 = DX0 + DW / 2 - AW / 2; AY0 = cy - AH / 2   # centred, as VIEW_OFFSET_X = 0 in the case. CHECK
# connector on the back of the display
add(bx(DX0 + 3.0, cy - 8.5, dz0 - 4.5, DX0 + 7.5, cy + 8.5, dz0), (0.93, 0.90, 0.82), 0, 0.6, "disp_conn")

# ------------------------------------------------------------------ JST PH plug in J3
ref, fid, f, rot, pos, fp = next(x for x in footprints if x[0] == "J3")
pins = [f(i * 2.0, 0) for i in range(8)]
xs, ys = [p[0] for p in pins], [p[1] for p in pins]
add(bx(min(xs) - 1.4, min(ys) - 1.95, -7.0, max(xs) + 1.4, max(ys) + 1.95, -1.6), (0.94, 0.92, 0.85), 0, 0.6, "ph_plug")
ref, fid, f, rot, pos, fp = next(x for x in footprints if x[0] == "J4")
j4 = [f(0, k * 2.54) for k in range(4)]

scene = trimesh.Scene()
for i, (m, rgb, metal, rough, name) in enumerate(meshes):
    if m is None: continue
    mat = trimesh.visual.material.PBRMaterial(baseColorFactor=[*(float(c) ** 2.2 for c in rgb), 1.0], metallicFactor=metal, roughnessFactor=rough, name=f"{name}_{i}")
    m.visual = trimesh.visual.TextureVisuals(material=mat)
    scene.add_geometry(m, node_name=f"{name}_{i}", geom_name=f"{name}_{i}")
scene.export(OUT + "/scene.glb")
json.dump({
    "board": [BX0, -BY1, BX1, -BY0, T],
    "active": [AX0, AY0, AX0 + AW, AY0 + AH, gz + 1.16],
    "wires_from": [[p[0], p[1], -7.0] for p in pins],
    "j4": [[p[0], p[1], 0.0] for p in j4],
    "scd": [(DX0 - 69.2) + 103.75, cy + 0.2, -9.4],
    "wires_to": [[DX0 + 3.0, cy - 7.0 + 2.0 * i, dz0 - 2.2] for i in range(8)],
    "radar": [rx0, ry0, rx1, ry1, rz + 1.0],
}, open(OUT + "/scene.json", "w"))
print("meshes", len(meshes), "bounds", scene.bounds)
