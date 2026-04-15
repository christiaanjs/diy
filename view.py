#!/usr/bin/env python3
"""
view.py — render a project's model to preview.png using CadQuery's SVG exporter.

Usage:
  python view.py <project>                              # iso view → preview.png
  python view.py <project> --view <name>                # choose viewpoint
  python view.py <project> --output <path>              # custom output path
  python view.py <project> --view front --output a.png  # combine both

Views: iso (default), front, back, side, left, top

Requires: cairosvg  (pip install cairosvg)
          fallbacks: rsvg-convert (brew install librsvg) or inkscape
"""

import sys
import subprocess
from pathlib import Path

PROJECTS_DIR = Path(__file__).parent / "projects"

# projectionDir tuples: direction FROM which the camera views the shape.
# Z is up in all CadQuery models.
VIEWS = {
    "iso": (1.0, -1.0, 1.0),  # CadQuery default — upper-left-front
    "front": (0.0, -1.0, 0.0),  # looking at +Y face (front wall)
    "back": (0.0, 1.0, 0.0),  # looking at -Y face (back wall)
    "side": (1.0, 0.0, 0.0),  # right side, looking along -X
    "left": (-1.0, 0.0, 0.0),  # left side, looking along +X
    "top": (0.0, 0.0, -1.0),  # plan view, looking straight down
}


def die(msg: str):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def find_model_file(proj_dir: Path) -> Path:
    """Return the most recently modified .py file in models/."""
    models_dir = proj_dir / "models"
    py_files = sorted(
        models_dir.glob("*.py"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    if not py_files:
        die(f"No .py model files found in {models_dir}")
    return py_files[0]


def load_show_object(model_file: Path):
    """Execute a model file and return its show_object."""
    src = model_file.read_text()
    namespace = {"__file__": str(model_file), "__name__": "__main__"}
    try:
        exec(compile(src, str(model_file), "exec"), namespace)
    except Exception as e:
        die(f"Model error in {model_file.name}: {e}")
    obj = namespace.get("show_object")
    if obj is None:
        die(f"{model_file.name} does not set show_object")
    return obj


def export_svg(obj, svg_path: Path, view: str = "iso"):
    """Export a CadQuery object to an SVG file with the given viewpoint."""
    import cadquery as cq
    from cadquery.occ_impl.exporters.svg import getSVG
    from cadquery.occ_impl.shapes import Shape

    proj_dir = VIEWS.get(view, VIEWS["iso"])

    # Resolve to a bare Shape — getSVG() takes a Shape, not a Workplane
    if isinstance(obj, cq.Assembly):
        shape = obj.toCompound()
    elif isinstance(obj, cq.Workplane):
        shape = obj.val()
    elif isinstance(obj, Shape):
        shape = obj
    else:
        die(f"show_object is an unrecognised type: {type(obj)}")

    svg_text = getSVG(
        shape,
        opts={
            "width": 1400,
            "height": 900,
            "projectionDir": proj_dir,
            "showAxes": False,
            "showHidden": True,
            "strokeWidth": -1,
            "strokeColor": (0, 0, 0),
            "hiddenColor": (160, 160, 160),
        },
    )
    svg_path.write_text(svg_text)
    print(f"  SVG exported  : {svg_path.name}")


def svg_to_png(svg_path: Path, png_path: Path, width: int = 1400, height: int = 900):
    """Convert SVG → PNG. Tries cairosvg, rsvg-convert, then inkscape.

    CadQuery's SVG template uses scale(s, -s) to flip Y for CAD conventions.
    cairosvg and rsvg-convert render this flipped relative to how a browser would,
    so we correct with a vertical flip after conversion.
    """
    tmp_path = png_path.with_suffix(".tmp.png")

    success = False
    method = ""

    # cairosvg  (pip install cairosvg)
    try:
        import cairosvg

        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(tmp_path),
            output_width=width,
            output_height=height,
            background_color="white",
        )
        success = True
        method = "cairosvg"
    except ImportError:
        pass
    except Exception as e:
        print(f"  cairosvg failed: {e} — trying fallback…")

    # rsvg-convert  (brew install librsvg)
    if not success:
        r = subprocess.run(
            [
                "rsvg-convert",
                "-w",
                str(width),
                "-h",
                str(height),
                "-o",
                str(tmp_path),
                str(svg_path),
            ],
            capture_output=True,
        )
        if r.returncode == 0:
            success = True
            method = "rsvg-convert"

    # Inkscape
    if not success:
        r = subprocess.run(
            [
                "inkscape",
                "--export-type=png",
                f"--export-width={width}",
                f"--export-filename={tmp_path}",
                str(svg_path),
            ],
            capture_output=True,
        )
        if r.returncode == 0:
            success = True
            method = "inkscape"

    if not success:
        die(
            "No SVG-to-PNG converter found.\n"
            "  pip install cairosvg        (recommended)\n"
            "  brew install librsvg        (rsvg-convert)\n"
            "  brew install inkscape"
        )

    # CadQuery's SVG uses scale(s, -s) which SVG renderers flip relative to browsers.
    # Correct with a vertical flip so floor stays at the bottom, roof at the top.
    from PIL import Image

    img = Image.open(tmp_path).transpose(Image.FLIP_TOP_BOTTOM)
    img.save(png_path)
    tmp_path.unlink(missing_ok=True)

    print(f"  PNG saved     : {png_path}  ({method})")


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        print(__doc__)
        sys.exit(1)

    slug = args[0]

    view = "iso"
    if "--view" in args:
        idx = args.index("--view")
        if idx + 1 >= len(args):
            die(f"--view requires a name: {', '.join(VIEWS)}")
        view = args[idx + 1]
        if view not in VIEWS:
            die(f"Unknown view '{view}'. Choose from: {', '.join(VIEWS)}")

    proj_dir = PROJECTS_DIR / slug
    if not proj_dir.exists():
        die(f"Project '{slug}' not found.")

    png_path = proj_dir / "preview.png"
    if "--output" in args:
        idx = args.index("--output")
        if idx + 1 >= len(args):
            die("--output requires a file path")
        png_path = Path(args[idx + 1])

    model_file = find_model_file(proj_dir)
    print(f"  Model         : {model_file.name}  (view: {view})")

    svg_path = proj_dir / "_preview_tmp.svg"

    obj = load_show_object(model_file)
    export_svg(obj, svg_path, view=view)
    svg_to_png(svg_path, png_path)
    svg_path.unlink(missing_ok=True)

    print("Done.")


if __name__ == "__main__":
    main()
