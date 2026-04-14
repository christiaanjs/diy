"""
Firewood Shelter — parametric CadQuery model.

Foundation : 3 × H4 sleepers 200×75×2400, running front-to-back
Posts      : 6 × H4 100×75 — front 1800 mm, back 1400 mm (skillion slope)
Framing    : 90×45 — wall plates, rafters @ 600 mm centres, back-wall noggins
Cladding   : rough-sawn paling on back wall
Roof       : skillion corrugated iron (modelled as a flat sheet, correct slope angle)
Open face  : front — no framing, full access for stacking / retrieval

Coordinate system
  X  left → right  (looking at the open front)
  Y  front → back
  Z  ground → sky
"""
import cadquery as cq
import math

# ── Parameters ────────────────────────────────────────────────────────────────

# Sleepers — H4 treated 200 × 75
SL_W  = 200     # width  (left-right when positioned)
SL_H  = 50      # height (standing on edge is not typical — these lay flat)
SL_L  = 2400    # length (front-to-back)

# Sleeper layout
N_SL  = 3       # number of sleepers
BAY_W = 1200    # centre-to-centre spacing  →  total frame width = 2 400

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

# Rafters
N_RAF = 5       # number of rafters (incl. two edge rafters)

# Back-wall paling
PAL_T = 18      # paling board thickness

# Roof sheet
ROOF_T = 1.0    # corrugated iron (modelled flat)

# Rebar pegs: 12 mm dia, 1 200 mm long, ~400 mm proud of ground
REBAR_D    = 12
REBAR_L    = 1200
REBAR_SHOW = 400  # portion above ground that is visible

# ── Derived ───────────────────────────────────────────────────────────────────
TOTAL_W = BAY_W * (N_SL - 1)   # 2 400
TOTAL_D = SL_L                  # 2 400

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
SLOPE_RUN  = TOTAL_D                     # 2 400 mm
SLOPE_DEG  = math.degrees(math.atan2(SLOPE_RISE, SLOPE_RUN))  # ≈ 9.46°
SLOPE_RAD  = math.radians(SLOPE_DEG)

print(f"Roof slope : {SLOPE_DEG:.1f}°  ({SLOPE_RISE}/{SLOPE_RUN} mm)")
print(f"Frame width: {TOTAL_W} mm   depth: {TOTAL_D} mm")

# Sleeper-centred X positions of posts
POST_XS = [i * BAY_W + SL_W / 2 for i in range(N_SL)]   # [100, 1300, 2500]

# Full width span of top members (sleeper-face to sleeper-face)
SPAN_W = TOTAL_W + SL_W    # 2 600

# Rafter X positions (evenly spaced, outermost over edge sleepers)
RAF_XS = [POST_XS[0] + i * (TOTAL_W / (N_RAF - 1)) for i in range(N_RAF)]

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
# Board count: ceil(SPAN_W / 100) = ceil(2 600 / 100) = 26 boards + 2 spare = 28 total.
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

rebar_positions = [
    # Left face of leftmost sleeper
    (0,         OV_F,         0),
    (0,         TOTAL_D - OV_F, 0),
    # Right face of rightmost sleeper
    (SPAN_W,    OV_F,         0),
    (SPAN_W,    TOTAL_D - OV_F, 0),
    # Front and back ends of middle sleeper (outer face of end grain)
    (POST_XS[1], 0,            0),
    (POST_XS[1], TOTAL_D,      0),
    # Extra pegs on left/right sleeper ends to resist fore-aft movement
    (POST_XS[0], 0,            0),
    (POST_XS[0], TOTAL_D,      0),
]

for i, (rx, ry, rz) in enumerate(rebar_positions):
    asm.add(
        rebar_cyl,
        name=f"rebar_{i}",
        loc=cq.Location(cq.Vector(rx, ry, rz)),
        color=C_RB,
    )

# ── Export ────────────────────────────────────────────────────────────────────
show_object = asm
