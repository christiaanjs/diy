"""
Garage Workbench — parametric CadQuery model.

All timber is 90 × 45 mm H3.2 structural pine — the standard rough-sawn
framing section used in NZ house construction.  Buy it off the framing
rack at any Mitre 10 / Bunnings; no dressing or facing required.
Dimensions are nominal — actual cross-section varies ±2–3 mm per piece.

Structure:
  Top        : single 18 mm structural plywood sheet (shortened when PEGBOARD)
  Legs       : 90 × 45 mm pine — front pair at bench height, back pair
               extended above the work surface when PEGBOARD is on
  Aprons     : 90 × 45 mm pine — long front/back + short end aprons
  Lower shelf: 18 mm structural plywood, inset between legs
  Stretchers : 90 × 45 mm pine — long + end pairs supporting shelf
  Pegboard   : optional — 6 mm hardboard in a perimeter frame formed by
               the extended back legs + back top rail

Joinery: 75 mm construction screws toe-nailed from inside + PVA throughout — face grain to
         face grain at every joint, no end grain, no crossing screw paths, no jigs needed.

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

# Pegboard — set False to omit entirely
PEGBOARD = True
PB_T     = 6     # panel thickness (6 mm hardboard)
PB_H     = 600   # panel height above work surface

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

# When PEGBOARD: back legs extend above the work surface; top is shortened to clear them.
LEG_H_B = (BENCH_H + PB_H) if PEGBOARD else LEG_H
TOP_D   = BENCH_D - LEG_D if PEGBOARD else BENCH_D

# ── Colours ───────────────────────────────────────────────────────────────────
C_LEG   = cq.Color(0.66, 0.48, 0.30)   # pine — same as all framing
C_FRAME = cq.Color(0.66, 0.48, 0.30)   # pine framing (aprons / stretchers)
C_PLY   = cq.Color(0.82, 0.72, 0.50)   # plywood top and shelf
C_PEG   = cq.Color(0.45, 0.32, 0.20)   # hardboard pegboard

asm = cq.Assembly()

# ── Legs ──────────────────────────────────────────────────────────────────────
front_leg = cq.Workplane("XY").box(LEG_W, LEG_D, LEG_H)
back_leg  = cq.Workplane("XY").box(LEG_W, LEG_D, LEG_H_B)
for cx, cy, name in [(LEG_CX_L, LEG_CY_F, "FL"), (LEG_CX_R, LEG_CY_F, "FR")]:
    asm.add(
        front_leg,
        name=f"leg_{name}",
        loc=cq.Location(cq.Vector(cx, cy, LEG_H / 2)),
        color=C_LEG,
    )
for cx, cy, name in [(LEG_CX_L, LEG_CY_B, "BL"), (LEG_CX_R, LEG_CY_B, "BR")]:
    asm.add(
        back_leg,
        name=f"leg_{name}",
        loc=cq.Location(cq.Vector(cx, cy, LEG_H_B / 2)),
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

# ── Work surface ──────────────────────────────────────────────────────────────
# TOP_D is shortened to clear the back legs when PEGBOARD is on.
top_layer = cq.Workplane("XY").box(BENCH_W, TOP_D, TOP_T)
for i in range(TOP_LAYERS):
    z = LEG_H + TOP_T * i + TOP_T / 2
    asm.add(
        top_layer,
        name=f"top_layer_{i}",
        loc=cq.Location(cq.Vector(BENCH_W / 2, TOP_D / 2, z)),
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

# ── Pegboard (optional) ───────────────────────────────────────────────────────
if PEGBOARD:
    # Back top rail — spans between the extended back legs at the top of the panel,
    # completing the perimeter frame the hardboard panel screws into.
    pb_top_rail = cq.Workplane("XY").box(APR_LONG_LEN, APR_T, APR_H)
    asm.add(
        pb_top_rail,
        name="pb_top_rail",
        loc=cq.Location(cq.Vector(APR_LONG_CX, BENCH_D - LEG_D - APR_T / 2, BENCH_H + PB_H - APR_H / 2)),
        color=C_FRAME,
    )
    pb = cq.Workplane("XY").box(BENCH_W, PB_T, PB_H)
    asm.add(
        pb,
        name="pegboard",
        loc=cq.Location(cq.Vector(
            BENCH_W / 2,
            BENCH_D - LEG_D - PB_T / 2,   # flush against the front face of the back legs
            BENCH_H + PB_H / 2,            # sits directly above the work surface
        )),
        color=C_PEG,
    )

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"Overall        : {BENCH_W} W × {BENCH_D} D × {BENCH_H} H mm")
print(f"Leg height     : front {LEG_H} mm / back {LEG_H_B} mm")
print(f"Shelf at       : {SHELF_Z} mm (top face)")
print(f"Top surface    : {BENCH_W}×{TOP_D}×{TOP_T} mm  ({TOP_LAYERS} layer)")
print(f"Apron span     : {APR_LONG_LEN} mm (long)  ×  {APR_SHORT_LEN} mm (short)")
print(f"Pegboard       : {'%d W × %d H × %d T mm' % (BENCH_W, PB_H, PB_T) if PEGBOARD else 'omitted'}")

# ── Budget & build-plan sync ──────────────────────────────────────────────────

import math as _math
import json as _json
from pathlib import Path as _Path

_framing_exact_m = (
    2 * LEG_H + 2 * LEG_H_B                   # front + back legs (may differ)
    + 2 * APR_LONG_LEN + 2 * APR_SHORT_LEN   # aprons
    + 2 * APR_LONG_LEN + 2 * APR_SHORT_LEN   # stretchers (same spans)
    + (APR_LONG_LEN if PEGBOARD else 0)        # back top rail
) / 1000
_framing_buy_m = int(round(_framing_exact_m)) + 1

_COMPUTED = [
    ("90×45 H3.2 rough-sawn framing pine — legs, aprons, stretchers", _framing_buy_m, "meters"),
    ("18mm F8 structural plywood 2400×1200 — top and shelf", 2, "sheets"),
    ("75mm construction screws (box 100) — all frame joints, top and shelf", 1, "box"),
    ("PVA wood glue 1L", 1, "each"),
    ("6mm hardboard 1800×900mm sheet — pegboard", 1 if PEGBOARD else 0, "each"),
    ("30mm screws (box 50) — pegboard mounting", 1 if PEGBOARD else 0, "box"),
]

_budget_path = _Path(__file__).parent.parent / "budget.json"
if _budget_path.exists():
    _budget = _json.loads(_budget_path.read_text())
    _by_name = {item["name"]: item for item in _budget["items"]}
    _new_items = []
    for _name, _qty, _unit in _COMPUTED:
        _existing = _by_name.get(_name, {})
        _unit_price = _existing.get("unit_price", 0.0)
        _new_items.append({
            "name": _name,
            "qty": float(_qty),
            "unit": _unit,
            "unit_price": _unit_price,
            "subtotal": round(_unit_price * _qty, 2),
            "added": _existing.get("added", "2026-05-01"),
        })
    _budget["items"] = _new_items
    _budget_path.write_text(_json.dumps(_budget, indent=2, ensure_ascii=False) + "\n")
    _total = sum(i["subtotal"] for i in _new_items)
    print(f"Budget synced  : {len(_new_items)} items  total ${_total:.2f}")

_STR_BOT_Z = int(SHELF_Z - SHELF_T - STR_H)

_steps = []
_steps.append(
    "**Buy rough-sawn framing timber** — Purchase 90×45 H3.2 rough-sawn framing pine from the framing rack "
    "(not the dressed joinery section). This is standard house-framing stock — cheaper, widely available, and "
    "perfectly adequate for a workbench. Wear gloves when handling green treated timber. Sight down each length "
    "and reject anything badly bowed or twisted; a slight crown is fine. Actual cross-sections run ±2–3 mm from "
    "nominal — this makes no difference for toe-nailed butt-joint construction."
)
if PEGBOARD:
    _steps.append(
        f"**Cut legs to length** — Cross-cut 2 front legs at {LEG_H} mm and 2 back legs at {LEG_H_B} mm using a "
        "handsaw. Mark a square line around all four faces before each cut. Keep front and back legs in separate "
        "bundles — they look similar until you measure them."
    )
else:
    _steps.append(
        f"**Cut legs to length** — Cross-cut 4 legs at {LEG_H} mm using a handsaw. Mark a square line around all "
        "four faces with a combination square before cutting. Bundle the 4 legs and check they are the same length."
    )
_pb_rail_cut = (
    f"   - 1× {APR_LONG_LEN} mm (back top rail — pegboard frame top)\n"
    if PEGBOARD else ""
)
_steps.append(
    f"**Cut aprons and stretchers** — Cross-cut the remaining 90×45 to:\n"
    f"   - 2× {APR_LONG_LEN} mm (long aprons)\n"
    f"   - 2× {APR_SHORT_LEN} mm (short aprons)\n"
    f"   - 2× {APR_LONG_LEN} mm (long stretchers)\n"
    f"   - 2× {APR_SHORT_LEN} mm (short stretchers)\n"
    f"{_pb_rail_cut}\n"
    "   Label each piece immediately — aprons and stretchers are the same length per pair but live at different heights."
)
_steps.append(
    f"**Mark the leg joint positions** — On each leg, mark two lines with a square:\n"
    f"   - Apron shoulder: {APR_H} mm down from the top (the apron top face is flush with the leg top).\n"
    f"   - Stretcher shoulder: {_STR_BOT_Z} mm up from the bottom "
    f"(stretcher bottom face = {_STR_BOT_Z} mm; top face = {SHELF_Z - SHELF_T} mm; shelf top = {SHELF_Z} mm)."
    + ("\n   Mark all 4 legs at these positions — both joints are the same height on front and back legs." if PEGBOARD else "")
)
_steps.append(
    f"**Build the end frames** — For each of the two end frames (left and right):\n\n"
    f"   a. Lay one front leg and one back leg on the floor parallel, {APR_SHORT_LEN} mm apart (inside-face to inside-face).\n\n"
    "   b. Clamp a short apron across the top between the legs, top faces flush, inside face of apron flush with "
    "the inside face of each leg. Check square by measuring both diagonals.\n\n"
    "   c. Toe-nail 3× 75 mm construction screws per joint from **inside the frame**: tilt the drill to ~30° and "
    "start each screw on the **inside face** of the apron, about 20–25 mm back from the joint end, angling into "
    "the leg face — one angled up, one angled down, one roughly straight. The screw travels through apron face "
    "grain and bites into leg face grain — no end grain involved. Apply PVA to the joint face first. A 3 mm pilot "
    "at the same angle prevents splitting.\n\n"
    "   d. Repeat for the short stretcher at the lower position.\n\n"
    "   e. Stand the end frame up. Build the second end frame identically."
)
_steps.append(
    f"**Connect the end frames with long aprons and stretchers** — Stand both end frames upright "
    f"{APR_LONG_LEN} mm apart (inside-face to inside-face) and prop them vertical.\n\n"
    "   a. Fit the two long aprons front and back. Clamp them in position and check the frame is square "
    "(measure diagonals across the top opening).\n\n"
    "   b. Working from **inside the frame**, toe-nail 3× 75 mm construction screws per joint: tilt the drill "
    "to ~30°, start each screw on the **inside face** of the apron about 20–25 mm from the end, angling into "
    "the leg face — one angled up, one angled down, one straight. Apply a dab of PVA to the joint face first.\n\n"
    "   c. Fit the long stretchers the same way.\n\n"
    "   d. Recheck square and adjust if needed (a diagonal tap with a hammer usually corrects a few mm)."
)
if PEGBOARD:
    _steps.append(
        f"**Fit the back top rail** — Toe-nail the {APR_LONG_LEN} mm back top rail between the tops of the two "
        "extended back legs, flush with their top faces and with the front face of the legs — facing the "
        "workspace. This completes the pegboard perimeter frame. 3× 75 mm screws per joint from behind."
    )
_top_cut_note = (
    f"{BENCH_W}×{TOP_D} mm (shortened to clear the extended back legs)"
    if PEGBOARD else f"{BENCH_W}×{TOP_D} mm"
)
_pb_panel_cut = (
    f" From the hardboard sheet, cut the pegboard panel: {BENCH_W}×{PB_H} mm."
    if PEGBOARD else ""
)
_steps.append(
    f"**Cut sheet materials** — From sheet 1, cut the top: {_top_cut_note}. "
    f"From sheet 2, cut the shelf: {SHELF_W}×{SHELF_D} mm.{_pb_panel_cut} "
    "A circular saw with a clamped straight-edge gives a clean straight cut; alternatively ask the timber yard "
    "to rip the sheets for you."
)
if PEGBOARD:
    _steps.append(
        f"**Attach the top** — Place the {BENCH_W}×{TOP_D} mm plywood top on the frame flush with the front "
        "and side faces, butting its back edge against the front faces of the extended back legs. Drive 75 mm "
        "construction screws at an angle through the top edge of each apron up into the underside of the plywood "
        "— 3 screws per long apron and 2 per short apron."
    )
else:
    _steps.append(
        "**Attach the top** — Place the plywood top on the frame, centred side-to-side. Drive 75 mm construction "
        "screws at an angle through the top edge of each apron up into the underside of the plywood — 3 screws per "
        "long apron and 2 per short apron. No countersink needed; the screw head pulls into pine."
    )
_steps.append(
    "**Fit the shelf** — Drop the shelf panel onto the stretchers. Drive 2× 75 mm screws per stretcher through "
    "the shelf into the stretcher top face to hold it captive."
)
if PEGBOARD:
    _steps.append(
        f"**Mount the pegboard** — Slide the {BENCH_W}×{PB_H} mm hardboard panel into the frame against the "
        f"front faces of the back legs, facing the workspace: bottom edge resting on the work surface, top edge "
        f"against the back top rail, side edges flush with the outer faces of the back legs. Pre-drill 3 mm "
        f"pilot holes through the {PB_T} mm hardboard into each back leg (at ⅓ and ⅔ of the panel height) and "
        "into the back top rail near the quarter-points. Drive 30 mm screws from the front face."
    )
_steps.append(
    "**Finish** — The H3.2 treated pine needs no additional finish for a garage environment. Round any sharp "
    "corners with a few passes of 80-grit sandpaper. The plywood top can be left bare and will harden with use, "
    "or apply 2 coats of boiled linseed oil for moisture resistance."
)

_leg_cut_rows = (
    f"| Front leg | 2 | {LEG_H} | 90 | 45 | 90×45 H3.2 pine | 90 mm face runs left-right |\n"
    f"| Back leg | 2 | {LEG_H_B} | 90 | 45 | 90×45 H3.2 pine | Extended — pegboard frame uprights |"
    if PEGBOARD else
    f"| Leg | 4 | {LEG_H} | 90 | 45 | 90×45 H3.2 pine | 90 mm face runs left-right |"
)
_pb_frame_rows = (
    f"\n| Back top rail | 1 | {APR_LONG_LEN} | 90 | 45 | 90×45 pine | Pegboard frame top |\n"
    f"| Pegboard | 1 | {BENCH_W} | {PB_H} | {PB_T} | 6 mm hardboard | Mount on back face |"
    if PEGBOARD else ""
)
_pb_ply_note = (
    f"\n**Pegboard:** 1 sheet of 1800×900×6 mm hardboard, cut to {BENCH_W}×{PB_H} mm."
    if PEGBOARD else ""
)
_pb_notes_item = (
    "- **Pegboard frame:** The two extended back legs and back top rail form a rigid perimeter. "
    "The hardboard panel screws into all four sides — no bowing under tool loads.\n"
    if PEGBOARD else
    "- **Pegboard:** The model supports an optional pegboard — set `PEGBOARD = True` to include it in the build.\n"
)
_pb_future = (
    ""
    if PEGBOARD else
    " Peg-board or plywood tool storage can be screwed directly to the back apron."
)

_steps_text = "\n\n".join(f"{i + 1}. {s}" for i, s in enumerate(_steps))

_plan_text = f"""# Garage Workbench — Build Plan

## Tools required

### Power tools
- Drill/driver (pilot holes and driving construction screws)
- Circular saw or jigsaw (cutting plywood sheet to size) — optional; a panel saw at the timber yard can do this

### Hand tools
- Handsaw (cross-cutting 90×45 framing to length — no table saw needed)
- Tape measure, combination square, pencil
- Clamps — 4× F-clamps or G-clamps (600 mm jaw sufficient)
- Hammer (for tapping joints square)

### Jigs & accessories
- Straight-edge or clamping guide for circular saw (plywood cuts)
- 3 mm HSS drill bit (optional pilot holes for toe-nailed screws — prevents splitting near ends)

---

## Cut list

| Part | Qty | L (mm) | W (mm) | T (mm) | Material | Notes |
|------|-----|--------|--------|--------|----------|-------|
{_leg_cut_rows}
| Long apron | 2 | {APR_LONG_LEN} | 90 | 45 | 90×45 pine | Front and back, top |
| Short apron | 2 | {APR_SHORT_LEN} | 90 | 45 | 90×45 pine | Left and right ends, top |
| Long stretcher | 2 | {APR_LONG_LEN} | 90 | 45 | 90×45 pine | Front and back, lower |
| Short stretcher | 2 | {APR_SHORT_LEN} | 90 | 45 | 90×45 pine | Left and right ends, lower |
| Top | 1 | {BENCH_W} | {TOP_D} | {TOP_T} | 18 mm F8 ply | Work surface |
| Lower shelf | 1 | {SHELF_W} | {SHELF_D} | {SHELF_T} | 18 mm F8 ply | Inset between legs |{_pb_frame_rows}

**Framing total:** {_framing_exact_m:.1f} m of 90×45 mm — buy {_framing_buy_m} m to allow for end cuts.

**Plywood:** 2 sheets of 2400×1200×{TOP_T} mm F8 structural ply.
Sheet 1 → top ({BENCH_W}×{TOP_D}). Sheet 2 → shelf ({SHELF_W}×{SHELF_D}) with offcut to spare.{_pb_ply_note}

---

## Build steps

{_steps_text}

---

## Notes

- **No facing / milling:** Rough-sawn framing timber needs nothing done to it. Just cut to length.
- **Assembly order:** Build end frames on the floor first — it is far easier to keep joints square when the pieces are lying flat. Stand them up only when both frames are complete.
- **Square check:** After every glue-and-screw step, measure both diagonals. Equal diagonals = square frame. A 2 mm difference is acceptable; correct anything over 4 mm by tapping a corner before the glue sets.
- **Toe-nailing technique:** Start each screw about 20–25 mm back from the joint face on the inside face of the apron or stretcher. Tilt the drill to approximately 30°. A 3 mm pilot hole at the same angle prevents splitting near the ends. Three screws per joint — one angled up, one angled down, one roughly straight — gives good pull-out resistance with no screws entering end grain and no crossing paths inside any timber section.
- **Leg orientation:** The 90 mm face of each leg faces left-right (visible from the front), the 45 mm face goes front-to-back. This keeps the bench shallow and saves material while maintaining good load-bearing capacity.
{_pb_notes_item}- **Future upgrades:** A face vice (Record #52 or similar) bolts to the left-end apron. The 90 mm apron face provides a good clamping surface.{_pb_future}
"""

_plan_path = _Path(__file__).parent.parent / "build-plan.md"
_plan_path.write_text(_plan_text)
print(f"Build plan updated: {_plan_path.name}")

# ── Export ────────────────────────────────────────────────────────────────────
show_object = asm
