// Behavioural test for the typing-practice logic.
// Extracts typeWords from the real generated page and drives the state machine
// exactly as typeOnInput does, to prove: space speaks the word just typed, and
// completing a sentence advances to the next one.
'use strict';
const fs = require('fs');
const path = require('path');

const DOCS = path.resolve(__dirname, '..', 'docs');

// Pull the real source out of a generated page so we test the shipped code.
function loadPage(file) {
  const html = fs.readFileSync(path.join(DOCS, file), 'utf8');
  const js = html.match(/<script>([\s\S]*?)<\/script>/)[1];
  const sandbox = {};
  const fn = new Function(
    'window', 'document', 'navigator', 'location', 'speechSynthesis',
    'SpeechSynthesisUtterance',
    js + '\nreturn {typeWords: typeWords, TYPE_SENTENCES: TYPE_SENTENCES, ' +
         'typeOnInput: typeOnInput, typeGo: typeGo, typeRender: typeRender, ' +
         'get typeIdx(){return typeIdx}, get typeDone(){return typeDone}, ' +
         'typeRestart: function(){ typeIdx = 0; typeDone = false; typeRender(); }, ' +
         'typeRewind: function(){ typeIdx = 0; typeDone = false; }};'
  );
  const fakeDoc = makeFakeDoc();
  const api = fn(fakeDoc.window, fakeDoc.document, fakeDoc.navigator,
                 fakeDoc.location, fakeDoc.window.speechSynthesis,
                 function Utterance(text) { this.text = text; });
  return { api: api, doc: fakeDoc };
}

// Minimal DOM: just the elements the typing code touches.
function makeFakeDoc() {
  const store = {};
  const mk = (id) => ({
    id: id,
    value: '',
    disabled: false,
    hidden: false,
    textContent: '',
    focus: function () {},
    classList: { toggle: function () {} },
    addEventListener: function () {},
    selectedOptions: [],
    appendChild: function () {},
    setAttribute: function () {},
  });
  ['typePanel', 'btnType', 'typeCount', 'typeTarget', 'typeInput',
   'voiceSelect', 'rateRange', 'rateVal'].forEach((id) => { store[id] = mk(id); });
  store.rateRange.value = '0.8';
  let spokenText = null;
  const synth = {
    speaking: false,
    onvoiceschanged: undefined,
    getVoices: () => [],
    speak(u) { spokenText = u && u.text; },
    cancel() {},
  };
  // The page does `const synth = window.speechSynthesis`, so the recorder has
  // to be reachable through window, not through a bare parameter.
  const window = { speechSynthesis: synth };
  return {
    window: window,
    navigator: {},
    location: {},
    speechSynthesis: synth,
    spoken_reset: function () { spokenText = null; },
    get spoken() { return spokenText; },
    document: {
      getElementById: (id) => store[id] || null,
      querySelectorAll: () => [],
      body: {},
    },
    store: store,
  };
}

let pass = 0, fail = 0;
const pressSpace_kept = null;
function check(name, cond, extra) {
  if (cond) { pass++; console.log('  ok   ' + name); }
  else { fail++; console.log('  FAIL ' + name + (extra ? '  <- ' + extra : '')); }
}

const cases = JSON.parse(fs.readFileSync(path.join(__dirname, 'cases.json'), 'utf8'));

for (const c of cases) {
  console.log('\n== ' + c.file + ' ==');
  const { api, doc } = loadPage(c.file);

  api.typeRestart();
  check('starts at sentence 1', api.typeIdx === 0);

  const input = doc.store.typeInput;

  function pressSpace(value) {
    input.value = value;
    api.typeOnInput();
  }

  const target = api.TYPE_SENTENCES[api.typeIdx];
  const words = api.typeWords(target);
  let acc = '';
  for (let i = 0; i < words.length; i++) {
    acc += (i === 0 ? '' : ' ') + words[i];
    pressSpace(acc + ' ');
    const expect = words[i];
    check('space speaks word ' + (i + 1) + ' ("' + expect + '")',
          doc.spoken && doc.spoken.toLowerCase() === expect,
          'spoken=' + JSON.stringify(doc.spoken));
  }
  check('sentence 1 complete -> advanced to 2', api.typeIdx === 1);

  api.typeGo(1);
  check('typeGo moves forward', api.typeIdx === 2);
  const s3 = api.TYPE_SENTENCES[api.typeIdx];
  const mess = s3.toUpperCase().replace(/ /g, '  ') + '. ';
  pressSpace(mess);
  check('messy case/punctuation still advances', api.typeIdx === 3,
        'idx=' + api.typeIdx + ' value=' + JSON.stringify(input.value));

  api.typeGo(-1);
  const s3b = api.TYPE_SENTENCES[api.typeIdx];
  const before = api.typeIdx;
  pressSpace(api.typeWords(s3b).slice(0, 2).join(' ') + ' ');
  check('partial sentence does not advance', api.typeIdx === before,
        'idx=' + api.typeIdx);

  while (api.typeIdx < api.TYPE_SENTENCES.length - 1) api.typeGo(1);
  api.typeRender();
  const last = api.TYPE_SENTENCES[api.typeIdx];
  pressSpace(api.typeWords(last).join(' ') + ' ');
  check('last sentence sets done', api.typeDone === true);
  check('done disables input', input.disabled === true);
  check('count shows completion',
        doc.store.typeCount.textContent.indexOf('全部完成') !== -1,
        doc.store.typeCount.textContent);

  api.typeGo(5);
  check('typeGo clamps at last index', api.typeIdx === api.TYPE_SENTENCES.length - 1);
  api.typeGo(-99);
  check('typeGo clamps at 0', api.typeIdx === 0);

  api.typeRestart();
  doc.spoken_reset();
  pressSpace('   ');
  check('whitespace only does not speak', doc.spoken === null, doc.spoken);
}

console.log('\n' + '='.repeat(50));
console.log('typing-practice behaviour: ' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
