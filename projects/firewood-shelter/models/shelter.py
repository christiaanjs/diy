"""
Firewood Shelter — parametric CadQuery model.

Foundation : N_SL × H4 sleepers 200×50, running front-to-back
Posts      : H4 100×100 — front 1800 mm, back 1400 mm (skillion slope)
Framing    : 90×45 — wall plates, rafters @ ≤600 mm centres, back-wall noggins
Cladding   : rough-sawn paling on back wall
Roof       : skillion corrugated iron (modelled as a flat sheet, correct slope angle)
Open face  : front — no framing, full access for stacking / retrieval

Sized for FIREWOOD_VOL_M3 m³ of firewood — see firewood sizing section below.
Sleeper count and rafter count are derived from the firewood and structural parameters.

Coordinate system
  X  left → right  (looking at the open front)
  Y  front → back
  Z  ground → sky
"""
import cadquery as cq
import math

# ── Firewood sizing ───────────────────────────────────────────────────────────
# Target storage and standard stack geometry drive the shelter width and depth.

FIREWOOD_VOL_M3 = 3.0   # target storage volume (m³)
STACK_H_M       = 1.6   # standard stack height (m)
STACK_D_M       = 0.5   # standard stack depth (m)
STACK_ROWS      = 3     # rows of wood — one along the front, one along the back

_linear_m    = FIREWOOD_VOL_M3 / (STACK_H_M * STACK_D_M) 
_row_width_m = _linear_m / STACK_ROWS 

# ── Parameters ────────────────────────────────────────────────────────────────

# Sleepers — H4 treated 200 × 50
SL_W  = 200     # width  (left-right when positioned)
SL_H  = 50      # height (laying flat)
SL_L  = round((STACK_ROWS * STACK_D_M) * 1000)   # front-to-back: 2000 mm

# Sleeper layout
BAY_W = 1400    # centre-to-centre spacing (max structural bay, mm)
# N_SL is derived in the Derived section below

# Posts — H4 treated 100 × 75
POST_W = 100    # along wall length (left-right on front/back walls)
POST_D = 100    # into the wall (front-back depth of post section)
PH_F   = 1800   # front post height above top of sleeper
PH_B   = 1400   # back post height

# Framing members — 90 × 45
FR_D = 90       # depth  (vertical dimension when used as plate/rafter)
FR_T = 45       # thickness (horizontal)

# Roof overhangs
OV_F = 300      # overhang beyond front wall plate
OV_B = 150      # overhang beyond back wall plate
OV_S = 150      # overhang each side

# Back-wall paling
PAL_T = 18      # paling board thickness

# Roof sheet
ROOF_T = 1.0    # corrugated iron (modelled flat)

# Rebar pegs: 12 mm dia, 1 200 mm long, ~400 mm proud of ground
REBAR_D    = 12
REBAR_L    = 1200
REBAR_SHOW = 400  # portion above ground that is visible

# ── Derived ───────────────────────────────────────────────────────────────────
# Number of sleepers: enough bays to meet the minimum row width
N_SL    = math.ceil(_row_width_m * 1000 / BAY_W) + 1

TOTAL_W = BAY_W * (N_SL - 1)
TOTAL_D = SL_L

SL_TOP = SL_H                   # z of top face of sleepers = 75

# Post top z values
FRONT_POST_TOP = SL_TOP + PH_F  # 1 875
BACK_POST_TOP  = SL_TOP + PH_B  # 1 475

# Wall plate: plate sits ON TOP of posts; FR_D is the vertical dimension
PLATE_F_Z  = FRONT_POST_TOP + FR_D / 2   # centre-z of front plate  = 1 920
PLATE_B_Z  = BACK_POST_TOP  + FR_D / 2   # centre-z of back  plate  = 1 520

# Rafter bottom z at each end (rafters rest on top of wall plates)
RAF_Z_F = FRONT_POST_TOP + FR_D          # 1 965
RAF_Z_B = BACK_POST_TOP  + FR_D          # 1 565

# Slope geometry
SLOPE_RISE = RAF_Z_F - RAF_Z_B           # 400 mm
SLOPE_RUN  = TOTAL_D
SLOPE_DEG  = math.degrees(math.atan2(SLOPE_RISE, SLOPE_RUN))  # ≈ 9.46°
SLOPE_RAD  = math.radians(SLOPE_DEG)

print(f"No of bays    : {N_SL - 1} (based on target row width of {_row_width_m:.2f} m)")
print(f"Roof slope    : {SLOPE_DEG:.1f}°  ({SLOPE_RISE}/{SLOPE_RUN} mm)")
print(f"Frame         : {TOTAL_W} mm wide  ×  {TOTAL_D} mm deep")
print(f"Firewood rows : {STACK_ROWS} × {TOTAL_W} mm = {STACK_ROWS * TOTAL_W / 1000:.1f} m linear  "
      f"(target {_linear_m:.1f} m for {FIREWOOD_VOL_M3} m³)")

# Sleeper-centred X positions of posts
POST_XS = [i * BAY_W + SL_W / 2 for i in range(N_SL)]

# Full width span of top members (sleeper-face to sleeper-face)
SPAN_W = TOTAL_W + SL_W

# Rafter positions: one rafter at each post, intermediates added where bay > 750 mm.
# This keeps rafters aligned with posts for modular bay-by-bay construction.
RAF_MAX_SPACING = 750   # mm
RAF_XS = []
for _i in range(N_SL - 1):
    _n_spaces = math.ceil(BAY_W / RAF_MAX_SPACING)
    for _j in range(_n_spaces):
        RAF_XS.append(POST_XS[_i] + _j * BAY_W / _n_spaces)
RAF_XS.append(POST_XS[-1])
N_RAF = len(RAF_XS)

# Rafter geometry: sloped length and mid-height
RAF_LEN_HORIZ = TOTAL_D + OV_F + OV_B         # 2 850 horizontal span
RAF_LEN_SLOPE = math.sqrt(RAF_LEN_HORIZ**2 + SLOPE_RISE**2)  # actual slope length
RAF_MID_Z     = (RAF_Z_F + RAF_Z_B) / 2       # average height of rafter bottom = 1 765
RAF_CEN_Z     = RAF_MID_Z + FR_D / 2           # rafter centroid z = 1 810
# Y centre adjusted for asymmetric overhangs
RAF_CEN_Y     = TOTAL_D / 2 + (OV_B - OV_F) / 2   # = 1 275  (shifted back by net overhang diff)

# ── Colours ───────────────────────────────────────────────────────────────────
C_SL   = cq.Color(0.42, 0.28, 0.18)    # dark treated timber (sleepers/posts)
C_FR   = cq.Color(0.65, 0.48, 0.30)    # lighter framing (plates/rafters)
C_PAL  = cq.Color(0.72, 0.56, 0.35)    # rough-sawn paling
C_ROOF = cq.Color(0.78, 0.80, 0.83)    # galvanised iron
C_RB   = cq.Color(0.35, 0.35, 0.35)    # rebar (dark grey)

asm = cq.Assembly()

# ── Sleepers ──────────────────────────────────────────────────────────────────
sleeper_box = cq.Workplane("XY").box(SL_W, SL_L, SL_H)
for i, cx in enumerate(POST_XS):
    asm.add(
        sleeper_box,
        name=f"sleeper_{i}",
        loc=cq.Location(cq.Vector(cx, SL_L / 2, SL_H / 2)),
        color=C_SL,
    )

# ── Posts ─────────────────────────────────────────────────────────────────────
for i, cx in enumerate(POST_XS):
    # Front post
    fp = cq.Workplane("XY").box(POST_W, POST_D, PH_F)
    asm.add(
        fp,
        name=f"post_front_{i}",
        loc=cq.Location(cq.Vector(cx, POST_D / 2, SL_TOP + PH_F / 2)),
        color=C_SL,
    )
    # Back post
    bp = cq.Workplane("XY").box(POST_W, POST_D, PH_B)
    asm.add(
        bp,
        name=f"post_back_{i}",
        loc=cq.Location(cq.Vector(cx, TOTAL_D - POST_D / 2, SL_TOP + PH_B / 2)),
        color=C_SL,
    )

# ── Front wall plate (runs left-right on top of front posts) ─────────────────
fp_plate = cq.Workplane("XY").box(SPAN_W, FR_T, FR_D)
asm.add(
    fp_plate,
    name="plate_front",
    loc=cq.Location(cq.Vector(SPAN_W / 2, POST_D / 2, PLATE_F_Z)),
    color=C_FR,
)

# ── Back wall plate ───────────────────────────────────────────────────────────
bp_plate = cq.Workplane("XY").box(SPAN_W, FR_T, FR_D)
asm.add(
    bp_plate,
    name="plate_back",
    loc=cq.Location(cq.Vector(SPAN_W / 2, TOTAL_D - POST_D / 2, PLATE_B_Z)),
    color=C_FR,
)

# ── Rafters (sloped, running front-to-back) ───────────────────────────────────
# Each rafter: FR_T wide × FR_D deep × RAF_LEN_SLOPE long.
# Created horizontal, then rotated around X by −SLOPE_DEG (front up, back down),
# then translated to its centre position.
rafter_box = cq.Workplane("XY").box(FR_T, RAF_LEN_SLOPE, FR_D)

for i, rx in enumerate(RAF_XS):
    asm.add(
        rafter_box,
        name=f"rafter_{i}",
        loc=cq.Location(
            cq.Vector(rx, RAF_CEN_Y, RAF_CEN_Z),
            cq.Vector(1, 0, 0),   # rotate around X axis
            -SLOPE_DEG,           # tilt front-high, back-low
        ),
        color=C_FR,
    )

# ── Back-wall noggins (2 rows × 2 bays = 4 total) ────────────────────────────
# Noggins fill between the back posts; 2 rows at 1/3 and 2/3 of post height.
for row, frac in enumerate([1 / 3, 2 / 3]):
    nz = SL_TOP + PH_B * frac
    for bay in range(N_SL - 1):
        x0 = POST_XS[bay]
        x1 = POST_XS[bay + 1]
        nog_len = x1 - x0 - POST_W            # clear span between posts
        nog = cq.Workplane("XY").box(nog_len, FR_T, FR_D)
        asm.add(
            nog,
            name=f"noggin_back_r{row}_b{bay}",
            loc=cq.Location(cq.Vector((x0 + x1) / 2, TOTAL_D - POST_D / 2, nz)),
            color=C_FR,
        )

# ── Back-wall paling cladding ─────────────────────────────────────────────────
# Rough-sawn paling boards: 100 × 18 mm face, run vertically, butted tight.
# Board length needed: 1 450 mm (use 1 500 mm stock, trim 50 mm off each board).
# Board count: ceil(SPAN_W / 100) = ceil(4 400 / 100) = 44 boards + 2 spare = 46 total.
# Modelled as a solid panel for clarity.
pal_h = BACK_POST_TOP               # full post height = 1 450 mm
paling = cq.Workplane("XY").box(SPAN_W, PAL_T, pal_h)
asm.add(
    paling,
    name="back_paling",
    loc=cq.Location(cq.Vector(SPAN_W / 2, TOTAL_D + PAL_T / 2, SL_TOP + pal_h / 2)),
    color=C_PAL,
)

# ── Roof sheet ────────────────────────────────────────────────────────────────
# Flat sheet representing corrugated iron.  Correct slope angle, correct span.
roof_w = SPAN_W + 2 * OV_S
roof_d = RAF_LEN_SLOPE + ROOF_T    # along-slope length of sheet
roof = cq.Workplane("XY").box(roof_w, roof_d, ROOF_T)

# Centre the sheet at mean rafter top, then tilt
roof_cen_z = RAF_CEN_Z + FR_D / 2 + ROOF_T / 2

asm.add(
    roof,
    name="roof_sheet",
    loc=cq.Location(
        cq.Vector(SPAN_W / 2, RAF_CEN_Y, roof_cen_z),
        cq.Vector(1, 0, 0),
        -SLOPE_DEG,
    ),
    color=C_ROOF,
)

# ── Rebar pegs (12 mm dia, show 400 mm above ground, on outer sleeper faces) ──
rebar_cyl = (
    cq.Workplane("XY")
    .circle(REBAR_D / 2)
    .extrude(REBAR_SHOW)
)

rebar_positions = []
# Outer face of leftmost and rightmost sleepers (resist lateral movement)
for _y in [OV_F, TOTAL_D - OV_F]:
    rebar_positions.append((0,      _y, 0))
    rebar_positions.append((SPAN_W, _y, 0))
# Front and back ends of each interior sleeper (resist fore-aft movement)
for _cx in POST_XS[1:-1]:
    rebar_positions.append((_cx, 0,       0))
    rebar_positions.append((_cx, TOTAL_D, 0))

for i, (rx, ry, rz) in enumerate(rebar_positions):
    asm.add(
        rebar_cyl,
        name=f"rebar_{i}",
        loc=cq.Location(cq.Vector(rx, ry, rz)),
        color=C_RB,
    )

# ── Budget sync ───────────────────────────────────────────────────────────────
# Quantities are derived from model parameters above.  Unit prices are read from
# the existing budget.json so they survive re-runs without manual re-entry.

import json as _json
from pathlib import Path as _Path

_noggin_len  = BAY_W - POST_W                            # clear span between posts
_framing_m   = round(
    2  * SPAN_W          / 1000 +                        # wall plates (front + back)
    N_RAF * RAF_LEN_SLOPE / 1000 +                       # rafters (slope length each)
    (N_SL - 1) * 2 * _noggin_len / 1000,                 # noggins (2 rows × n bays)
    1
)
_paling_qty  = math.ceil(SPAN_W / 100) + 2              # boards needed + 2 spare
_roof_sheets = math.ceil((SPAN_W + 2 * OV_S) / 760)     # 760 mm effective coverage/sheet
_brackets    = N_SL * 2 * 2                              # 2 per post, posts on 2 faces
_coach_qty   = N_SL * 2                                  # 2 per sleeper (optional tie-down)

# (name, computed qty, unit)
_COMPUTED = [
    ("H4 sleepers 200×50",                                               round(N_SL * SL_L / 1000, 1), "meters"),
    ("H4 posts 100×100×2400 (front posts)",                              N_SL,              "each"),
    ("H4 posts 100×100×1800 (back posts)",                               N_SL,              "each"),
    ("90×45 CCA treated pine (plates rafters noggins)",                  _framing_m,        "meters"),
    ("75×75 galv angle brackets",                                        _brackets,         "each"),
    ("12mm rebar 1.2m pegs",                                             len(rebar_positions), "each"),
    ("Roofing screws hex head 65mm box/100",                             1,                 "box"),
    ("Joist hanger nails 40mm 1kg box",                                  1,                 "box"),
    ("Coach screws M10×100 (sleeper-to-rebar tie-down, optional)",       _coach_qty,        "each"),
    ("Rough-sawn paling 100×18mm×1500mm (vertical back wall cladding)", _paling_qty,        "each"),
    ("Corrugated roofing iron 810×3300mm sheet",                         _roof_sheets,      "each"),
]

_budget_path = _Path(__file__).parent.parent / "budget.json"
if _budget_path.exists():
    _budget  = _json.loads(_budget_path.read_text())
    _by_name = {item["name"]: item for item in _budget["items"]}

    _new_items = []
    for _name, _qty, _unit in _COMPUTED:
        _existing   = _by_name.get(_name, {})
        _unit_price = _existing.get("unit_price", 0.0)
        _new_items.append({
            "name":       _name,
            "qty":        float(_qty),
            "unit":       _unit,
            "unit_price": _unit_price,
            "subtotal":   round(_unit_price * _qty, 2),
            "added":      _existing.get("added", "2026-04-15"),
        })

    _budget["items"] = _new_items
    _budget_path.write_text(_json.dumps(_budget, indent=2, ensure_ascii=False) + "\n")

    _total = sum(i["subtotal"] for i in _new_items)
    print(f"Budget synced  : {len(_new_items)} items  total ${_total:.2f}")

# ── Export ────────────────────────────────────────────────────────────────────
show_object = asm
