#!/usr/bin/env python3
"""
generate-index.py — build a self-contained HTML gallery from all project previews.

Scans projects/*/preview*.png and embeds each image as a base64 data URI so
the output gallery.html works when opened from an unzipped artifact with no
server required.

Usage:
  python generate-index.py              # writes gallery.html in repo root
  python generate-index.py --out a.html # custom output path
"""

import base64
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECTS_DIR = Path(__file__).parent / "projects"
DEFAULT_OUT = Path(__file__).parent / "gallery.html"

VIEW_ORDER = ["preview", "preview-front", "preview-back", "preview-side",
              "preview-left", "preview-top"]
VIEW_LABELS = {
    "preview": "Isometric",
    "preview-front": "Front",
    "preview-back": "Back",
    "preview-side": "Side (right)",
    "preview-left": "Left",
    "preview-top": "Top",
}


def img_tag(path: Path) -> str:
    data = base64.b64encode(path.read_bytes()).decode()
    return f'<img src="data:image/png;base64,{data}" alt="{path.stem}">'


def project_title(slug: str) -> str:
    readme = PROJECTS_DIR / slug / "README.md"
    if readme.exists():
        for line in readme.read_text().splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return slug.replace("-", " ").title()


def build_gallery(out: Path) -> None:
    slugs = sorted(p.name for p in PROJECTS_DIR.iterdir() if p.is_dir())
    if not slugs:
        print("No projects found.", file=sys.stderr)
        sys.exit(1)

    sections = []
    for slug in slugs:
        proj = PROJECTS_DIR / slug
        title = project_title(slug)

        cards = []
        for stem in VIEW_ORDER:
            png = proj / f"{stem}.png"
            if png.exists():
                label = VIEW_LABELS.get(stem, stem)
                cards.append(f"""
          <figure>
            <figcaption>{label}</figcaption>
            {img_tag(png)}
          </figure>""")

        if not cards:
            continue

        sections.append(f"""
    <section>
      <h2>{title}</h2>
      <p class="slug">{slug}</p>
      <div class="grid">{"".join(cards)}
      </div>
    </section>""")

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Woodworking Previews</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: system-ui, sans-serif;
      background: #111;
      color: #ddd;
      padding: 2rem 1.5rem;
    }}
    h1 {{ font-size: 1.6rem; margin-bottom: 0.25rem; color: #fff; }}
    .meta {{ font-size: 0.8rem; color: #777; margin-bottom: 2.5rem; }}
    section {{ margin-bottom: 3rem; }}
    h2 {{ font-size: 1.25rem; color: #c8a96e; margin-bottom: 0.2rem; }}
    .slug {{ font-size: 0.75rem; color: #555; margin-bottom: 1rem; font-family: monospace; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 1rem;
    }}
    figure {{
      background: #1e1e1e;
      border: 1px solid #333;
      border-radius: 6px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    figcaption {{
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #888;
      padding: 0.4rem 0.6rem;
      border-bottom: 1px solid #2a2a2a;
    }}
    figure img {{
      width: 100%;
      height: auto;
      display: block;
      background: #fff;
    }}
  </style>
</head>
<body>
  <h1>Woodworking Previews</h1>
  <p class="meta">Generated {generated} &mdash; {len(sections)} project(s)</p>
{"".join(sections)}
</body>
</html>
"""
    out.write_text(html, encoding="utf-8")
    print(f"Gallery written to {out}  ({len(sections)} project(s))")


if __name__ == "__main__":
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else DEFAULT_OUT
    build_gallery(out)
