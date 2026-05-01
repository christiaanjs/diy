#!/usr/bin/env python3
"""
generate-index.py — build a multi-page static preview site.

Outputs:
  <out-dir>/index.html              overview with project cards
  <out-dir>/<slug>/index.html       per-project detail page (all views)
  <out-dir>/<slug>/<stem>.png       preview images (copied)
  <out-dir>/projects.json           [{slug, title}, ...] for CI tooling

Usage:
  python generate-index.py                  # writes to _site/
  python generate-index.py --out-dir DIR    # custom output directory
"""

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECTS_DIR = Path(__file__).parent / "projects"

VIEW_ORDER = [
    ("preview",       "Isometric"),
    ("preview-front", "Front"),
    ("preview-back",  "Back"),
    ("preview-side",  "Side (right)"),
    ("preview-left",  "Left"),
    ("preview-top",   "Top"),
]

_SHARED_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: system-ui, sans-serif;
  background: #111;
  color: #ddd;
  padding: 2rem 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}
a { color: #c8a96e; text-decoration: none; }
a:hover { text-decoration: underline; }
h1 { font-size: 1.6rem; margin-bottom: 0.25rem; color: #fff; }
h2 { font-size: 1.3rem; color: #c8a96e; margin-bottom: 1rem; }
.meta { font-size: 0.8rem; color: #666; margin-bottom: 2.5rem; }
.back { font-size: 0.85rem; margin-bottom: 1.5rem; }
"""

_INDEX_CSS = _SHARED_CSS + """
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
}
.card {
  background: #1e1e1e;
  border: 1px solid #2e2e2e;
  border-radius: 8px;
  overflow: hidden;
  display: block;
  transition: border-color 0.15s;
}
.card:hover { border-color: #c8a96e; }
.card img { width: 100%; height: auto; display: block; background: #fff; }
.card-body { padding: 0.75rem 1rem; }
.card-title { font-size: 1rem; color: #eee; font-weight: 600; }
"""

_PROJECT_CSS = _SHARED_CSS + """
.views {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}
figure {
  background: #1e1e1e;
  border: 1px solid #2e2e2e;
  border-radius: 6px;
  overflow: hidden;
}
figcaption {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #888;
  padding: 0.4rem 0.6rem;
  border-bottom: 1px solid #252525;
}
figure img { width: 100%; height: auto; display: block; background: #fff; }
"""


def _project_title(slug: str) -> str:
    readme = PROJECTS_DIR / slug / "README.md"
    if readme.exists():
        for line in readme.read_text().splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return slug.replace("-", " ").title()


def _render_index(projects: list[dict], generated: str) -> str:
    cards = "".join(f"""
    <a class="card" href="{p['slug']}/">
      <img src="{p['slug']}/preview.png" alt="{p['title']}">
      <div class="card-body">
        <div class="card-title">{p['title']}</div>
      </div>
    </a>""" for p in projects)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Woodworking Projects</title>
  <style>{_INDEX_CSS}</style>
</head>
<body>
  <h1>Woodworking Projects</h1>
  <p class="meta">Generated {generated} &mdash; {len(projects)} project(s)</p>
  <div class="grid">{cards}
  </div>
</body>
</html>
"""


def _render_project(title: str, views: list[tuple[str, str]], generated: str) -> str:
    figs = "".join(f"""
    <figure>
      <figcaption>{label}</figcaption>
      <img src="{stem}.png" alt="{label}">
    </figure>""" for stem, label in views)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — Woodworking</title>
  <style>{_PROJECT_CSS}</style>
</head>
<body>
  <p class="back"><a href="../">← All Projects</a></p>
  <h2>{title}</h2>
  <p class="meta">Generated {generated}</p>
  <div class="views">{figs}
  </div>
</body>
</html>
"""


def build_site(out_dir: Path) -> list[dict]:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out_dir.mkdir(parents=True, exist_ok=True)

    slugs = sorted(p.name for p in PROJECTS_DIR.iterdir() if p.is_dir())
    projects = []

    for slug in slugs:
        src = PROJECTS_DIR / slug
        dst = out_dir / slug

        views = [(stem, label) for stem, label in VIEW_ORDER
                 if (src / f"{stem}.png").exists()]
        if not views:
            continue

        dst.mkdir(parents=True, exist_ok=True)
        for stem, _ in views:
            shutil.copy2(src / f"{stem}.png", dst / f"{stem}.png")

        title = _project_title(slug)
        (dst / "index.html").write_text(
            _render_project(title, views, generated), encoding="utf-8"
        )
        projects.append({"slug": slug, "title": title})

    if not projects:
        print("No projects with previews found.", file=sys.stderr)
        sys.exit(1)

    (out_dir / "index.html").write_text(
        _render_index(projects, generated), encoding="utf-8"
    )
    (out_dir / "projects.json").write_text(
        json.dumps(projects, indent=2), encoding="utf-8"
    )
    return projects


if __name__ == "__main__":
    out = (
        Path(sys.argv[sys.argv.index("--out-dir") + 1])
        if "--out-dir" in sys.argv
        else Path("_site")
    )
    projects = build_site(out)
    print(f"Site written to {out}/  ({len(projects)} project(s))")
    for p in projects:
        print(f"  {p['slug']}/  →  {p['title']}")
