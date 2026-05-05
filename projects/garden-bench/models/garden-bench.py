import cadquery as cq

# ── Parameters ────────────────────────────────────────────────────────────────

BENCH_W    = 1200   # overall length (X)
BENCH_H    = 450    # seat height (Z)
BENCH_D    = 380    # overall depth front-to-back (Y)

LEG_W      = 70     # leg section width  (X, faces outward)
LEG_D      = 70     # leg section depth  (Y)

RAIL_W     = 70     # seat rail width (X, faces front/back)
RAIL_T     = 35     # seat rail thickness (Y)
RAIL_H     = 70     # seat rail height (Z) — same stock as legs

BACK_RAIL_H = 35    # thickness of back top rail (Z)
BACK_RAIL_W = 70    # back rail width (Y)
BACK_POST_H = 380   # leg extension above seat for back post

SEAT_SLAT_T  = 28   # slat thickness (Z)
SEAT_SLAT_W  = 70   # slat width (Y)
SEAT_SLATS   = 4    # number of seat slats
SLAT_GAP     = 10   # gap between slats

BACK_SLAT_T  = 28
BACK_SLAT_W  = 70
BACK_SLATS   = 2

# Through-tenon on rail ends: tenon protrudes through leg
TENON_T      = 12   # tenon thickness (Y)
TENON_H      = 40   # tenon height (Z)  — centred on rail height
TENON_L      = LEG_D + 8   # total tenon length (through + 8 mm proud)

# ── Derived ───────────────────────────────────────────────────────────────────

INNER_W = BENCH_W - 2 * LEG_W   # clear span between legs (X)
LEG_H   = BENCH_H - SEAT_SLAT_T  # leg height to underside of seat

# Seat slat total span check
_slat_total = SEAT_SLATS * SEAT_SLAT_W + (SEAT_SLATS - 1) * SLAT_GAP  # should be <= BENCH_D

# ── Leg (with mortise cutouts for rails) ──────────────────────────────────────

def make_leg(with_back_post=False):
    h = LEG_H + (BACK_POST_H if with_back_post else 0)
    leg = cq.Workplane("XY").box(LEG_W, LEG_D, h)
    # Seat rail mortise — centred on leg depth, centred on rail height from bottom
    rail_centre_z = LEG_H / 2
    leg = (
        leg.faces(">X").workplane()
        .center(0, rail_centre_z - h / 2)
        .rect(TENON_T, TENON_H)
        .cutThruAll()
    )
    return leg.translate((0, 0, h / 2))

leg_front_left  = make_leg(with_back_post=True) .translate((-INNER_W/2 - LEG_W/2,  BENCH_D/2 - LEG_D/2, 0))
leg_front_right = make_leg(with_back_post=True) .translate(( INNER_W/2 + LEG_W/2,  BENCH_D/2 - LEG_D/2, 0))
leg_back_left   = make_leg(with_back_post=False).translate((-INNER_W/2 - LEG_W/2, -BENCH_D/2 + LEG_D/2, 0))
leg_back_right  = make_leg(with_back_post=False).translate(( INNER_W/2 + LEG_W/2, -BENCH_D/2 + LEG_D/2, 0))

# ── Seat rail (with through-tenons at each end) ───────────────────────────────

def make_seat_rail():
    rail = cq.Workplane("XY").box(INNER_W + 2 * TENON_L, RAIL_T, RAIL_H)
    return rail

front_rail = make_seat_rail().translate((0,  BENCH_D/2 - LEG_D/2, LEG_H / 2))
back_rail  = make_seat_rail().translate((0, -BENCH_D/2 + LEG_D/2, LEG_H / 2))

# ── Back top rail (connects the back-post tops) ───────────────────────────────

back_top_rail_z = LEG_H + BACK_POST_H - BACK_RAIL_H / 2
back_top_rail = (
    cq.Workplane("XY")
    .box(INNER_W + 2 * LEG_W, BACK_RAIL_W, BACK_RAIL_H)
    .translate((0, BENCH_D/2 - LEG_D/2, back_top_rail_z))
)

# ── Seat slats ────────────────────────────────────────────────────────────────

slat_start_y = -(BENCH_D / 2) + SLAT_GAP + SEAT_SLAT_W / 2

def make_slat(y_pos, w=SEAT_SLAT_W):
    return (
        cq.Workplane("XY")
        .box(BENCH_W, w, SEAT_SLAT_T)
        .translate((0, y_pos, LEG_H + SEAT_SLAT_T / 2))
    )

seat_slats = [
    make_slat(slat_start_y + i * (SEAT_SLAT_W + SLAT_GAP))
    for i in range(SEAT_SLATS)
]

# ── Back slats ────────────────────────────────────────────────────────────────

back_slat_spacing = (BACK_POST_H - BACK_RAIL_H) / (BACK_SLATS + 1)
back_slat_start_z = LEG_H + back_slat_spacing

back_slats = [
    (cq.Workplane("XY")
     .box(BENCH_W, BACK_SLAT_T, BACK_SLAT_W)
     .translate((0, BENCH_D/2 - LEG_D/2, back_slat_start_z + i * back_slat_spacing)))
    for i in range(BACK_SLATS)
]

# ── Assembly ──────────────────────────────────────────────────────────────────

wood = cq.Color("burlywood")

assy = (
    cq.Assembly()
    .add(leg_front_left,  name="leg_fl", color=wood)
    .add(leg_front_right, name="leg_fr", color=wood)
    .add(leg_back_left,   name="leg_bl", color=wood)
    .add(leg_back_right,  name="leg_br", color=wood)
    .add(front_rail,      name="rail_front", color=wood)
    .add(back_rail,       name="rail_back",  color=wood)
    .add(back_top_rail,   name="rail_top",   color=wood)
)

for i, s in enumerate(seat_slats):
    assy.add(s, name=f"seat_slat_{i}", color=wood)
for i, s in enumerate(back_slats):
    assy.add(s, name=f"back_slat_{i}", color=wood)

show_object = assy.toCompound()
