# Fuentes

El sitio usa **Junicode** y nada más: titulares, texto y elementos de interfaz.

Los `.woff2` de esta carpeta son versiones **subseteadas a latín**, generadas
con `tools/build_fonts.py`. Las cuatro variantes pasaron de 1978 KB a 159 KB
(−92 %) sacando los ~3000 glifos medievalistas que Junicode trae y el sitio no
usa.

| Archivo | Peso | Uso |
|---|---|---|
| `junicode-regular.woff2` | 44 KB | texto corriente |
| `junicode-italic.woff2` | 40 KB | énfasis, nombres de revistas |
| `junicode-bold.woff2` | 38 KB | títulos, negritas |
| `junicode-bolditalic.woff2` | 37 KB | ambas cosas |

## Licencia — SIL Open Font License 1.1

Copyright © 1998–2018 Peter S. Baker.

La licencia completa está en [`OFL.txt`](OFL.txt), **y tiene que quedar en el
repo**: la OFL exige distribuir el texto de la licencia junto a la fuente,
incluso cuando la modificás (subsetear cuenta como modificar).

Otras dos condiciones que sí te aplican:

- No podés vender las fuentes por separado (el sitio no lo hace).
- «Junicode» es *Reserved Font Name*: no podés publicar una versión modificada
  usando ese nombre como nombre del font software. Los nombres actuales
  (`junicode-regular.woff2`, familia CSS `"Junicode"`) están bien, porque
  identifican la fuente que estás usando. Si algún día hacés una versión muy
  modificada y la redistribuís como producto propio, renombrala.

## Regenerar los woff2

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install "fonttools[woff]"
python3 tools/build_fonts.py
```

Lee los originales de `../junicode-1/` (fuera del repo). Si movés esa carpeta,
ajustá `SOURCES` en el script.
