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
check('voice select present', html.includes('id="voiceSelect"'));
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
check('rate presets are the same three speeds',
      ['data-rate="0.6"', 'data-rate="0.9"', 'data-rate="1.2"']
        .every(s => html.includes(s)));
check('setSpeechRate / updateRateLabel / speechRateLabel present',
      html.includes('function setSpeechRate') &&
      html.includes('function updateRateLabel') &&
      html.includes('function speechRateLabel'));

/* ---------- 5. JS 真的可執行（從頁面抽出來跑） ---------- */
function boot(withData) {
  const store = {};
  const mk = (id) => {
    const el = {
      id, value: '', innerHTML: '', textContent: '', hidden: false,
      disabled: false, className: '', dataset: {}, children: [],
      _attrs: {}, _cls: new Set(),
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
      querySelectorAll: () => [],
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
   'voiceSelect', 'rateVal', 'ratePresets', 'readAll', 'stopRead']
    .forEach((id) => { store[id] = mk(id); });
  store.apiKey.value = 'gsk_test';
  store.level.value = 'intermediate';
  store.qcount.value = '4';
  store.rateVal.textContent = '0.9x';

  const presets = mk('ratePresets');
  presets.children = [];
  [0.6, 0.9, 1.2].forEach((r) => {
    const b = mk('btn-rate');
    b.setAttribute('data-rate', String(r));
    if (r === 0.9) b.classList.add('is-active');
    presets.children.push(b);
  });
  presets.querySelectorAll = (s) => s === '.btn-rate' ? presets.children : [];

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

  // answer() does document.querySelectorAll('.q-card, .card')[qi], so the stub
  // has to be able to actually find the cards renderQuestions appended.
  const byClass = (root, want, out) => {
    (root.children || []).forEach(c => {
      if ((c.className || '').split(/\s+/).includes(want)) out.push(c);
      byClass(c, want, out);
    });
    return out;
  };
  const synth = {
    speaking: false, onvoiceschanged: undefined,
    getVoices: () => [],
    speak(u) { this.last = u; },
    cancel() {},
  };

  // answer() writes into #explain-N, so unknown ids must materialise instead of
  // returning null — a real DOM would have created them already.
  const doc = {
    getElementById: (id) => {
      if (id === 'ratePresets') return presets;
      if (!store[id]) store[id] = mk(id);
      return store[id];
    },
    querySelectorAll: (sel) => {
      const hits = [];
      sel.split(',').forEach(s => {
        byClass(store.questions, s.trim().replace(/^\./, ''), hits);
      });
      return hits;
    },
    createElement: (tag) => mk('created-' + tag),
    addEventListener() {},
    body: mk('body'),
  };

  const api = new Function(
    'window', 'document', 'navigator', 'location', 'speechSynthesis',
    'SpeechSynthesisUtterance', 'fetch', 'localStorage', 'setTimeout',
    js + '\nreturn {' +
    'setSpeechRate, updateRateLabel, speechRateLabel, normalize, normalizeProg,' +
    'buildExplain, buildPrompt, parseJSON, esc, md, state, progCache,' +
    'callGroq, generate, renderAll, answer, updateScore, playSequential,' +
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
  return { api, store, presets, getFetched: () => fetched, doc };
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

const { api, store, presets } = booted;

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

    /* ---------- 7. 答題 ---------- */
    api.answer(0, 1);
    check('answer() records the reply', api.state.answered[0] === 1);
    // The explanation is written into #explain-0, not into #questions.
    const explained = store['explain-0'].innerHTML;
    check('explanation mentions AI disclaimer',
          explained.includes('以下解析由 AI 即時生成，未經人工檢核'),
          'len=' + explained.length);
    check('explanation shows the correct answer line',
          explained.includes('為什麼答案是 B'));

    /* ---------- 8. 語速預設 ---------- */
    const active = () => {
      for (const b of presets.children) if (b.classList.contains('is-active')) return b;
      return null;
    };
    for (const r of [0.6, 0.9, 1.2]) {
      api.setSpeechRate(r);
      check('setSpeechRate(' + r + ') sets the rate', api.SPEECH_RATE === r);
      check('setSpeechRate(' + r + ') moves the highlight',
            active() && active().getAttribute('data-rate') === String(r));
      check('setSpeechRate(' + r + ') updates the label',
            store.rateVal.textContent === r + 'x', store.rateVal.textContent);
    }

    /* ---------- 9. prompt 不含洩漏的答案 ---------- */
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
