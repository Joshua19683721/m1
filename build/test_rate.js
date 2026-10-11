// Verify the speech-rate slider: that every kind of speech uses the rate the
// user dragged to, that the label tracks it, and that the slider position never
// drifts from the stored rate.
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
  'voiceSelect', 'rateVal', 'rateRange'].forEach((id) => { store[id] = mkEl(id); });

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
       'syncRateSlider: syncRateSlider, speechRateLabel: speechRateLabel, ' +
       'typeOnInput: typeOnInput, typeWords: typeWords, ' +
       'get SPEECH_RATE(){return SPEECH_RATE}, ' +
       'get MIN(){return SPEECH_RATE_MIN}, get MAX(){return SPEECH_RATE_MAX}, ' +
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

const slider = store.rateRange;

// 1) markup: a real draggable slider, and the old preset group is gone
const rangeTag = html.match(/<input[^>]*id="rateRange"[^>]*>/);
check('slider is present in the markup', !!rangeTag);
check('slider has type=range', !!rangeTag && /type="range"/.test(rangeTag[0]));
check('slider min is 0.5', !!rangeTag && /min="0\.5"/.test(rangeTag[0]));
check('slider max is 1.5', !!rangeTag && /max="1\.5"/.test(rangeTag[0]));
check('slider step is 0.1', !!rangeTag && /step="0\.1"/.test(rangeTag[0]));
check('slider default value is 0.9', !!rangeTag && /value="0\.9"/.test(rangeTag[0]));
check('slider is labelled', !!rangeTag && /aria-label=/.test(rangeTag[0]));
check('preset buttons are gone', !/class="btn-rate"/.test(html));
check('rate-presets group is gone', !/class="rate-presets"/.test(html));
check('label points at the slider', /<label for="rateRange">/.test(html));

// The label starts as static HTML, so seed the stub the way the page renders.
store.rateVal.textContent = '0.9x';
slider.value = '0.9';
check('default is 0.9x', api.SPEECH_RATE === 0.9, 'rate=' + api.SPEECH_RATE);
check('label shows default', store.rateVal.textContent === '0.9x',
      'label=' + store.rateVal.textContent);
check('bounds are 0.5 to 1.5', api.MIN === 0.5 && api.MAX === 1.5,
      api.MIN + '..' + api.MAX);

// 2) dragging to any position sets the rate, the label and the slider together
for (const r of [0.5, 0.7, 0.9, 1.1, 1.3, 1.5]) {
  // Drive it the way the browser does: set .value then fire oninput.
  slider.value = String(r);
  api.setSpeechRate(slider.value);
  check('drag to ' + r + 'x sets SPEECH_RATE', api.SPEECH_RATE === r,
        'rate=' + api.SPEECH_RATE);
  check('drag to ' + r + 'x updates label', store.rateVal.textContent === r.toFixed(1) + 'x',
        'label=' + store.rateVal.textContent);
  check('drag to ' + r + 'x keeps slider in sync',
        parseFloat(slider.value) === r, 'slider=' + slider.value);
  api.speakText('w');
  check('speakText uses ' + r + 'x', utterances.at(-1).rate === r,
        'rate=' + utterances.at(-1).rate);
}

// 3) values outside the slider's travel are clamped, not accepted blindly
api.setSpeechRate(9);
check('rate above max is clamped to 1.5', api.SPEECH_RATE === 1.5,
      'rate=' + api.SPEECH_RATE);
api.setSpeechRate(0.01);
check('rate below min is clamped to 0.5', api.SPEECH_RATE === 0.5,
      'rate=' + api.SPEECH_RATE);
check('label follows the clamp', store.rateVal.textContent === '0.5x',
      'label=' + store.rateVal.textContent);
api.setSpeechRate('not a number');
check('garbage input keeps a usable rate',
      api.SPEECH_RATE >= 0.5 && api.SPEECH_RATE <= 1.5, 'rate=' + api.SPEECH_RATE);

// 4) every kind of speech inherits the dragged rate
api.setSpeechRate(1.4);
api.speakParagraph(['a b', 'c d']);
check('paragraph read uses the chosen rate', utterances.at(-1).rate === 1.4,
      'rate=' + utterances.at(-1).rate);

const input = store.typeInput;
api.typeRestart();
input.value = 'word ';
api.typeOnInput();
check('typing word uses the chosen rate',
      utterances.at(-1) && utterances.at(-1).rate === 1.4,
      utterances.at(-1) ? 'rate=' + utterances.at(-1).rate : 'no utterance');

// 5) the slider never drifts away from the stored rate
slider.value = '0.5';
api.setSpeechRate(1.1);
check('programmatic change re-syncs the slider', parseFloat(slider.value) === 1.1,
      'slider=' + slider.value);
slider.value = '9';
api.syncRateSlider();
check('syncRateSlider pulls a stray slider back', parseFloat(slider.value) === 1.1,
      'slider=' + slider.value);
slider.value = '1.1';
api.syncRateSlider();
check('syncRateSlider is a no-op when already correct',
      parseFloat(slider.value) === 1.1, 'slider=' + slider.value);

// 6) every utterance must carry a lang.
// The pages are lang="zh-TW". If lang is left empty and no voice matched (the
// voices list is loaded asynchronously, and the user may not have the voice
// installed), the browser picks by document language and reads English with a
// Chinese voice.
store.voiceSelect.selectedOptions = [{ getAttribute: () => null }];
api.setSpeechRate(0.9);
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

console.log('\nrate slider: ' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);