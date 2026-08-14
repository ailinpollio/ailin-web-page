from pathlib import Path
from urllib.request import Request, urlopen
import datetime as dt
import json
import re

FAVORITAS = [
    "https://letterboxd.com/film/the-killing-of-a-sacred-deer/",
    "https://letterboxd.com/film/perfect-blue/",
    "https://letterboxd.com/film/a-brighter-tomorrow-2023/",
    "https://letterboxd.com/film/the-hand-of-god/",
]

SALIDA = Path(__file__).resolve().parent.parent / "assets" / "js" / "films.js"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36")

def bajar(url: str) -> str:
    pedido = Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urlopen(pedido, timeout=45) as r:
        return r.read().decode("utf-8", "replace")

def leer_pelicula(url: str) -> dict:
    html = bajar(url)

    m = re.search(r'<script type="application/ld\+json">\s*(?:/\*[^*]*\*/)?\s*'
                  r'(\{.*?\})\s*(?:/\*[^*]*\*/)?\s*</script>', html, re.S)
    datos = json.loads(m.group(1)) if m else {}

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
