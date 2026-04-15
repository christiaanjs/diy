# Firewood Shelter — Build Plan

Sized for **{{ FIREWOOD_VOL_M3 }} m³** of firewood
({{ STACK_ROWS }} rows × {{ TOTAL_W }} mm = {{ (STACK_ROWS * TOTAL_W / 1000) | round(1) }} m linear stacking length;
target {{ linear_m | round(1) }} m at {{ STACK_H_M }} m high × {{ STACK_D_M }} m deep stacks).

## Tools required

### Power tools
- Circular saw (or mitre saw) — framing cuts
- Drill/driver — screws throughout
- SDS hammer drill or angle grinder — driving rebar pegs
{%- if REAR_PALING %}
- Jigsaw — optional, trimming paling
{% endif %}
### Hand tools
- Tape measure and square
- Level (1.2 m or longer)
- String line and pegs — layout
- Hammer — {% if REAR_PALING %}nailing paling and noggins{% else %}toe-nailing and driving rebar{% endif %}
- Sledgehammer — driving rebar
- Clamps × 4 — holding plates while fixing
- Pencil and marking knife

### Jigs & accessories
- Post holder / post level — plumbing posts
- Saw horses × 2
- Safety glasses, hearing protection, gloves

---

## Cut list

| Part | Qty | L (mm) | W (mm) | T (mm) | Notes |
|------|-----|--------|--------|--------|-------|
| Sleeper | {{ N_SL }} | {{ SL_L }} | {{ SL_W }} | {{ SL_H }} | H4 treated |
| Front post | {{ N_SL }} | {{ PH_F }} | {{ POST_W }} | {{ POST_D }} | H4 treated |
| Back post | {{ N_SL }} | {{ PH_B }} | {{ POST_W }} | {{ POST_D }} | H4 treated |
| Front wall plate | 1 | {{ SPAN_W }} | {{ FR_T }} | {{ FR_D }} | 90×45 CCA pine, laid flat ({{ FR_D }} mm vertical) |
| Back wall plate | 1 | {{ SPAN_W }} | {{ FR_T }} | {{ FR_D }} | 90×45 CCA pine, laid flat |
| Rafter | {{ N_RAF }} | {{ raf_len_slope }} | {{ FR_T }} | {{ FR_D }} | Along-slope length; 90×45 CCA pine |
{% if REAR_PALING %}| Back-wall noggin | {{ nog_qty }} | {{ noggin_len }} | {{ FR_T }} | {{ FR_D }} | 90×45 CCA pine; {{ n_bays }} bay{{'s' if n_bays > 1 else ''}} × 2 rows |
{% endif %}
{% if REAR_PALING %}| Paling board | {{ pal_needed }} | {{ pal_h }} | 100 | {{ PAL_T }} | Rough-sawn; trim {{ pal_trim }} mm from 1500 mm stock |
{% else %}| Knee brace | {{ knee_count }} | {{ KNEE_DIAG }} | {{ FR_D }} | {{ FR_T }} | 90×45 CCA pine; 45° cuts both ends; one per upper rear post corner |
{% endif %}| Roof sheet | {{ roof_sheets }} | 3300 | 810 | — | Corrugated iron; cover width ~760 mm lapped |

> Rafter along-slope length = √({{ raf_len_horiz }}² + {{ SLOPE_RISE }}²) ≈ {{ raf_len_slope }} mm. Cut a birdsmouth notch {{ BIRDSMOUTH_DEPTH }} mm deep × {{ BIRDSMOUTH_SEAT }} mm seat at each plate bearing point.
{% if REAR_PALING %}> Paling boards: {{ pal_needed }} needed across {{ SPAN_W }} mm span; {{ paling_qty }} purchased (2 spare).
{% else %}> Knee braces: {{ KNEE_DIAG }} mm long at 45°; {{ knee_count }} total (one per upper rear post corner). No housing required — face-fix with 2× 90 mm structural screws per end.
{% endif %}

---

## Build steps

1. **Set out the site** — Mark the {{ TOTAL_D }} × {{ SPAN_W }} mm footprint with string lines. Check square by measuring diagonals (should match). Confirm the ground is reasonably level; pack low spots if needed.

2. **Position sleepers** — Lay the {{ N_SL }} sleepers parallel, running front-to-back ({{ TOTAL_D }} mm direction), at {{ BAY_W }} mm centre-to-centre. Outermost sleeper faces are {{ SPAN_W }} mm apart. Check they are level with each other; use a long level and packing.

3. **Drive rebar pegs** — Drive rebar pegs tight against the outer sleeper faces (2 pegs per side, at {{ OV_F }} mm from each end) and at the front and back ends of each interior sleeper. {{ rebar_qty }} pegs total. Leave ~{{ REBAR_SHOW }} mm proud. Confirm sleepers cannot shift.

4. **Cut posts to length** — Cut {{ N_SL }} front posts to {{ PH_F }} mm and {{ N_SL }} back posts to {{ PH_B }} mm. Treat cut ends with H4 end-grain preservative. Label F (front) and B (back).

5. **Erect and plumb posts** — Stand each post on the centreline of its sleeper at the front and back edges. Brace temporarily, check plumb on two faces. Fix with 75 × 75 galv angle brackets (2 per post base, one each side). Toe-nail through bracket with 40 mm joist hanger nails.

6. **Fix front wall plate** — Cut the {{ SPAN_W }} mm front plate from 90 × 45. Rest it flat ({{ FR_D }} mm vertical) on top of the {{ N_SL }} front posts, flush with the outer sleeper faces. Clamp, level, then fix with 2 × angle brackets per post. The plate overhangs {{ plate_overhang }} mm each side of the outer posts.

7. **Fix back wall plate** — Repeat for the back plate on the {{ N_SL }} back posts. The back plate sits {{ SLOPE_RISE }} mm lower than the front — this creates the {{ slope_deg }}° skillion slope. Confirm the height difference at each post pair before fixing.

8. **Cut and fix rafters** — Cut {{ N_RAF }} rafters to {{ raf_len_slope }} mm (along-slope). Cut a birdsmouth notch ({{ BIRDSMOUTH_DEPTH }} mm deep × {{ BIRDSMOUTH_SEAT }} mm seat) at each end where the rafter will cross the plate. Place one rafter directly above each post, with {{ raf_intermediates }} intermediate{{'s' if raf_intermediates > 1 else ''}} per bay at {{ raf_spacing }} mm spacing. Seat each rafter into its birdsmouth notch with {{ OV_F }} mm overhang at the front and {{ OV_B }} mm at the rear. Fix with 2× 90 mm structural screws toe-screwed at ~30° through rafter into plate at each end.

{% if REAR_PALING %}9. **Cut and fix back-wall noggins** — Cut {{ nog_qty }} noggins to {{ noggin_len }} mm (clear span between posts). Fix 2 rows per bay at {{ nog_h1 }} mm and {{ nog_h2 }} mm above sleeper top (⅓ and ⅔ of back post height). Face-screw or nail through from post face into noggin end; two fixings per joint.
{% else %}9. *(No noggins — knee braces provide back-wall stability. Skip to step 10.)*
{% endif %}

{% if REAR_PALING %}10. **Nail back-wall paling** — Trim {{ pal_needed }} paling boards from 1500 mm to {{ pal_h }} mm. Start from one end, butt boards tight vertically. Nail each board to the wall plate, both noggin rows, and the bottom rail (4 fixings per board). Keep boards plumb as you work across.
{% else %}10. **Fix back-wall knee braces** — Cut {{ knee_count }} knee braces to {{ KNEE_DIAG }} mm from 90×45 CCA pine. Mark 45° on each face at both ends and crosscut. Fix one brace at each upper inside corner of the rear posts: two 90 mm structural screws through each brace end into the post face and plate face. No housing required.
{% endif %}

11. **Fix roof sheeting** — Lay {{ roof_sheets }} × 810 × 3300 mm corrugated iron sheets across the rafters, starting from the low (rear) end and lapping each sheet over the one below. Lap sheets 1.5 corrugations side-to-side. Fix with 65 mm hex-head roofing screws into every rafter through the crown of the corrugation.

12. **Final checks and treatment** — Apply timber preservative to any untreated cut ends. Check all brackets are fully nailed/screwed. Verify the roof slopes away from the stack (water runs to the back). Clear offcuts and stack the firewood.

---

## Notes

- **Assembly order** — erect all posts before fixing any plates; fix both plates before cutting rafters so you can measure the actual along-slope dimension if anything has shifted.
- **Post plumb** — diagonal bracing with scrap timber between opposite posts during erection keeps things square until the plates are on.
- **Grain/end treatment** — all H4 cut ends must be treated; preservative takes 30 min to dry before assembly.
- **Roof screws** — drive into the crest of each corrugation, not the valley; use the neoprene-washer hex screws included in the box.
{% if REAR_PALING %}- **Paling airflow** — butt-jointed (no gaps) is fine; the open front provides adequate airflow for seasoning. Alternatively leave 5 mm gaps for extra ventilation.
{% else %}- **Open back** — with knee bracing instead of paling the rear wall is open on both sides; ventilation is excellent but the stack is more exposed. Add weed mat or shade cloth if a partial windbreak is needed.
- **Knee brace fixing** — drive 2× 90 mm TimberLok or similar structural screws per end face. Predrill if using hardwood; treated pine typically fine without.
{% endif %}
- **Modular extension** — the shelter is designed to add bays later. When extending, splice new plate sections over the new post and continue roof sheets sideways. The extension-side of the current build should be left without a fascia board.
- **Rebar alternative** — if the ground is rocky, M10 × 100 coach screws driven at an angle through pre-drilled sleeper holes are a softer alternative to rebar.
