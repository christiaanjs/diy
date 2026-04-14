# CadQuery Woodworking — Claude Code Brief

You are helping design woodworking projects using CadQuery.

## Project structure

Each build lives in its own directory:

```
projects/<slug>/
├── README.md       ← project description, goals, and status (keep up to date)
├── budget.json     ← materials budget (managed via budget.py)
├── build-plan.md   ← step-by-step build instructions and tool list
├── viewer.json     ← optional viewer settings (background colour, etc.)
├── preview.png     ← latest screenshot captured by view.py
├── models/         ← CadQuery .py files (one per component or assembly)
└── exports/        ← .step / .dxf / .stl outputs
```

The viewer (`viewer/index.html`) and server (`server.py`) are shared across all projects.

## Workflow

1. Create a project (if it doesn't exist):
   ```
   python budget.py new "Project Name"
   ```
2. Write/edit model files in `projects/<slug>/models/`
3. Test before the user views it:
   ```
   python projects/<slug>/models/filename.py
   ```
4. Take a preview screenshot to visually inspect the model:
   ```
   python view.py <slug> --no-browser
   ```
   This starts the server, waits for WebGL to render, captures `projects/<slug>/preview.png`,
   and shuts down. Read the screenshot with the Read tool to verify the geometry looks correct
   before handing off to the user. Use `python view.py <slug>` (without `--no-browser`) to
   also open the live viewer in a browser.
5. Start the viewer for a project (live, interactive):
   ```
   python server.py <slug>
   ```
6. Write or update `projects/<slug>/README.md` whenever a project is created or its models,
   budget, or build plan change significantly. See the README section below for the format.
7. Generate a build plan at `projects/<slug>/build-plan.md` covering:
   - **Tools required** — list every hand tool, power tool, and jig needed
   - **Step-by-step instructions** — ordered build sequence referencing part names and dimensions from the model
   - **Joint/joinery callouts** — note the technique (dado, mortise & tenon, pocket hole, etc.) at each step
   - **Tips** — any grain direction, assembly order, or clamping considerations
8. Export:
   ```python
   result.val().exportStep("projects/<slug>/exports/part.step")   # CAM
   result.val().exportDxf("projects/<slug>/exports/part.dxf")     # 2D cutting
   result.exportStl("projects/<slug>/exports/part.stl")            # 3D printing
   ```

## Build plan

Generate `projects/<slug>/build-plan.md` whenever a project's models are complete or significantly updated. Use this structure:

```markdown
# <Project Name> — Build Plan

## Tools required
### Power tools
- ...
### Hand tools
- ...
### Jigs & accessories
- ...

## Cut list
| Part | Qty | L (mm) | W (mm) | T (mm) | Notes |
|------|-----|--------|--------|--------|-------|
| ...  |     |        |        |        |       |

## Build steps
1. **Mill stock** — ...
2. **Cut to size** — ...
3. **Cut joinery** — ...
4. **Dry fit** — ...
5. **Glue up** — ...
6. **Final assembly** — ...
7. **Finishing** — ...

## Notes
- Assembly order, clamping strategy, grain direction considerations, etc.
```

Derive part names, quantities, and dimensions directly from the model parameters. Keep steps ordered so each one builds on the last.

## Project README

Create `projects/<slug>/README.md` when a project is first created. Update it whenever models, the budget, or the build plan change significantly. Use this structure:

```markdown
# <Project Name>

<One-paragraph description of what the piece is, what it's for, and any design intent.>

## Status
<!-- one of: planning | modelling | ready-to-build | complete -->
**planning**

## Dimensions
- Overall: W × D × H mm
- Key parts: ...

## Materials
- Primary: e.g. 18mm birch plywood
- Secondary: ...

## Joinery
- e.g. dado joints for shelves, pocket-hole face frame

## Notes
- Any design decisions, constraints, or open questions.
```

## Budget management

```bash
python budget.py add <slug> "<item>" <qty> <unit_price> [unit]
python budget.py list <slug>
python budget.py remove <slug> <index>
python budget.py summary        # all projects
```

When the user mentions buying materials, add them to the budget automatically.

## Viewer config

Create `projects/<slug>/viewer.json` to customise the Three.js viewer for a project. All fields are optional — omitted fields fall back to the viewer default.

```json
{
  "background": "#1a1a2e"
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `background` | CSS hex string | `"#1a1a2e"` | Scene and page background colour |

The server reads `viewer.json` on every `/status` poll, so changes take effect in the live viewer without a restart.

## Python environment

`setup.sh` chooses one of two paths:

| Path | When | How it activates |
|------|------|-----------------|
| **pyenv-virtualenv** | `cadquery` virtualenv exists | `.python-version` written to repo root; pyenv auto-activates in every subshell |
| **`.venv`** | fallback | must be activated manually once per session: `source .venv/bin/activate` |

With the pyenv path (the default on this machine), `python` resolves correctly in any subshell without an explicit activation prefix. All commands below assume this. If using `.venv`, activate it once before running any `python` commands.

## Stack

Python + CadQuery (OCCT kernel). Use **mm**. Standard stock is **18mm (3/4")**.

## Model file conventions

- Always use parametric variables at the top of each file
- Each file must set: `show_object = <CadQuery Workplane or Shape>`
- For assemblies: `show_object = assy.toCompound()` where `assy` is `cq.Assembly()`
- The server picks up the **last modified** `.py` file in the project's `models/` on startup

## Common woodworking patterns

### Dado joint (shelf groove)
```python
import cadquery as cq

thickness = 18
width, depth, height = 400, 300, 200
dado_depth = 6

box = cq.Workplane("XY").box(width, depth, height).shell(-thickness)

shelf_z = 80
dado = (
    cq.Workplane("XY")
    .transformed(offset=(0, depth/2 - thickness/2, shelf_z))
    .box(width - thickness*2, dado_depth, thickness)
)

result = box.cut(dado)
show_object = result
```

### Mortise & tenon
```python
import cadquery as cq

tenon_l, tenon_w, tenon_h = 40, 35, 15

rail = cq.Workplane("XY").box(200, 50, 50)
tenon = cq.Workplane("YZ").workplane(offset=100).box(tenon_l, tenon_w, tenon_h)
rail_with_tenon = rail.union(tenon)

stile = cq.Workplane("XY").box(50, 50, 400)
mortise = cq.Workplane("YZ").workplane(offset=-25).box(tenon_l + 1, tenon_w + 0.5, tenon_h + 0.5)
stile_with_mortise = stile.cut(mortise)

show_object = rail_with_tenon
```

Other patterns: finger joints (alternating cuts on mating edges), pocket holes (angled cylindrical cuts).
