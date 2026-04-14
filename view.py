#!/usr/bin/env python3
"""
view.py — start the live viewer for a project and capture a screenshot.

The screenshot is saved to projects/<slug>/preview.png so Claude Code can
read it and verify the rendered model visually.

Usage:
  python view.py <project>               # start server, take screenshot, open browser
  python view.py <project> --no-browser  # screenshot only, don't open browser
  python view.py <project> --no-shot     # open browser only, no screenshot

Requires: playwright  (pip install playwright && python -m playwright install chromium)
"""

import sys
import time
import signal
import subprocess
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

PROJECTS_DIR = Path(__file__).parent / "projects"
SERVER_PORT  = 5002
SERVER_URL   = f"http://localhost:{SERVER_PORT}"
WAIT_SECONDS = 8    # time to let Three.js finish rendering before screenshot


def die(msg: str):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def wait_for_server(timeout: int = 15) -> bool:
    """Poll /status until the server responds or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urlopen(f"{SERVER_URL}/status", timeout=1)
            return True
        except (URLError, OSError):
            time.sleep(0.4)
    return False


def wait_for_model(timeout: int = 20) -> dict:
    """Poll /status until updated > 0. Returns the final status dict."""
    import json
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            data = json.loads(urlopen(f"{SERVER_URL}/status", timeout=2).read())
            if data.get("updated", 0) > 0:
                return data
        except Exception:
            pass
        time.sleep(0.5)
    return {}


def take_screenshot(path: Path, wait: float = WAIT_SECONDS) -> dict:
    """
    Load the viewer in headless Chromium, capture a screenshot, and
    return a dict with the DOM state:
      { "status": str, "error": str | None, "screenshot": Path | None }
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed — skipping screenshot.")
        print("  pip install playwright && python -m playwright install chromium")
        return {"status": "unknown", "error": None, "screenshot": None}

    print(f"  Waiting {wait}s for WebGL to render…")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(SERVER_URL)
        page.wait_for_timeout(int(wait * 1000))
        page.screenshot(path=str(path))

        # Read the UI overlay text from the DOM
        status_text = page.text_content("#status") or ""
        error_text  = page.text_content("#error")  or ""

        browser.close()

    result = {
        "status":     status_text.strip(),
        "error":      error_text.strip() or None,
        "screenshot": path,
    }
    print(f"  Viewer status : {result['status']}")
    if result["error"]:
        print(f"  Viewer error  : {result['error']}")
    print(f"  Screenshot    : {path}")
    return result


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    slug        = args[0]
    open_browser = "--no-browser" not in args
    do_shot      = "--no-shot"    not in args

    proj_dir = PROJECTS_DIR / slug
    if not proj_dir.exists():
        die(f"Project '{slug}' not found.")

    shot_path = proj_dir / "preview.png"

    # ── Kill any existing server on the port ─────────────────────────────────
    port = int(SERVER_URL.rsplit(":", 1)[-1])
    subprocess.run(
        ["lsof", "-ti", f":{port}"],
        capture_output=True, text=True
    ).stdout.strip().split("\n")
    existing = subprocess.run(
        ["lsof", "-ti", f":{port}"], capture_output=True, text=True
    ).stdout.strip()
    if existing:
        for pid in existing.split("\n"):
            try:
                subprocess.run(["kill", pid.strip()], check=False)
            except Exception:
                pass
        time.sleep(0.5)

    # ── Start server ──────────────────────────────────────────────────────────
    print(f"Starting server for '{slug}'…")
    server = subprocess.Popen(
        [sys.executable, "server.py", slug, "--port", str(SERVER_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if not wait_for_server():
        server.terminate()
        die("Server did not start within 15 s.")

    print(f"  Server ready at {SERVER_URL}")

    status = wait_for_model()
    if not status:
        print("  Warning: model may not have loaded yet (continuing anyway).")
    elif status.get("error"):
        print(f"  Build error   : {status['error']}")
    else:
        print("  Model built OK.")

    # ── Screenshot + DOM error extraction ────────────────────────────────────
    viewer_result = {}
    if do_shot:
        viewer_result = take_screenshot(shot_path)
        if viewer_result.get("error"):
            print(f"\n  !! Viewer reported an error — check preview.png and error above.")

    # ── Open browser ─────────────────────────────────────────────────────────
    if open_browser:
        import webbrowser
        webbrowser.open(SERVER_URL)
        print(f"  Browser opened: {SERVER_URL}")

    # ── Keep server alive until Ctrl-C ────────────────────────────────────────
    if open_browser:
        print("\nServer running. Ctrl-C to stop.\n")
        try:
            server.wait()
        except KeyboardInterrupt:
            pass
    else:
        # screenshot-only mode — shut down immediately after capture
        pass

    server.terminate()
    server.wait()
    print("Done.")


if __name__ == "__main__":
    main()
