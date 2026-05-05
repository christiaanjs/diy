import cadquery as cq
import math

# ── Parameters ────────────────────────────────────────────────────────────────

SEAT_DIA   = 280    # seat disc diameter (mm)
SEAT_T     = 40     # seat thickness
SEAT_H     = 450    # finished height from floor to top of seat

LEG_DIA    = 35     # round leg diameter
LEG_SPLAY  = 10     # outward splay from vertical (degrees)
N_LEGS     = 3

TENON_DIA  = 22     # round tenon diameter (fits into seat mortise)
TENON_L    = 30     # tenon length protruding into seat

# Derived
LEG_H_VERT = SEAT_H - SEAT_T          # vertical component of leg length
# Actual leg length slightly longer due to splay
LEG_L      = int(LEG_H_VERT / math.cos(math.radians(LEG_SPLAY))) + 5

MORTISE_DEPTH = TENON_L + 2           # blind mortise in seat underside

# ── Seat ──────────────────────────────────────────────────────────────────────

seat = cq.Workplane("XY").cylinder(SEAT_T, SEAT_DIA / 2)
seat = seat.translate((0, 0, SEAT_H - SEAT_T / 2))

# Chamfer top rim
seat = seat.faces(">Z").chamfer(4)

# Blind mortises on underside — 3 holes at 120° intervals, inset from edge
mortise_r = SEAT_DIA / 2 * 0.55   # radial distance from centre

mortise_pts = [
    (mortise_r * math.cos(math.radians(a)),
     mortise_r * math.sin(math.radians(a)))
    for a in (90, 90 + 120, 90 + 240)
]

seat_bottom_z = SEAT_H - SEAT_T
seat = (
    seat.faces("<Z")
    .workplane()
    .pushPoints(mortise_pts)
    .hole(TENON_DIA + 1, MORTISE_DEPTH)  # +1 clearance
)

# ── One leg + tenon (positioned upright; splay applied via translate/rotate) ──

leg = cq.Workplane("XY").cylinder(LEG_L, LEG_DIA / 2)

# Round tenon at top end
tenon = cq.Workplane("XY").cylinder(TENON_L, TENON_DIA / 2)
tenon = tenon.translate((0, 0, LEG_L / 2 + TENON_L / 2 - 1))

leg = leg.union(tenon)

# ── Place three legs at splay ─────────────────────────────────────────────────

assy = cq.Assembly()
assy.add(seat, name="seat", color=cq.Color("burlywood"))

for i, (mx, my) in enumerate(mortise_pts):
    angle_out = math.degrees(math.atan2(my, mx))   # direction of splay in XY
    # Build leg centred at origin, rotate outward, then translate to mortise position
    leg_placed = (
        leg
        .rotate((0, 0, 0), (0, 0, 1), angle_out)
        .rotate(
            (0, 0, 0),
            (math.cos(math.radians(angle_out + 90)), math.sin(math.radians(angle_out + 90)), 0),
            -LEG_SPLAY
        )
        .translate((mx, my, LEG_L / 2 - MORTISE_DEPTH + 5))
    )
    assy.add(leg_placed, name=f"leg_{i}", color=cq.Color("peru"))

show_object = assy.toCompound()
