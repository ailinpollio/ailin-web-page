# ailin-web-page

Página personal de Ailín Pollio. HTML y CSS a mano, sin framework, sin build
step. Lo que ves en la carpeta es exactamente lo que GitHub Pages sirve.

**Secciones:** About · Publications · CV
**Idiomas:** español e inglés, con selector en el pie
**Tipografía:** Junicode

> **Nunca guardes tokens ni contraseñas en este repo.** Es público: cualquier
> cosa que commitees queda visible, y sigue en el historial de git aunque
> después la borres. Los tokens van en el llavero de macOS, que es donde git
> los deja solo después del primer `push`.

---

## Ver los cambios mientras trabajás

```bash
python3 dev.py
```

Abre `http://localhost:8000` y **cada vez que guardás un archivo, la pestaña se
refresca sola**. No necesitás instalar nada: usa sólo la librería estándar de
Python.

```bash
python3 dev.py --port 9000   # si el 8000 está ocupado
python3 dev.py --no-open     # no abrir el navegador
```

El script de recarga se inyecta al vuelo en la respuesta HTTP; **no toca los
archivos del disco**, así que nunca se te va a colar en lo que subís a GitHub.

> Podrías abrir los `.html` haciendo doble clic, pero no lo hagas: sobre
> `file://` las fuentes no cargan y la lista de publicaciones tampoco. Usá
> siempre `dev.py`.

---

## Cómo cambiar la foto

La foto actual ya está puesta en `assets/img/portrait.jpg` (800×1000, 155 KB),
recortada a 4:5 desde el original que está en la carpeta de arriba.

**Las fotos van en JPG, no en SVG.** Convertir una foto a SVG la vectoriza:
la reduce a miles de contornos de un solo color, queda negra y pesa diez veces
más. El SVG sirve para logos, íconos y dibujos planos.

Para reemplazarla por otra:

1. **Recortala a 4:5** (más alta que ancha) y bajala a ~800×1000 px. En Mac lo
   hacés sin instalar nada, con `sips`:

   ```bash
   # 1) recorte centrado a 4:5 — poné la altura de TU foto y ancho = altura × 0.8
   sips -c 2747 2198 original.jpg --out recortada.jpg
   # 2) achicar a 1000 px de alto y comprimir
   sips -Z 1000 recortada.jpg --out chica.jpg
   sips -s format jpeg -s formatOptions 82 chica.jpg \
        --out ailin-web-page/assets/img/portrait.jpg
   ```

   Apuntá a que quede **abajo de ~200 KB**. Más grande no se ve mejor: en
   pantalla ocupa 208 px de ancho, así que 800 px ya cubre hasta pantallas 3×.

2. **Guardala como `assets/img/portrait.jpg`**, con ese nombre exacto: sin
   tildes, sin espacios, en minúscula.

3. **Actualizá el `alt` en `index.html`.** Aparece **dos veces**, una en el
   bloque en español y otra en el inglés. Es lo que se lee en voz alta para
   quien usa lector de pantalla, y lo que aparece si la imagen no carga.
   Describí qué se ve; no pongas “foto de Ailín”.

4. Si cambian las dimensiones, actualizá también `width` y `height` en el
   `<img>`. No son el tamaño en pantalla (eso lo decide el CSS): le sirven al
   navegador para reservar el espacio y que el texto no salte mientras carga.

**Para cambiarle la forma o el tamaño en pantalla**, tocá `.portrait` en
`assets/css/site.css`: `width` controla cuánto ocupa, `aspect-ratio` el
recorte, y `border-radius` las esquinas (poné `50%` si la querés redonda).

---

## Los dos idiomas

El texto está escrito **dos veces dentro del mismo archivo**, marcado con
`lang="es"` y `lang="en"`. El CSS oculta el idioma que no está activo, así que
el cambio es instantáneo y funciona aunque el JavaScript no cargue.

```html
<p lang="es">Soy investigadora en…</p>
<p lang="en">I am a researcher at…</p>
```

En `index.html` y `cv.html` hay dos bloques grandes marcados con comentarios
(`ESPAÑOL` / `ENGLISH`): editás uno, después el otro. **Si escribís algo nuevo,
acordate de escribirlo en los dos lados** — si sólo lo ponés en uno, en el otro
idioma desaparece.

Qué idioma ve alguien que entra por primera vez: el que tenga el navegador (si
está en inglés, entra en inglés; si no, español). Después queda guardado lo que
elija con el botón.

Tres cosas que no se traducen solas y viven en otro lado:

- **Los nombres de las secciones** (About, Publications, CV) están en inglés a
  propósito en los dos idiomas.
- **El `<title>` y la descripción** de cada página usan `data-es` / `data-en`
  en el `<head>`.
- **Los `aria-label`** (texto invisible para lectores de pantalla) usan
  `data-aria-es` / `data-aria-en`.

---

## Qué editar

Todo lo que falta completar está marcado con `TODO:` en mayúsculas. Para
encontrarlos todos:

```bash
grep -rn "TODO" --include="*.html" --include="*.js" .
```

| Qué querés cambiar | Dónde |
|---|---|
| Tu bio, intereses, datos rápidos | `index.html` (dos veces: es y en) |
| La lista de publicaciones | `assets/js/publications.js` |
| Formación, experiencia, docencia | `cv.html` (dos veces: es y en) |
| Tu foto | ver arriba |
| El PDF del CV | `assets/cv/Ailin-Pollio-CV.pdf` |
| Colores y tipografía | `assets/css/tokens.css` |
| Ancho de la página y del texto | `--shell` y `--measure` en `tokens.css` |
| Layout y componentes | `assets/css/site.css` |
| Nombre, rol, redes (riel izquierdo) | `index.html` → después `sync_shell.py` |

### Las publicaciones

Se arman solas a partir de `assets/js/publications.js`. Copiás un bloque y lo
editás; el sitio agrupa por año y ordena solo. Marcá tu nombre con `*` al final
(`"Pollio, A.*"`) y se resalta con un subrayado verde.

El campo `type` (`journal`, `preprint`, `conference`, `chapter`) alimenta los
botones de filtro. Los títulos **no se traducen** (van como salieron
publicados), pero sí podés traducir `venue`, `note` y el `label` de cada link
agregándoles `_en`:

```js
venue: "[Congreso], [Ciudad]",
venue_en: "[Conference], [City]",
```

### El riel izquierdo está repetido en las tres páginas

Es el costo de no tener build step. **Editá siempre `index.html`** y después:

```bash
python3 tools/sync_shell.py
```

Copia el riel y el pie a `publications.html` y `cv.html`. Con `--check` sólo
avisa si hay diferencias, sin escribir.

---

## Publicar en GitHub Pages

Una sola vez:

```bash
cd ailin-web-page
git init -b main
git add .
git commit -m "Primera versión de la página"
gh repo create ailin-web-page --public --source=. --push
```

(Sin `gh`: creá el repo `ailin-web-page` desde github.com, y después
`git remote add origin https://github.com/ailinpollio/ailin-web-page.git &&
git push -u origin main`.)

Después, en el repo: **Settings → Pages → Source: Deploy from a branch →
`main` / `/ (root)` → Save**.

En un minuto queda en:

```
https://ailinpollio.github.io/ailin-web-page/
```

No hace falta ningún workflow de GitHub Actions: el sitio ya es HTML plano.

Cada cambio posterior:

```bash
git add . && git commit -m "Actualizo la bio" && git push
```

### Si algún día querés dominio propio

Poné el dominio en **Settings → Pages → Custom domain** (crea un archivo
`CNAME`), y acordate de dos cosas:

- En `404.html`, borrá el prefijo `/ailin-web-page/` de los tres links.
- En los `<meta property="og:url">` de cada página, actualizá la URL.

---

## Estructura

```
ailin-web-page/
├── index.html              About (portada)
├── publications.html       lista filtrable
├── cv.html                 línea de tiempo
├── 404.html                autocontenido, sin dependencias
├── dev.py                  servidor local con auto-reload
├── .nojekyll               que GitHub no procese nada
├── assets/
│   ├── css/
│   │   ├── tokens.css      color, tipografía, medidas, idioma
│   │   └── site.css        layout y componentes
│   ├── js/
│   │   ├── publications.js tus datos
│   │   └── site.js         render, filtros, tema, idioma
│   ├── fonts/              Junicode subseteada + OFL.txt
│   ├── img/
│   └── cv/                 tu PDF acá
└── tools/
    ├── build_fonts.py      regenera los woff2 desde el original
    └── sync_shell.py       propaga el riel/pie a las otras páginas
```

---

## Decisiones que ya están tomadas (y por qué)

**Los colores tienen roles fijos, no son intercambiables.** Medí el contraste
de la paleta contra los fondos reales:

| Color | Sobre fondo claro | Sobre fondo oscuro | Rol |
|---|---|---|---|
| `#53424C` | 8.84:1 ✅ AAA | — | texto principal (claro) |
| `#914779` | 5.89:1 ✅ AA | 2.71:1 ❌ | links (sólo en claro) |
| `#00715D` | 5.66:1 ✅ AA | 2.83:1 ❌ | segundo acento (sólo en claro) |
| `#17A68F` | 2.89:1 ❌ | 5.53:1 ✅ AA | decoración en claro, texto en oscuro |
| `#BAA6B2` | 2.17:1 ❌ | 7.37:1 ✅ AAA | bordes en claro, texto gris en oscuro |

Por eso en tema oscuro el violeta se aclara a `#D890BE` (6.95:1) y el verde
brillante pasa a ser el acento legible. Si cambiás un color, medí de nuevo:
usar `#17A68F` como texto sobre fondo claro reprueba WCAG AA.

**El tema es claro u oscuro, sin opción automática.** La primera visita sigue
la preferencia del sistema; apenas tocás un botón, queda fijo en ese navegador.

**El ancho está calibrado.** `--shell` (74rem) y `--measure` (47rem) van
juntos: riel + separación + texto ≈ el ancho total, para que la columna de
lectura llegue hasta el margen derecho en vez de quedar flotando al medio. Si
subís uno, subí el otro; si no, vuelve a aparecer el hueco a la derecha.

**Junicode está subseteada.** Trae ~3000 glifos medievalistas. Recortada a
latín, las cuatro variantes pesan 159 KB en vez de 1978 KB (−92 %).
Ver [`assets/fonts/README.md`](assets/fonts/README.md).

**Junicode es OFL 1.1**, y eso obliga a distribuir `assets/fonts/OFL.txt` junto
con las fuentes. No lo borres.

**Sin JavaScript**, About y CV se ven perfectas y el idioma sigue funcionando
(lo resuelve el CSS); sólo la lista de publicaciones necesita JS, y hay un
`<noscript>` que remite a ORCID y Scholar.
