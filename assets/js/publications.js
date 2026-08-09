/* ==========================================================================
   publications.js — la única fuente de verdad de la lista de publicaciones.
   Para agregar una: copiá un bloque y editalo. El orden acá no importa,
   el sitio agrupa y ordena por año automáticamente.

   Campos
     year      (número, requerido)
     title     (texto, requerido — va tal cual salió publicado, no se traduce)
     authors   (array; marcá el tuyo con "*" al final para que salga resaltado)
     venue     (revista / congreso / editorial)
     type      "journal" | "preprint" | "conference" | "chapter" | "thesis"
     links     array de { label, href } — opcionalmente label_en
     note      (opcional) una línea corta de contexto

   Traducciones: agregá "_en" al nombre del campo y se usa cuando la página
   está en inglés. Si falta, cae al español. Campos traducibles: venue, note,
   y el label de cada link.

   Los botones de filtro se arman solos a partir de los "type" que aparezcan
   acá: no hay que tocar el HTML al agregar una categoría nueva.
   ========================================================================== */

window.PUBLICATIONS = [
  {
    year: 2026,
    title: "How Bilingual Are SSL Speech Models? Cross-Lingual Probing of " +
           "Articulatory Encoding with Finnish and Russian EMA",
    authors: ["Pollio San Pedro, A.*", "Kinnunen, T.", "Nikolaev, A.", "Pandey, R."],
    venue: "Interspeech 2026",
    venue_en: "Interspeech 2026",
    type: "conference",
    note: "Aceptado.",
    note_en: "Accepted.",
    links: [
      { label: "DOI", href: "https://arxiv.org/abs/2606.31527" }
    ]
    // TODO: cuando salgan las actas, agregá acá el DOI y el PDF:
    //   { label: "DOI", href: "https://doi.org/..." },
    //   { label: "PDF", href: "..." }
  },
  {
    year: 2025,
    title: "The Presence of Articulatory Representations in Self-Supervised " +
           "Speech Models: A Cross-Linguistic Perspective",
    authors: ["Pollio San Pedro, A.*"],
    venue: "Tesis de maestría, European Master’s in Clinical Linguistics",
    venue_en: "Master’s thesis, European Master’s in Clinical Linguistics",
    type: "thesis",
    note: "Dirección: Prof. Dr. Tomi Kinnunen y Dr. Alexandre Nikolaev.",
    note_en: "Advisors: Prof. Dr. Tomi Kinnunen and Dr. Alexandre Nikolaev.",
    links: [
      { label: "DOI", href: "https://erepo.uef.fi/items/0abeb78b-3b19-4d36-8e26-dc76084712dc" }
    ]
  }
];
