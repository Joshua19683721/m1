// Structural + behavioural checks for docs/reading.html.
// It is a standalone tool page (not one of the 60 lessons), so it gets its own
// test instead of being forced through verify.js.
'use strict';
const fs = require('fs');
const path = require('path');

const DOCS = path.resolve(__dirname, '..', 'docs');
const html = fs.readFileSync(path.join(DOCS, 'reading.html'), 'utf8');

let pass = 0, fail = 0;
const check = (n, c, e) => {
  if (c) { pass++; console.log('  ok   ' + n); }
  else { fail++; console.log('  FAIL ' + n + (e ? '  <- ' + e : '')); }
};

/* ---------- 1. 頁面結構 ---------- */
check('title mentions KET 閱讀理解練習',
      /<title>[^<]*KET 閱讀理解練習/.test(html));
check('back link to index.html', html.includes('href="index.html"'));
check('API key input present', html.includes('id="apiKey"'));
check('level selector present', html.includes('id="level"'));
check('question count selector present', html.includes('id="qcount"'));
check('generate button present', html.includes('id="generate"'));
check('article card present', html.includes('id="articleCard"'));
check('questions container present', html.includes('id="questions"'));
check('score card present', html.includes('id="scoreCard"'));
check('voice name display present', html.includes('id="voiceName"'));
check('readAll + stopRead buttons present',
      html.includes('id="readAll"') && html.includes('id="stopRead"'));

/* ---------- 2. AI 生成標注（使用者明確要求） ---------- */
check('page-level AI disclaimer present', html.includes('未經人工檢核'));
check('per-explanation AI disclaimer present',
      (html.match(/以下解析由 AI 即時生成，未經人工檢核/g) || []).length === 1);
check('拆解 button tooltip flags AI', /看這句話的漸進式拆解與文法解析（內容由 AI 生成，未經人工檢核）/.test(html));
check('progressive popup carries an AI tag', html.includes('<span class="ai-tag">AI 生成</span>'));
check('footer flags AI content', html.includes('由 AI 即時出題，內容未經人工檢核'));

/* ---------- 3. 排版配色沿用 60 課的設計語言 ---------- */
check('uses the project font stack', html.includes('PingFang TC'));
check('uses the project primary colour', html.includes('--primary:#1e3a8a'));
check('uses the project teal accent', html.includes('--teal:#0f766e'));
check('reuses the header block', /<header>[\s\S]*<h1>/.test(html));
check('reuses the tool-row / btn-tool classes',
      html.includes('class="tool-row"') && html.includes('class="btn-tool'));
check('reuses audio-panel + control-group',
      html.includes('class="audio-panel"') && html.includes('class="control-group"'));
check('reuses the badge component', html.includes('class="badge"'));
check('uses the project card radius', html.includes('border-radius:16px'));

/* ---------- 4. 語速控制與 60 課一致 ---------- */
check('rate control is a draggable slider',
      /id="rateRange"[\s\S]{0,200}?type="range"/.test(html) ||
      /type="range"[\s\S]{0,200}?id="rateRange"/.test(html));
check('setSpeechRate / updateRateLabel / speechRateLabel present',
      html.includes('function setSpeechRate') &&
      html.includes('function updateRateLabel') &&
      html.includes('function speechRateLabel'));

/* ---------- 5. JS 真的可執行（從頁面抽出來跑） ---------- */
// Stands in for whatever voices the machine actually has installed.
let availableVoices = [
  { name: 'Microsoft Zira - English (United States)', lang: 'en-US' },
  { name: 'Microsoft Mark - English (United States)', lang: 'en-US' },
  { name: 'Google US English', lang: 'en-US' },
  { name: 'Google 國語（臺灣）', lang: 'zh-TW' },
];

function boot(withData) {
  const store = {};
  const mk = (id) => {
    const el = {
      id, value: '', innerHTML: '', textContent: '', hidden: false,
      disabled: false, className: '', dataset: {}, children: [],
      _attrs: {}, _cls: new Set(),
      // Every real element has a style object; refreshVoices writes to it.
      style: {},
      focus() {},
      // A real appendChild must collect children, or code that checks
      // `el.children.length` (renderArticle does) crashes on the stub.
      appendChild(c) { this.children.push(c); return c; },
      // closeProgressive() calls old.remove(), so the stub needs one.
      remove() {
        const p = this.parent;
        if (p) {
          const i = p.children.indexOf(this);
          if (i >= 0) p.children.splice(i, 1);
        }
      },
      setAttribute(k, v) { this._attrs[k] = v; },
      getAttribute(k) { return this._attrs[k]; },
      addEventListener() {},
      // innerHTML is only a string on the stub, so there are no real child nodes
      // to find; callers already treat a null result as "not present".
      querySelector: () => null,
      // Elements DO get appended children, so class lookup has to recurse —
      // answer() calls card.querySelectorAll('.option') to paint the
      // correct/wrong borders.
      querySelectorAll(sel) {
        const want = sel.trim().replace(/^\./, '');
        const hits = [];
        const walk = (n) => (n.children || []).forEach(c => {
          if ((c.className || '').split(/\s+/).includes(want)) hits.push(c);
          walk(c);
        });
        walk(this);
        return hits;
      },
      classList: {
        add(c) { this._own && this._own._cls.add(c); },
        remove(c) { this._own && this._own._cls.delete(c); },
        toggle(c, on) {
          if (on) this._own._cls.add(c); else this._own._cls.delete(c);
          return on;
        },
        contains(c) { return this._own._cls.has(c); },
      },
    };
    el.classList._own = el;
    // The page writes innerText; keep it in sync with textContent so checks
    // can read either. (In a browser they are the same for visible elements.)
    Object.defineProperty(el, 'innerText', {
      get() { return this.textContent; },
      set(v) { this.textContent = v; },
    });
    return el;
  };
  ['apiKey', 'level', 'qcount', 'generate', 'status', 'articleCard',
   'artTitle', 'artTitleZh', 'artMeta', 'artBody', 'questions', 'scoreCard',
   'voiceSelect', 'rateVal', 'rateRange', 'voiceName', 'readAll', 'stopRead']
    .forEach((id) => { store[id] = mk(id); });
  store.apiKey.value = 'gsk_test';
  store.level.value = 'intermediate';
  store.qcount.value = '4';
  store.rateVal.textContent = '0.9x';
  store.rateRange.value = '0.9';

  const js = html.match(/<script>([\s\S]*?)<\/script>/g)
    .map(s => s.replace(/^<script>/, '').replace(/<\/script>$/, '')).join('\n');

  let fetched = null;
  const fetchStub = (url, opt) => {
    fetched = { url: url, opt: opt };
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({
        choices: [{ message: { content: JSON.stringify(withData) } }]
      }),
    });
  };

  // Real DOM class matching, restricted to one subtree.
  const byClass = (root, want, out) => {
    (root.children || []).forEach(c => {
      if ((c.className || '').split(/\s+/).includes(want)) out.push(c);
      byClass(c, want, out);
    });
    return out;
  };

  // The page has several .card elements outside #questions (the Groq API key
  // card, #articleCard, #scoreCard). Before this was modelled, the stub matched
  // '.card' only inside #questions, which hid a real bug: answer() looked cards
  // up with document.querySelectorAll('.q-card, .card')[qi] and therefore grabbed
  // the API key card, found no .option inside, and never drew the red/green
  // border. So the decoys must hang off the page root exactly as they do in the
  // real document, and matching must consider every node, not just children.
  const pageRoot = mk('body');
  const decoyCards = ['card setup', 'card article', 'card score'].map(cls => {
    const e = mk(cls);
    e.className = cls;
    pageRoot.children.push(e);   // siblings of #questions, earlier in the document
    return e;
  });
  pageRoot.children.push(store.questions);

  const synth = {
    speaking: false, onvoiceschanged: undefined,
    getVoices: () => availableVoices,
    speak(u) { spoken.push(u); },
    cancel() {},
  };
  const spoken = [];

  // answer() writes into #explain-N, so unknown ids must materialise instead of
  // returning null — a real DOM would have created them already.
  const doc = {
    getElementById: (id) => {
      if (!store[id]) store[id] = mk(id);
      return store[id];
    },
    querySelectorAll: (sel) => {
      const hits = [];
      sel.split(',').forEach(raw => {
        const s = raw.trim();
        // '#questions .card' scopes to the question container; a bare '.card'
        // searches the whole document, decoys included.
        const scoped = /^#questions\s+/.test(s);
        const cls = s.replace(/^#questions\s+/, '').replace(/^\./, '');
        if (scoped) byClass(store.questions, cls, hits);
        else byClass(pageRoot, cls, hits);
      });
      return hits;
    },
    createElement: (tag) => mk('created-' + tag),
    addEventListener() {},
    body: pageRoot,
  };

  const api = new Function(
    'window', 'document', 'navigator', 'location', 'speechSynthesis',
    'SpeechSynthesisUtterance', 'fetch', 'localStorage', 'setTimeout',
    js + '\nreturn {' +
    'setSpeechRate, updateRateLabel, speechRateLabel, normalize, normalizeProg,' +
    'buildExplain, buildPrompt, parseJSON, esc, md, state, progCache,' +
    'callGroq, generate, renderAll, answer, updateScore, playSequential, speak,' +
    'pickVoice, refreshVoices, ' +
    'get SPEECH_RATE(){return SPEECH_RATE}};'
  )(
    { speechSynthesis: synth }, doc, {}, {}, synth,
    function Utterance(t) { this.text = t; this.rate = 1; this.voice = null; },
    fetchStub,
    { getItem: () => '', setItem() {} },
    (fn) => fn && fn()
  );

  // `fetched` is written later by the fetch stub, so expose it lazily —
  // returning it directly would snapshot the pre-generate null.
  return { api, store, spoken, getFetched: () => fetched, doc };
}

const SAMPLE = {
  title: 'A Day at the Animal Shelter',
  titleZh: '動物收容所的一天',
  paragraphs: [
    { sentences: [
      { en: 'Last Saturday, our class visited an animal shelter near our school.', zh: '上星期六，我們班參觀了學校附近的一間動物收容所。' },
      { en: 'A kind nurse showed us where the dogs sleep.', zh: '一位親切的護理師帶我們看狗睡覺的地方。' },
    ] },
  ],
  questions: [{
    stem: 'Why did the class visit the shelter?',
    stemZh: '他們為什麼去收容所？',
    options: ['To buy a dog', 'To help the animals', 'To meet the nurse', 'To find a school'],
    optionsZh: ['買狗', '幫助動物', '看護理師', '找學校'],
    answerIndex: 1,
    correctReason: 'The text says they went to help.',
    optionNotes: ['They did not want to buy.', 'Correct.', 'Not the reason.', 'No.'],
    vocab: [{ en: 'shelter', phonetic: '/ˈʃeltər/', zh: '收容所', note: 'a place to stay' }],
    phrases: [{ en: 'look after', phonetic: '', zh: '照顧', note: 'take care of' }],
    grammar: 'because 表原因。',
  }],
};

let booted;
try {
  booted = boot(SAMPLE);
  check('page script evaluates without error', true);
} catch (e) {
  check('page script evaluates without error', false, e.message);
  console.log('\nreading page: ' + pass + ' passed, ' + fail + ' failed');
  process.exit(1);
}

const { api, store, spoken } = booted;

/* ---------- 6. 出題流程 ---------- */
api.generate().then(() => {
  try {
    check('generate() called Groq with the key',
          booted.getFetched() &&
          booted.getFetched().opt.headers.Authorization === 'Bearer gsk_test');
    check('generate() called the Groq endpoint',
          booted.getFetched() && /api\.groq\.com/.test(booted.getFetched().url));
    check('generate() normalised the article',
          api.state.data && api.state.data.paragraphs.length === 1);
    check('article card is shown', store.articleCard.hidden === false);
    check('title rendered', store.artTitle.textContent === 'A Day at the Animal Shelter');
    check('level badge rendered', store.artMeta.textContent === '中級 級');

    /* ---------- 7. 答題：選項必須畫出紅框／綠框 ---------- */
    // 答錯（選 A，正確是 B）：A 紅框、B 綠框。
    api.answer(0, 0);
    check('answer() records the reply', api.state.answered[0] === 0);

    const card = store.questions.children.find(c => (c.className || '') === 'card');
    const opts = card ? card.querySelectorAll('.option') : [];
    check('the question card was found inside #questions', !!card);
    check('its four options are reachable', opts.length === 4, 'n=' + opts.length);
    check('a wrong pick is marked wrong', opts[0] && opts[0].classList.contains('wrong'),
          opts[0] && opts[0].className);
    check('the correct answer is marked correct',
          opts[1] && opts[1].classList.contains('correct'),
          opts[1] && opts[1].className);
    check('an untouched option gets neither class',
          opts[2] && !opts[2].classList.contains('correct') &&
                   !opts[2].classList.contains('wrong'),
          opts[2] && opts[2].className);
    check('all options are locked after answering',
          opts.every(o => o.classList.contains('done')));

    // The explanation is written into #explain-0, not into #questions.
    const explained = store['explain-0'].innerHTML;
    check('explanation mentions AI disclaimer',
          explained.includes('以下解析由 AI 即時生成，未經人工檢核'),
          'len=' + explained.length);
    check('explanation shows the correct answer line',
          explained.includes('為什麼答案是 B'));

    /* ---------- 8. 語速滑桿 ---------- */
    const sliderTag = (html.match(/<input[^>]*rateRange[^>]*>/) || [''])[0];
    check('slider markup is a range input',
          /type="range"/.test(sliderTag) && /id="rateRange"/.test(sliderTag),
          sliderTag.slice(0, 90));
    check('slider spans 0.5 to 1.5',
          /min="0\.5"/.test(sliderTag) && /max="1\.5"/.test(sliderTag),
          sliderTag.slice(0, 90));
    check('preset buttons are gone', !/class="btn-rate"/.test(html));
    for (const r of [0.5, 0.9, 1.3, 1.5]) {
      store.rateRange.value = String(r);
      api.setSpeechRate(store.rateRange.value);
      check('setSpeechRate(' + r + ') sets the rate', api.SPEECH_RATE === r,
            'rate=' + api.SPEECH_RATE);
      check('setSpeechRate(' + r + ') updates the label',
            store.rateVal.textContent === r.toFixed(1) + 'x',
            store.rateVal.textContent);
      check('setSpeechRate(' + r + ') keeps the slider in sync',
            parseFloat(store.rateRange.value) === r,
            'slider=' + store.rateRange.value);
    }
    api.setSpeechRate(99);
    check('rate above max is clamped', api.SPEECH_RATE === 1.5,
          'rate=' + api.SPEECH_RATE);

    /* ---------- 9. 語音固定為 Microsoft Mark (en-US) ---------- */
    check('no voice dropdown left on the reading page', !html.includes('id="voiceSelect"'));
    check('the voice is shown as read-only text', html.includes('id="voiceName"'));
    check('there is no tts_voice preference any more',
          !html.includes("localStorage.setItem('tts_voice'"));

    const mark = api.pickVoice();
    check('pickVoice returns Microsoft Mark',
          mark && mark.name === 'Microsoft Mark - English (United States)', mark && mark.name);
    check('pickVoice is not the Google voice', !/Google/.test(mark.name), mark.name);

    spoken.length = 0;
    api.speak('The weather is lovely today.');
    check('speak() uses Microsoft Mark',
          spoken[0] && spoken[0].voice &&
          spoken[0].voice.name === 'Microsoft Mark - English (United States)',
          spoken[0] && spoken[0].voice && spoken[0].voice.name);
    check('speak() sends the voice lang', spoken[0] && spoken[0].lang === 'en-US',
          spoken[0] && spoken[0].lang);
    check('the label names the voice in use',
          store.voiceName.textContent.indexOf('Microsoft Mark') !== -1,
          store.voiceName.textContent);

    // Mark missing -> another English voice, never a Chinese one.
    const saved = availableVoices;
    availableVoices = [
      { name: 'Microsoft Zira - English (United States)', lang: 'en-US' },
      { name: 'Google 國語（臺灣）', lang: 'zh-TW' },
    ];
    api.refreshVoices();
    const fallback = api.pickVoice();
    check('without Mark it falls back to a Microsoft en-US voice',
          fallback && fallback.name === 'Microsoft Zira - English (United States)',
          fallback && fallback.name);
    check('the fallback never picks a Chinese voice',
          fallback && !/^zh/i.test(fallback.lang), fallback && fallback.lang);
    check('the label warns that Mark is missing',
          store.voiceName.style.color === '#b45309', store.voiceName.style.color);

    availableVoices = [{ name: 'Google 國語（臺灣）', lang: 'zh-TW' }];
    api.refreshVoices();
    check('with no English voice it does not pick a Chinese one', api.pickVoice() === null,
          api.pickVoice() && api.pickVoice().name);
    spoken.length = 0;
    api.speak('hello');
    check('with no English voice it still forces lang=en-US',
          spoken[0] && spoken[0].lang === 'en-US', spoken[0] && spoken[0].lang);

    availableVoices = saved;
    api.refreshVoices();
    check('restoring the roster brings Mark back',
          store.voiceName.textContent.indexOf('Microsoft Mark') !== -1,
          store.voiceName.textContent);

    /* ---------- 10. prompt 不含洩漏的答案 ---------- */
    const p = api.buildPrompt();
    check('prompt asks for Traditional Chinese', p.includes('繁體中文'));
    check('prompt forbids answerProgressive', p.includes('不需要產生 answerProgressive'));

    console.log('\nreading page: ' + pass + ' passed, ' + fail + ' failed');
    process.exit(fail ? 1 : 0);
  } catch (e) {
    check('post-generate checks ran', false, e.message);
    console.log('\nreading page: ' + pass + ' passed, ' + fail + ' failed');
    process.exit(1);
  }
}).catch(e => {
  check('generate() resolved', false, e.message);
  console.log('\nreading page: ' + pass + ' passed, ' + fail + ' failed');
  process.exit(1);
});
