import cadquery as cq

# ── Parameters ────────────────────────────────────────────────────────────────

# Table
T_W   = 1800   # table width  (X)
T_D   = 900    # table depth  (Y)
T_H   = 750    # table height (Z)

# Bench (two benches, one each side)
B_W   = 1600   # bench length (X)
B_D   = 350    # bench depth  (Y)
B_H   = 450    # bench seat height (Z)

# Shared section sizes
LEG_W = 90     # leg section (square)
LEG_D = 90

APRON_H = 90   # apron / end-rail height (Z)
APRON_T = 40   # apron thickness

TOP_T   = 22   # solid timber top thickness
TOP_OVERHANG = 30

SEAT_T  = 40   # bench seat board thickness

BB_W    = 50   # breadboard end width

# Tenon geometry
TENON_T = 15   # tenon thickness
TENON_H = 55   # tenon height (centred on apron)
TENON_L = LEG_W

# ── Shared helpers ────────────────────────────────────────────────────────────

def leg(h):
    b = cq.Workplane("XY").box(LEG_W, LEG_D, h)
    # Long-side mortise
    b = (b.faces(">X").workplane()
         .center(0, 0).rect(TENON_T + 1, TENON_H + 1).cutBlind(-(TENON_T + 3)))
    # Short-side mortise
    b = (b.faces(">Y").workplane()
         .center(0, 0).rect(TENON_T + 1, TENON_H + 1).cutBlind(-(TENON_T + 3)))
    return b.translate((0, 0, h / 2))

def long_apron(span, inset=0):
    return cq.Workplane("XY").box(span + 2 * TENON_L, APRON_T, APRON_H)

def short_apron(span):
    return cq.Workplane("XY").box(APRON_T, span + 2 * TENON_L, APRON_H)

def top_panel(w, d, t, with_bb=True):
    panel_w = w - (2 * BB_W if with_bb else 0)
    panel = cq.Workplane("XY").box(panel_w, d, t)
    if with_bb:
        bb_l = cq.Workplane("XY").box(BB_W, d, t).translate((-(panel_w/2 + BB_W/2), 0, 0))
        bb_r = cq.Workplane("XY").box(BB_W, d, t).translate(( panel_w/2 + BB_W/2,  0, 0))
        return panel, bb_l, bb_r
    return panel, None, None

# ── TABLE ─────────────────────────────────────────────────────────────────────

t_leg_h   = T_H - TOP_T
t_inner_w = T_W - 2 * LEG_W
t_inner_d = T_D - 2 * LEG_D
t_apron_z = t_leg_h - APRON_H / 2

t_legs = [
    leg(t_leg_h).translate((sx * (t_inner_w/2 + LEG_W/2), sy * (t_inner_d/2 + LEG_D/2), 0))
    for sx in (-1, 1) for sy in (-1, 1)
]

t_front = long_apron(t_inner_w).translate((0,  t_inner_d/2 + LEG_D/2, t_apron_z))
t_back  = long_apron(t_inner_w).translate((0, -t_inner_d/2 - LEG_D/2, t_apron_z))
t_left  = short_apron(t_inner_d).translate((-(t_inner_w/2 + LEG_W/2), 0, t_apron_z))
t_right = short_apron(t_inner_d).translate(( t_inner_w/2 + LEG_W/2,  0, t_apron_z))

t_panel, t_bb_l, t_bb_r = top_panel(T_W, T_D, TOP_T)
t_top_z = T_H - TOP_T / 2
t_panel  = t_panel.translate((0, 0, t_top_z))
t_bb_l   = t_bb_l.translate((0, 0, t_top_z))
t_bb_r   = t_bb_r.translate((0, 0, t_top_z))

# ── BENCH (one; second is mirrored in assembly) ───────────────────────────────

b_leg_h   = B_H - SEAT_T
b_inner_w = B_W - 2 * LEG_W
b_inner_d = B_D - 2 * LEG_D
b_apron_z = b_leg_h - APRON_H / 2

b_legs = [
    leg(b_leg_h).translate((sx * (b_inner_w/2 + LEG_W/2), sy * (b_inner_d/2 + LEG_D/2), 0))
    for sx in (-1, 1) for sy in (-1, 1)
]

b_front = long_apron(b_inner_w).translate((0,  b_inner_d/2 + LEG_D/2, b_apron_z))
b_back  = long_apron(b_inner_w).translate((0, -b_inner_d/2 - LEG_D/2, b_apron_z))
b_left  = short_apron(b_inner_d).translate((-(b_inner_w/2 + LEG_W/2), 0, b_apron_z))
b_right = short_apron(b_inner_d).translate(( b_inner_w/2 + LEG_W/2,  0, b_apron_z))

b_panel, b_bb_l, b_bb_r = top_panel(B_W, B_D, SEAT_T)
b_seat_z = B_H - SEAT_T / 2
b_panel  = b_panel.translate((0, 0, b_seat_z))
b_bb_l   = b_bb_l.translate((0, 0, b_seat_z))
b_bb_r   = b_bb_r.translate((0, 0, b_seat_z))

# ── Assembly ──────────────────────────────────────────────────────────────────

wood    = cq.Color("burlywood")
top_col = cq.Color("wheat")

BENCH_OFFSET_Y = T_D / 2 + B_D / 2 + 400  # 400 mm gap between bench and table

assy = cq.Assembly()

# Table
for i, l in enumerate(t_legs):
    assy.add(l, name=f"t_leg_{i}", color=wood)
for name, part in [("t_front", t_front), ("t_back", t_back),
                   ("t_left", t_left),  ("t_right", t_right)]:
    assy.add(part, name=name, color=wood)
assy.add(t_panel, name="t_top",   color=top_col)
assy.add(t_bb_l,  name="t_bb_l",  color=wood)
assy.add(t_bb_r,  name="t_bb_r",  color=wood)

# Bench 1 (front)
bench1_offset = (0, BENCH_OFFSET_Y, 0)
for i, l in enumerate(b_legs):
    assy.add(l.translate(bench1_offset), name=f"b1_leg_{i}", color=wood)
for name, part in [("b1_front", b_front), ("b1_back", b_back),
                   ("b1_left",  b_left),  ("b1_right", b_right)]:
    assy.add(part.translate(bench1_offset), name=name, color=wood)
assy.add(b_panel.translate(bench1_offset), name="b1_seat",  color=top_col)
assy.add(b_bb_l.translate(bench1_offset),  name="b1_bb_l",  color=wood)
assy.add(b_bb_r.translate(bench1_offset),  name="b1_bb_r",  color=wood)

# Bench 2 (back)
bench2_offset = (0, -BENCH_OFFSET_Y, 0)
for i, l in enumerate(b_legs):
    assy.add(l.translate(bench2_offset), name=f"b2_leg_{i}", color=wood)
for name, part in [("b2_front", b_front), ("b2_back", b_back),
                   ("b2_left",  b_left),  ("b2_right", b_right)]:
    assy.add(part.translate(bench2_offset), name=name, color=wood)
assy.add(b_panel.translate(bench2_offset), name="b2_seat",  color=top_col)
assy.add(b_bb_l.translate(bench2_offset),  name="b2_bb_l",  color=wood)
assy.add(b_bb_r.translate(bench2_offset),  name="b2_bb_r",  color=wood)

show_object = assy.toCompound()
