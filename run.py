#!/usr/bin/env python3
"""
run.py — build and inspect a project model from the command line.

Usage:
  python run.py <project>              # runs the last-modified model in the project
  python run.py <project> <model>      # runs projects/<project>/models/<model>.py

Output:
  - Any print() output from the model file
  - Bounding box dimensions
  - Assembly component count
  - Success / error summary
"""

import sys
import importlib.util
import traceback
from pathlib import Path

PROJECTS_DIR = Path(__file__).parent / "projects"


def die(msg: str):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def load_model(filepath: Path):
    spec = importlib.util.spec_from_file_location("model", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "show_object", None)


def shape_info(shape) -> str:
    """Return a human-readable summary of a CadQuery shape."""
    import cadquery as cq

    # Bounding box
    bb = shape.BoundingBox()
    w = bb.xmax - bb.xmin
    d = bb.ymax - bb.ymin
    h = bb.zmax - bb.zmin

    lines = [
        f"  Bounding box : {w:.0f} × {d:.0f} × {h:.0f} mm  (W × D × H)",
        f"  X            : {bb.xmin:.0f} → {bb.xmax:.0f}",
        f"  Y            : {bb.ymin:.0f} → {bb.ymax:.0f}",
        f"  Z            : {bb.zmin:.0f} → {bb.zmax:.0f}",
    ]

    # Solid count
    try:
        solids = shape.Solids()
        lines.append(f"  Solids       : {len(solids)}")
    except Exception:
        pass

    return "\n".join(lines)


def run(slug: str, model_name: str | None = None):
    proj_dir = PROJECTS_DIR / slug
    if not proj_dir.exists():
        die(f"Project '{slug}' not found.")

    models_dir = proj_dir / "models"

    if model_name:
        # Allow passing with or without .py extension
        stem = model_name.removesuffix(".py")
        filepath = models_dir / f"{stem}.py"
        if not filepath.exists():
            die(f"Model file not found: {filepath}")
    else:
        py_files = sorted(models_dir.glob("*.py"), key=lambda f: f.stat().st_mtime)
        if not py_files:
            die(f"No .py files in {models_dir}")
        filepath = py_files[-1]

    print(f"Project : {slug}")
    print(f"Model   : {filepath.relative_to(Path(__file__).parent)}")
    print("─" * 60)

    try:
        show_object = load_model(filepath)
    except Exception:
        print("\nBuild FAILED\n")
        traceback.print_exc()
        sys.exit(1)

    if show_object is None:
        die("Model file ran without errors but did not set show_object.")

    print()
    try:
        import cadquery as cq
        if isinstance(show_object, cq.Assembly):
            shape = show_object.toCompound()
        elif isinstance(show_object, cq.Workplane):
            shape = show_object.val()
        else:
            shape = show_object   # already a bare Shape / Compound
        print(shape_info(shape))
    except Exception as e:
        print(f"  (could not inspect shape: {e})")

    print("─" * 60)
    print("Build OK")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    slug       = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else None
    run(slug, model_name)
