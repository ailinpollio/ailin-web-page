#!/usr/bin/env python3
"""Servidor de desarrollo con recarga automática.

    python3 dev.py            # abre http://localhost:8000 en el navegador
    python3 dev.py --port 9000
    python3 dev.py --no-open

Cada vez que guardás un .html, .css o .js, la pestaña se refresca sola.
Sólo escucha en 127.0.0.1, así que no queda expuesto en la red.

El script de recarga se inyecta al vuelo y NUNCA toca los archivos del disco:
lo que subís a GitHub no lo incluye.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import sys
import threading
import time
import webbrowser

ROOT = Path(__file__).resolve().parent
WATCH_SUFFIXES = {".html", ".css", ".js", ".svg", ".json"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}

RELOAD_SNIPPET = """
<!-- inyectado por dev.py — no existe en los archivos del repo -->
<script>
(function(){
  var es = new EventSource("/__reload");
  es.onmessage = function(e){ if (e.data === "reload") location.reload(); };
  es.onerror = function(){
    // el servidor se cayó: reintentar hasta que vuelva
    es.close();
    var t = setInterval(function(){
      fetch("/__ping", {cache:"no-store"})
        .then(function(){ clearInterval(t); location.reload(); })
        .catch(function(){});
    }, 700);
  };
})();
</script>
"""


def fingerprint() -> str:
    """Estado del árbol de archivos: cambia si algo se guarda, agrega o borra."""
    stamps = []
    for path in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in WATCH_SUFFIXES:
            try:
                stamps.append(f"{path}:{path.stat().st_mtime_ns}")
            except OSError:
                pass
    return json.dumps(sorted(stamps))


class DevHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        if "__reload" in (args[0] if args else ""):
            return
        sys.stderr.write("  %s\n" % (fmt % args))

    def do_GET(self):
        if self.path.startswith("/__reload"):
            return self.stream_reloads()
        if self.path.startswith("/__ping"):
            self.send_response(204)
            self.end_headers()
            return
        return super().do_GET()

    def stream_reloads(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        last = fingerprint()
        try:
            while True:
                time.sleep(0.4)
                current = fingerprint()
                if current != last:
                    last = current
                    self.wfile.write(b"data: reload\n\n")
                else:
                    self.wfile.write(b": keep-alive\n\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def send_head(self):
        """Para HTML: inyecta el snippet de recarga antes de </body>."""
        path = self.translate_path(self.path)
        if Path(path).is_dir():
            for index in ("index.html", "index.htm"):
                candidate = Path(path) / index
                if candidate.is_file():
                    path = str(candidate)
                    break
            else:
                return super().send_head()

        if not path.endswith((".html", ".htm")):
            return super().send_head()

        try:
            body = Path(path).read_bytes()
        except OSError:
            self.send_error(404, "File not found")
            return None

        if b"</body>" in body:
            body = body.replace(b"</body>", RELOAD_SNIPPET.encode() + b"</body>", 1)
        else:
            body += RELOAD_SNIPPET.encode()

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

        import io
        return io.BytesIO(body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-open", action="store_true", help="no abrir el navegador")
    args = parser.parse_args()

    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), DevHandler)
    except OSError as exc:
        print(f"No se pudo usar el puerto {args.port}: {exc}")
        print(f"Probá:  python3 dev.py --port {args.port + 1}")
        return 1

    server.daemon_threads = True
    url = f"http://localhost:{args.port}/"

    print(f"\n  ailin-web-page  ->  {url}")
    print("  Guardá cualquier archivo y el navegador se refresca solo.")
    print("  Ctrl+C para cortar.\n")

    if not args.no_open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Listo.\n")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

