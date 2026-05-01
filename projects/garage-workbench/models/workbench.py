"""
Garage Workbench — parametric CadQuery model.

All timber is 90 × 45 mm H3.2 structural pine — the standard rough-sawn
framing section used in NZ house construction.  Buy it off the framing
rack at any Mitre 10 / Bunnings; no dressing or facing required.
Dimensions are nominal — actual cross-section varies ±2–3 mm per piece.

Structure:
  Top        : single 18 mm structural plywood sheet (1800 × 600)
  Legs       : 90 × 45 mm pine, 4 off — same section as everything else
  Aprons     : 90 × 45 mm pine — long front/back + short end aprons
  Lower shelf: 18 mm structural plywood, inset between legs
  Stretchers : 90 × 45 mm pine — long + end pairs supporting shelf

Joinery: coach screws (M10 × 100) + PVA throughout — no jigs needed.

Coordinate system
  X  left → right  (looking at the front face)
  Y  front → back
  Z  ground → sky
"""

import cadquery as cq

# ── Parameters ────────────────────────────────────────────────────────────────

# Overall work surface dimensions
BENCH_W  = 1800   # total width  (X)
BENCH_D  = 600    # total depth  (Y)
BENCH_H  = 900    # finished height from floor to top surface (Z)

# Top
TOP_T    = 18     # plywood thickness
TOP_LAYERS = 1    # single sheet — adequate over a well-spaced frame

# Legs — same 90 × 45 section as all framing; no special stock needed
LEG_W    = 90     # leg face width (X) — the 90 mm face runs left-right
LEG_D    = 45     # leg depth (Y)      — the 45 mm face goes front-to-back
LEG_H    = BENCH_H - TOP_T * TOP_LAYERS  # leg height (top of leg = underside of top)

# Aprons (connect legs at the top, inside face flush with leg inside face)
APR_H    = 90     # apron height (vertical)
APR_T    = 45     # apron thickness

# Lower shelf
SHELF_T  = 18                  # shelf plywood thickness
SHELF_Z  = 250                 # Z of shelf top face (above floor)
SHELF_INSET = LEG_W            # shelf sits flush with inside of legs

# Shelf stretchers (support shelf underside)
STR_H    = 90     # stretcher height
STR_T    = 45     # stretcher thickness

# ── Derived ───────────────────────────────────────────────────────────────────

# Leg corner positions (centre of leg section)
LEG_CX_L = LEG_W / 2
LEG_CX_R = BENCH_W - LEG_W / 2
LEG_CY_F = LEG_D / 2
LEG_CY_B = BENCH_D - LEG_D / 2

LEG_POSITIONS = [
    (LEG_CX_L, LEG_CY_F, "FL"),
    (LEG_CX_R, LEG_CY_F, "FR"),
    (LEG_CX_L, LEG_CY_B, "BL"),
    (LEG_CX_R, LEG_CY_B, "BR"),
]

# Long apron clear span between leg inside faces
APR_LONG_LEN = BENCH_W - LEG_W * 2   # net clear, but we run it leg-face to leg-face
APR_LONG_CX  = BENCH_W / 2
APR_FRONT_CY = LEG_D - APR_T / 2     # apron front face flush with front leg face
APR_BACK_CY  = BENCH_D - LEG_D + APR_T / 2

# Short apron (end-to-end, inset between the two long aprons)
APR_SHORT_LEN = BENCH_D - LEG_D * 2
APR_SHORT_CY  = BENCH_D / 2
APR_SHORT_CZ  = LEG_H - APR_H / 2   # centred vertically within leg height at top

# Long apron Z centred so top face aligns with top of legs
APR_LONG_Z = LEG_H - APR_H / 2

# Shelf clear span inside legs
SHELF_W = BENCH_W - LEG_W * 2
SHELF_D = BENCH_D - LEG_D * 2

# Stretcher positions
STR_LONG_CX  = BENCH_W / 2
STR_FRONT_CY = APR_FRONT_CY        # same front/back Y as aprons
STR_BACK_CY  = APR_BACK_CY
STR_Z        = SHELF_Z - SHELF_T - STR_H / 2   # shelf sits on top of stretchers

# ── Colours ───────────────────────────────────────────────────────────────────
C_LEG   = cq.Color(0.66, 0.48, 0.30)   # pine — same as all framing
C_FRAME = cq.Color(0.66, 0.48, 0.30)   # pine framing (aprons / stretchers)
C_PLY   = cq.Color(0.82, 0.72, 0.50)   # plywood top and shelf

asm = cq.Assembly()

# ── Legs ──────────────────────────────────────────────────────────────────────
leg = cq.Workplane("XY").box(LEG_W, LEG_D, LEG_H)
for cx, cy, name in LEG_POSITIONS:
    asm.add(
        leg,
        name=f"leg_{name}",
        loc=cq.Location(cq.Vector(cx, cy, LEG_H / 2)),
        color=C_LEG,
    )

# ── Long aprons (front and back, running left-right) ─────────────────────────
long_apron = cq.Workplane("XY").box(APR_LONG_LEN, APR_T, APR_H)
asm.add(
    long_apron,
    name="apron_front",
    loc=cq.Location(cq.Vector(APR_LONG_CX, APR_FRONT_CY, APR_LONG_Z)),
    color=C_FRAME,
)
asm.add(
    long_apron,
    name="apron_back",
    loc=cq.Location(cq.Vector(APR_LONG_CX, APR_BACK_CY, APR_LONG_Z)),
    color=C_FRAME,
)

# ── Short aprons (left and right ends, running front-to-back) ─────────────────
short_apron = cq.Workplane("XY").box(APR_T, APR_SHORT_LEN, APR_H)
asm.add(
    short_apron,
    name="apron_left",
    loc=cq.Location(cq.Vector(LEG_W - APR_T / 2, APR_SHORT_CY, APR_SHORT_CZ)),
    color=C_FRAME,
)
asm.add(
    short_apron,
    name="apron_right",
    loc=cq.Location(cq.Vector(BENCH_W - LEG_W + APR_T / 2, APR_SHORT_CY, APR_SHORT_CZ)),
    color=C_FRAME,
)

# ── Work surface — two layers of 18 mm plywood ───────────────────────────────
top_layer = cq.Workplane("XY").box(BENCH_W, BENCH_D, TOP_T)
for i in range(TOP_LAYERS):
    z = LEG_H + TOP_T * i + TOP_T / 2
    asm.add(
        top_layer,
        name=f"top_layer_{i}",
        loc=cq.Location(cq.Vector(BENCH_W / 2, BENCH_D / 2, z)),
        color=C_PLY,
    )

# ── Lower shelf stretchers ────────────────────────────────────────────────────
long_str = cq.Workplane("XY").box(APR_LONG_LEN, STR_T, STR_H)
asm.add(
    long_str,
    name="str_front",
    loc=cq.Location(cq.Vector(STR_LONG_CX, STR_FRONT_CY, STR_Z)),
    color=C_FRAME,
)
asm.add(
    long_str,
    name="str_back",
    loc=cq.Location(cq.Vector(STR_LONG_CX, STR_BACK_CY, STR_Z)),
    color=C_FRAME,
)

short_str = cq.Workplane("XY").box(STR_T, APR_SHORT_LEN, STR_H)
asm.add(
    short_str,
    name="str_left",
    loc=cq.Location(cq.Vector(LEG_W - STR_T / 2, APR_SHORT_CY, STR_Z)),
    color=C_FRAME,
)
asm.add(
    short_str,
    name="str_right",
    loc=cq.Location(cq.Vector(BENCH_W - LEG_W + STR_T / 2, APR_SHORT_CY, STR_Z)),
    color=C_FRAME,
)

# ── Lower shelf ───────────────────────────────────────────────────────────────
shelf = cq.Workplane("XY").box(SHELF_W, SHELF_D, SHELF_T)
asm.add(
    shelf,
    name="shelf",
    loc=cq.Location(cq.Vector(BENCH_W / 2, BENCH_D / 2, SHELF_Z - SHELF_T / 2)),
    color=C_PLY,
)

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"Overall        : {BENCH_W} W × {BENCH_D} D × {BENCH_H} H mm")
print(f"Leg height     : {LEG_H} mm")
print(f"Shelf at       : {SHELF_Z} mm (top face)")
print(f"Top surface    : {TOP_LAYERS} × {TOP_T} mm = {TOP_LAYERS * TOP_T} mm thick")
print(f"Apron span     : {APR_LONG_LEN} mm (long)  ×  {APR_SHORT_LEN} mm (short)")

# ── Export ────────────────────────────────────────────────────────────────────
show_object = asm
