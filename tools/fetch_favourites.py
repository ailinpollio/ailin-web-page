#!/usr/bin/env python3
"""Escribe assets/js/films.js con tus películas destacadas de Letterboxd.

    python3 tools/fetch_favourites.py

Para cambiar la selección, editá la lista FAVORITAS de abajo.

Por qué es a mano y no automático: Letterboxd bloquea la lectura de las
páginas de perfil (403 vía Cloudflare), que es donde viven los destacados. Las
páginas de cada película sí son públicas, así que de ahí salen el título, el
año, el director y el póster. Como los destacados cambian una vez cada tanto,
pegar cuatro direcciones cuesta menos que cualquier alternativa.

Ojo con los títulos repetidos: "A Brighter Tomorrow" es a la vez la película
de Yassine Qnia (2021) y la de Nanni Moretti (2023). Por eso la lista guarda
direcciones exactas y no títulos, y el script imprime el director para que
puedas comprobar de un vistazo que trajo la correcta.
"""

from pathlib import Path
from urllib.request import Request, urlopen
import datetime as dt
import json
import re

# ---------------------------------------------------------------------------
# EDITÁ ACÁ: las direcciones de tus destacadas, en el orden en que querés que
# aparezcan. Se copian de la barra del navegador estando en la película.
# ---------------------------------------------------------------------------
FAVORITAS = [
    "https://letterboxd.com/film/the-killing-of-a-sacred-deer/",
    "https://letterboxd.com/film/perfect-blue/",
    "https://letterboxd.com/film/a-brighter-tomorrow-2023/",   # Moretti, no Qnia
    "https://letterboxd.com/film/the-hand-of-god/",
]
# ---------------------------------------------------------------------------

SALIDA = Path(__file__).resolve().parent.parent / "assets" / "js" / "films.js"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def bajar(url: str) -> str:
    pedido = Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urlopen(pedido, timeout=45) as r:
        return r.read().decode("utf-8", "replace")


def leer_pelicula(url: str) -> dict:
    html = bajar(url)

    # Los datos vienen en JSON-LD, más estable que raspar el HTML: si alguna
    # vez rediseñan la página, esto sigue funcionando.
    m = re.search(r'<script type="application/ld\+json">\s*(?:/\*[^*]*\*/)?\s*'
                  r'(\{.*?\})\s*(?:/\*[^*]*\*/)?\s*</script>', html, re.S)
    datos = json.loads(m.group(1)) if m else {}

    # El año no está en el JSON-LD pero sí en og:title -> "Perfect Blue (1997)"
    og = re.search(r'<meta property="og:title" content="([^"]+)"', html)
    anio = None
    if og:
        a = re.search(r"\((\d{4})\)\s*$", og.group(1))
        anio = int(a.group(1)) if a else None

    return {
        "title":    datos.get("name"),
        "year":     anio,
        "director": ", ".join(d.get("name", "") for d in (datos.get("director") or [])),
        "link":     url,
        "poster":   datos.get("image"),
    }


def main() -> int:
    peliculas = []
    for url in FAVORITAS:
        try:
            p = leer_pelicula(url)
        except Exception as exc:
            print(f"  {url}\n    no se pudo leer: {exc}")
            return 1
        if not p["title"] or not p["poster"]:
            print(f"  {url}\n    la página no trajo título o póster")
            return 1
        peliculas.append(p)
        print(f"  {p['title'][:34]:36s} {p['year']}   {p['director'][:26]}")

    texto = "\n".join([
        "/* ==========================================================================",
        "   films.js — GENERADO AUTOMÁTICAMENTE. No lo edites a mano: se reescribe.",
        "",
        "   Tus películas destacadas de Letterboxd.",
        "   Para cambiar cuáles son: editá FAVORITAS en tools/fetch_favourites.py",
        "   y volvé a correrlo.",
        f"   Generado: {dt.date.today().isoformat()}",
        "   ========================================================================== */",
        "",
        "window.FILMS = [",
    ] + ["  " + json.dumps(p, ensure_ascii=False) + "," for p in peliculas] + ["];", ""])

    SALIDA.write_text(texto, encoding="utf-8")
    print(f"\n  films.js actualizado · {len(peliculas)} destacadas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
