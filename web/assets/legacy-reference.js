// Preserve Garden term bookmarks made when the explorer lived at the site root.
if (/^#(?:sao|spec|specsao|rdf|rdfs|owl|sh|xsd):/.test(window.location.hash)) {
  window.location.replace('./reference/' + window.location.hash);
}
