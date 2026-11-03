"""
Parametric case for the Universal Room Board (room-panel role).

Layout (front view): 37 x 54 mm PCB on the left with the knob and four buttons
in a column, landscape Waveshare 2.9" e-paper module on the right, CO2
breakout behind the display, XIAO at the bottom left with USB-C exiting down.

Run:  python3 room_panel_case.py        -> writes STL + STEP files to ./out
Needs: pip install cadquery

All front-view coordinates below are in mm, measured from the TOP-LEFT corner
of the case as seen from the front (x to the right, y downwards). They are
converted to CadQuery coordinates with fx()/fy().

Values marked CHECK are estimates; measure your real parts / KiCad board
(File > Export > STEP) and adjust before printing.
"""
from pathlib import Path
import cadquery as cq

# ----------------------------------------------------------------- case
W, H = 145.0, 70.0          # outer size, front view
R = 8.0                     # corner radius
WALL = 2.0                  # side wall
FRONT = 2.0                 # front panel thickness
INNER_DEPTH = 19.0          # inside depth, front panel to back plate
BACK = 3.0                  # back plate thickness
LIP = 2.0                   # back plate alignment lip height
CLR = 0.3                   # fit clearance

SHELL_H = FRONT + INNER_DEPTH

# ----------------------------------------------------------------- PCB
PCB_X, PCB_Y = 8.0, 8.0     # PCB top-left corner (front view)
PCB_W, PCB_H = 37.0, 54.0
PCB_T = 1.6
PCB_GAP = 8.0               # inner face of front panel -> PCB top (component) side. CHECK

# Positions relative to the PCB top-left corner (front view). CHECK in KiCad.
KNOB = (26.3, 3.2)
BUTTONS = [(26.3, 14.9), (26.3, 26.2), (26.3, 38.3), (26.3, 50.0)]
RADAR = (0.5, 7.8, 22.3, 32.1)      # x0, y0, x1, y1 of the C4002 module footprint
LIGHT = (33.5, 41.0)                # BH1750
SHT40 = (33.5, 49.0)
USB_X = 14.9                        # XIAO USB-C centre, x
SWITCH_H = 1.5                      # TS-1187A height above PCB

# ----------------------------------------------------------------- display
DISP_W, DISP_H = 89.5, 38.0         # Waveshare 2.9" module outline
DISP_X = PCB_X + PCB_W + 4.0        # module left edge
DISP_Y = (H - DISP_H) / 2           # vertically centred
VIEW_W, VIEW_H = 66.9, 29.1         # active area
VIEW_OFFSET_X = 0.0                 # active area offset from module centre. CHECK Waveshare drawing
DISP_LOCATOR_H = 4.0

# ----------------------------------------------------------------- helpers
def fx(x):  # front-view x -> model x (front panel is printed face-down on z=0)
    return W - x

def fy(y):
    return H - y

def rbox(w, h, d, r):
    b = cq.Workplane("XY").box(w, h, d, centered=(True, True, False))
    return b.edges("|Z").fillet(r) if r > 0 else b

def at(shape, x, y, z=0.0):
    """place a centred shape at front-view (x, y) and model z"""
    return shape.translate((fx(x), fy(y), z))

def cyl(d, h):
    return cq.Workplane("XY").circle(d / 2).extrude(h)


# ================================================================= front shell
def front_shell():
    outer = at(rbox(W, H, SHELL_H, R), W / 2, H / 2)
    inner = at(rbox(W - 2 * WALL, H - 2 * WALL, SHELL_H, R - WALL), W / 2, H / 2, FRONT)
    shell = outer.cut(inner)

    px = lambda x: PCB_X + x
    py = lambda y: PCB_Y + y

    # display window, small chamfer-free rounded opening
    vcx = DISP_X + DISP_W / 2 + VIEW_OFFSET_X
    vcy = DISP_Y + DISP_H / 2
    shell = shell.cut(at(rbox(VIEW_W + 0.6, VIEW_H + 0.6, FRONT, 1.0), vcx, vcy))

    # display locators: four L-shaped corners around the module outline
    c = 0.4
    for sx in (0, 1):
        for sy in (0, 1):
            x0 = DISP_X - c - 1.5 if sx == 0 else DISP_X + DISP_W + c
            y0 = DISP_Y - c - 1.5 if sy == 0 else DISP_Y + DISP_H + c
            leg = 8.0
            hx = x0 if sx == 0 else x0 + 1.5 - leg
            vy = y0 if sy == 0 else y0 + 1.5 - leg
            a = at(cq.Workplane("XY").box(leg, 1.5, DISP_LOCATOR_H, centered=False).translate((-leg / 2, -0.75, 0)),
                   hx + leg / 2, y0 + 0.75, FRONT)
            b = at(cq.Workplane("XY").box(1.5, leg, DISP_LOCATOR_H, centered=False).translate((-0.75, -leg / 2, 0)),
                   x0 + 0.75, vy + leg / 2, FRONT)
            shell = shell.union(a).union(b)

    # knob shaft hole and button holes
    shell = shell.cut(at(cyl(7.5, FRONT), px(KNOB[0]), py(KNOB[1])))
    for bx, by in BUTTONS:
        shell = shell.cut(at(cyl(8.4, FRONT), px(bx), py(by)))

    # radar window: thin the front panel to 1.0 mm from the inside
    rx0, ry0, rx1, ry1 = RADAR
    shell = shell.cut(at(rbox(rx1 - rx0, ry1 - ry0, FRONT - 1.0, 1.0),
                         px((rx0 + rx1) / 2), py((ry0 + ry1) / 2), 1.0))

    # light sensor hole
    shell = shell.cut(at(cyl(3.0, FRONT), px(LIGHT[0]), py(LIGHT[1])))

    # PCB locating corners: L guides outside the board edge + 1.2 mm shelves under each corner
    gh = PCB_GAP + PCB_T + 1.0
    for cx in (0, 1):
        for cy in (0, 1):
            x = PCB_X if cx == 0 else PCB_X + PCB_W
            y = PCB_Y if cy == 0 else PCB_Y + PCB_H
            dx = -1 if cx == 0 else 1
            dy = -1 if cy == 0 else 1
            # guide walls (outside board outline)
            g1 = at(cq.Workplane("XY").box(6, 1.2, gh, centered=(True, True, False)),
                    x - dx * 3, y + dy * (CLR + 0.6), FRONT)
            g2 = at(cq.Workplane("XY").box(1.2, 6, gh, centered=(True, True, False)),
                    x + dx * (CLR + 0.6), y - dy * 3, FRONT)
            # shelf under the corner (1.2 x 1.2 mm of board)
            s = at(cq.Workplane("XY").box(2.2, 2.2, PCB_GAP, centered=(True, True, False)),
                   x - dx * 0.2, y - dy * 0.2, FRONT)
            shell = shell.union(g1).union(g2).union(s)

    # screw bosses for the back plate
    for bx, by in ((5, 5), (W - 5, 5), (5, H - 5), (W - 5, H - 5)):
        boss = at(cyl(5.5, SHELL_H - FRONT), bx, by, FRONT).cut(
            at(cyl(2.2, SHELL_H - FRONT), bx, by, FRONT))
        shell = shell.union(boss)

    # USB-C slot in the bottom wall (XIAO on the PCB top side, facing the front)
    usb_z = FRONT + PCB_GAP - 3.0
    slot = cq.Workplane("XY").box(12.0, WALL * 3, 7.0).translate((fx(px(USB_X)), fy(H - WALL / 2), usb_z))
    shell = shell.cut(slot)

    # vents: top and bottom walls behind the display (CO2), bottom wall under the SHT40
    def wall_slots(x_from, x_to, y_wall, z0, z1, pitch=4.0, w=2.0):
        nonlocal shell
        x = x_from
        while x <= x_to:
            s = cq.Workplane("XY").box(w, WALL * 3, z1 - z0).translate((fx(x), fy(y_wall), (z0 + z1) / 2))
            shell = shell.cut(s)
            x += pitch

    behind_disp_z = (FRONT + 10.0, SHELL_H - 2.0)
    wall_slots(DISP_X + 12, DISP_X + DISP_W - 12, WALL / 2, *behind_disp_z)
    wall_slots(DISP_X + 12, DISP_X + DISP_W - 12, H - WALL / 2, *behind_disp_z)
    wall_slots(px(SHT40[0]) - 6, px(SHT40[0]) + 6, H - WALL / 2, FRONT + 3.0, FRONT + PCB_GAP + 1.0, pitch=3.0, w=1.6)

    return shell


# ================================================================= back plate
def back_plate():
    z0 = SHELL_H
    plate = at(rbox(W, H, BACK, R), W / 2, H / 2, z0)
    lip_o = at(rbox(W - 2 * WALL - 2 * CLR, H - 2 * WALL - 2 * CLR, LIP, R - WALL), W / 2, H / 2, z0 - LIP)
    lip_i = at(rbox(W - 2 * WALL - 2 * CLR - 3.0, H - 2 * WALL - 2 * CLR - 3.0, LIP, R - WALL - 1.5),
               W / 2, H / 2, z0 - LIP)
    plate = plate.union(lip_o.cut(lip_i))

    # clear the lip around the screw bosses
    for bx, by in ((5, 5), (W - 5, 5), (5, H - 5), (W - 5, H - 5)):
        plate = plate.cut(at(cyl(7.0, LIP), bx, by, z0 - LIP))
        plate = plate.cut(at(cyl(2.8, BACK), bx, by, z0))                 # screw clearance
        plate = plate.cut(at(cyl(5.2, 1.6), bx, by, z0 + BACK - 1.6))     # head recess

    # PCB pressers: press on the back side of the board corners
    pcb_back_z = FRONT + PCB_GAP + PCB_T
    pl = z0 - pcb_back_z
    for cx in (1.5, PCB_W - 1.5):
        for cy in (1.5, PCB_H - 1.5):
            plate = plate.union(at(cyl(3.0, pl), PCB_X + cx, PCB_Y + cy, pcb_back_z))

    # CO2 breakout cradle behind the display (breakout lies flat, sensor facing the display)
    cw, ch, wall = 26.0, 18.0, 1.2     # inner size. CHECK against your breakout
    ccx, ccy = DISP_X + DISP_W / 2 - 10, H / 2
    cradle = at(rbox(cw + 2 * wall, ch + 2 * wall, 3.0, 1.0), ccx, ccy, z0 - 3.0).cut(
        at(rbox(cw, ch, 3.0, 0.5), ccx, ccy, z0 - 3.0))
    cradle = cradle.cut(cq.Workplane("XY").box(8, ch + 10, 3.0)          # cable gap
                        .translate((fx(ccx - cw / 2), fy(ccy), z0 - 1.5)))
    plate = plate.union(cradle)

    # two keyhole slots for wall screws
    for kx in (W / 2 - 40, W / 2 + 40):
        plate = plate.cut(at(cyl(8.0, BACK), kx, H / 2 + 4, z0))
        plate = plate.cut(at(rbox(4.5, 8.0, BACK, 0), kx, H / 2, z0))
        plate = plate.cut(at(cyl(4.5, BACK), kx, H / 2 - 4, z0))
    return plate


# ================================================================= caps
def button_cap():
    """printed plunger; print flange-down. z=0 is the outer tip."""
    protrude = 1.5
    switch_top = FRONT + PCB_GAP - SWITCH_H
    stem_len = protrude + FRONT + 0.2
    flange_t = 1.0
    plunger_len = switch_top - 0.2 - (FRONT + 0.2 + flange_t)
    stem = cyl(7.8, stem_len).edges(">Z or <Z").chamfer(0.4)
    flange = cyl(10.5, flange_t).translate((0, 0, stem_len))
    plunger = cyl(4.0, plunger_len).translate((0, 0, stem_len + flange_t))
    return stem.union(flange).union(plunger)


def knob():
    """Ø18 knurled knob for a 6 mm D-shaft. CHECK shaft type/length in the BMQ22 datasheet."""
    d, h = 18.0, 12.0
    shaft_d, flat = 5.95, 4.5          # press fit; tune with a test print
    k = cyl(d, h).edges(">Z").fillet(1.5)
    n = 24
    for i in range(n):
        g = cq.Workplane("XY").box(1.2, 1.2, h - 2).translate((d / 2, 0, (h - 2) / 2)).rotate((0, 0, 0), (0, 0, 1), 360 / n * i)
        k = k.cut(g)
    hole = cyl(shaft_d, h - 2.0)
    hole = hole.cut(cq.Workplane("XY").box(shaft_d, shaft_d, h).translate((flat - shaft_d / 2 + shaft_d / 2, 0, h / 2)))
    k = k.cut(hole)
    k = k.cut(cyl(3.0, 1.0).translate((0, d / 2 - 3.0, h - 1.0)))      # indicator dot
    return k


# ================================================================= export
if __name__ == "__main__":
    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    parts = {
        "front_shell": front_shell(),
        "back_plate": back_plate(),
        "button_cap": button_cap(),
        "knob": knob(),
    }
    for name, shape in parts.items():
        cq.exporters.export(shape, str(out / f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)
        cq.exporters.export(shape, str(out / f"{name}.step"))
        bb = shape.val().BoundingBox()
        print(f"{name:12s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:6.1f} mm")
    asm = cq.Assembly()
    asm.add(parts["front_shell"], name="front_shell", color=cq.Color(0.85, 0.85, 0.82))
    asm.add(parts["back_plate"], name="back_plate", color=cq.Color(0.6, 0.6, 0.6))
    asm.save(str(out / "assembly.step"))
