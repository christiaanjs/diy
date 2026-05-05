import cadquery as cq

# ── Parameters ────────────────────────────────────────────────────────────────

OUTER_W = 800   # external length (X)
OUTER_D = 300   # external width  (Y)
OUTER_H = 300   # external height (Z)

WALL_T  = 18    # side/end board thickness (18 mm dressed pine or cedar)
BASE_T  = 18    # bottom panel thickness

# Dado groove that the base sits in
DADO_DEPTH = 6   # groove depth cut into side walls
DADO_H     = 30  # height of groove centre from bottom of side wall

# Drainage holes in base
DRAIN_DIA  = 20
DRAIN_ROWS = 2
DRAIN_COLS = 4

# ── Derived dims ──────────────────────────────────────────────────────────────

INNER_W = OUTER_W - 2 * WALL_T
INNER_D = OUTER_D - 2 * WALL_T
INNER_H = OUTER_H - BASE_T   # base sits in dado so interior floor is slightly raised

# ── Side walls (long, run the full outer width) ───────────────────────────────

side_wall = (
    cq.Workplane("XY")
    .box(OUTER_W, WALL_T, OUTER_H)
    # dado groove on the inside face, centred at DADO_H from bottom
    .faces(">Y")
    .workplane()
    .center(0, DADO_H - OUTER_H / 2 + BASE_T / 2)
    .rect(INNER_W, BASE_T)
    .cutBlind(-DADO_DEPTH)
)

front_wall = side_wall.translate((0,  (OUTER_D - WALL_T) / 2, OUTER_H / 2))
back_wall  = side_wall.translate((0, -(OUTER_D - WALL_T) / 2, OUTER_H / 2))

# ── End walls (short, sit between the two long sides) ─────────────────────────

end_wall = cq.Workplane("XY").box(WALL_T, INNER_D, OUTER_H)

left_wall  = end_wall.translate(( (OUTER_W - WALL_T) / 2, 0, OUTER_H / 2))
right_wall = end_wall.translate((-(OUTER_W - WALL_T) / 2, 0, OUTER_H / 2))

# ── Base panel (seats in dado, trimmed to inner width) ───────────────────────

base = (
    cq.Workplane("XY")
    .box(INNER_W, INNER_D, BASE_T)
)

# drainage holes
xs = [(i - (DRAIN_COLS - 1) / 2) * (INNER_W / (DRAIN_COLS + 1)) for i in range(DRAIN_COLS)]
ys = [(j - (DRAIN_ROWS - 1) / 2) * (INNER_D / (DRAIN_ROWS + 1)) for j in range(DRAIN_ROWS)]
for x in xs:
    for y in ys:
        base = base.faces(">Z").workplane().center(x, y).hole(DRAIN_DIA)

# position base at dado height
base_z = DADO_H + BASE_T / 2   # bottom of base aligns with dado floor
base = base.translate((0, 0, base_z))

# ── Assembly ──────────────────────────────────────────────────────────────────

assy = (
    cq.Assembly()
    .add(front_wall,  name="front",  color=cq.Color("burlywood"))
    .add(back_wall,   name="back",   color=cq.Color("burlywood"))
    .add(left_wall,   name="left",   color=cq.Color("burlywood"))
    .add(right_wall,  name="right",  color=cq.Color("burlywood"))
    .add(base,        name="base",   color=cq.Color("tan"))
)

show_object = assy.toCompound()
