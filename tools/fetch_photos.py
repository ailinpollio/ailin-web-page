#!/usr/bin/env python3
"""Renueva las miniaturas de fotos desde tu portfolio de Adobe.

    pip install Pillow
    python3 tools/fetch_photos.py
    python3 tools/fetch_photos.py --por-galeria 3

Baja unas fotos de cada galería, las recorta en cuadrado y las guarda en
assets/img/photos/. Las imágenes quedan alojadas en tu propio repositorio a
propósito: enlazar al CDN de Adobe sería más cómodo pero la página dependería
de que ese servicio siga en pie y no cambie las direcciones.

A diferencia de fetch_letterboxd.py, este NO corre en GitHub Actions: se usa
a mano, cuando quieras cambiar la selección.
"""

from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
import argparse
import re
import sys

PORTFOLIO = "https://ailinpollio.myportfolio.com"
GALERIAS = ["landscapes", "people", "urban"]
DESTINO = Path(__file__).resolve().parent.parent / "assets" / "img" / "photos"
LADO = 420          # px del lado de la miniatura cuadrada
CALIDAD = 82

CABECERAS = {"User-Agent": "Mozilla/5.0 (ailin-web-page)"}


def bajar(url: str) -> bytes:
    with urlopen(Request(url, headers=CABECERAS), timeout=60) as r:
        return r.read()


def fotos_de(galeria: str) -> list[str]:
    """Direcciones de las fotos de una galería, sin repetir."""
    html = bajar(f"{PORTFOLIO}/{galeria}").decode("utf-8", "replace")
    # Adobe publica varios anchos por foto; 600 alcanza y sobra para una miniatura
    urls = re.findall(r"https://cdn\.myportfolio\.com/\S+?_rw_600\.jpg\?h=\w+", html)
    vistas, unicas = set(), []
    for u in urls:
        clave = u.split("/")[-1].split("_rw_")[0]
        if clave not in vistas:
            vistas.add(clave)
            unicas.append(u)
    return unicas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--por-galeria", type=int, default=2,
                    help="cuántas fotos tomar de cada galería (por defecto 2)")
    args = ap.parse_args()

    try:
        from PIL import Image
    except ImportError:
        print("  Falta Pillow:  pip install Pillow")
        return 1

    DESTINO.mkdir(parents=True, exist_ok=True)
    n = 0

    for galeria in GALERIAS:
        try:
            urls = fotos_de(galeria)
        except Exception as exc:
            print(f"  /{galeria}: no se pudo leer ({exc})")
            continue

        print(f"  /{galeria}: {len(urls)} fotos, tomo {args.por_galeria}")
        for url in urls[:args.por_galeria]:
            n += 1
            im = Image.open(BytesIO(bajar(url))).convert("RGB")
            w, h = im.size
            lado = min(w, h)                     # recorte cuadrado, centrado
            im = im.crop(((w - lado) // 2, (h - lado) // 2,
                          (w + lado) // 2, (h + lado) // 2))
            im = im.resize((LADO, LADO), Image.LANCZOS)

            ruta = DESTINO / f"foto-{n}.jpg"
            im.save(ruta, quality=CALIDAD, optimize=True, progressive=True)
            print(f"    {ruta.name}  {ruta.stat().st_size / 1024:.0f} KB  (original {w}×{h})")

    if not n:
        print("  No se bajó ninguna foto.")
        return 1

    print(f"\n  {n} miniaturas en assets/img/photos/")
    print("  Acordate de actualizar los alt en personal.html: describen cada")
    print("  foto y hay que reescribirlos si cambiaste la selección.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
