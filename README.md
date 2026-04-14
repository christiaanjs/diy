# DIY Woodworking — CadQuery Design Environment

Parametric woodworking models in Python (CadQuery), with a live 3D browser viewer and per-project budget tracking.

## Structure

```
diy/
├── setup.sh              ← run once to install deps + create viewer
├── requirements.txt
├── budget.py             ← project + budget management CLI
├── server.py             ← live viewer (pass project slug as arg)
├── viewer/
│   └── index.html        ← Three.js viewer (shared across projects)
└── projects/
    └── <project-slug>/
        ├── budget.json   ← materials budget
        ├── models/       ← CadQuery .py files
        └── exports/      ← .step / .dxf / .stl outputs
```

## Setup (once)

```bash
chmod +x setup.sh
./setup.sh
```

## Creating a project

```bash
python budget.py new "Workshop Cabinet"
# → creates projects/workshop-cabinet/
```

## Budget management

```bash
# Add a line item:  add <project> <item> <qty> <unit_price> [unit]
python budget.py add workshop-cabinet "Pine plywood 18mm" 3 285.00 sheet
python budget.py add workshop-cabinet "Wood screws 4x40" 2 45.00 box
python budget.py add workshop-cabinet "Piano hinge 900mm" 1 120.00 piece

# View project budget:
python budget.py list workshop-cabinet

# Totals across all projects:
python budget.py summary

# Remove a line item by index:
python budget.py remove workshop-cabinet 2
```

## Live viewer

```bash
source .venv/bin/activate
python server.py workshop-cabinet
# → http://localhost:5000
```

Add `.py` files to `projects/workshop-cabinet/models/` — the viewer auto-refreshes on save.

## Troubleshooting

| Problem | Fix |
|---|---|
| `import cadquery` fails | `source .venv/bin/activate` |
| Project not found | Run `python budget.py new "..."` first |
| Viewer shows blank | Check terminal for Python errors |
| GLTF export error | `pip install --upgrade cadquery` (need ≥ 2.4) |
| Port 5000 in use | Change `port=5000` in `server.py` |
| Model not refreshing | Save the file — watchdog triggers on write |
