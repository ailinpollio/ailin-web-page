/* ==========================================================================
   site.js — idioma, tema, navegación activa y render de publicaciones.
   Sin dependencias, sin build.
   ========================================================================== */

(function () {
  "use strict";

  var STORE_THEME = "ailin:theme";
  var STORE_LANG = "ailin:lang";
  var root = document.documentElement;

  function save(key, value) {
    try { localStorage.setItem(key, value); } catch (e) { /* modo privado */ }
  }

  function stored(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }

  function currentLang() {
    return root.getAttribute("data-lang") === "en" ? "en" : "es";
  }

  /* ---------------------------------------------------------------------
     Tema: claro u oscuro, sin opción automática.
     Si nunca elegiste, arranca siguiendo la preferencia del sistema, pero
     apenas tocás un botón queda fijo.
     --------------------------------------------------------------------- */

  (function themeSwitch() {
    var group = document.querySelector("[data-switch='theme']");
    if (!group) return;
    var buttons = Array.prototype.slice.call(group.querySelectorAll("button[data-value]"));

    function effective() {
      var explicit = root.getAttribute("data-theme");
      if (explicit === "light" || explicit === "dark") return explicit;
      return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }

    function sync() {
      var now = effective();
      buttons.forEach(function (btn) {
        btn.setAttribute("aria-pressed", String(btn.dataset.value === now));
      });
    }

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        root.setAttribute("data-theme", btn.dataset.value);
        save(STORE_THEME, btn.dataset.value);
        sync();
      });
    });

    // Mientras no hayas elegido, seguí al sistema si cambia (ej. modo noche).
    var media = window.matchMedia("(prefers-color-scheme: dark)");
    var onChange = function () { if (!root.getAttribute("data-theme")) sync(); };
    if (media.addEventListener) media.addEventListener("change", onChange);
    else if (media.addListener) media.addListener(onChange);

    sync();
  })();

  /* ---------------------------------------------------------------------
     Idioma: español o inglés.
     El texto de las dos versiones ya está en el HTML; el CSS oculta el que
     no corresponde. Acá sólo cambiamos el atributo y los textos que viven
     fuera del <body> (el <title> y la meta description).
     --------------------------------------------------------------------- */

  function applyLang(lang) {
    root.setAttribute("data-lang", lang);
    root.setAttribute("lang", lang);

    var title = document.querySelector("title");
    if (title && title.dataset[lang]) title.textContent = title.dataset[lang];

    var desc = document.querySelector('meta[name="description"]');
    if (desc && desc.dataset[lang]) desc.setAttribute("content", desc.dataset[lang]);

    /* Los aria-label no son texto visible, así que el CSS no puede
       traducirlos. Cualquier elemento con data-aria-es / data-aria-en se
       actualiza acá. */
    document.querySelectorAll("[data-aria-" + lang + "]").forEach(function (node) {
      node.setAttribute("aria-label", node.getAttribute("data-aria-" + lang));
    });
  }

  // Al cargar, alinear title/description/aria-labels con el idioma que el
  // script del <head> ya eligió.
  applyLang(currentLang());

  (function langSwitch() {
    var group = document.querySelector("[data-switch='lang']");
    if (!group) return;
    var buttons = Array.prototype.slice.call(group.querySelectorAll("button[data-value]"));

    function sync() {
      var now = currentLang();
      buttons.forEach(function (btn) {
        btn.setAttribute("aria-pressed", String(btn.dataset.value === now));
      });
    }

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyLang(btn.dataset.value);
        save(STORE_LANG, btn.dataset.value);
        sync();
        if (typeof window.renderPublications === "function") {
          window.renderPublications();
        }
      });
    });

    sync();
  })();

  /* ---------------------------------------------------------------------
     Cursor wug
     Un pajarito celeste reemplaza al puntero y aletea mientras se mueve.
     Se activa sólo con puntero fino (mouse o trackpad) y si nadie pidió
     menos movimiento. En celulares y tablets no se activa: no hay puntero
     que seguir y ocultar el cursor no tendría sentido.
     --------------------------------------------------------------------- */

  (function wugCursor() {
    var finePointer = window.matchMedia("(pointer: fine)").matches;
    var quietMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!finePointer || quietMotion) return;

    /* El wug de la tarjeta de 1958 (copia de dominio público de Wikimedia
       Commons), partido en cuerpo y patas para poder animarlos por separado.
       Ningún trazo es agregado: las dos capas son recortes del original. */
    var wug = document.createElement("div");
    wug.className = "wug";
    wug.setAttribute("aria-hidden", "true");

    var bird = document.createElement("div");
    bird.className = "wug__bird";
    [["wug__body",  "assets/img/wug-body.png"],
     ["wug__leg-l", "assets/img/wug-leg-l.png"],
     ["wug__leg-r", "assets/img/wug-leg-r.png"]].forEach(function (capa) {
      var img = document.createElement("img");
      img.className = capa[0];
      img.src = capa[1];
      img.alt = "";
      img.decoding = "async";
      bird.appendChild(img);
    });
    wug.appendChild(bird);
    document.body.appendChild(wug);
    /* Ojo: el cursor del sistema NO se oculta acá. Se oculta recién cuando el
       wug se dibujó por primera vez (más abajo). Si algo fallara en el medio,
       quedarse sin wug Y sin flecha dejaría la página inusable. */

    /* El puntero cae cerca de la cabeza del wug, arriba a la izquierda, que es
       donde el sistema pone la punta de la flecha. Si lo centráramos, el clic
       aterrizaría más abajo de donde uno cree estar apuntando. */
    var HOTSPOT_X = -14;
    var HOTSPOT_Y = -10;

    var px = 0, py = 0, pending = false, quieto;

    /* Sólo posición. El cuerpo no se inclina ni se deforma al desplazarse:
       lo único que se mueve son las patas, y de eso se encarga el CSS. */
    function draw() {
      pending = false;
      wug.style.transform =
        "translate3d(" + px + "px," + py + "px,0)" +
        "translate(" + HOTSPOT_X + "%," + HOTSPOT_Y + "%)";
    }

    function mover(event) {
      /* Sólo descartamos el dedo. Safari a veces deja pointerType vacío para
         el mouse y el trackpad, así que exigir === "mouse" dejaba la página
         sin wug y sin cursor. El filtro real ya lo hizo (pointer: fine). */
      if (event.pointerType === "touch") return;

      // Recién ahora escondemos la flecha: ya sabemos que vamos a dibujar.
      root.classList.add("has-wug");

      px = event.clientX;
      py = event.clientY;

      wug.classList.add("wug--ready", "wug--flying");
      clearTimeout(quieto);
      quieto = setTimeout(function () {
        wug.classList.remove("wug--flying");   // quieto, las patas descansan
      }, 140);

      /* Una sola actualización por cuadro: mover el puntero dispara muchos
         más eventos que refrescos de pantalla. */
      if (!pending) {
        pending = true;
        requestAnimationFrame(draw);
      }
    }

    /* Escuchamos los dos: pointermove donde exista, y mousemove como red de
       seguridad. Un mismo movimiento puede disparar ambos, pero draw() se
       limita a un dibujo por cuadro, así que no cuesta nada. */
    document.addEventListener("pointermove", mover, { passive: true });
    document.addEventListener("mousemove", mover, { passive: true });

    /* Al hacer clic: picotea una vez y, en el instante del golpe, invierte
       sus colores. Antes el picoteo vivía en el hover y no paraba nunca;
       como respuesta a una acción concreta se lee mucho mejor. */
    var flash;
    document.addEventListener("pointerdown", function () {
      wug.classList.remove("wug--peck");
      void wug.offsetWidth;          // reinicia la animación desde cero
      wug.classList.add("wug--peck");

      clearTimeout(flash);
      flash = setTimeout(function () {
        wug.classList.remove("wug--peck");
      }, 260);                       // igual a la duración del picotazo
    }, { passive: true });

    /* Si el mouse se va de la ventana, el wug se va con él. */
    document.addEventListener("pointerleave", function () {
      wug.classList.remove("wug--ready");
    });
    window.addEventListener("blur", function () {
      wug.classList.remove("wug--ready");
    });
  })();

  /* ---------------------------------------------------------------------
     Últimas películas vistas (página Personal)
     Los datos salen de assets/js/films.js, que reescribe cada día un workflow
     de GitHub Actions leyendo el RSS de Letterboxd. Acá sólo se dibujan.
     --------------------------------------------------------------------- */

  (function films() {
    var mount = document.getElementById("film-list");
    if (!mount || !window.FILMS || !window.FILMS.length) return;

    /* Los pósters se cargan desde el servidor de Letterboxd, no se copian al
       repositorio. Son imágenes con derechos de los estudios: enlazarlas
       apunta a la fuente en vez de redistribuirlas. Si algún día dejan de
       verse, es que cambiaron sus direcciones — regenerá films.js con
       tools/fetch_favourites.py */
    var lista = document.createElement("ul");
    lista.className = "films";

    window.FILMS.forEach(function (peli) {
      var li = document.createElement("li");
      li.className = "film";

      var a = document.createElement("a");
      a.className = "film__link";
      a.href = peli.link;
      a.rel = "noopener";

      if (peli.poster) {
        var img = document.createElement("img");
        img.className = "film__poster";
        img.src = peli.poster;
        /* alt vacío a propósito: el título va escrito justo debajo, y
           repetirlo haría que un lector de pantalla lo diga dos veces. */
        img.alt = "";
        img.loading = "lazy";
        img.width = 600;
        img.height = 900;
        a.appendChild(img);
      }

      var titulo = document.createElement("span");
      titulo.className = "film__title";
      titulo.textContent = peli.title;
      a.appendChild(titulo);
      li.appendChild(a);

      var meta = document.createElement("span");
      meta.className = "film__meta";
      var partes = [];
      if (peli.director) partes.push(peli.director);
      if (peli.year) partes.push(String(peli.year));
      meta.textContent = partes.join(" · ");
      li.appendChild(meta);

      lista.appendChild(li);
    });

    mount.appendChild(lista);
  })();

  /* ---------------------------------------------------------------------
     Marca el enlace de navegación de la página actual
     --------------------------------------------------------------------- */

  (function markCurrentNav() {
    var here = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".nav a").forEach(function (link) {
      var target = link.getAttribute("href");
      if (target === here || (here === "" && target === "index.html")) {
        link.setAttribute("aria-current", "page");
      }
    });
  })();

  /* ---------------------------------------------------------------------
     Publicaciones: agrupar por año, filtrar por tipo
     --------------------------------------------------------------------- */

  var mount = document.getElementById("publication-list");
  if (!mount || !window.PUBLICATIONS) return;

  /* Etiqueta de la chapita que lleva cada publicación (singular). */
  var TYPE_LABEL = {
    es: { journal: "Artículo", preprint: "Preprint", conference: "Congreso",
          chapter: "Capítulo", thesis: "Tesis" },
    en: { journal: "Article", preprint: "Preprint", conference: "Conference",
          chapter: "Chapter", thesis: "Thesis" }
  };

  /* Etiqueta de los botones de filtro (plural), y el orden en que aparecen. */
  var TYPE_ORDER = ["journal", "conference", "preprint", "chapter", "thesis"];

  var FILTER_LABEL = {
    es: { all: "Todas", journal: "Artículos", conference: "Congresos",
          preprint: "Preprints", chapter: "Capítulos", thesis: "Tesis" },
    en: { all: "All", journal: "Articles", conference: "Conferences",
          preprint: "Preprints", chapter: "Chapters", thesis: "Theses" }
  };

  var EMPTY_TEXT = {
    es: "Todavía no hay nada en esta categoría.",
    en: "Nothing here yet."
  };

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  /* Los autores llevan "*" al final para marcar cuál sos vos. Lo sacamos del
     texto visible y en su lugar resaltamos el nombre. */
  function renderAuthors(authors) {
    var p = el("p", "pub__authors");
    (authors || []).forEach(function (author, i) {
      var isMe = author.slice(-1) === "*";
      var name = isMe ? author.slice(0, -1) : author;
      if (i > 0) p.appendChild(document.createTextNode(", "));
      if (isMe) {
        p.appendChild(el("span", "me", name));
      } else {
        p.appendChild(document.createTextNode(name));
      }
    });
    return p;
  }

  /* Devuelve el campo en el idioma activo, con el español como respaldo:
     note / note_en, venue / venue_en. */
  function localized(pub, field) {
    if (currentLang() === "en" && pub[field + "_en"]) return pub[field + "_en"];
    return pub[field];
  }

  function renderPub(pub) {
    var lang = currentLang();
    var item = el("li", "pub");

    var title = el("h3", "pub__title");
    var primary = (pub.links || []).find(function (l) { return l.href && l.href !== "#"; });
    if (primary) {
      var a = el("a", null, pub.title);
      a.href = primary.href;
      a.rel = "noopener";
      title.appendChild(a);
    } else {
      title.textContent = pub.title;
    }
    item.appendChild(title);

    if (pub.authors && pub.authors.length) item.appendChild(renderAuthors(pub.authors));

    var venue = el("p", "pub__venue");
    var venueText = localized(pub, "venue");
    var noteText = localized(pub, "note");
    if (venueText) venue.appendChild(el("em", null, venueText));
    if (noteText) {
      if (venueText) venue.appendChild(document.createTextNode(" · "));
      venue.appendChild(document.createTextNode(noteText));
    }
    if (venue.childNodes.length) item.appendChild(venue);

    var links = el("ul", "pub__links");
    var typeChip = el("li");
    typeChip.appendChild(el("span", "chip", TYPE_LABEL[lang][pub.type] || pub.type || "—"));
    links.appendChild(typeChip);

    (pub.links || []).forEach(function (link) {
      if (!link.href) return;
      var li = el("li");
      var a = el("a", "chip", (lang === "en" && link.label_en) ? link.label_en : link.label);
      a.href = link.href;
      a.rel = "noopener";
      li.appendChild(a);
      links.appendChild(li);
    });
    item.appendChild(links);

    return item;
  }

  var activeFilter = "all";

  function render() {
    mount.textContent = "";

    var visible = window.PUBLICATIONS.filter(function (pub) {
      return activeFilter === "all" || pub.type === activeFilter;
    });

    if (!visible.length) {
      mount.appendChild(el("p", "empty-state", EMPTY_TEXT[currentLang()]));
      return;
    }

    var years = {};
    visible.forEach(function (pub) {
      (years[pub.year] = years[pub.year] || []).push(pub);
    });

    Object.keys(years)
      .sort(function (a, b) { return b - a; })
      .forEach(function (year) {
        var section = el("section", "pub-year");
        section.appendChild(el("h2", null, year));
        var list = el("ul", "pub-list");
        years[year].forEach(function (pub) { list.appendChild(renderPub(pub)); });
        section.appendChild(list);
        mount.appendChild(section);
      });
  }

  var filterBar = document.querySelector("[data-filters]");

  /* Los botones se arman a partir de los tipos que realmente existen en
     publications.js. Así nunca aparece un filtro que no devuelve nada, y al
     agregar una publicación de una categoría nueva el botón sale solo. */
  function buildFilters() {
    if (!filterBar) return;

    var presentes = TYPE_ORDER.filter(function (type) {
      return window.PUBLICATIONS.some(function (pub) { return pub.type === type; });
    });

    // Con una sola categoría, filtrar no cambia nada: escondemos la barra.
    filterBar.hidden = presentes.length < 2;
    if (filterBar.hidden) { activeFilter = "all"; return; }

    // Si el filtro activo quedó sin publicaciones, volvemos a "todas".
    if (activeFilter !== "all" && presentes.indexOf(activeFilter) === -1) {
      activeFilter = "all";
    }

    var lang = currentLang();
    filterBar.querySelectorAll("button[data-filter]").forEach(function (b) {
      b.remove();
    });

    ["all"].concat(presentes).forEach(function (type) {
      var btn = el("button", "filter", FILTER_LABEL[lang][type] || type);
      btn.type = "button";
      btn.dataset.filter = type;
      btn.setAttribute("aria-pressed", String(type === activeFilter));
      filterBar.appendChild(btn);
    });
  }

  function refresh() {
    buildFilters();
    render();
  }

  // El selector de idioma la llama para redibujar las etiquetas traducidas.
  window.renderPublications = refresh;

  if (filterBar) {
    filterBar.addEventListener("click", function (event) {
      var btn = event.target.closest("button[data-filter]");
      if (!btn) return;
      filterBar.querySelectorAll("button[data-filter]").forEach(function (b) {
        b.setAttribute("aria-pressed", String(b === btn));
      });
      activeFilter = btn.dataset.filter;
      render();
    });
  }

  refresh();
})();
