from pathlib import Path
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "index.html"
TARGETS = ["publications.html", "cv.html", "personal.html"]

BLOCKS = [
    ("riel", re.compile(r'<aside class="rail">.*?</aside>', re.S)),
    ("pie", re.compile(r'<footer class="site-footer">.*?</footer>', re.S)),
]

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="no escribir; salir con código 1 si algo difiere")
    args = parser.parse_args()

    source_html = SOURCE.read_text(encoding="utf-8")
    canonical = {}
    for name, pattern in BLOCKS:
        match = pattern.search(source_html)
        if not match:
            print(f"No encontré el bloque «{name}» en index.html. "
                  f"¿Le cambiaste la clase?")
            return 2
        canonical[name] = match.group(0)

    drift = False
    for target_name in TARGETS:
        target = ROOT / target_name
        if not target.exists():
            print(f"  {target_name}: no existe, lo salteo")
            continue

        html = target.read_text(encoding="utf-8")
        original = html
        changed = []

        for name, pattern in BLOCKS:
            match = pattern.search(html)
            if not match:
                print(f"  {target_name}: falta el bloque «{name}»")
                drift = True
                continue
            if match.group(0) != canonical[name]:
                changed.append(name)
                html = html[:match.start()] + canonical[name] + html[match.end():]

        if html == original:
            print(f"  {target_name}: al día")
            continue

        drift = True
        if args.check:
            print(f"  {target_name}: desactualizado ({', '.join(changed)})")
        else:
            target.write_text(html, encoding="utf-8")
            print(f"  {target_name}: actualizado ({', '.join(changed)})")

    if args.check and drift:
        print("\nCorré  python3 tools/sync_shell.py  para sincronizar.")
        return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
