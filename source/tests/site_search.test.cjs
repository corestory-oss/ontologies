// Copyright (c) 2026 CoreStory, Inc.
// SPDX-License-Identifier: Apache-2.0
// No packages: node tests/site_search.test.cjs < generated/search-index.json
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {LIMIT, MAX_QUERY_LENGTH, prepare, search} = require('../web/assets/site-search.js');
const index = JSON.parse(fs.readFileSync(0, 'utf8'));
const records = prepare(index);
assert.equal(LIMIT, 12);
assert.deepEqual(search(records, ''), []);
assert.deepEqual(search(records, '   : / '), []);
assert.deepEqual(search(records, 'no-such-term-zzqq999999'), []);
for (const id of ['sao:CallableUnit', 'spec:Requirement', 'specsao:RequirementImplementationLink']) {
  assert.equal(search(records, id)[0].entry.id, id);
  assert.equal(search(records, id.toUpperCase())[0].url, 'reference/#' + id);
}
const terms = index.entries.filter(entry => entry.kind !== 'Guide');
assert.ok(terms.length > 0, 'the generated index must contain real ontology terms');
for (const entry of terms) {
  assert.equal(typeof entry.iri, 'string', entry.id + ' has a literal IRI');
  assert.equal(search(records, entry.iri)[0].entry.iri, entry.iri, entry.iri + ' ranks first');
  assert.equal(search(records, ' \n' + entry.iri + '\t ')[0].url, entry.url);
  const hostCaseVariant = entry.iri.replace(/^https:\/\/ontologies\.corestory\.ai\//,
    'HTTPS://ONTOLOGIES.CORESTORY.AI/');
  assert.equal(search(records, hostCaseVariant)[0].entry.iri, entry.iri);
}
assert.equal(search(records, 'https://ontologies.corestory.ai/sao/System')[0].entry.id, 'sao:System');

const termRecord = (iri, id = 'sao:ZExact') => ({
  kind: 'Class', id, iri, title: 'Unrelated label', description: '', text: '',
  url: 'reference/#' + id, ontology: 'sao', version: 'test',
});
const exact = termRecord('https://ontologies.corestory.ai/sao/System');
const distractors = [
  {...termRecord('https://example.invalid/Name', exact.iri), title: exact.iri, text: exact.iri},
  {...termRecord('https://example.invalid/Title', 'sao:ATitle'), title: exact.iri},
  {...termRecord('https://example.invalid/Text', 'sao:AText'), text: exact.iri.repeat(30)},
];
const priorityRecords = prepare({version: 1, entries: [...distractors, exact]});
assert.equal(search(priorityRecords, exact.iri)[0].entry.id, exact.id,
  'exact IRI outranks exact name, title, and repeated prose even when absent from entry.text');
assert.equal(search(priorityRecords, 'HTTPS://ONTOLOGIES.CORESTORY.AI/sao/System')[0].entry.id, exact.id);

// Paths, query strings, fragments, and escapes retain literal IRI identity.
for (const [firstIri, secondIri] of [
  ['https://example.invalid/sao/System', 'https://example.invalid/sao/system'],
  ['https://example.invalid/sao/System', 'https://example.invalid/SAO/System'],
  ['https://example.invalid/Term?Key=Value', 'https://example.invalid/Term?key=value'],
  ['https://example.invalid/Term#Class', 'https://example.invalid/Term#class'],
  ['https://example.invalid/Term_Name', 'https://example.invalid/Term-Name'],
  ['https://example.invalid/Term/', 'https://example.invalid/Term'],
  ['https://example.invalid/Folder/../Term', 'https://example.invalid/Term'],
  ['https://example.invalid/%53ystem', 'https://example.invalid/System'],
  ['https://example.invalid/%2f', 'https://example.invalid/%2F'],
  ['https://example.invalid/Café', 'https://example.invalid/Cafe\u0301'],
  ['https://example.invalid/Ｔerm', 'https://example.invalid/Term'],
  ['https://example.invalid/😀', 'https://example.invalid/🙂'],
]) {
  const pair = prepare({version: 1, entries: [termRecord(firstIri, 'sao:AFirst'), termRecord(secondIri)]});
  assert.deepEqual(search(pair, firstIri).map(match => match.entry.iri), [firstIri]);
  assert.deepEqual(search(pair, secondIri).map(match => match.entry.iri), [secondIri]);
  assert.deepEqual(pair.map(record => record.entry.iri), [firstIri, secondIri]);
}

for (const iri of [undefined, null, 123, {}, [], '', 'sao:System', '/sao/System', 'https://',
  'https://bad host/System', 'https://example.invalid/System Name', 'https://example.invalid/%oops',
  'https://example.invalid:bad/System', 'https://[broken/System',
  'https://example.invalid/<System>', 'https://example.invalid/\\System',
  'https://example.invalid/\u0000System', 'https://user:password@example.invalid/System',
  'https://example.invalid/\uD800', 'https://example.invalid/\uDC00', 'https://example.invalid/\u0080',
  ' https://example.invalid/System ', 'javascript:alert(1)']) {
  for (const kind of ['Class', 'Property']) {
    assert.throws(() => prepare({version: 1, entries: [{...exact, kind, iri}]}), /Invalid search entry/);
  }
}

assert.equal(MAX_QUERY_LENGTH, 200);
const maxIri = 'https://example.invalid/' + 'x'.repeat(MAX_QUERY_LENGTH - 'https://example.invalid/'.length);
const lengthRecords = prepare({version: 1, entries: [termRecord(maxIri), termRecord(maxIri + 'y', 'sao:Long')]});
assert.equal(search(lengthRecords, maxIri)[0].entry.iri, maxIri);
assert.deepEqual(search(lengthRecords, maxIri + 'y'), search(lengthRecords, maxIri),
  'IRI matching obeys the same 200-character query prefix as text matching');
assert.deepEqual(search(records, ' '.repeat(MAX_QUERY_LENGTH) + exact.iri), []);
assert.deepEqual(search(records, 'sao:CallableUnit' + ' '.repeat(MAX_QUERY_LENGTH) + 'no-such-suffix'),
  search(records, 'sao:CallableUnit'));
assert.equal(search(records, 'CallableUnit')[0].entry.id, 'sao:CallableUnit');
assert.ok(search(records, 'document_db').some(result => result.entry.id === 'sao:DataStoreType'));
for (const [notation, id] of [['List<T>', 'sao:has_type_parameters'], ['Option<T>', 'sao:nullability_model']]) {
  assert.ok(search(records, notation).some(match => match.entry.id === id), notation + ' is searchable');
}
assert.ok(search(records, 'source').length > LIMIT);
assert.deepEqual(search(records, '<script>alert("pwned")</script>'), []);
const guide = {kind: 'Guide', id: 'docs/test.md', title: 'A guide', description: 'Check a graph.',
  text: 'A guide Check a graph. Verify evidence café', url: 'guides/docs/test.html',
  headings: [{id: 'verify-evidence', title: 'Verify evidence'}]};
assert.equal(search(prepare({version: 1, entries: [guide]}), 'verify evidence')[0].url,
  'guides/docs/test.html#verify-evidence');
assert.equal(search(prepare({version: 1, entries: [guide]}), 'café').length, 1);
assert.equal(prepare({version: 1, entries: [guide]})[0].iri, null, 'guides need no ontology IRI');
for (const iri of [null, 123, '', 'not an IRI']) {
  assert.throws(() => prepare({version: 1, entries: [{...guide, iri}]}), /Invalid search entry/);
}
for (const url of ['https://evil.invalid/', '//evil.invalid/', 'javascript:alert(1)', 'guides/../outside.html']) {
  assert.throws(() => prepare({version: 1, entries: [{...guide, url}]}));
}
assert.throws(() => prepare({version: 99, entries: []}));
// Exercise the actual UI callbacks: programmatic input also obeys the cap.
async function checkUiQueryLength() {
  const element = () => ({
    children: [], listeners: {},
    addEventListener(type, listener) { this.listeners[type] = listener; },
    replaceChildren() { this.children = []; },
    append(...children) { this.children.push(...children); },
    setAttribute() {},
  });
  const controls = Object.fromEntries(['input', 'form', 'results', 'status', 'retry', 'clear']
    .map(name => ['[data-search-' + name + ']', element()]));
  const panel = {...element(), querySelector: selector => controls[selector]};
  let fetches = 0;
  const context = {
    URL, AbortController, setTimeout, clearTimeout,
    document: {querySelector: () => panel, createElement: element,
      currentScript: {src: 'https://site.example/assets/site-search.js'}},
    fetch: async () => {
      fetches++;
      return {ok: true, json: async () => ({version: 1, entries: lengthRecords.map(record => record.entry)})};
    },
  };
  vm.runInNewContext(fs.readFileSync(require.resolve('../web/assets/site-search.js'), 'utf8'), context);
  for (const [query, expected] of [
    [' '.repeat(MAX_QUERY_LENGTH) + maxIri, 0],
    [maxIri, 1], [maxIri + 'y', 1],
    [' '.repeat(MAX_QUERY_LENGTH) + maxIri, 0],
  ]) {
    controls['[data-search-input]'].value = query;
    controls['[data-search-form]'].listeners.submit({preventDefault() {}});
    await new Promise(setImmediate);
    assert.equal(controls['[data-search-results]'].children.length, expected);
    if (expected) {
      const link = controls['[data-search-results]'].children[0].children[0];
      assert.equal(link.href, 'https://site.example/reference/#sao:ZExact');
    } else {
      assert.equal(controls['[data-search-status]'].textContent, 'Enter a term or topic to begin.');
    }
  }
  assert.equal(fetches, 1);
}
function checkVideoActivation() {
  const script = fs.readFileSync(require.resolve('../web/assets/guide-video.js'), 'utf8');
  const element = () => ({
    hidden: true, children: [], attrs: {}, listeners: {}, textContent: '',
    addEventListener(type, listener) { this.listeners[type] = listener; },
    setAttribute(name, value) { this.attrs[name] = value; },
    replaceChildren(...children) { this.children = children; },
    focus() { this.focused = true; },
  });
  for (const broken of [false, true]) {
    const button = element(), stage = element(), status = element();
    const controls = {'[data-video-load]': button, '[data-video-stage]': stage, '[data-video-status]': status};
    const created = [];
    const document = {
      querySelector: () => ({querySelector: selector => controls[selector]}),
      createElement(tag) {
        if (broken) throw Error('DOM unavailable');
        const node = {...element(), tag}; created.push(node); return node;
      },
    };
    const refuse = () => { throw Error('No network API or timer is needed by the video facade'); };
    vm.runInNewContext(script, {document, fetch: refuse, XMLHttpRequest: refuse, Image: refuse,
      setTimeout: refuse, setInterval: refuse});
    assert.equal(button.hidden, false);
    assert.equal(created.length, 0, 'no iframe or remote image before activation');
    assert.deepEqual(Object.keys(button.listeners), ['click'], 'native click covers mouse, Enter, and Space');
    button.listeners.click();
    if (broken) {
      assert.match(status.textContent, /could not be loaded/i);
      assert.match(status.textContent, /YouTube link below/);
      assert.equal(created.length, 0);
      continue;
    }
    assert.equal(created.length, 1);
    const frame = created[0];
    assert.equal(frame.tag, 'iframe');
    assert.equal(frame.attrs.src, 'https://www.youtube-nocookie.com/embed/gQVNWIBSrEY?autoplay=0');
    assert.equal(frame.attrs.title, 'Tell the CoreStory of your system - Ontologies Explainer');
    assert.equal(frame.attrs.referrerpolicy, 'strict-origin-when-cross-origin');
    assert.equal(frame.attrs.allow, 'encrypted-media; picture-in-picture; fullscreen');
    assert.equal(frame.focused, true);
    assert.deepEqual(stage.children, [frame]);
    assert.match(status.textContent, /If it does not appear or play/);
    assert.match(status.textContent, /YouTube link below/);
    button.listeners.click();
    assert.equal(created.length, 1, 'repeated activation cannot create another frame');
  }
  vm.runInNewContext(script, {document: {querySelector: () => null}});
  console.log('Video facade: no pre-click requests, exact embed/title/referrer, focus, no autoplay, duplicate guard and failure fallback pass.');
}
checkVideoActivation();
checkUiQueryLength().then(() => {
  console.log(`Search matcher: ${terms.length} real exact IRIs rank first; case/literal identity, missing/malformed IRIs, ` +
    'matcher/UI query length, generic notation, prefixes, headings, empty states, Unicode and unsafe URLs pass.');
}).catch(error => { console.error(error); process.exitCode = 1; });
