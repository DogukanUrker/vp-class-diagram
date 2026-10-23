import json
import subprocess
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import screenshot

KINDS = {"class", "abstract", "interface"}
TYPES = {"generalization", "realization", "dependency", "association", "aggregation", "composition"}
ROUTES = {None, "left", "right"}
RENDERER = Path(__file__).resolve().parent.parent / "assets" / "renderer.html"


def cell_name(cell):
    return cell if isinstance(cell, str) else cell.get("name")


def check(model):
    errors = []
    classes = model.get("classes", [])
    names = [c.get("name") for c in classes]
    known = set(names)
    errors += [f"duplicate class: {n}" for n in sorted({n for n in names if names.count(n) > 1})]
    errors += [f"{c.get('name')}: unknown kind '{c.get('kind')}'" for c in classes if c.get("kind", "class") not in KINDS]

    placed = [cell_name(cell) for row in model.get("layout", []) for cell in row if cell is not None]
    errors += [f"layout: unknown class {n}" for n in placed if n not in known]
    errors += [f"layout: {n} is placed more than once" for n in sorted({n for n in placed if placed.count(n) > 1})]
    errors += [f"layout: {n} is missing" for n in names if n not in placed]

    for r in model.get("relations", []):
        label = f"relation {r.get('from')} -> {r.get('to')}"
        errors += [f"{label}: unknown class {r.get(end)}" for end in ("from", "to") if r.get(end) not in known]
        if r.get("type") not in TYPES:
            errors.append(f"{label}: unknown type '{r.get('type')}'")
        if r.get("route") not in ROUTES:
            errors.append(f"{label}: route must be 'left' or 'right'")
        errors += [f"{label}: {key} must be text" for key in ("fromLabel", "toLabel") if key in r and not isinstance(r[key], str)]

    for group in model.get("sameWidth", []):
        errors += [f"sameWidth: unknown class {n}" for n in group if n not in known]
    return errors


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: build.py <model.json> <out.html>")
    model = json.loads(Path(sys.argv[1]).read_text())
    errors = check(model)
    if errors:
        sys.exit("model errors:\n" + "\n".join(f"- {e}" for e in errors))
    data = json.dumps(model, indent=2).replace("</", "<\\/")
    html = RENDERER.read_text().replace("__TITLE__", escape(model.get("title", "Class Diagram")))
    page = Path(sys.argv[2]).resolve()
    page.write_text(html.replace("__MODEL__", data))
    print(f"wrote {page}")
    png = page.with_suffix(".png")
    try:
        screenshot.report(png, screenshot.take(page, png))
    except (RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"no screenshot: {error}")


if __name__ == "__main__":
    main()
