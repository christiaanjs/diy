#!/usr/bin/env python3
"""
budget.py — per-project budget tracker for woodworking builds.

Usage:
  python budget.py new "Cabinet Build"
  python budget.py add <project> <item> <qty> <unit_price> [unit]
  python budget.py list <project>
  python budget.py remove <project> <item_index>
  python budget.py price <project> <item_index> <new_unit_price>
  python budget.py summary
"""

import json
import sys
import re
from datetime import date
from pathlib import Path

PROJECTS_DIR = Path(__file__).parent / "projects"


# ── helpers ───────────────────────────────────────────────────────────────────

def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def project_dir(slug: str) -> Path:
    return PROJECTS_DIR / slug


def budget_path(slug: str) -> Path:
    return project_dir(slug) / "budget.json"


def load_budget(slug: str) -> dict:
    p = budget_path(slug)
    if not p.exists():
        die(f"Project '{slug}' not found. Run: python budget.py new \"<name>\"")
    return json.loads(p.read_text())


def save_budget(slug: str, data: dict):
    budget_path(slug).write_text(json.dumps(data, indent=2))


def all_projects() -> list[str]:
    if not PROJECTS_DIR.exists():
        return []
    return sorted(
        d.name for d in PROJECTS_DIR.iterdir()
        if d.is_dir() and (d / "budget.json").exists()
    )


def fmt_money(value: float) -> str:
    return f"${value:,.2f}"


def die(msg: str):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def total(budget: dict) -> float:
    return sum(i["qty"] * i["unit_price"] for i in budget["items"])


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_new(args):
    if not args:
        die("usage: new \"<project name>\"")
    name = " ".join(args)
    slug = slugify(name)
    d = project_dir(slug)
    if d.exists():
        die(f"Project '{slug}' already exists.")
    (d / "models").mkdir(parents=True)
    (d / "exports").mkdir()
    data = {
        "project": name,
        "slug": slug,
        "created": str(date.today()),
        "items": [],
    }
    save_budget(slug, data)
    print(f"Created project: {name}")
    print(f"  Directory : projects/{slug}/")
    print(f"  Models    : projects/{slug}/models/")
    print(f"  Exports   : projects/{slug}/exports/")
    print(f"  Budget    : projects/{slug}/budget.json")
    print(f"\nStart viewer: python server.py {slug}")


def cmd_add(args):
    # add <project> <item name> <qty> <unit_price> [unit]
    if len(args) < 4:
        die("usage: add <project> <item> <qty> <unit_price> [unit]")
    slug, *rest = args
    # item name may be quoted — just take up to the last 2 or 3 positional args
    try:
        if len(rest) >= 4:
            # unit provided
            *name_parts, qty_s, price_s, unit = rest
        else:
            *name_parts, qty_s, price_s = rest
            unit = "unit"
    except ValueError:
        die("usage: add <project> <item> <qty> <unit_price> [unit]")

    try:
        qty = float(qty_s)
        unit_price = float(price_s)
    except ValueError:
        die("<qty> and <unit_price> must be numbers")

    name = " ".join(name_parts)
    budget = load_budget(slug)
    budget["items"].append({
        "name": name,
        "qty": qty,
        "unit": unit,
        "unit_price": unit_price,
        "subtotal": qty * unit_price,
        "added": str(date.today()),
    })
    save_budget(slug, budget)
    print(f"Added: {name}  {qty} × {fmt_money(unit_price)} = {fmt_money(qty * unit_price)}")
    print(f"Project total: {fmt_money(total(budget))}")


def cmd_list(args):
    if not args:
        die("usage: list <project>")
    slug = args[0]
    budget = load_budget(slug)
    items = budget["items"]
    print(f"\n{budget['project']}  (created {budget['created']})")
    if not items:
        print("─" * 40)
        print("  (no items yet)")
        print("─" * 40)
        print()
        return
    name_w = max(len(item["name"]) for item in items)
    idx_w = len(f"[{len(items) - 1}]")
    price_w = max(len(fmt_money(item["unit_price"])) for item in items)
    # chars before "= subtotal": 2 + idx_w + 2 + name_w + 2 + 6 + 1 + 8 + 2 + 2 + price_w + 2 = idx_w + name_w + price_w + 27
    total_label_w = idx_w + name_w + price_w + 25  # so that "  TOTAL..." + "= " aligns with data rows
    rows = []
    for i, item in enumerate(items):
        subtotal = item["qty"] * item["unit_price"]
        rows.append(
            f"  {f'[{i}]':<{idx_w}}  {item['name']:<{name_w}}"
            f"  {item['qty']:>6g} {item.get('unit', 'unit'):<8}"
            f"  @ {fmt_money(item['unit_price']):<{price_w}}"
            f"  = {fmt_money(subtotal)}"
        )
    sep_w = max(len(r) for r in rows)
    print("─" * sep_w)
    for row in rows:
        print(row)
    print("─" * sep_w)
    print(f"  {'TOTAL':<{total_label_w}}= {fmt_money(total(budget))}")
    print()


def cmd_remove(args):
    if len(args) < 2:
        die("usage: remove <project> <item_index>")
    slug, idx_s = args[0], args[1]
    try:
        idx = int(idx_s)
    except ValueError:
        die("<item_index> must be an integer")
    budget = load_budget(slug)
    if idx < 0 or idx >= len(budget["items"]):
        die(f"No item at index {idx}")
    removed = budget["items"].pop(idx)
    save_budget(slug, budget)
    print(f"Removed: {removed['name']}")
    print(f"Project total: {fmt_money(total(budget))}")


def cmd_price(args):
    if len(args) < 3:
        die("usage: price <project> <item_index> <new_unit_price>")
    slug, idx_s, price_s = args[0], args[1], args[2]
    try:
        idx = int(idx_s)
    except ValueError:
        die("<item_index> must be an integer")
    try:
        new_price = float(price_s)
    except ValueError:
        die("<new_unit_price> must be a number")
    budget = load_budget(slug)
    if idx < 0 or idx >= len(budget["items"]):
        die(f"No item at index {idx}")
    item = budget["items"][idx]
    old_price = item["unit_price"]
    item["unit_price"] = new_price
    item["subtotal"] = item["qty"] * new_price
    save_budget(slug, budget)
    print(f"Updated: {item['name']}")
    print(f"  {fmt_money(old_price)} → {fmt_money(new_price)}  ({item['qty']:g} × {fmt_money(new_price)} = {fmt_money(item['subtotal'])})")
    print(f"Project total: {fmt_money(total(budget))}")


def cmd_summary(args):
    projects = all_projects()
    if not projects:
        print("No projects yet. Run: python budget.py new \"<name>\"")
        return
    budgets = {slug: load_budget(slug) for slug in projects}
    name_w = max(len(b["project"]) for b in budgets.values())
    name_w = max(name_w, len("PROJECT"), len("GRAND TOTAL"))
    sep_w = 2 + name_w + 2 + 5 + 2 + 12 + 2 + 10
    grand = 0.0
    print(f"\n  {'PROJECT':<{name_w}}  {'ITEMS':>5}  {'TOTAL':>12}  CREATED")
    print("─" * sep_w)
    for slug in projects:
        budget = budgets[slug]
        t = total(budget)
        grand += t
        print(
            f"  {budget['project']:<{name_w}}  {len(budget['items']):>5}  "
            f"{fmt_money(t):>12}  {budget['created']}"
        )
    print("─" * sep_w)
    print(f"  {'GRAND TOTAL':<{name_w}}  {'':>5}  {fmt_money(grand):>12}")
    print()


# ── dispatch ──────────────────────────────────────────────────────────────────

COMMANDS = {
    "new": cmd_new,
    "add": cmd_add,
    "list": cmd_list,
    "remove": cmd_remove,
    "price": cmd_price,
    "summary": cmd_summary,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        print("Commands:", ", ".join(COMMANDS))
        sys.exit(1)
    COMMANDS[sys.argv[1]](sys.argv[2:])
