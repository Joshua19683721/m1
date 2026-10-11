// Verify the speech-rate preset buttons: that clicking one sets the rate used
// by every kind of speech, and that the active button follows the choice.
'use strict';
const fs = require('fs');
const path = require('path');

const DOCS = path.resolve(__dirname, '..', 'docs');
const file = process.argv[2] || '01-new-term-at-school.html';
const html = fs.readFileSync(path.join(DOCS, file), 'utf8');
const js = html.match(/<script>([\s\S]*?)<\/script>/)[1];

// innerText is what updateRateLabel writes to, so the stub must honour it.
function mkEl(id) {
  const el = {
    id, value: '', disabled: false, hidden: false, textContent: '',
    _attrs: {},
    focus() {}, appendChild() {}, setAttribute(k, v) { this._attrs[k] = v; },
    getAttribute(k) { return this._attrs[k]; },
    selectedOptions: [],
    classList: {
      _s: new Set(),
      add(c) { this._s.add(c); },
      remove(c) { this._s.delete(c); },
      toggle(c, on) { if (on) this._s.add(c); else this._s.delete(c); return on; },
      contains(c) { return this._s.has(c); },
    },
    addEventListener() {},
  };
  Object.defineProperty(el, 'innerText', {
    get() { return this.textContent; },
    set(v) { this.textContent = v; },
  });
  return el;
}

const store = {};
['typePanel', 'btnType', 'typeCount', 'typeTarget', 'typeInput',
 'voiceSelect', 'rateVal', 'ratePresets'].forEach((id) => { store[id] = mkEl(id); });

// The rate preset group, as rendered.
const presets = mkEl('ratePresets');
presets.children = [];
[0.6, 0.9, 1.2].forEach((r) => {
  const b = mkEl('btn-rate');
  b.setAttribute('data-rate', String(r));
  presets.children.push(b);
});
presets.querySelectorAll = (sel) =>
  sel === '.btn-rate' ? presets.children : [];
store.ratePresets = presets;

const utterances = [];
const synth = {
  speaking: false,
  onvoiceschanged: undefined,
  getVoices: () => [],
  speak(u) { utterances.push(u); },
  cancel() {},
};
const fakeWindow = { speechSynthesis: synth };

const api = new Function(
  'window', 'document', 'navigator', 'location', 'speechSynthesis',
  'SpeechSynthesisUtterance',
  js + '\nreturn {speakText: speakText, speakParagraph: speakParagraph, ' +
       'setSpeechRate: setSpeechRate, updateRateLabel: updateRateLabel, ' +
       'typeOnInput: typeOnInput, typeWords: typeWords, ' +
       'get SPEECH_RATE(){return SPEECH_RATE}, ' +
       'typeRestart: function(){typeIdx=0;typeDone=false;}};'
)(fakeWindow,
  { getElementById: (id) => store[id] || null, querySelectorAll: () => [], body: {} },
  {}, {}, synth,
  function Utterance(t) { this.text = t; this.rate = 1; this.voice = null; });

let pass = 0, fail = 0;
const check = (n, c, e) => {
  if (c) { pass++; console.log('  ok   ' + n); }
  else { fail++; console.log('  FAIL ' + n + (e ? '  <- ' + e : '')); }
};

const activeRate = () => {
  for (const b of presets.children) {
    if (b.classList.contains('is-active')) {
      return parseFloat(b.getAttribute('data-rate'));
    }
  }
  return null;
};

// 1) markup: three presets, exactly one active, no slider left behind
check('three rate presets rendered', presets.children.length === 3,
      'n=' + presets.children.length);
// A dead CSS selector is fine; what matters is that no range INPUT remains.
check('no range input left in the page', !/<input[^>]*type="range"/.test(html));
check('no rateRange id left', !html.includes('id="rateRange"'));
// The label starts as static HTML, so seed the stub the way the page renders.
store.rateVal.textContent = '0.9x';
presets.children[1].classList.add('is-active');
check('default is 正常 0.9x', api.SPEECH_RATE === 0.9, 'rate=' + api.SPEECH_RATE);
check('label shows default', store.rateVal.textContent === '0.9x',
      'label=' + store.rateVal.textContent);

// 2) each preset sets the rate and highlights exactly itself
for (const r of [0.6, 0.9, 1.2]) {
  api.setSpeechRate(r);
  check('preset ' + r + 'x sets SPEECH_RATE', api.SPEECH_RATE === r,
        'rate=' + api.SPEECH_RATE);
  check('preset ' + r + 'x updates label', store.rateVal.textContent === r + 'x',
        'label=' + store.rateVal.textContent);
  check('preset ' + r + 'x is the only active one', activeRate() === r,
        'active=' + activeRate());
  check('exactly one active button',
        presets.children.filter(b => b.classList.contains('is-active')).length === 1);
  api.speakText('w');
  check('speakText uses ' + r + 'x', utterances.at(-1).rate === r,
        'rate=' + utterances.at(-1).rate);
}

// 3) paragraph read and typing-practice words inherit the rate
api.setSpeechRate(0.6);
api.speakParagraph(['a b', 'c d']);
check('paragraph read uses the chosen rate', utterances.at(-1).rate === 0.6,
      'rate=' + utterances.at(-1).rate);

const input = store.typeInput;
api.typeRestart();
input.value = 'word ';
api.typeOnInput();
check('typing word uses the chosen rate',
      utterances.at(-1) && utterances.at(-1).rate === 0.6,
      utterances.at(-1) ? 'rate=' + utterances.at(-1).rate : 'no utterance');

// 4) an unknown preset value does not blow up or clear the highlight
api.setSpeechRate(0.9);
api.updateRateLabel('2.5x');
check('unknown value leaves no active button', activeRate() === null,
      'active=' + activeRate());

// 5) every utterance must carry a lang.
// The pages are lang="zh-TW". If lang is left empty and no voice matched (the
// voices list is loaded asynchronously, and the user may not have the voice
// installed), the browser picks by document language and reads English with a
// Chinese voice. Caught in a real browser, not in the unit stub.
store.voiceSelect.selectedOptions = [{ getAttribute: () => null }];
api.speakText('hello');
check('speakText always sets a lang', !!utterances.at(-1).lang,
      'lang=' + JSON.stringify(utterances.at(-1).lang));
check('speakText falls back to en-US with no voice',
      utterances.at(-1).lang === 'en-US', 'lang=' + utterances.at(-1).lang);

api.speakParagraph(['hello there']);
check('paragraph read sets a lang', utterances.at(-1).lang === 'en-US',
      'lang=' + utterances.at(-1).lang);

api.typeRestart();
store.typeInput.value = 'word ';
api.typeOnInput();
check('typing word sets a lang',
      utterances.at(-1) && utterances.at(-1).lang === 'en-US',
      utterances.at(-1) ? 'lang=' + utterances.at(-1).lang : 'no utterance');

console.log('\nrate presets: ' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
