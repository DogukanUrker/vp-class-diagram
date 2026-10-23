import json
import re
import shutil
import subprocess
import sys
import tempfile
from html import unescape
from pathlib import Path

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]
CHROME_NAMES = ["google-chrome", "chromium", "chromium-browser", "microsoft-edge"]
SCALE = 2


def find_chrome():
    for path in CHROME_PATHS:
        if Path(path).exists():
            return path
    for name in CHROME_NAMES:
        if shutil.which(name):
            return shutil.which(name)
    raise RuntimeError("no chrome, chromium, edge or brave found")


def run_chrome(binary, profile, *args):
    cmd = [
        binary,
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--hide-scrollbars",
        f"--user-data-dir={profile}",
        *args,
    ]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout


def take(page, out):
    page = Path(page).resolve()
    out = Path(out).resolve()
    binary = find_chrome()
    out.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        dom = run_chrome(binary, profile, "--dump-dom", page.as_uri())
        tag = re.search(r'<svg id="diagram"[^>]*>', dom)
        if not tag:
            raise RuntimeError(f"no diagram found in {page}")
        attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', tag.group(0)))
        width, height = attrs["width"], attrs["height"]
        warnings = json.loads(unescape(attrs.get("data-warnings", "[]")))
        run_chrome(
            binary,
            profile,
            f"--force-device-scale-factor={SCALE}",
            f"--window-size={width},{height}",
            f"--screenshot={out}",
            page.as_uri(),
        )
    if not out.exists():
        raise RuntimeError("chrome did not write the screenshot")
    return width, height, warnings


def report(out, result):
    width, height, warnings = result
    print(f"wrote {out} ({width}x{height}, {SCALE}x scale)")
    print("warnings: " + ("; ".join(warnings) if warnings else "none"))


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit("usage: screenshot.py <diagram.html> [out.png]")
    page = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) == 3 else page.with_suffix(".png")
    try:
        report(out.resolve(), take(page, out))
    except (RuntimeError, subprocess.TimeoutExpired) as error:
        sys.exit(f"screenshot failed: {error}")


if __name__ == "__main__":
    main()
