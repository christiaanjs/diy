import cadquery as cq

# ── Parameters ────────────────────────────────────────────────────────────────

TABLE_W  = 600    # width  (X)
TABLE_D  = 400    # depth  (Y)
TABLE_H  = 700    # height (Z)

LEG_W    = 50     # leg section (square)
LEG_D    = 50

APRON_H  = 70     # apron height (Z)
APRON_T  = 22     # apron thickness (X or Y)

TOP_T    = 20     # glued-up solid timber top thickness
TOP_OVERHANG = 25 # top overhang beyond apron on each side

# Mortise and tenon: tenons on apron ends into legs
TENON_T  = 10     # tenon thickness (into leg face)
TENON_H  = 40     # tenon height (centred on apron height)
TENON_L  = LEG_W  # tenon length (full through-leg width)

# Breadboard ends on top (to manage wood movement)
BB_W     = 40     # breadboard end width (X) — end grain pieces

# ── Derived ───────────────────────────────────────────────────────────────────

INNER_W  = TABLE_W - 2 * LEG_W   # clear span between legs (X)
INNER_D  = TABLE_D - 2 * LEG_D   # clear span between legs (Y)
LEG_H    = TABLE_H - TOP_T        # leg height

# ── Legs ──────────────────────────────────────────────────────────────────────

def make_leg():
    leg = cq.Workplane("XY").box(LEG_W, LEG_D, LEG_H)
    # Mortise on X face (for long apron)
    leg = (
        leg.faces(">X").workplane()
        .center(0, 0)
        .rect(TENON_T + 0.5, TENON_H + 0.5)
        .cutBlind(-TENON_T - 2)
    )
    # Mortise on Y face (for short apron)
    leg = (
        leg.faces(">Y").workplane()
        .center(0, 0)
        .rect(TENON_T + 0.5, TENON_H + 0.5)
        .cutBlind(-TENON_T - 2)
    )
    return leg.translate((0, 0, LEG_H / 2))

leg_positions = [
    (-(INNER_W/2 + LEG_W/2),  (INNER_D/2 + LEG_D/2)),
    ( (INNER_W/2 + LEG_W/2),  (INNER_D/2 + LEG_D/2)),
    (-(INNER_W/2 + LEG_W/2), -(INNER_D/2 + LEG_D/2)),
    ( (INNER_W/2 + LEG_W/2), -(INNER_D/2 + LEG_D/2)),
]

legs = [make_leg().translate((x, y, 0)) for x, y in leg_positions]

# ── Aprons (with tenons at each end) ─────────────────────────────────────────

def make_long_apron():
    # length = inner span + 2 tenon lengths
    return cq.Workplane("XY").box(INNER_W + 2 * TENON_L, APRON_T, APRON_H)

def make_short_apron():
    return cq.Workplane("XY").box(APRON_T, INNER_D + 2 * TENON_L, APRON_H)

apron_z = LEG_H - APRON_H / 2   # aprons flush with top of legs

front_apron = make_long_apron() .translate((0,  INNER_D/2 + LEG_D/2, apron_z))
back_apron  = make_long_apron() .translate((0, -INNER_D/2 - LEG_D/2, apron_z))
left_apron  = make_short_apron().translate((-(INNER_W/2 + LEG_W/2), 0, apron_z))
right_apron = make_short_apron().translate(( (INNER_W/2 + LEG_W/2), 0, apron_z))

# ── Glued-up solid top (3 boards edge-joined) ────────────────────────────────

BOARD_W   = (TABLE_D - 2 * BB_W) / 3   # each board width before joining
BOARD_L   = TABLE_W - 2 * BB_W         # board length (between breadboard ends)

top_panel = cq.Workplane("XY").box(BOARD_L, TABLE_D - 2 * BB_W, TOP_T)
top_panel = top_panel.translate((0, 0, TABLE_H - TOP_T / 2))

# Breadboard ends (across the grain, slotted to allow movement)
bb_left  = (cq.Workplane("XY").box(BB_W, TABLE_D, TOP_T)
            .translate((-(BOARD_L/2 + BB_W/2), 0, TABLE_H - TOP_T/2)))
bb_right = (cq.Workplane("XY").box(BB_W, TABLE_D, TOP_T)
            .translate(( (BOARD_L/2 + BB_W/2), 0, TABLE_H - TOP_T/2)))

# ── Assembly ──────────────────────────────────────────────────────────────────

wood  = cq.Color("burlywood")
light = cq.Color("wheat")

assy = cq.Assembly()
for i, leg in enumerate(legs):
    assy.add(leg, name=f"leg_{i}", color=wood)

assy.add(front_apron,  name="apron_front",  color=wood)
assy.add(back_apron,   name="apron_back",   color=wood)
assy.add(left_apron,   name="apron_left",   color=wood)
assy.add(right_apron,  name="apron_right",  color=wood)
assy.add(top_panel,    name="top_panel",    color=light)
assy.add(bb_left,      name="breadboard_l", color=wood)
assy.add(bb_right,     name="breadboard_r", color=wood)

show_object = assy.toCompound()
