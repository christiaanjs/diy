#!/usr/bin/env python3
"""
CadQuery live viewer server — per-project edition.

Usage:
  python server.py <project-slug>

Example:
  python server.py my-cabinet

Watches projects/<project-slug>/models/ for .py changes and serves
an auto-refreshing 3D viewer at http://localhost:5000.
"""

import os
import sys
import json
import queue
import time
import argparse
import threading
import importlib.util
import tempfile
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, Response, stream_with_context
from flask_cors import CORS
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ── project setup ─────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("slug", nargs="?")
parser.add_argument("--port", type=int, default=5001)
args, _ = parser.parse_known_args()

if not args.slug:
    print(__doc__)
    sys.exit(1)

PROJECT_SLUG = args.slug
PORT = args.port
PROJECT_DIR  = Path(__file__).parent / "projects" / PROJECT_SLUG
MODEL_DIR    = PROJECT_DIR / "models"
EXPORT_DIR   = PROJECT_DIR / "exports"
VIEWER_DIR   = Path(__file__).parent / "viewer"

if not PROJECT_DIR.exists():
    print(f"error: project '{PROJECT_SLUG}' not found.")
    print(f"  Run: python budget.py new \"<project name>\"")
    sys.exit(1)

EXPORT_DIR.mkdir(exist_ok=True)

# ── app ───────────────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)

current_model = {"glb": None, "error": None, "updated": 0}

VIEWER_CONFIG_PATH = PROJECT_DIR / "viewer.json"

def load_viewer_config() -> dict:
    """Return viewer.json contents, or {} if the file doesn't exist."""
    if VIEWER_CONFIG_PATH.exists():
        try:
            return json.loads(VIEWER_CONFIG_PATH.read_text())
        except Exception:
            return {}
    return {}


# ── SSE client registry ───────────────────────────────────────────────────────

_sse_clients: list[queue.Queue] = []
_sse_lock = threading.Lock()


def push_event(event_type: str, data: dict):
    """Push a named SSE event to every connected browser client."""
    msg = {"type": event_type, "data": data}
    with _sse_lock:
        stale = []
        for q in _sse_clients:
            try:
                q.put_nowait(msg)
            except queue.Full:
                stale.append(q)
        for q in stale:
            _sse_clients.remove(q)


def load_model(filepath: Path):
    spec = importlib.util.spec_from_file_location("model", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "show_object", None)


def export_glb(shape) -> bytes:
    """Export shape to a self-contained binary GLB (no external .bin dependency)."""
    import cadquery as cq
    with tempfile.NamedTemporaryFile(suffix=".glb", delete=False) as f:
        tmp_path = f.name
    # Assembly.export() picks format from the file extension
    if isinstance(shape, cq.Assembly):
        shape.export(tmp_path)
    else:
        assy = cq.Assembly()
        assy.add(shape, name="model")
        assy.export(tmp_path)
    with open(tmp_path, "rb") as f:
        data = f.read()
    os.unlink(tmp_path)
    return data

def rebuild(filepath: Path):
    print(f"  Rebuilding: {filepath.name}")
    try:
        shape = load_model(filepath)
        if shape is None:
            raise ValueError("Model must set:  show_object = <your shape>")
        glb = export_glb(shape)
        current_model.update(glb=glb, error=None, updated=time.time())
        print("  ✓ Model updated")
        push_event("model", {"error": None})
    except Exception as e:
        current_model.update(error=str(e), updated=time.time())
        print(f"  ✗ Error: {e}")
        push_event("model", {"error": str(e)})


class ModelHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            rebuild(Path(event.src_path))

    def on_created(self, event):
        if event.src_path.endswith(".py"):
            rebuild(Path(event.src_path))


class ViewerConfigHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if Path(event.src_path).name == "viewer.json":
            push_event("config", load_viewer_config())

    def on_created(self, event):
        self.on_modified(event)


@app.route("/")
def index():
    return send_from_directory(str(VIEWER_DIR), "index.html")


@app.route("/model.glb")
def model_glb():
    if current_model["glb"]:
        return app.response_class(current_model["glb"], mimetype="model/gltf-binary")
    return jsonify({"error": "No model loaded"}), 404


@app.route("/status")
def status():
    cfg = load_viewer_config()
    return jsonify({
        "project": PROJECT_SLUG,
        "error": current_model["error"],
        "updated": current_model["updated"],
        "background": cfg.get("background"),
    })


@app.route("/events")
def events():
    def stream():
        q: queue.Queue = queue.Queue(maxsize=20)
        with _sse_lock:
            _sse_clients.append(q)
        try:
            # Send current state immediately so the browser doesn't wait for the first event
            cfg = {"project": PROJECT_SLUG, **load_viewer_config()}
            yield f"event: config\ndata: {json.dumps(cfg)}\n\n"
            if current_model["glb"]:
                yield f"event: model\ndata: {json.dumps({'error': None})}\n\n"
            elif current_model["error"]:
                yield f"event: model\ndata: {json.dumps({'error': current_model['error']})}\n\n"

            while True:
                try:
                    msg = q.get(timeout=25)
                    yield f"event: {msg['type']}\ndata: {json.dumps(msg['data'])}\n\n"
                except queue.Empty:
                    yield ": heartbeat\n\n"   # keep the connection alive through proxies
        finally:
            with _sse_lock:
                try:
                    _sse_clients.remove(q)
                except ValueError:
                    pass

    return Response(
        stream_with_context(stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/export/<filename>")
def export_file(filename):
    return send_from_directory(str(EXPORT_DIR), filename)


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    py_files = sorted(MODEL_DIR.glob("*.py"), key=lambda f: f.stat().st_mtime)
    if py_files:
        rebuild(py_files[-1])
    else:
        print(f"  (no .py files in {MODEL_DIR} yet — add one to get started)")

    observer = Observer()
    observer.schedule(ModelHandler(), str(MODEL_DIR), recursive=False)
    observer.schedule(ViewerConfigHandler(), str(PROJECT_DIR), recursive=False)
    observer.start()

    print(f"\n=== CadQuery Live Viewer ===")
    print(f"Project : {PROJECT_SLUG}")
    print(f"Models  : {MODEL_DIR}")
    print(f"Open    : http://localhost:{PORT}")
    print(f"Ctrl+C to stop\n")

    try:
        app.run(port=PORT, debug=False, threaded=True)
    finally:
        observer.stop()
        observer.join()
