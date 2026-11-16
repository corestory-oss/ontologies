// Copyright (c) 2026 CoreStory, Inc.
// SPDX-License-Identifier: Apache-2.0
// Local search only: no analytics, third-party requests, or HTML interpolation.
(() => {
  'use strict';
  const LIMIT = 12;
  const MAX_QUERY_LENGTH = 200;
  const normalize = value => value.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
  const queryPrefix = value => value.slice(0, MAX_QUERY_LENGTH).trim();

  function iriKey(value) {
    // Only scheme and host are case-insensitive. Do not use text normalization
    // or URL serialization: either can rewrite a case-sensitive/literal path.
    if (typeof value !== 'string' || /[\s\u0000-\u0020\u007f-\u009f\uD800-\uDFFF<>"{}|^`\\]/u.test(value) ||
        /%(?![0-9a-f]{2})/i.test(value)) return null;
    const parts = /^(https?):\/\/([^/?#]+)(.*)$/i.exec(value);
    if (!parts || parts[2].includes('@')) return null;
    try {
      new URL(value); // Validate the host and port, without rewriting the IRI.
    } catch (_) {
      return null;
    }
    return parts[1].toLowerCase() + '://' + parts[2].toLowerCase() + parts[3];
  }

  function prepare(index) {
    if (index.version !== 1 || !Array.isArray(index.entries)) throw new Error('Unsupported search index');
    return index.entries.map(entry => {
      const iri = iriKey(entry.iri);
      if (!['Class', 'Property', 'Guide'].includes(entry.kind) ||
          !['id', 'title', 'url', 'text', 'description'].every(key => typeof entry[key] === 'string') ||
          !/^(reference\/#[^\s]+|guides\/[a-zA-Z0-9_./-]+\.html)$/.test(entry.url) ||
          entry.url.split('/').includes('..') ||
          ((entry.kind !== 'Guide' || entry.iri !== undefined) && !iri) ||
          (entry.kind !== 'Guide' && (typeof entry.ontology !== 'string' || typeof entry.version !== 'string')) ||
          (entry.headings && (!Array.isArray(entry.headings) || entry.headings.some(h =>
            typeof h.id !== 'string' || typeof h.title !== 'string')))) {
        throw new Error('Invalid search entry');
      }
      return {entry, iri, name: normalize(entry.id), title: normalize(entry.title), text: normalize(entry.text)};
    });
  }

  function search(records, query) {
    const boundedQuery = queryPrefix(query);
    const iri = iriKey(boundedQuery);
    const needle = normalize(boundedQuery);
    if (!needle) return [];
    const words = needle.split(/\s+/);
    return records.flatMap(record => {
      const {entry, name, title, text} = record;
      const exactIri = iri !== null && record.iri === iri;
      if (!exactIri && !words.every(word => (name + ' ' + title + ' ' + text).includes(word))) return [];
      const score = exactIri ? 1000 : (name === needle ? 100 : title === needle ? 90 : 0) +
        (name.endsWith(' ' + needle) ? 60 : 0) + (title.startsWith(needle) ? 40 : 0) +
        (name.includes(needle) ? 20 : 0) + (title.includes(needle) ? 10 : 0);
      const heading = (entry.headings || []).find(h => words.every(word => normalize(h.title).includes(word)));
      return [{entry, score, url: entry.url + (heading ? '#' + encodeURIComponent(heading.id) : ''),
        heading: heading ? heading.title : ''}];
    }).sort((left, right) => right.score - left.score ||
      (left.entry.id < right.entry.id ? -1 : left.entry.id > right.entry.id ? 1 : 0));
  }

  // The pure matching contract can also run under Node, without a DOM or dependencies.
  if (typeof module !== 'undefined' && module.exports) module.exports = {LIMIT, MAX_QUERY_LENGTH, normalize, prepare, search};
  if (typeof document === 'undefined') return;
  const panel = document.querySelector('[data-search]');
  if (!panel) return;
  const root = new URL('../', document.currentScript.src);
  const input = panel.querySelector('[data-search-input]');
  const form = panel.querySelector('[data-search-form]');
  const results = panel.querySelector('[data-search-results]');
  const status = panel.querySelector('[data-search-status]');
  const retry = panel.querySelector('[data-search-retry]');
  let records;
  let pending;
  let timer;

  function show() {
    results.replaceChildren();
    retry.hidden = true;
    const query = queryPrefix(input.value);
    if (!normalize(query)) {
      status.textContent = 'Enter a term or topic to begin.';
      return;
    }
    const matches = search(records, query);
    status.textContent = matches.length ?
      (matches.length > LIMIT ? `Showing ${LIMIT} of ${matches.length} results. Add another word to narrow your search.` :
        `${matches.length} result${matches.length === 1 ? '' : 's'}.`) :
      'No matches. Try a term name, a shorter phrase, or a topic such as evidence or validation.';
    for (const match of matches.slice(0, LIMIT)) {
      const {entry} = match;
      const item = document.createElement('li');
      const link = document.createElement('a');
      link.href = new URL(match.url, root).href;
      link.textContent = entry.title + (match.heading ? ' — ' + match.heading : '');
      const context = document.createElement('p');
      context.className = 'search-result-context';
      context.textContent = entry.kind + ' · ' + entry.id +
        (entry.version ? ' · ' + entry.ontology.toUpperCase() + ' ' + entry.version : '') +
        (entry.deprecated ? ' · Deprecated' : '');
      const description = document.createElement('p');
      description.textContent = entry.description;
      item.append(link, context, description);
      results.append(item);
    }
  }

  async function load() {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(new URL('search-index.json', root), {signal: controller.signal});
      if (!response.ok) throw new Error('Search index request failed');
      return prepare(await response.json());
    } finally {
      clearTimeout(timeout);
    }
  }

  async function run() {
    clearTimeout(timer);
    if (!normalize(queryPrefix(input.value)) || records) {
      show();
      return;
    }
    results.replaceChildren();
    retry.hidden = true;
    panel.setAttribute('aria-busy', 'true');
    status.textContent = 'Loading the local search index…';
    try {
      // Share an in-flight request; render the latest input, never an old query.
      pending = pending || load();
      records = await pending;
      show();
    } catch (_) {
      if (normalize(queryPrefix(input.value))) {
        status.textContent = 'Search could not load. Retry, or use Guides and Explore in the navigation.';
        retry.hidden = false;
      } else {
        show();
      }
    } finally {
      pending = null;
      panel.setAttribute('aria-busy', 'false');
    }
  }

  form.addEventListener('submit', event => { event.preventDefault(); run(); });
  input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(run, 150); });
  retry.addEventListener('click', run);
  panel.querySelector('[data-search-clear]').addEventListener('click', () => {
    input.value = '';
    run();
    input.focus();
  });
})();
