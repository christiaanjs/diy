#!/usr/bin/env python3
"""
export.py — export a project model to STEP, STL, or DXF.

Usage:
  python export.py <project>                   flat STEP of last-modified model
  python export.py <project> <model>           specific model file (stem or .py)
  python export.py <project> --format stl      STL output
  python export.py <project> --format dxf      DXF output (flat shapes only)
  python export.py <project> --assembly        structured STEP assembly (preserves hierarchy)
  python export.py <project> --split           one STEP file per named component

  --assembly and --split only apply to cq.Assembly objects.
  --out <dir> overrides the output directory (default: projects/<slug>/exports/).
"""

import sys
import argparse
import traceback
import importlib.util
from pathlib import Path

PROJECTS_DIR = Path(__file__).parent / "projects"


def die(msg: str):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def load_model(filepath: Path):
    spec = importlib.util.spec_from_file_location("model", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    obj = getattr(mod, "show_object", None)
    if obj is None:
        die("Model ran without errors but did not set show_object.")
    return obj


def resolve_model_path(slug: str, model_name: str | None) -> Path:
    proj_dir = PROJECTS_DIR / slug
    if not proj_dir.exists():
        die(f"Project '{slug}' not found.")
    models_dir = proj_dir / "models"
    if model_name:
        stem = model_name.removesuffix(".py")
        fp = models_dir / f"{stem}.py"
        if not fp.exists():
            die(f"Model file not found: {fp}")
        return fp
    py_files = sorted(models_dir.glob("*.py"), key=lambda f: f.stat().st_mtime)
    if not py_files:
        die(f"No .py files found in {models_dir}")
    return py_files[-1]


def to_shape(obj):
    """Normalise a show_object value to a bare CadQuery Shape/Compound."""
    import cadquery as cq
    if isinstance(obj, cq.Assembly):
        return obj.toCompound()
    if isinstance(obj, cq.Workplane):
        return obj.val()
    return obj  # already a Shape / Compound


def iter_components(asm):
    """Yield (name, shape) for every named leaf component in an Assembly tree.

    Shapes are returned in their local coordinate system so each part can be
    imported flat into CAM software.
    """
    import cadquery as cq
    if asm.obj is not None:
        name = asm.name or "unnamed"
        obj = asm.obj
        shape = obj.val() if isinstance(obj, cq.Workplane) else obj
        yield name, shape
    for child in asm.children:
        yield from iter_components(child)


def export_step_flat(shape, path: Path):
    shape.exportStep(str(path))
    print(f"  wrote {path}")


def export_step_assembly(asm, path: Path):
    """Export a structured AP214 STEP file preserving the assembly hierarchy."""
    asm.save(str(path), exportType="STEP")
    print(f"  wrote {path}")


def export_step_split(asm, exports_dir: Path, stem: str):
    """Export one STEP file per named component."""
    seen: dict[str, int] = {}
    count = 0
    for name, shape in iter_components(asm):
        suffix = seen.get(name, 0)
        seen[name] = suffix + 1
        filename = f"{stem}_{name}" + (f"_{suffix}" if suffix else "") + ".step"
        path = exports_dir / filename
        shape.exportStep(str(path))
        print(f"  wrote {path}")
        count += 1
    return count


def export_stl(obj, path: Path):
    import cadquery as cq
    if isinstance(obj, cq.Assembly):
        obj.toCompound().exportStl(str(path))
    elif isinstance(obj, cq.Workplane):
        obj.exportStl(str(path))
    else:
        obj.exportStl(str(path))
    print(f"  wrote {path}")


def export_dxf(obj, path: Path):
    import cadquery as cq
    if isinstance(obj, cq.Assembly):
        die("DXF export is not supported for Assembly objects — use a flat Workplane.")
    if isinstance(obj, cq.Workplane):
        obj.val().exportDxf(str(path))
    else:
        obj.exportDxf(str(path))
    print(f"  wrote {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Export a CadQuery project model to STEP, STL, or DXF.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("project", help="Project slug (subdirectory of projects/)")
    parser.add_argument("model", nargs="?", help="Model file stem or filename (optional)")
    parser.add_argument(
        "--format", choices=["step", "stl", "dxf"], default="step",
        help="Export format (default: step)",
    )
    parser.add_argument(
        "--assembly", action="store_true",
        help="Structured STEP: preserve Assembly hierarchy in one file",
    )
    parser.add_argument(
        "--split", action="store_true",
        help="Split STEP: one file per named Assembly component",
    )
    parser.add_argument(
        "--out", metavar="DIR",
        help="Output directory (default: projects/<slug>/exports/)",
    )
    args = parser.parse_args()

    if args.assembly and args.split:
        die("--assembly and --split are mutually exclusive.")

    filepath = resolve_model_path(args.project, args.model)
    stem = filepath.stem

    exports_dir = Path(args.out) if args.out else PROJECTS_DIR / args.project / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

    print(f"Project : {args.project}")
    print(f"Model   : {filepath.relative_to(Path(__file__).parent)}")
    print(f"Output  : {exports_dir}")
    print("─" * 60)

    try:
        show_object = load_model(filepath)
    except Exception:
        print("\nBuild FAILED\n")
        traceback.print_exc()
        sys.exit(1)

    import cadquery as cq
    is_assembly = isinstance(show_object, cq.Assembly)

    if args.format == "stl":
        export_stl(show_object, exports_dir / f"{stem}.stl")

    elif args.format == "dxf":
        export_dxf(show_object, exports_dir / f"{stem}.dxf")

    else:  # step
        if args.split:
            if not is_assembly:
                print("warning: --split requested but show_object is not a cq.Assembly; "
                      "falling back to flat STEP.")
                export_step_flat(to_shape(show_object), exports_dir / f"{stem}.step")
            else:
                n = export_step_split(show_object, exports_dir, stem)
                print(f"─" * 60)
                print(f"Exported {n} component(s).")
                return

        elif args.assembly:
            if not is_assembly:
                print("warning: --assembly requested but show_object is not a cq.Assembly; "
                      "falling back to flat STEP.")
                export_step_flat(to_shape(show_object), exports_dir / f"{stem}.step")
            else:
                export_step_assembly(show_object, exports_dir / f"{stem}.step")

        else:
            export_step_flat(to_shape(show_object), exports_dir / f"{stem}.step")

    print("─" * 60)
    print("Export OK")


if __name__ == "__main__":
    main()
